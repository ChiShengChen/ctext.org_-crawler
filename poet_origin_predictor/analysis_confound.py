# -*- coding: utf-8 -*-
"""
Analysis #1 — Is the "regional signal" real, or a confound?

A reviewer's first objection: maybe the classifier is not reading geography at all
but some correlate of it. We test the two confounds that are clean in this data:

  (A) CORPUS SIZE — prolific poets have more text; if regions differ in average
      corpus length the model might exploit length, not dialect. Control by
      truncating every poet to the SAME character budget and re-running CV.

  (B) ERA — if regions are unevenly distributed across 初/盛/中/晚唐, era could
      masquerade as region. We tabulate region x era (chi-square) and re-run the
      classifier WITHIN each era (era held constant).

(Occupation/gender are intentionally not used as controls: the CBDB 背景 tags are
noisy — e.g. 白居易 is tagged "monk" — and gender is 239:3, too skewed to model.)

If south/north accuracy survives both controls, the regional signal is not merely
a length or era artifact.

Usage:  python3 analysis_confound.py
"""
import os
import re
import csv
import warnings
import collections

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

import build_dataset as bd
from train import SOUTH, NORTH, build_features

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))

# Unified Tang periodisation (pre-618 Sui-Tang folded into 初唐; 五代 >907 dropped).
ERAS = [("初唐", 0, 712), ("盛唐", 713, 765),
        ("中唐", 766, 835), ("晚唐", 836, 907)]


def era_of(year):
    for name, lo, hi in ERAS:
        if lo <= year <= hi:
            return name
    return None


def load_years():
    """poet -> midpoint year, parsed from the birth-death column."""
    years = {}
    with open(bd.DEFAULT_GEO, encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            m = re.match(r"\s*\d+\.\s*(.+?):\s*\d+\s*首", row[0])
            if not m or len(row) < 4:
                continue
            m2 = re.search(r"(\d{3,4})\s*-\s*(\d{3,4})", row[3])
            if m2:
                years[m.group(1).strip()] = (int(m2.group(1)) + int(m2.group(2))) // 2
    return years


def south_north(df):
    df = df.copy()
    df["label"] = df["region"].map(
        lambda r: "南方" if r in SOUTH else ("北方" if r in NORTH else None))
    return df.dropna(subset=["label"]).reset_index(drop=True)


def cv_score(texts, labels):
    le = LabelEncoder(); y = le.fit_transform(labels)
    X, _, _ = build_features(list(texts))
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    pred = cross_val_predict(clf, X, y, cv=skf)
    return accuracy_score(y, pred), f1_score(y, pred, average="macro"), y, pred


def main():
    df = pd.read_csv(os.path.join(HERE, "dataset.csv"))
    df = df[df["n_poems"] >= 10].reset_index(drop=True)
    df = south_north(df)
    print(f"Poets: {len(df)} | 南 {(df.label=='南方').sum()} / 北 {(df.label=='北方').sum()}")

    # ---- Baseline ----
    acc0, f10, _, _ = cv_score(df["text"], df["label"])
    print(f"\n[Baseline] full corpus           acc {acc0:.3f} | macro-F1 {f10:.3f}")

    # ---- (A) Corpus-size control ----
    # Is corpus length itself different by region, and does the model lean on it?
    south_len = df[df.label == "南方"]["n_chars"].median()
    north_len = df[df.label == "北方"]["n_chars"].median()
    print(f"\n=== (A) Corpus-size confound ===")
    print(f"median chars  南 {south_len:.0f} | 北 {north_len:.0f}")
    budget = int(df["n_chars"].quantile(0.25))   # truncate all to a common budget
    trunc = df["text"].str.slice(0, budget)
    accA, f1A, _, _ = cv_score(trunc, df["label"])
    print(f"truncated to {budget} chars/poet     acc {accA:.3f} | macro-F1 {f1A:.3f}")
    print("  -> if close to baseline, signal is NOT a corpus-length artifact")

    # ---- (B) Era control ----
    years = load_years()
    df["era"] = df["poet"].map(lambda p: era_of(years[p]) if p in years else None)
    sub = df.dropna(subset=["era"])
    print(f"\n=== (B) Era confound ===  ({len(sub)} poets with known era)")
    ct = pd.crosstab(sub["era"], sub["label"])
    ct = ct.reindex([e[0] for e in ERAS]).dropna(how="all")
    print(ct.to_string())
    chi2, p, _, _ = chi2_contingency(ct.fillna(0))
    print(f"region x era chi-square: chi2={chi2:.2f}, p={p:.3f} "
          f"({'associated' if p < 0.05 else 'no strong association'})")

    print("\nwithin-era south/north classification:")
    for era, lo, hi in ERAS:
        e = sub[sub.era == era]
        if e["label"].nunique() < 2 or e["label"].value_counts().min() < 5:
            print(f"  {era}: too few poets ({len(e)}) for a fair split")
            continue
        acc, f1, _, _ = cv_score(e["text"], e["label"])
        print(f"  {era}: n={len(e):3d}  acc {acc:.3f} | macro-F1 {f1:.3f}")
    print("  -> signal persisting within eras means it is not just an era artifact")


if __name__ == "__main__":
    main()
