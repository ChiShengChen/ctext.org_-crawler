# -*- coding: utf-8 -*-
"""
Robustness checks for the distance-decay and periphery claims (paper §"Distance
decay" and §"Jiangnan vs. the center").

Two questions reviewers tend to ask about small geographic-correlation studies:

  1. Is the reported significance honest? The 36 inter-circuit pairs are NOT
     independent, so the naive Pearson p (the one matplotlib prints on the
     scatter) understates the true uncertainty. We report both the naive p and
     the Mantel permutation p; only the latter is valid.

  2. Is the effect carried by a single outlier (the large, distinctive Jiangnan
     circuit)? We leave each circuit out in turn and re-fit.

Reproduces the numbers quoted in the paper:
  * Distance decay, 9 circuits:  r = +0.40, naive p = 0.016, Mantel p ~ 0.09.
    Leave-one-out keeps r positive throughout (0.24..0.60); dropping Jiangnan
    *strengthens* it (r = 0.60, Mantel p ~ 0.02) -- i.e. NOT an outlier artifact.
  * Periphery (recall vs distance from the capital): not significant (p > 0.3)
    and the sign REVERSES when Jiangnan is removed -- hence reported as a
    Jiangnan-vs-center contrast, not a distance gradient.

Usage:  python3 analysis_distance_decay_robustness.py
"""
import os
import warnings
from math import radians, sin, cos, asin, sqrt

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import recall_score
from scipy.stats import pearsonr, spearmanr

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))

# Tang circuit centroids (lon, lat) -- same table as analysis_distance_decay.py.
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


def mantel(d1, d2, n_perm=10000, seed=42):
    """Return (Pearson r, Mantel permutation p, naive Pearson p, n_pairs)."""
    n = d1.shape[0]
    iu = np.triu_indices(n, 1)
    r, naive_p = pearsonr(d1[iu], d2[iu])
    rng = np.random.RandomState(seed)
    count = 0
    for _ in range(n_perm):
        p = rng.permutation(n)
        if abs(pearsonr(d1[np.ix_(p, p)][iu], d2[iu])[0]) >= abs(r):
            count += 1
    return r, (count + 1) / (n_perm + 1), naive_p, len(iu[0])


def kept_circuits(df, min_poets, min_poems):
    df = df[df["n_poems"] >= min_poems]
    vc = df["region"].value_counts()
    keep = [r for r in vc[vc >= min_poets].index if r in CIRCUIT_COORDS]
    return df[df["region"].isin(keep)].reset_index(drop=True)


def linguistic_geo(regions, df, X):
    cent = np.vstack([np.asarray(X[(df.region == r).values].mean(axis=0)).ravel()
                      for r in regions])
    cent /= (np.linalg.norm(cent, axis=1, keepdims=True) + 1e-12)
    ling = 1 - cent @ cent.T
    geo = np.array([[haversine(CIRCUIT_COORDS[a], CIRCUIT_COORDS[b])
                     for b in regions] for a in regions])
    return geo, ling


def main():
    df_all = pd.read_csv(os.path.join(HERE, "dataset.csv"))

    # ---- Distance decay: paper's fig03 config (>=5 poets -> 9 circuits) ----
    df = kept_circuits(df_all, min_poets=5, min_poems=10)
    regions = sorted(df["region"].unique())
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                          max_features=8000, sublinear_tf=True)
    Xall = vec.fit_transform(df["text"])

    print(f"=== DISTANCE DECAY ({len(regions)} circuits) ===")
    geo, ling = linguistic_geo(regions, df, Xall)
    r, mp, npv, npair = mantel(geo, ling)
    print(f"  FULL: r={r:+.3f} | naive p={npv:.3f} | Mantel p={mp:.3f} "
          f"({npair} pairs)")
    print("  Leave-one-circuit-out:")
    for drop in regions:
        regs = [x for x in regions if x != drop]
        sub = df[df.region != drop].reset_index(drop=True)
        Xs = vec.transform(sub["text"])
        g, l = linguistic_geo(regs, sub, Xs)
        rr, mpp, npp, _ = mantel(g, l)
        flag = "   <-- Jiangnan" if drop == "江南道" else ""
        print(f"    drop {drop}: r={rr:+.3f} | naive p={npp:.3f} | "
              f"Mantel p={mpp:.3f}{flag}")

    # ---- Periphery: recall vs distance from the capital ----
    le = LabelEncoder(); y = le.fit_transform(df["region"]); order = list(le.classes_)
    pred = cross_val_predict(
        LogisticRegression(max_iter=2000, class_weight="balanced"),
        Xall, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    rec = recall_score(y, pred, average=None, labels=range(len(order)))
    distcap = {r: haversine(CIRCUIT_COORDS[r], CIRCUIT_COORDS[CAPITAL]) for r in order}
    dd = np.array([distcap[r] for r in order]); rr = np.asarray(rec)

    print("\n=== PERIPHERY (recall vs distance from Chang'an) ===")
    print("  region  dist_km  recall")
    for r in sorted(order, key=lambda x: distcap[x]):
        print(f"    {r}  {distcap[r]:7.0f}   {rec[order.index(r)]:.3f}")
    rc, pc = pearsonr(dd, rr); rho, pr = spearmanr(dd, rr)
    print(f"  FULL:        Pearson r={rc:+.3f} (p={pc:.3f}) | "
          f"Spearman rho={rho:+.3f} (p={pr:.3f})")
    m = np.array([r != "江南道" for r in order])
    rc2, pc2 = pearsonr(dd[m], rr[m]); rho2, pr2 = spearmanr(dd[m], rr[m])
    print(f"  drop Jiangnan: Pearson r={rc2:+.3f} (p={pc2:.3f}) | "
          f"Spearman rho={rho2:+.3f} (p={pr2:.3f})   <-- sign flips")


if __name__ == "__main__":
    main()
