# -*- coding: utf-8 -*-
"""
Comprehensive statistical follow-up analyses for the origin-prediction study.

  1  Permutation test for South/North accuracy (label shuffling, B=1000)
  2  Bootstrap 95% CIs for accuracy / per-circuit recall / per-era accuracy
     + Fisher test on era differences
  3  Feature-family ablation: char n-grams only / domain only / combined
  4  Era-controlled Jiangnan family tests (stratified permutation)
  5  Function-character vs content-character signal (style vs topic)
  6  Sensitivity: min-poems threshold + learning curve
  7  High-confidence misclassification case table
  8  McNemar between models + Cohen's kappa per task
  9  Style-similarity network: geographic assortativity (permutation)
 10  Circuit dendrogram vs geography (cophenetic correlation, exact perm)

Usage: python3 analyze_stats.py   (prints a report; ~15-30 min, mostly #1)
"""
import sys
import traceback
import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu
from scipy.cluster.hierarchy import linkage, cophenet
from scipy.spatial.distance import squareform
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (accuracy_score, f1_score, recall_score,
                             cohen_kappa_score)
from sklearn.feature_extraction.text import TfidfVectorizer

import make_figures as m
import features as feat
from train import build_features, apply_task, SOUTH, NORTH

RNG = np.random.RandomState(42)
SKF = StratifiedKFold(5, shuffle=True, random_state=42)


def section(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def guard(fn):
    try:
        fn()
    except Exception:
        traceback.print_exc()


# ---- shared data -----------------------------------------------------
df_sn = m.sn_label(m.load_df())
y_sn = LabelEncoder().fit_transform(df_sn["label"])
X_sn, vec_sn, _ = build_features(df_sn["text"].tolist())

df_c = m.apply_task(m.load_df(), "circuit")
keepc = df_c["label"].value_counts(); keepc = keepc[keepc >= 8].index
keepc = [r for r in keepc if r in m.CIRCUIT_COORDS]
df_c = df_c[df_c["label"].isin(keepc)].reset_index(drop=True)
le_c = LabelEncoder(); y_c = le_c.fit_transform(df_c["label"])
X_c, vec_c, _ = build_features(df_c["text"].tolist())

years = m.load_years()


def cv_acc(X, y, model=None):
    model = model or LinearSVC(class_weight="balanced", C=0.5)
    p = cross_val_predict(model, X, y, cv=SKF)
    return accuracy_score(y, p), f1_score(y, p, average="macro"), p


# =====================================================================
def s1_permutation():
    section("1  PERMUTATION TEST: South/North accuracy (B=1000, LinearSVC)")
    acc_obs, f1_obs, _ = cv_acc(X_sn, y_sn)
    B = 1000
    null_acc = np.empty(B)
    for b in range(B):
        yp = RNG.permutation(y_sn)
        null_acc[b] = accuracy_score(
            yp, cross_val_predict(LinearSVC(class_weight="balanced", C=0.5),
                                  X_sn, yp, cv=SKF))
        if (b + 1) % 200 == 0:
            print(f"  ... {b+1}/{B}")
    p = (1 + (null_acc >= acc_obs).sum()) / (B + 1)
    print(f"observed acc={acc_obs:.3f} macroF1={f1_obs:.3f}")
    print(f"null acc: mean={null_acc.mean():.3f} sd={null_acc.std():.3f} "
          f"max={null_acc.max():.3f}")
    print(f"permutation p = {p:.4g}  (B={B})")


# =====================================================================
def s2_bootstrap_cis():
    section("2  BOOTSTRAP 95% CIs + era-difference tests")
    _, _, p_sn = cv_acc(X_sn, y_sn)

    def boot_ci(yt, yp, metric, B=2000):
        n = len(yt); vals = np.empty(B)
        for b in range(B):
            i = RNG.randint(0, n, n)
            vals[b] = metric(yt[i], yp[i])
        return np.percentile(vals, [2.5, 97.5])

    lo, hi = boot_ci(y_sn, p_sn, accuracy_score)
    print(f"S/N accuracy {accuracy_score(y_sn, p_sn):.3f} "
          f"[95% CI {lo:.3f}, {hi:.3f}]  (n={len(y_sn)})")

    _, _, p_c = cv_acc(X_c, y_c)
    for k, cls in enumerate(le_c.classes_):
        msk = y_c == k
        acc = (p_c[msk] == k).mean()
        lo, hi = boot_ci((y_c[msk] == k).astype(int),
                         (p_c[msk] == k).astype(int),
                         lambda a, b: b.mean())
        print(f"  recall {cls}: {acc:.2f} [CI {lo:.2f}, {hi:.2f}] "
              f"(n={msk.sum()})")

    print("\nPer-era S/N accuracy (within-era CV) with CIs:")
    d = df_sn.copy()
    d["era"] = d["poet"].map(lambda q: m.era_of(years[q]) if q in years else None)
    sub = d.dropna(subset=["era"])
    era_pred = {}
    for era, _, _ in m.ERAS:
        e = sub[sub.era == era]
        le = LabelEncoder(); ye = le.fit_transform(e["label"])
        Xe, _, _ = build_features(e["text"].tolist())
        pe = cross_val_predict(LogisticRegression(max_iter=2000,
                                                  class_weight="balanced"),
                               Xe, ye, cv=SKF)
        era_pred[era] = (ye, pe)
        lo, hi = boot_ci(ye, pe, accuracy_score)
        print(f"  {era}: acc={accuracy_score(ye, pe):.2f} "
              f"[CI {lo:.2f}, {hi:.2f}] (n={len(e)})")
    print("\nPairwise era differences (Fisher on correct/wrong counts):")
    eras = [e for e, _, _ in m.ERAS]
    for i in range(len(eras)):
        for j in range(i + 1, len(eras)):
            (y1, p1), (y2, p2) = era_pred[eras[i]], era_pred[eras[j]]
            c1, w1 = (p1 == y1).sum(), (p1 != y1).sum()
            c2, w2 = (p2 == y2).sum(), (p2 != y2).sum()
            _, pv = fisher_exact([[c1, w1], [c2, w2]])
            print(f"  {eras[i]} vs {eras[j]}: p={pv:.3f}")


# =====================================================================
def s3_family_ablation():
    section("3  FEATURE-FAMILY ABLATION (South/North, LogReg + SVC)")
    texts = df_sn["text"].tolist()
    char_vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                               max_features=8000, sublinear_tf=True)
    Xc_ = char_vec.fit_transform(texts)
    from sklearn.preprocessing import StandardScaler
    Xd_ = StandardScaler().fit_transform(feat.vectorize(texts))
    from scipy.sparse import hstack, csr_matrix
    variants = {"char n-grams only": Xc_,
                "domain features only": csr_matrix(Xd_),
                "combined (paper)": hstack([Xc_, csr_matrix(Xd_)]).tocsr()}
    for nm, Xv in variants.items():
        for mdl, mn in [(LogisticRegression(max_iter=2000,
                                            class_weight="balanced"), "LogReg"),
                        (LinearSVC(class_weight="balanced", C=0.5), "SVC")]:
            a, f1_, _ = cv_acc(Xv, y_sn, mdl)
            print(f"  {nm:>22s} | {mn:>6s}: acc={a:.3f} macroF1={f1_:.3f}")


