# -*- coding: utf-8 -*-
"""
Hierarchical + hybrid transformer for regional-origin prediction.

The plain fine-tuning baseline (transformer_model.py) is handicapped: it only
ever sees 250-char fragments and averages their probabilities, while the TF-IDF
models read each poet's WHOLE corpus. This script removes that asymmetry.

Pipeline (apples-to-apples with the classical models):
  1. For each poet, slice the (Traditional->Simplified) corpus into 250-char
     windows — same as before.
  2. Encode every window with a frozen classical-Chinese encoder (GuwenBERT) and
     masked-mean-pool its token states -> one vector per window.
  3. Mean-pool the windows of a poet -> a single 768-d POET vector. Now the
     transformer also represents the entire corpus, like TF-IDF does.
  4. Evaluate three feature sets under the SAME StratifiedKFold(5) used for the
     classical models (each poet = one sample): TF-IDF, BERT, BERT+TF-IDF.

This answers "did we give the transformer a fair shot?" and tests whether the
pretrained encoder adds anything ON TOP OF TF-IDF (the hybrid).

Run on GPU:
  conda run -n pytorch291 python transformer_hier.py --task southnorth
"""
import os
import sys
import types
import argparse
import warnings
from importlib.machinery import ModuleSpec

import numpy as np
import pandas as pd

# Stub boto3/botocore (see transformer_model.py) in case of the broken pyOpenSSL.
for _m in ("boto3", "botocore"):
    if _m not in sys.modules:
        mod = types.ModuleType(_m); mod.__spec__ = ModuleSpec(_m, loader=None)
        mod.__version__ = "0.0.0-stub"; sys.modules[_m] = mod

import torch
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score, classification_report
from transformers import AutoTokenizer, AutoModel

from train import SOUTH, NORTH, build_features, apply_task
from nn_model import TorchMLP

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))


def get_converter(simplify):
    if not simplify:
        return lambda s: s
    try:
        import opencc
        return opencc.OpenCC("t2s").convert
    except Exception:
        print("WARNING: opencc missing; using traditional text (lossy for GuwenBERT)")
        return lambda s: s


def chunk(text, n, cap):
    chunks = [text[i:i+n] for i in range(0, len(text), n)]
    chunks = [c for c in chunks if len(c) >= n//2]
    return chunks[:cap] if cap else chunks


@torch.no_grad()
def encode_poets(texts, model_name, convert, chunk_chars, cap, max_len,
                 batch_size, device):
    """Return an (N_poets, H) matrix: masked-mean over tokens, mean over windows."""
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device).eval()

    # Flatten all windows, remember which poet each belongs to.
    flat, owner = [], []
    for i, t in enumerate(texts):
        for c in chunk(convert(t), chunk_chars, cap):
            flat.append(c); owner.append(i)
    if not flat:
        raise RuntimeError("no windows produced")
    owner = np.array(owner)

    vecs = np.zeros((len(flat), model.config.hidden_size), dtype=np.float32)
    for s in range(0, len(flat), batch_size):
        batch = flat[s:s+batch_size]
        enc = tok(batch, truncation=True, padding=True, max_length=max_len,
                  return_tensors="pt").to(device)
        out = model(**enc).last_hidden_state            # (B, L, H)
        mask = enc["attention_mask"].unsqueeze(-1).float()
        emb = (out*mask).sum(1) / mask.sum(1).clamp(min=1)
        vecs[s:s+len(batch)] = emb.cpu().numpy()
        if s % (batch_size*20) == 0:
            print(f"  encoded {s+len(batch)}/{len(flat)} windows", flush=True)

    # Pool windows -> poet vectors.
    H = vecs.shape[1]
    poet = np.zeros((len(texts), H), dtype=np.float32)
    for i in range(len(texts)):
        m = owner == i
        poet[i] = vecs[m].mean(0) if m.any() else 0.0
    return poet


def cv_eval(X, y, folds=5):
    skf = StratifiedKFold(folds, shuffle=True, random_state=42)
    out = {}
    for name, clf in [
        ("LogReg", LogisticRegression(max_iter=3000, class_weight="balanced")),
        ("MLP", TorchMLP(hidden=(256, 64), epochs=120, class_weight="balanced")),
    ]:
        p = cross_val_predict(clf, X, y, cv=skf)
        out[name] = (accuracy_score(y, p), f1_score(y, p, average="macro"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ethanyt/guwenbert-base")
    ap.add_argument("--task", choices=["southnorth", "circuit"], default="southnorth")
    ap.add_argument("--min-poems", type=int, default=10)
    ap.add_argument("--chunk-chars", type=int, default=250)
    ap.add_argument("--cap", type=int, default=30, help="max windows per poet")
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-regions", type=int, default=6)
    ap.add_argument("--no-simplify", action="store_true")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    df = pd.read_csv(os.path.join(HERE, "dataset.csv"))
    df = df[df["n_poems"] >= args.min_poems].reset_index(drop=True)
    if args.task == "southnorth":
        df["label"] = df["region"].map(
            lambda r: "南" if r in SOUTH else ("北" if r in NORTH else None))
        df = df.dropna(subset=["label"]).reset_index(drop=True)
    else:
        df = apply_task(df, "circuit")
        keep = df["label"].value_counts().nlargest(args.max_regions).index
        df = df[df["label"].isin(keep)].reset_index(drop=True)

    y = LabelEncoder().fit_transform(df["label"])
    print(f"Model: {args.model} | device: {device} | task: {args.task} | "
          f"poets: {len(df)}")

    # --- feature sets ---
    print("\nBuilding TF-IDF (full corpus per poet)...")
    Xtf, _, _ = build_features(df["text"].tolist())

    print("Encoding poets with frozen GuwenBERT...")
    convert = get_converter(not args.no_simplify)
    Xb = encode_poets(df["text"].tolist(), args.model, convert,
                      args.chunk_chars, args.cap, args.max_len,
                      args.batch_size, device)
    Xb_s = StandardScaler().fit_transform(Xb)
    Xhy = hstack([Xtf, csr_matrix(Xb_s)]).tocsr()

    print("\n=== 5-fold CV (StratifiedKFold, poet-level — same as classical models) ===")
    print(f"{'features':16s} {'model':8s} {'accuracy':>9s} {'macro-F1':>9s}")
    for fname, X in [("TF-IDF", Xtf), ("BERT(frozen)", Xb_s),
                     ("BERT+TF-IDF", Xhy)]:
        res = cv_eval(X, y)
        for mname, (acc, f1) in res.items():
            print(f"{fname:16s} {mname:8s} {acc:9.3f} {f1:9.3f}")


if __name__ == "__main__":
    main()
