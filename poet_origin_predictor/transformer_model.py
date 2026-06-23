# -*- coding: utf-8 -*-
"""
Transformer fine-tuning for regional-origin prediction.

Fine-tunes a classical-Chinese pretrained encoder (default: GuwenBERT, a RoBERTa
trained on 古文) for the regional classification task described in prompt.md.

A poet's full corpus far exceeds the 512-token limit, so we work in CHUNKS:
each poet's poems are concatenated and sliced into fixed-size windows that
inherit the author's region label. The model is fine-tuned on chunks, and at
evaluation chunk probabilities are averaged per poet to give a poet-level
prediction comparable to the other models.

IMPORTANT — script defaults convert Traditional -> Simplified (opencc) because
GuwenBERT's vocabulary is Simplified; 全唐詩 is Traditional, and without this
~half the characters tokenize to [UNK] and the model never learns (train acc
stays at chance). Pass --no-simplify to disable.

The train/test split is grouped BY POET (GroupShuffleSplit) so no poet's poems
appear in both splits — the model must generalize to unseen poets, not memorize
an author's vocabulary. Single split (not k-fold) because fine-tuning is
expensive.

Run on GPU via the conda env that has CUDA torch, e.g.:
  conda run -n pytorch291 python transformer_model.py --task southnorth \
      --epochs 6 --batch-size 32 --max-len 256 --lr 5e-5
Fallback model that tokenizes Traditional directly: --model bert-base-chinese
"""
import os
import sys
import types
import argparse
import warnings
import collections

# This environment ships a broken pyOpenSSL (its own import raises
# AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY').
# transformers -> accelerate -> boto3 -> botocore -> OpenSSL pulls it in at
# import time even though we never touch AWS. Stub boto3/botocore so the optional
# import succeeds without loading the broken SSL chain.
from importlib.machinery import ModuleSpec
for _m in ("boto3", "botocore"):
    if _m not in sys.modules:
        _mod = types.ModuleType(_m)
        _mod.__spec__ = ModuleSpec(_m, loader=None)
        _mod.__version__ = "0.0.0-stub"
        sys.modules[_m] = _mod

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)

import build_dataset as bd
from train import SOUTH, NORTH

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))


def macro_label(region, task):
    if task == "southnorth":
        if region in SOUTH:
            return "南方"
        if region in NORTH:
            return "北方"
    return region


def get_converter(simplify):
    """Traditional->Simplified converter (GuwenBERT's vocab is simplified).

    全唐詩 is in Traditional Chinese; without conversion ~half the characters
    tokenize to [UNK] and the model cannot learn. Returns identity if disabled
    or opencc is unavailable.
    """
    if not simplify:
        return lambda s: s
    try:
        import opencc
        cc = opencc.OpenCC("t2s")
        return cc.convert
    except Exception:
        print("WARNING: opencc not available; feeding traditional text as-is.")
        return lambda s: s


