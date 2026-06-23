# -*- coding: utf-8 -*-
"""
Step 3 — Train and evaluate regional-origin classifiers.

Frames the task as multi-class classification: predict a poet's 道 (Tang circuit
of origin) from their collected poems. Combines two feature families:

  * Character n-gram TF-IDF (lexical / imagery / phrasing signal)
  * Interpretable domain features from features.py (imagery, season, allusion)

Models: Logistic Regression, Linear SVM, Random Forest. Because the regions are
heavily imbalanced, evaluation uses Stratified K-Fold cross-validation and
reports macro-F1 alongside accuracy. The best model is then refit on all data to
expose the most regionally discriminative character features (interpretability).

Usage:  python3 train.py [--min-poems 10] [--folds 5] [--max-regions 6]
"""
import os
import argparse
import warnings

import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix,
)
from sklearn.dummy import DummyClassifier

import features as feat
from nn_model import TorchMLP

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))

# Macro grouping of Tang circuits into broad cultural regions, used by the
# "macro" and "southnorth" tasks (cf. the paper's dialectology framing).
SOUTH = {"江南道", "淮南道", "劍南道", "嶺南道", "山南道"}
NORTH = {"河北道", "河南道", "河東道", "關內道", "隴右道"}


def apply_task(df, task):
    """Relabel df['label'] according to the chosen prediction task."""
    if task == "circuit":
        df["label"] = df["region"]
    elif task == "southnorth":
        df["label"] = df["region"].map(
            lambda r: "南方" if r in SOUTH else ("北方" if r in NORTH else None))
    elif task == "macro":
        # Three-way: lower Yangtze south / central plains / frontier.
        macro = {
            "江南道": "東南", "淮南道": "東南",
            "河北道": "中原", "河南道": "中原", "河東道": "中原", "關內道": "中原",
            "劍南道": "邊陲", "嶺南道": "邊陲", "山南道": "邊陲", "隴右道": "邊陲",
        }
        df["label"] = df["region"].map(macro)
    return df.dropna(subset=["label"])


def load_data(path, min_poems, max_regions, task):
    df = pd.read_csv(path)
    df = df[df["n_poems"] >= min_poems].copy()
    df = apply_task(df, task)
    if task == "circuit" and max_regions:
        keep = df["label"].value_counts().nlargest(max_regions).index
        df = df[df["label"].isin(keep)].copy()
    # Drop classes too small to appear in every CV fold.
    counts = df["label"].value_counts()
    df = df[df["label"].isin(counts[counts >= 5].index)].copy()
    return df.reset_index(drop=True)


def build_features(texts):
    """Return (combined sparse matrix, char_vectorizer, domain_scaler)."""
    char_vec = TfidfVectorizer(
        analyzer="char", ngram_range=(1, 2), min_df=3, max_features=8000,
        sublinear_tf=True,
    )
    X_char = char_vec.fit_transform(texts)

    scaler = StandardScaler()
    X_dom = scaler.fit_transform(feat.vectorize(texts))
    X = hstack([X_char, csr_matrix(X_dom)]).tocsr()
    return X, char_vec, scaler


def evaluate(models, X, y, folds):
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    results = {}
    for name, model in models.items():
        pred = cross_val_predict(model, X, y, cv=skf)
        results[name] = {
            "acc": accuracy_score(y, pred),
            "macro_f1": f1_score(y, pred, average="macro"),
            "pred": pred,
        }
    return results


def report_discriminative(model, char_vec, classes, top=12):
    """Print top positive char features per region for a linear model."""
    if not hasattr(model, "coef_"):
        return
    names = np.array(char_vec.get_feature_names_out())
    n_char = len(names)
    coef = model.coef_
    print("\n=== Most regionally discriminative characters (linear weights) ===")
    if coef.shape[0] == 1:
        # Binary: positive weights -> classes[1], negative -> classes[0].
        c = coef[0][:n_char]
        for cls, idx in ((classes[1], np.argsort(c)[::-1][:top]),
                         (classes[0], np.argsort(c)[:top])):
            toks = [names[j].strip() for j in idx if names[j].strip()]
            print(f"  {cls}: {' '.join(toks)}")
    else:
        for i, cls in enumerate(classes):
            top_idx = np.argsort(coef[i][:n_char])[::-1][:top]
            toks = [names[j].strip() for j in top_idx if names[j].strip()]
            print(f"  {cls}: {' '.join(toks)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "dataset.csv"))
    ap.add_argument("--min-poems", type=int, default=10,
                    help="keep poets with at least this many surviving poems")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--max-regions", type=int, default=6,
                    help="keep the N largest regions (0 = all)")
    ap.add_argument("--task", choices=["circuit", "macro", "southnorth"],
                    default="circuit",
                    help="circuit = 10 道; macro = 3 regions; southnorth = binary")
    args = ap.parse_args()

    df = load_data(args.data, args.min_poems, args.max_regions, args.task)
    print(f"Task: {args.task} | Poets: {len(df)} | Classes: {df['label'].nunique()}")
    print(df["label"].value_counts().to_string())

    le = LabelEncoder()
    y = le.fit_transform(df["label"])
    X, char_vec, scaler = build_features(df["text"].tolist())
    print(f"\nFeature matrix: {X.shape[0]} poets x {X.shape[1]} features")

    models = {
        "Baseline (most-frequent)": DummyClassifier(strategy="most_frequent"),
        "LogisticRegression": LogisticRegression(
            max_iter=2000, class_weight="balanced", C=1.0),
        "LinearSVM": LinearSVC(class_weight="balanced", C=0.5),
        "RandomForest": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1),
        "MLP": TorchMLP(
            hidden=(256, 64), dropout=0.4, epochs=120, class_weight="balanced"),
    }

    print(f"\n=== {args.folds}-fold stratified cross-validation ===")
    results = evaluate(models, X, y, args.folds)
    print(f"{'model':28s} {'accuracy':>9s} {'macro-F1':>9s}")
    for name, r in results.items():
        print(f"{name:28s} {r['acc']:9.3f} {r['macro_f1']:9.3f}")

    # Pick best non-baseline model by macro-F1 for the detailed report.
    best = max(
        (n for n in results if not n.startswith("Baseline")),
        key=lambda n: results[n]["macro_f1"],
    )
    print(f"\n=== Best model: {best} — per-region performance (CV) ===")
    print(classification_report(
        y, results[best]["pred"], target_names=le.classes_, zero_division=0))

    print("Confusion matrix (rows = true, cols = pred):")
    cm = confusion_matrix(y, results[best]["pred"])
    print("      " + " ".join(f"{c[:3]:>4s}" for c in le.classes_))
    for i, c in enumerate(le.classes_):
        print(f"{c[:4]:>5s} " + " ".join(f"{v:4d}" for v in cm[i]))

    # Refit best linear model on all data for interpretability.
    refit = models.get("LogisticRegression")
    refit.fit(X, y)
    report_discriminative(refit, char_vec, le.classes_)
    report_domain_features(df, feat.FEATURE_NAMES)


def report_domain_features(df, names):
    """Mean per-character frequency of each domain feature, by class."""
    dom = feat.vectorize(df["text"].tolist())
    table = pd.DataFrame(dom, columns=names)
    table["label"] = df["label"].values
    means = table.groupby("label").mean()
    print("\n=== Domain-feature averages by region (per-char frequency) ===")
    with pd.option_context("display.float_format", lambda v: f"{v:.4f}",
                           "display.width", 200, "display.max_columns", 50):
        print(means.T.to_string())


if __name__ == "__main__":
    main()