# =====================================================================
def s4_era_controlled_jiangnan():
    section("4  ERA-CONTROLLED JIANGNAN FAMILY TESTS (stratified permutation)")
    d = df_c.copy()
    d["era"] = d["poet"].map(lambda q: m.era_of(years[q]) if q in years else None)
    dated = d.dropna(subset=["era"]).reset_index(drop=True)
    idx_dated = d.dropna(subset=["era"]).index.to_numpy()
    Xd_full = np.asarray(X_c.todense())
    pres = Xd_full > 0
    names = list(vec_c.get_feature_names_out()) + feat.FEATURE_NAMES
    name_idx = {n: i for i, n in enumerate(names)}
    COLLOQ = ["只", "只有", "不是", "多少", "未可", "何言", "好", "偏",
              "添", "謾", "歸去", "莫", "休", "爭得", "如今", "無端"]
    FLORA = ["蘆", "萋", "茗", "茶", "牡丹", "朵", "鱗", "猩", "猿",
             "橘", "楓", "蓮", "荷", "苔", "梅"]
    land_cols = [name_idx["img_mountain"], name_idx["img_water"]]
    fam_scores = {
        "landscape": Xd_full[:, land_cols].mean(1),
        "colloquial": pres[:, [name_idx[t] for t in COLLOQ
                               if t in name_idx]].mean(1),
        "flora": pres[:, [name_idx[t] for t in FLORA
                          if t in name_idx]].mean(1),
    }
    is_jn = (dated["label"] == "江南道").to_numpy()
    eras_arr = dated["era"].to_numpy()
    print(f"dated poets in 6-circuit set: {len(dated)} "
          f"(JN {is_jn.sum()})")
    B = 10000
    for fam, sc_full in fam_scores.items():
        sc = sc_full[idx_dated]
        obs = sc[is_jn].mean() - sc[~is_jn].mean()
        null = np.empty(B)
        for b in range(B):
            perm = is_jn.copy()
            for e in np.unique(eras_arr):
                em = eras_arr == e
                perm[em] = RNG.permutation(perm[em])
            null[b] = sc[perm].mean() - sc[~perm].mean()
        pv = (1 + (null >= obs).sum()) / (B + 1)
        # naive (unstratified) for comparison
        pv_naive = mannwhitneyu(sc[is_jn], sc[~is_jn],
                                alternative="greater").pvalue
        print(f"  {fam:>10s}: diff={obs:+.4f}  era-stratified perm p={pv:.4f}"
              f"  (naive Mann-Whitney p={pv_naive:.4f})")