def load_examples(task, min_poems, chunk_chars, max_per_poet, seed=42,
                  convert=lambda s: s):
    """Return (texts, labels, groups) as fixed-size chunks of each poet's corpus.

    A poet's poems are concatenated and sliced into windows of `chunk_chars`
    characters. Each window is one training example carrying the poet's region
    label; `groups` records the source poet so the split stays leak-free and
    predictions can be averaged back per poet. Windows give the encoder far more
    regional context than a single short poem.
    """
    poems = bd.load_poems(bd.DEFAULT_VOLUMES)
    regions = bd.load_regions(bd.DEFAULT_GEO)
    rng = np.random.RandomState(seed)

    texts, labels, groups = [], [], []
    for poet, plist in poems.items():
        region = regions.get(poet)
        if region is None or len(plist) < min_poems:
            continue
        label = macro_label(region, task)
        if label is None:
            continue
        corpus = convert("".join(plist))
        chunks = [corpus[i:i + chunk_chars]
                  for i in range(0, len(corpus), chunk_chars)]
        chunks = [c for c in chunks if len(c) >= chunk_chars // 2]
        if max_per_poet and len(chunks) > max_per_poet:
            idx = rng.choice(len(chunks), max_per_poet, replace=False)
            chunks = [chunks[i] for i in idx]
        for ch in chunks:
            texts.append(ch)
            labels.append(label)
            groups.append(poet)
    return texts, np.array(labels), np.array(groups)


class PoemDataset(Dataset):
    def __init__(self, enc, y):
        self.enc = enc
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        item = {k: v[i] for k, v in self.enc.items()}
        item["labels"] = self.y[i]
        return item


def train_one_split(model_name, texts, y_idx, groups, classes,
                    tr_mask, te_mask, max_len, epochs, batch_size, lr, device):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(classes)).to(device)

    def encode(idx):
        enc = tok([texts[i] for i in idx], truncation=True, padding="max_length",
                  max_length=max_len, return_tensors="pt")
        return {k: v for k, v in enc.items()}

    tr_idx = np.where(tr_mask)[0]
    te_idx = np.where(te_mask)[0]
    tr_ds = PoemDataset(encode(tr_idx), torch.tensor(y_idx[tr_idx]))
    te_ds = PoemDataset(encode(te_idx), torch.tensor(y_idx[te_idx]))
    tr_dl = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)
    te_dl = DataLoader(te_ds, batch_size=batch_size)

    w = compute_class_weight("balanced", classes=np.arange(len(classes)),
                             y=y_idx[tr_idx])
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32).to(device))
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    # Linear warmup + decay stabilizes BERT fine-tuning (avoids the constant-
    # output collapse seen without it).
    total_steps = len(tr_dl) * epochs
    sched = get_linear_schedule_with_warmup(
        opt, int(0.1 * total_steps), total_steps)

    for ep in range(epochs):
        model.train()
        running, correct, seen = 0.0, 0, 0
        for step, batch in enumerate(tr_dl):
            labels = batch.pop("labels").to(device)
            batch = {k: v.to(device) for k, v in batch.items()}
            opt.zero_grad()
            out = model(**batch).logits
            loss = loss_fn(out, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            running += loss.item()
            correct += (out.argmax(1) == labels).sum().item()
            seen += len(labels)
            if step % 50 == 0:
                print(f"  epoch {ep+1} step {step}/{len(tr_dl)} loss {loss.item():.3f}",
                      flush=True)
        print(f"  epoch {ep+1} avg loss {running/len(tr_dl):.3f} "
              f"train_acc {correct/seen:.3f}", flush=True)

    # Poem-level probabilities on the test split.
    model.eval()
    probs = []
    with torch.no_grad():
        for batch in te_dl:
            batch.pop("labels")
            batch = {k: v.to(device) for k, v in batch.items()}
            p = torch.softmax(model(**batch).logits, dim=1).cpu().numpy()
            probs.append(p)
    probs = np.vstack(probs)
    return te_idx, probs


def aggregate_by_poet(te_idx, probs, groups, y_idx):
    """Average poem probabilities per poet -> one prediction per poet."""
    by_poet = collections.defaultdict(list)
    truth = {}
    for j, gi in enumerate(te_idx):
        poet = groups[gi]
        by_poet[poet].append(probs[j])
        truth[poet] = y_idx[gi]
    poets = sorted(by_poet)
    y_true = np.array([truth[p] for p in poets])
    y_pred = np.array([np.mean(by_poet[p], axis=0).argmax() for p in poets])
    return y_true, y_pred, poets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ethanyt/guwenbert-base")
    ap.add_argument("--task", choices=["southnorth", "circuit"], default="southnorth")
    ap.add_argument("--min-poems", type=int, default=10)
    ap.add_argument("--chunk-chars", type=int, default=200,
                    help="characters per training window (per poet corpus)")
    ap.add_argument("--max-per-poet", type=int, default=8,
                    help="cap chunks sampled per poet (controls compute)")
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--test-size", type=float, default=0.25)
    ap.add_argument("--folds", type=int, default=5,
                    help="grouped CV folds (1 = single grouped hold-out split)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-simplify", action="store_true",
                    help="disable Traditional->Simplified conversion")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Model: {args.model} | device: {device} | task: {args.task}")

    convert = get_converter(not args.no_simplify)
    texts, labels, groups = load_examples(
        args.task, args.min_poems, args.chunk_chars, args.max_per_poet,
        args.seed, convert)
    classes = np.unique(labels)
    cls_idx = {c: i for i, c in enumerate(classes)}
    y_idx = np.array([cls_idx[c] for c in labels])
    print(f"Chunks: {len(texts)} | poets: {len(set(groups))} | classes: {list(classes)}")

    # Build the list of (train_mask, test_mask) folds, grouped by poet so no
    # poet straddles train/test. GroupKFold puts each poet in exactly one test
    # fold, so the per-poet predictions collected across folds cover every poet
    # once -> a single combined report plus per-fold mean +/- std.
    if args.folds and args.folds > 1:
        gkf = GroupKFold(n_splits=args.folds)
        splits = list(gkf.split(texts, y_idx, groups))
        print(f"Grouped {args.folds}-fold CV over {len(set(groups))} poets")
    else:
        gss = GroupShuffleSplit(n_splits=1, test_size=args.test_size,
                                random_state=args.seed)
        splits = list(gss.split(texts, y_idx, groups))
        print("Single grouped hold-out split")

    fold_acc, fold_f1 = [], []
    all_true, all_pred = [], []         # poet-level, accumulated across folds
    for fold, (tr_i, te_i) in enumerate(splits):
        tr_mask = np.zeros(len(texts), bool); tr_mask[tr_i] = True
        te_mask = np.zeros(len(texts), bool); te_mask[te_i] = True
        print(f"\n--- fold {fold+1}/{len(splits)} | train chunks {tr_mask.sum()} "
              f"| test chunks {te_mask.sum()} | test poets "
              f"{len(set(groups[te_mask]))} ---", flush=True)

        te_idx, probs = train_one_split(
            args.model, texts, y_idx, groups, classes, tr_mask, te_mask,
            args.max_len, args.epochs, args.batch_size, args.lr, device)

        y_true, y_pred, _ = aggregate_by_poet(te_idx, probs, groups, y_idx)
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="macro")
        fold_acc.append(acc); fold_f1.append(f1)
        all_true.extend(y_true); all_pred.extend(y_pred)
        print(f"  fold {fold+1} poet-level: accuracy {acc:.3f} | macro-F1 {f1:.3f}")

    print("\n=== Grouped CV summary (poet-level) ===")
    print(f"accuracy  {np.mean(fold_acc):.3f} +/- {np.std(fold_acc):.3f}")
    print(f"macro-F1  {np.mean(fold_f1):.3f} +/- {np.std(fold_f1):.3f}")
    if len(splits) > 1:
        print("\nCombined out-of-fold report (every poet predicted once):")
        print(classification_report(all_true, all_pred,
                                    target_names=list(classes), zero_division=0))


if __name__ == "__main__":
    main()
