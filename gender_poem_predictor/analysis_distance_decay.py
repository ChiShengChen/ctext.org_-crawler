# -*- coding: utf-8 -*-
"""
Analysis #3 — Does linguistic distance between regions track GEOGRAPHIC distance?

This upgrades the claim from "we can classify origin" to the dialect-geography
thesis: poetic language similarity should decay with physical distance. For every
pair of Tang circuits we compute

  * linguistic distance  = 1 - cosine(mean char-TF-IDF vector of each region)
  * confusion            = how often the classifier swaps the two regions
  * geographic distance  = haversine between circuit centroids

and test whether linguistic distance / confusion correlate with geographic
distance (Pearson + Spearman, with a Mantel permutation test for significance,
since pairwise distances are not independent).

We also quantify the paper's periphery-vs-center asymmetry: per-region
identifiability (classifier recall) vs distance from the capital (Chang'an).

Usage:  python3 analysis_distance_decay.py [--min-poets 8]
"""
import os
import argparse
import warnings
from math import radians, sin, cos, asin, sqrt

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import confusion_matrix, recall_score
from scipy.stats import pearsonr, spearmanr

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))

# Tang circuit centroids (lon, lat) — from the project's map scripts.
CIRCUIT_COORDS = {
    "關內道": (108.95, 34.27),   # near Chang'an (capital)
    "河南道": (113.65, 34.76),   # near Luoyang
    "河北道": (114.48, 38.03),
    "江南道": (120.15, 30.28),
    "河東道": (112.55, 37.87),
    "淮南道": (119.42, 32.39),
    "山南道": (106.71, 33.04),
    "隴右道": (103.85, 36.06),
    "劍南道": (104.07, 30.65),
    "嶺南道": (113.25, 23.13),
}
CAPITAL = "關內道"


def haversine(a, b):
    lon1, lat1, lon2, lat2 = map(radians, [a[0], a[1], b[0], b[1]])
    d = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(d))   # km


def mantel_test(d1, d2, n_perm=10000, seed=42):
    """Correlation of two distance matrices with a label-permutation p-value."""
    n = d1.shape[0]
    iu = np.triu_indices(n, 1)
    v1, v2 = d1[iu], d2[iu]
    r = pearsonr(v1, v2)[0]
    rng = np.random.RandomState(seed)
    count = 0
    for _ in range(n_perm):
        p = rng.permutation(n)
        rp = pearsonr(d1[np.ix_(p, p)][iu], v2)[0]
        if abs(rp) >= abs(r):
            count += 1
    return r, (count + 1) / (n_perm + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "dataset.csv"))
    ap.add_argument("--min-poets", type=int, default=8,
                    help="keep circuits with at least this many poets")
    ap.add_argument("--min-poems", type=int, default=10)
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    df = df[df["n_poems"] >= args.min_poems]
    keep = df["region"].value_counts()
    keep = keep[keep >= args.min_poets].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["region"].isin(keep)].reset_index(drop=True)
    regions = sorted(df["region"].unique())
    print(f"Circuits ({len(regions)}): " +
          ", ".join(f"{r}={(df.region==r).sum()}" for r in regions))

    # Char-TF-IDF per poet.
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                          max_features=8000, sublinear_tf=True)
    X = vec.fit_transform(df["text"])

    # Region centroids -> linguistic distance matrix (1 - cosine).
    cent = np.vstack([np.asarray(X[(df.region == r).values].mean(axis=0)).ravel()
                      for r in regions])
    cent /= (np.linalg.norm(cent, axis=1, keepdims=True) + 1e-12)
    ling = 1 - cent @ cent.T

    # Geographic distance matrix.
    geo = np.array([[haversine(CIRCUIT_COORDS[a], CIRCUIT_COORDS[b])
                     for b in regions] for a in regions])

    # Classifier confusion (symmetrized rate) as a second linguistic-closeness proxy.
    le = LabelEncoder(); y = le.fit_transform(df["region"])
    order = list(le.classes_)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    pred = cross_val_predict(clf, X, y, cv=skf)
    cm = confusion_matrix(y, pred).astype(float)
    cm /= cm.sum(axis=1, keepdims=True)            # row-normalized
    conf = (cm + cm.T) / 2                          # symmetric confusion rate
    # reorder confusion to match `regions`
    idx = [order.index(r) for r in regions]
    conf = conf[np.ix_(idx, idx)]
    confdist = 1 - conf                             # high distance = rarely confused

    print("\n=== Distance-decay correlations (region pairs) ===")
    iu = np.triu_indices(len(regions), 1)
    for name, mat in [("linguistic (1-cos)", ling), ("confusion-based", confdist)]:
        r_p, p_mantel = mantel_test(geo, mat)
        rho = spearmanr(geo[iu], mat[iu])[0]
        print(f"  geo vs {name:18s}: Pearson r={r_p:+.3f} (Mantel p={p_mantel:.4f}) "
              f"| Spearman rho={rho:+.3f}")
    print("  (positive r = farther apart geographically -> more linguistically "
          "distant = distance decay)")

    # Periphery vs center: identifiability (recall) vs distance from capital.
    rec = recall_score(y, pred, average=None, labels=range(len(order)))
    dist_cap = {r: haversine(CIRCUIT_COORDS[r], CIRCUIT_COORDS[CAPITAL])
                for r in order}
    rr = np.array([rec[i] for i in range(len(order))])
    dd = np.array([dist_cap[r] for r in order])
    r_cap, p_cap = pearsonr(dd, rr)
    print("\n=== Periphery vs center ===")
    print("  region   dist_to_Chang'an(km)  recall")
    for r in sorted(order, key=lambda x: dist_cap[x]):
        print(f"  {r:6s}  {dist_cap[r]:10.0f}            {rec[order.index(r)]:.3f}")
    print(f"  corr(distance_from_capital, identifiability): r={r_cap:+.3f} (p={p_cap:.3f})")
    print("  (positive = farther from capital -> more identifiable, as the paper claims)")

    # Optional scatter plot.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
        ax[0].scatter(geo[iu], ling[iu])
        ax[0].set_xlabel("geographic distance (km)")
        ax[0].set_ylabel("linguistic distance (1 - cosine)")
        ax[0].set_title("Distance decay of poetic language")
        ax[1].scatter(dd, rr)
        for r in order:
            ax[1].annotate(r, (dist_cap[r], rec[order.index(r)]))
        ax[1].set_xlabel("distance from Chang'an (km)")
        ax[1].set_ylabel("identifiability (recall)")
        ax[1].set_title("Periphery vs center")
        fig.tight_layout()
        out = os.path.join(HERE, "distance_decay.png")
        fig.savefig(out, dpi=120)
        print(f"\nSaved plot -> {out}")
    except Exception as e:
        print(f"(plot skipped: {e})")


if __name__ == "__main__":
    main()