# =====================================================================
FUNC_CHARS = set("之乎者也而何其於于以為不無有是自相與且若乃焉哉矣耳此彼安"
                 "孰即則雖然故遂復更未曾莫勿非豈但惟唯只又亦皆俱共還仍尚猶"
                 "或每誰爾汝吾我君所能可得應當須欲將已經從向對如同像被把")


def s5_function_vs_content():
    section("5  FUNCTION-CHARACTER vs CONTENT-CHARACTER SIGNAL (S/N)")
    texts = df_sn["text"].tolist()
    base = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                           max_features=8000, sublinear_tf=True)
    Xb = base.fit_transform(texts)
    vocab = base.get_feature_names_out()
    func_idx = [i for i, t in enumerate(vocab)
                if all(c in FUNC_CHARS for c in t)]
    cont_idx = [i for i, t in enumerate(vocab)
                if all(c not in FUNC_CHARS for c in t)]
    print(f"vocab {len(vocab)}: function-only n-grams {len(func_idx)}, "
          f"content-only {len(cont_idx)}")
    for nm, idx in [("function chars only", func_idx),
                    ("content chars only", cont_idx),
                    ("all n-grams", list(range(len(vocab))))]:
        a, f1_, _ = cv_acc(Xb[:, idx], y_sn,
                           LogisticRegression(max_iter=2000,
                                              class_weight="balanced"))
        print(f"  {nm:>20s}: acc={a:.3f} macroF1={f1_:.3f}")


# =====================================================================
def s6_sensitivity():
    section("6  SENSITIVITY: min-poems threshold + learning curve (S/N)")
    for mp in [5, 10, 20]:
        d = m.sn_label(m.load_df(min_poems=mp))
        yv = LabelEncoder().fit_transform(d["label"])
        Xv, _, _ = build_features(d["text"].tolist())
        a, f1_, _ = cv_acc(Xv, yv)
        print(f"  min_poems>={mp:>2d}: n={len(d):>3d}  acc={a:.3f} "
              f"macroF1={f1_:.3f}")
    print("\nlearning curve (fraction of poets, 5 subsamples each):")
    for frac in [0.4, 0.6, 0.8, 1.0]:
        accs = []
        for r in range(5):
            if frac == 1.0 and r > 0:
                break
            rng = np.random.RandomState(r)
            idx = []
            for cls in np.unique(y_sn):
                ci = np.where(y_sn == cls)[0]
                idx.extend(rng.choice(ci, max(10, int(len(ci) * frac)),
                                      replace=False))
            idx = np.array(idx)
            a, _, _ = cv_acc(X_sn[idx], y_sn[idx])
            accs.append(a)
        print(f"  {frac:.0%} of poets (n≈{int(len(y_sn)*frac)}): "
              f"acc={np.mean(accs):.3f} ± {np.std(accs):.3f}")


# =====================================================================
def s7_case_table():
    section("7  HIGH-CONFIDENCE MISCLASSIFICATIONS (S/N, LogReg prob)")
    lr = LogisticRegression(max_iter=2000, class_weight="balanced")
    prob = cross_val_predict(lr, X_sn, y_sn, cv=SKF, method="predict_proba")
    le = LabelEncoder().fit(df_sn["label"])
    pred = prob.argmax(1)
    conf = prob.max(1)
    wrong = np.where(pred != y_sn)[0]
    wrong = wrong[np.argsort(conf[wrong])[::-1]]
    print(f"{'poet':>6s} {'true':>4s} {'pred':>4s} {'conf':>6s} {'era':>4s}")
    for i in wrong[:15]:
        po = df_sn.iloc[i]["poet"]
        era = m.era_of(years[po]) if po in years else "?"
        print(f"{po:>6s} {df_sn.iloc[i]['label']:>4s} "
              f"{le.classes_[pred[i]]:>4s} {conf[i]:6.2f} {str(era):>4s}")


