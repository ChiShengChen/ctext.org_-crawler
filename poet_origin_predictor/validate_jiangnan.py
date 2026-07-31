# -*- coding: utf-8 -*-
"""Are fig13's Jiangnan markers model bias or statistically robust?

Three model-agnostic checks:
1. Fisher exact test on poet-level usage (presence) JN vs rest, BH-FDR.
2. Bootstrap (n=100) sign/rank stability of binary LogReg weights.
3. Cross-model agreement: multiclass LinearSVC vs binary LogReg top-50.
"""
import sys
sys.path.insert(0, "/media/meow/One Touch/ctext.org_-crawler/poet_origin_predictor")
import numpy as np
from scipy.stats import fisher_exact
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression

import make_figures as m
import features as feat
from train import build_features

df = m.apply_task(m.load_df(), "circuit")
keep = df["label"].value_counts(); keep = keep[keep >= 8].index
keep = [r for r in keep if r in m.CIRCUIT_COORDS]
df = df[df["label"].isin(keep)].reset_index(drop=True)
le = LabelEncoder(); y = le.fit_transform(df["label"])
X, vec, _ = build_features(df["text"].tolist())
names = list(vec.get_feature_names_out()) + feat.FEATURE_NAMES
jn = list(le.classes_).index("江南道")
yb = (y == jn).astype(int)
mask = yb.astype(bool)
Xd = np.asarray(X.todense())
n_jn, n_ot = mask.sum(), (~mask).sum()

lr = LogisticRegression(max_iter=3000, class_weight="balanced").fit(X, yb)
w = lr.coef_[0]
order = np.argsort(w)[::-1]
TOP = list(order[:16])            # the 16 shown in fig13 (positive side)
TOPNEG = list(order[-10:])        # the 10 negative shown

# ---- 1) Fisher exact on presence, BH-FDR over ALL 8013 features ------
pres = Xd > 0
pvals = np.ones(len(names))
odds = np.zeros(len(names))
for i in range(len(names)):
    a = pres[mask, i].sum(); b = n_jn - a
    c = pres[~mask, i].sum(); d = n_ot - c
    odds[i], pvals[i] = fisher_exact([[a, b], [c, d]])
# Benjamini-Hochberg
mfeat = len(names)
srt = np.argsort(pvals)
bh = np.empty(mfeat)
prev = 1.0
for rank_pos in range(mfeat - 1, -1, -1):
    i = srt[rank_pos]
    q = pvals[i] * mfeat / (rank_pos + 1)
    prev = min(prev, q)
    bh[i] = prev

# ---- 2) bootstrap stability of LogReg weights ------------------------
rng = np.random.RandomState(42)
B = 100
pos_frac = np.zeros(len(names))
topk_frac = np.zeros(len(names))
for b in range(B):
    idx = rng.choice(len(yb), len(yb), replace=True)
    if yb[idx].sum() < 5 or yb[idx].sum() > len(yb) - 5:
        continue
    wb_ = LogisticRegression(max_iter=2000, class_weight="balanced")\
        .fit(X[idx], yb[idx]).coef_[0]
    pos_frac[wb_ > 0] += 1
    topk = np.argsort(wb_)[::-1][:50]
    topk_frac[topk] += 1
pos_frac /= B; topk_frac /= B

# ---- 3) cross-model: multiclass SVC top-50 vs LogReg top-50 ----------
svc = LinearSVC(class_weight="balanced", C=0.5).fit(X, y)
svc_top50 = set(np.argsort(svc.coef_[jn])[::-1][:50])
lr_top50 = set(order[:50])
overlap = len(svc_top50 & lr_top50)

print(f"n = {len(yb)} poets (JN {n_jn} / other {n_ot}); bootstrap B={B}")
print(f"cross-model: SVC-top50 ∩ LogReg-top50 = {overlap}/50\n")
print(f"{'feature':>12s} {'w':>6s} {'use JN':>7s} {'use oth':>8s} "
      f"{'OR':>6s} {'p(Fisher)':>10s} {'q(FDR)':>8s} {'sign+%':>7s} {'top50%':>7s}")
print("--- fig13 positive (toward Jiangnan) ---")
for i in TOP:
    uj = pres[mask, i].mean(); uo = pres[~mask, i].mean()
    print(f"{names[i]:>12s} {w[i]:+.2f} {uj:7.0%} {uo:8.0%} "
          f"{odds[i]:6.2f} {pvals[i]:10.4f} {bh[i]:8.3f} "
          f"{pos_frac[i]:7.0%} {topk_frac[i]:7.0%}")
print("--- fig13 negative (away from Jiangnan) ---")
for i in TOPNEG:
    uj = pres[mask, i].mean(); uo = pres[~mask, i].mean()
    print(f"{names[i]:>12s} {w[i]:+.2f} {uj:7.0%} {uo:8.0%} "
          f"{odds[i]:6.2f} {pvals[i]:10.4f} {bh[i]:8.3f} "
          f"{(1-pos_frac[i]):7.0%} {'-':>7s}")

# how many of the 16 survive each bar
fisher_ok = sum(1 for i in TOP if pvals[i] < 0.05)
fdr_ok = sum(1 for i in TOP if bh[i] < 0.10)
sign_ok = sum(1 for i in TOP if pos_frac[i] >= 0.90)
print(f"\nof 16 shown positive markers: Fisher p<.05: {fisher_ok} | "
      f"FDR q<.10: {fdr_ok} | bootstrap sign-stable >=90%: {sign_ok}")
