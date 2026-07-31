# -*- coding: utf-8 -*-
"""What makes Jiangnan poets identifiable? Extract discriminative features."""
import sys, os
sys.path.insert(0, "/media/meow/One Touch/ctext.org_-crawler/poet_origin_predictor")
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import recall_score

import make_figures as m
import features as feat
from train import build_features, apply_task

df = m.apply_task(m.load_df(), "circuit")
keep = df["label"].value_counts(); keep = keep[keep >= 8].index
keep = [r for r in keep if r in m.CIRCUIT_COORDS]
df = df[df["label"].isin(keep)].reset_index(drop=True)
le = LabelEncoder(); y = le.fit_transform(df["label"])
X, vec, scaler = build_features(df["text"].tolist())
names = list(vec.get_feature_names_out()) + feat.FEATURE_NAMES
jn = list(le.classes_).index("江南道")
print("classes:", list(le.classes_), "| n_poets:", len(df),
      "| jiangnan:", (y == jn).sum())

# ---- 1) multiclass SVC (same as fig11) : Jiangnan row weights ----
clf = LinearSVC(class_weight="balanced", C=0.5).fit(X, y)
w = clf.coef_[jn]
order = np.argsort(w)[::-1]

Xd = np.asarray(X.todense())
mask = (y == jn)


def usage(i):
    """share of Jiangnan / other poets with nonzero tf-idf for feature i."""
    col = Xd[:, i]
    return (col[mask] > 0).mean(), (col[~mask] > 0).mean()


print("\n=== Top 30 features pushing TOWARD 江南道 (multiclass SVC) ===")
for i in order[:30]:
    uj, uo = usage(i)
    print(f"{names[i]:>8s}  w={w[i]:+.3f}  used-by: JN {uj:4.0%} vs other {uo:4.0%}")

print("\n=== Top 15 features pushing AWAY from 江南道 ===")
for i in order[-15:][::-1]:
    uj, uo = usage(i)
    print(f"{names[i]:>8s}  w={w[i]:+.3f}  used-by: JN {uj:4.0%} vs other {uo:4.0%}")

# ---- 2) binary Jiangnan vs rest with LogReg (cleaner odds) ----
yb = mask.astype(int)
lr = LogisticRegression(max_iter=3000, class_weight="balanced").fit(X, yb)
wb = lr.coef_[0]
ob = np.argsort(wb)[::-1]
print("\n=== Binary Jiangnan-vs-rest LogReg: top 25 Jiangnan markers ===")
for i in ob[:25]:
    uj, uo = usage(i)
    print(f"{names[i]:>8s}  w={wb[i]:+.3f}  used-by: JN {uj:4.0%} vs other {uo:4.0%}")

# binary CV recall for reference
p = cross_val_predict(LogisticRegression(max_iter=3000, class_weight="balanced"),
                      X, yb, cv=StratifiedKFold(5, shuffle=True, random_state=42))
print("\nbinary JN-vs-rest recall:", recall_score(yb, p, average=None))

# ---- 3) domain (readable) features: Jiangnan mean vs rest ----
print("\n=== Domain features (standardised): Jiangnan mean vs others ===")
nchar = len(vec.get_feature_names_out())
for k, nm in enumerate(feat.FEATURE_NAMES):
    col = Xd[:, nchar + k]
    print(f"{nm:>12s}  JN {col[mask].mean():+.2f}  others {col[~mask].mean():+.2f}")

# ---- 4) ablation: drop place-name-ish chars, does JN recall drop? ----
PLACE = set("吳越楚湘江湖溪浙淮楓橘蓮荷")
drop = [i for i, n in enumerate(names[:nchar]) if any(c in PLACE for c in n)]
print(f"\nablation: dropping {len(drop)} geographically-loaded n-grams "
      f"(chars: {''.join(sorted(PLACE))})")
keep_idx = np.array([i for i in range(X.shape[1]) if i not in set(drop)])
Xa = X[:, keep_idx]
pa = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), Xa, y,
                       cv=StratifiedKFold(5, shuffle=True, random_state=42))
rec_a = recall_score(y, pa, average=None)
pf = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), X, y,
                       cv=StratifiedKFold(5, shuffle=True, random_state=42))
rec_f = recall_score(y, pf, average=None)
for cls, rf_, ra_ in zip(le.classes_, rec_f, rec_a):
    print(f"{cls}: recall full={rf_:.2f}  without-place-chars={ra_:.2f}")