# =====================================================================
def s8_model_tests():
    section("8  McNEMAR BETWEEN MODELS + COHEN'S KAPPA")
    preds = {}
    for nm, mdl in [("LogReg", LogisticRegression(max_iter=2000,
                                                  class_weight="balanced")),
                    ("SVC", LinearSVC(class_weight="balanced", C=0.5)),
                    ("RF", RandomForestClassifier(n_estimators=400,
                                                  class_weight="balanced",
                                                  random_state=42, n_jobs=-1))]:
        preds[nm] = cross_val_predict(mdl, X_sn, y_sn, cv=SKF)
        print(f"  {nm}: acc={accuracy_score(y_sn, preds[nm]):.3f} "
              f"kappa={cohen_kappa_score(y_sn, preds[nm]):.3f}")
    from scipy.stats import binomtest
    ks = list(preds)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = preds[ks[i]], preds[ks[j]]
            b01 = ((a == y_sn) & (b != y_sn)).sum()
            c01 = ((a != y_sn) & (b == y_sn)).sum()
            pv = binomtest(b01, b01 + c01).pvalue if b01 + c01 else 1.0
            print(f"  McNemar {ks[i]} vs {ks[j]}: b={b01} c={c01} p={pv:.3f}")
    # kappa per task granularity (SVC)
    for task, Xv, yv in [("south/north", X_sn, y_sn), ("circuit", X_c, y_c)]:
        p = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5),
                              Xv, yv, cv=SKF)
        print(f"  kappa[{task}] = {cohen_kappa_score(yv, p):.3f}")


# =====================================================================
def s9_network():
    section("9  STYLE-SIMILARITY NETWORK: geographic assortativity")
    from sklearn.preprocessing import normalize
    Xn = normalize(X_sn)
    S = (Xn @ Xn.T).toarray()
    np.fill_diagonal(S, -1)
    k = 10
    same = 0; total = 0
    edges = set()
    for i in range(len(y_sn)):
        for j in np.argsort(S[i])[::-1][:k]:
            edges.add((min(i, j), max(i, j)))
    edges = list(edges)
    obs = np.mean([y_sn[a] == y_sn[b] for a, b in edges])
    B = 2000
    null = np.empty(B)
    for b in range(B):
        yp = RNG.permutation(y_sn)
        null[b] = np.mean([yp[a] == yp[b] for a, b in edges])
    pv = (1 + (null >= obs).sum()) / (B + 1)
    print(f"kNN graph (k={k}, {len(edges)} edges, n={len(y_sn)} poets, S/N)")
    print(f"same-region edge share: observed={obs:.3f}  "
          f"null={null.mean():.3f}±{null.std():.3f}  perm p={pv:.4g}")


# =====================================================================
def s10_dendrogram():
    section("10  CIRCUIT DENDROGRAM vs GEOGRAPHY (cophenetic corr, exact perm)")
    from sklearn.preprocessing import normalize
    regions = sorted(df_c["label"].unique())
    cents = []
    for r in regions:
        msk = (df_c["label"] == r).to_numpy()
        cents.append(np.asarray(X_c[msk].mean(0)).ravel())
    C = np.vstack(cents)
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    ling = 1 - C @ C.T
    Z = linkage(squareform(ling, checks=False), method="average")
    coph = squareform(cophenet(Z))
    geo = np.array([[m.haversine(m.CIRCUIT_COORDS[a], m.CIRCUIT_COORDS[b])
                     for b in regions] for a in regions])
    iu = np.triu_indices(len(regions), 1)
    from scipy.stats import pearsonr
    r_obs = pearsonr(coph[iu], geo[iu])[0]
    from itertools import permutations
    null = []
    for perm in permutations(range(len(regions))):
        pm = np.array(perm)
        null.append(pearsonr(coph[np.ix_(pm, pm)][iu], geo[iu])[0])
    null = np.array(null)
    pv = (null >= r_obs).mean()
    print("regions:", regions)
    print(f"cophenetic(style tree) vs geographic distance: r={r_obs:.3f}, "
          f"exact permutation p={pv:.4f} ({len(null)} perms)")


if __name__ == "__main__":
    for s in [s2_bootstrap_cis, s3_family_ablation, s4_era_controlled_jiangnan,
              s5_function_vs_content, s6_sensitivity, s7_case_table,
              s8_model_tests, s9_network, s10_dendrogram, s1_permutation]:
        guard(s)
    print("\nDONE.")
