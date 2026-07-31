# -*- coding: utf-8 -*-
"""
Generate all result figures for the regional-origin prediction study.

Writes 11 figures (PNG). Most are recomputed from dataset.csv; the transformer
panel reads tf_curve.log if present and otherwise falls back to the metrics
recorded in the README.

Bilingual: pass --lang zh (default, -> ./figures) or --lang en (-> ./figures_en).
The CJK font is used in both languages so the Chinese characters that ARE data
(fig08 discriminative characters) always render.

Figures
  fig01_model_comparison    model accuracy / macro-F1 (south vs north)
  fig02_confusion           circuit confusion matrix + per-circuit recall
  fig03_distance_decay      geographic vs linguistic distance
  fig04_era_evolution       south/north separability by era
  fig05_misclass_by_era     misclassification direction by era
  fig06_region_distribution poets per circuit
  fig07_domain_radar        imagery features, south vs north
  fig08_discriminative_chars top characters per side
  fig09_transformer         transformer protocol / training curve / folds
  fig10_length_control      corpus-length control
  fig11_periphery           distance from capital vs identifiability

Usage:  python3 make_figures.py [--lang zh|en]
"""
import os
import re
import csv
import argparse
import warnings
from math import radians, sin, cos, asin, sqrt

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (accuracy_score, f1_score, confusion_matrix,
                             recall_score)
from scipy.stats import pearsonr

import build_dataset as bd
import features as feat
from train import SOUTH, NORTH, build_features, apply_task
from nn_model import TorchMLP

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- i18n ------------------------------------------------------------
LANG = "zh"


def T(zh, en):
    return en if LANG == "en" else zh


PINYIN = {
    "關內道": "Guannei", "河南道": "Henan", "河北道": "Hebei", "江南道": "Jiangnan",
    "河東道": "Hedong", "淮南道": "Huainan", "山南道": "Shannan", "隴右道": "Longyou",
    "劍南道": "Jiannan", "嶺南道": "Lingnan",
}
ERA_EN = {"初唐": "Early Tang", "盛唐": "High Tang", "中唐": "Mid Tang", "晚唐": "Late Tang"}
SIDE_EN = {"南": "South", "北": "North", "南方": "South", "北方": "North"}
IMG_EN = {"山": "Mountain", "川": "Water", "草木": "Plant", "鳥獸": "Fauna", "天體": "Celestial"}


def R(r):
    return PINYIN.get(r, r) if LANG == "en" else r


def RR(rs):
    return [R(r) for r in rs]


def E(e):
    return ERA_EN.get(e, e) if LANG == "en" else e


def S(s):
    return SIDE_EN.get(s, s) if LANG == "en" else s


# ---- shared data helpers --------------------------------------------
CIRCUIT_COORDS = {
    "關內道": (108.95, 34.27), "河南道": (113.65, 34.76), "河北道": (114.48, 38.03),
    "江南道": (120.15, 30.28), "河東道": (112.55, 37.87), "淮南道": (119.42, 32.39),
    "山南道": (106.71, 33.04), "隴右道": (103.85, 36.06), "劍南道": (104.07, 30.65),
    "嶺南道": (113.25, 23.13),
}
CAP = "關內道"
# Unified Tang periodisation (pre-618 Sui-Tang folded into 初唐; 五代 >907 dropped).
ERAS = [("初唐", 0, 712), ("盛唐", 713, 765), ("中唐", 766, 835), ("晚唐", 836, 907)]


def haversine(a, b):
    lon1, lat1, lon2, lat2 = map(radians, [a[0], a[1], b[0], b[1]])
    d = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 2*6371*asin(sqrt(d))


def mantel_p(d1, d2, n_perm=10000, seed=42):
    """Label-permutation p-value for the correlation of two distance matrices
    (pairwise distances are not independent, so the naive Pearson p is invalid)."""
    n = d1.shape[0]
    iu = np.triu_indices(n, 1)
    r = pearsonr(d1[iu], d2[iu])[0]
    rng = np.random.RandomState(seed)
    count = sum(abs(pearsonr(d1[np.ix_(p, p)][iu], d2[iu])[0]) >= abs(r)
                for p in (rng.permutation(n) for _ in range(n_perm)))
    return r, (count + 1) / (n_perm + 1)


def load_df(min_poems=10):
    df = pd.read_csv(os.path.join(HERE, "dataset.csv"))
    return df[df["n_poems"] >= min_poems].reset_index(drop=True)


def sn_label(df):
    df = df.copy()
    df["label"] = df["region"].map(
        lambda r: "南" if r in SOUTH else ("北" if r in NORTH else None))
    return df.dropna(subset=["label"]).reset_index(drop=True)


def load_years():
    years = {}
    with open(bd.DEFAULT_GEO, encoding="utf-8") as f:
        r = csv.reader(f); next(r)
        for row in r:
            m = re.match(r"\s*\d+\.\s*(.+?):\s*\d+\s*首", row[0])
            if m and len(row) > 3:
                mm = re.search(r"(\d{3,4})\s*-\s*(\d{3,4})", row[3])
                if mm:
                    years[m.group(1).strip()] = (int(mm.group(1))+int(mm.group(2)))//2
    return years


def era_of(mid):
    for nm, lo, hi in ERAS:
        if lo <= mid <= hi:
            return nm
    return None


def save(fig, name, transparent=False, tight=True):
    p = os.path.join(FIGDIR, name)
    if tight:
        fig.tight_layout()
    fig.savefig(p, dpi=130, transparent=transparent)
    plt.close(fig)
    print(f"  saved {os.path.relpath(p, HERE)}")


# Slide-deck palette (Tang_Poets_Origins_slides): brick red / warm gray / ink.
SLIDE_RED, SLIDE_GRAY, SLIDE_INK = "#A63C2A", "#8C8478", "#2E2723"


def _slide_axes(ax):
    ax.tick_params(colors=SLIDE_INK, labelsize=11)
    for sp in ax.spines.values():
        sp.set_color(SLIDE_GRAY)
    ax.xaxis.label.set_color(SLIDE_INK); ax.yaxis.label.set_color(SLIDE_INK)
    ax.title.set_color(SLIDE_INK)


def _sn_cv_predict(df):
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    p = cross_val_predict(clf, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    return le, y, p


# ---- figures ---------------------------------------------------------
def fig01_model_comparison():
    df = sn_label(load_df())
    y = LabelEncoder().fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    models = {
        "Baseline": DummyClassifier(strategy="most_frequent"),
        "LogReg": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "LinearSVM": LinearSVC(class_weight="balanced", C=0.5),
        "RandomForest": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1),
        "MLP": TorchMLP(hidden=(256, 64), epochs=120, class_weight="balanced"),
    }
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    accs, f1s = [], []
    for m in models.values():
        p = cross_val_predict(m, X, y, cv=skf)
        accs.append(accuracy_score(y, p)); f1s.append(f1_score(y, p, average="macro"))
    x = np.arange(len(models)); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x-w/2, accs, w, label="accuracy")
    ax.bar(x+w/2, f1s, w, label="macro-F1")
    ax.axhline(0.5, ls="--", c="gray", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(models.keys())
    ax.set_ylim(0, 1); ax.set_ylabel(T("分數", "score"))
    ax.set_title(T("南/北二分類:模型比較（5 折 CV）",
                   "South vs North: model comparison (5-fold CV)"))
    ax.legend()
    for i, (a, f) in enumerate(zip(accs, f1s)):
        ax.text(i-w/2, a+.01, f"{a:.2f}", ha="center", fontsize=8)
        ax.text(i+w/2, f+.01, f"{f:.2f}", ha="center", fontsize=8)
    save(fig, "fig01_model_comparison.png")


def fig02_confusion():
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts().nlargest(6).index
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    p = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), X, y,
                          cv=StratifiedKFold(5, shuffle=True, random_state=42))
    cm = confusion_matrix(y, p).astype(float)
    cmn = cm / cm.sum(1, keepdims=True)
    rec = recall_score(y, p, average=None)
    labels = RR(list(le.classes_))
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    im = ax[0].imshow(cmn, cmap="Blues", vmin=0, vmax=1)
    ax[0].set_xticks(range(len(labels))); ax[0].set_xticklabels(labels, rotation=45)
    ax[0].set_yticks(range(len(labels))); ax[0].set_yticklabels(labels)
    ax[0].set_xlabel(T("預測", "predicted")); ax[0].set_ylabel(T("實際", "true"))
    ax[0].set_title(T("道級混淆矩陣（列正規化）", "Circuit confusion (row-normalized)"))
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax[0].text(j, i, f"{cmn[i,j]:.2f}", ha="center", va="center",
                       color="white" if cmn[i, j] > .5 else "black", fontsize=8)
    fig.colorbar(im, ax=ax[0], fraction=.046)
    order = np.argsort(rec)
    ax[1].barh([labels[i] for i in order], rec[order], color="teal")
    ax[1].set_xlim(0, 1); ax[1].set_xlabel(T("recall（辨識率）", "recall"))
    ax[1].set_title(T("各道辨識率", "Per-circuit identifiability"))
    save(fig, "fig02_confusion.png")


def fig03_distance_decay(slide=False):
    # slide=True writes fig03_distance_decay_slide.png: transparent background,
    # deck palette, larger type. The paper figure is unchanged.
    from sklearn.feature_extraction.text import TfidfVectorizer
    df = load_df()
    keep = df["region"].value_counts(); keep = keep[keep >= 5].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["region"].isin(keep)].reset_index(drop=True)
    regions = sorted(df["region"].unique())
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                          max_features=8000, sublinear_tf=True)
    X = vec.fit_transform(df["text"])
    cent = np.vstack([np.asarray(X[(df.region == r).values].mean(0)).ravel()
                      for r in regions])
    cent /= (np.linalg.norm(cent, axis=1, keepdims=True)+1e-12)
    ling = 1 - cent @ cent.T
    geo = np.array([[haversine(CIRCUIT_COORDS[a], CIRCUIT_COORDS[b])
                     for b in regions] for a in regions])
    iu = np.triu_indices(len(regions), 1)
    gx, ly = geo[iu], ling[iu]
    r, p_naive = pearsonr(gx, ly)
    _, p_mantel = mantel_p(geo, ling)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    fs = 13 if slide else None
    ax.scatter(gx, ly, alpha=.8 if slide else .7,
               color=SLIDE_GRAY if slide else None, s=55 if slide else None)
    z = np.polyfit(gx, ly, 1)
    xs = np.linspace(gx.min(), gx.max(), 50)
    ax.plot(xs, np.polyval(z, xs), ls="--",
            color=SLIDE_RED if slide else "r", lw=2 if slide else None,
            label=f"r={r:.2f}, Mantel p={p_mantel:.2f}\n(naive p={p_naive:.3f})")
    ax.set_xlabel(T("地理距離（km）", "geographic distance (km)"), fontsize=fs)
    ax.set_ylabel(T("語言距離（1 − cosine）", "linguistic distance (1 - cosine)"),
                  fontsize=fs)
    if slide:
        _slide_axes(ax)
        ax.legend(fontsize=11, labelcolor=SLIDE_INK)
        save(fig, "fig03_distance_decay_slide.png", transparent=True)
    else:
        ax.set_title(T(f"詩歌語言的距離衰減（{len(regions)} 道）",
                       f"Distance decay of poetic language ({len(regions)} circuits)"))
        ax.legend()
        save(fig, "fig03_distance_decay.png")


def fig04_era_evolution():
    df = sn_label(load_df())
    years = load_years()
    df["era"] = df["poet"].map(lambda p: era_of(years[p]) if p in years else None)
    sub = df.dropna(subset=["era"])
    names, accs, ns = [], [], []
    for era, lo, hi in ERAS:
        e = sub[sub.era == era]
        if e["label"].nunique() < 2 or e["label"].value_counts().min() < 5:
            continue
        le, y, p = _sn_cv_predict(e)
        names.append(E(era)); accs.append(accuracy_score(y, p)); ns.append(len(e))
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(names, accs, "o-", ms=10, lw=2, color="darkred")
    ax.axhline(0.5, ls="--", c="gray", label=T("亂猜", "chance"))
    for n_, a, c in zip(names, accs, ns):
        ax.text(n_, a+.02, f"{a:.2f}\n(n={c})", ha="center", fontsize=9)
    ax.set_ylim(0.3, 0.85); ax.set_ylabel(T("南/北 accuracy", "South/North accuracy"))
    ax.set_title(T("逐期南/北可分性:盛唐同質化 → 晚唐地方化",
                   "Separability by era: High-Tang homogenization -> Late-Tang divergence"))
    ax.legend()
    save(fig, "fig04_era_evolution.png")


def fig05_misclass_by_era():
    df = sn_label(load_df())
    le, y, p = _sn_cv_predict(df)
    df["pred"] = le.inverse_transform(p)
    df["wrong"] = df["pred"] != df["label"]
    years = load_years()
    rows = []
    for _, row in df[df.wrong].iterrows():
        yr = years.get(row["poet"])
        if yr is None:
            continue
        e = era_of(yr)
        if e:
            rows.append((e, f"{row['label']}→{row['pred']}"))
    ed = pd.DataFrame(rows, columns=["era", "dir"])
    tab = pd.crosstab(ed["era"], ed["dir"]).reindex([e[0] for e in ERAS]).fillna(0)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bottom = np.zeros(len(tab))
    colors = {"南→北": "#c44", "北→南": "#46a"}
    leg = {"南→北": T("南→北", "S→N"), "北→南": T("北→南", "N→S")}
    for col in tab.columns:
        ax.bar([E(i) for i in tab.index], tab[col], bottom=bottom,
               label=leg.get(col, col), color=colors.get(col))
        bottom += tab[col].values
    ax.set_ylabel(T("誤分類詩人數", "# misclassified poets"))
    ax.set_title(T("誤分類方向 × 時代（初唐全為 南→北）",
                   "Error direction by era (Early Tang: all South->North)"))
    ax.legend()
    save(fig, "fig05_misclass_by_era.png")


def fig06_region_distribution():
    df = load_df(min_poems=5)
    vc = df["region"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#c44" if r in SOUTH else "#46a" for r in vc.index]
    ax.bar(RR(list(vc.index)), vc.values, color=colors)
    ax.set_xticklabels(RR(list(vc.index)), rotation=45)
    ax.set_ylabel(T("詩人數", "# poets"))
    ax.set_title(T("各道詩人數（紅=南，藍=北；≥5 首）",
                   "Poets per circuit (red=South, blue=North; >=5 poems)"))
    for i, v in enumerate(vc.values):
        ax.text(i, v+1, str(v), ha="center", fontsize=8)
    save(fig, "fig06_region_distribution.png")


def fig07_domain_radar():
    df = sn_label(load_df())
    cats = ["img_mountain", "img_water", "img_plant", "img_animal", "img_celestial"]
    labels = [IMG_EN["山"], IMG_EN["川"], IMG_EN["草木"], IMG_EN["鳥獸"], IMG_EN["天體"]] \
        if LANG == "en" else ["山", "川", "草木", "鳥獸", "天體"]
    dom = pd.DataFrame(feat.vectorize(df["text"].tolist()), columns=feat.FEATURE_NAMES)
    dom["label"] = df["label"].values
    means = dom.groupby("label")[cats].mean()
    ang = np.linspace(0, 2*np.pi, len(cats), endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    for side, color in [("南", "#c44"), ("北", "#46a")]:
        vals = means.loc[side].tolist(); vals += vals[:1]
        ax.plot(ang, vals, color=color, label=S(side), lw=2)
        ax.fill(ang, vals, color=color, alpha=.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels)
    ax.set_title(T("意象特徵:南 vs 北（每字頻率）",
                   "Imagery features: South vs North (per-char freq)"), pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1))
    save(fig, "fig07_domain_radar.png")


def fig08_discriminative_chars(top=12):
    from sklearn.feature_extraction.text import TfidfVectorizer
    df = sn_label(load_df())
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                          max_features=8000, sublinear_tf=True)
    X = vec.fit_transform(df["text"])
    clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X, y)
    names = np.array(vec.get_feature_names_out())
    coef = clf.coef_[0]
    pos_cls, neg_cls = le.classes_[1], le.classes_[0]
    pos = np.argsort(coef)[::-1][:top]
    neg = np.argsort(coef)[:top]
    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    ax[0].barh([names[i] for i in pos][::-1], [coef[i] for i in pos][::-1], color="#c44")
    ax[0].set_title(T(f"最偏「{pos_cls}」的字元", f"Top characters for {S(pos_cls)}"))
    ax[0].set_xlabel(T("權重", "weight"))
    ax[1].barh([names[i] for i in neg][::-1], [-coef[i] for i in neg][::-1], color="#46a")
    ax[1].set_title(T(f"最偏「{neg_cls}」的字元", f"Top characters for {S(neg_cls)}"))
    ax[1].set_xlabel(T("權重", "weight"))
    save(fig, "fig08_discriminative_chars.png")


def fig09_transformer():
    epochs, losses, accs = [], [], []
    log = os.path.join(HERE, "tf_curve.log")
    if os.path.exists(log):
        for line in open(log, encoding="utf-8", errors="ignore"):
            m = re.search(r"epoch (\d+) avg loss ([\d.]+) train_acc ([\d.]+)", line)
            if m:
                epochs.append(int(m.group(1))); losses.append(float(m.group(2)))
                accs.append(float(m.group(3)))
    if not epochs:
        epochs = [1, 2, 3, 4, 5, 6]
        losses = [0.697, 0.673, 0.664, 0.620, 0.580, 0.544]
        accs = [0.525, 0.614, 0.592, 0.660, 0.705, 0.750]
    fold_acc = [0.551, 0.686, 0.688, 0.562, 0.633]
    single, cv_mean, cv_std = 0.705, 0.624, 0.059
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.3))
    ax[0].bar([T("單次留出", "single hold-out"), T("5 折 CV", "5-fold CV")],
              [single, cv_mean], yerr=[0, cv_std], capsize=6, color=["#999", "#c44"])
    ax[0].set_ylim(0, 1); ax[0].axhline(0.5, ls="--", c="gray")
    ax[0].set_title(T("GuwenBERT:評估協定", "GuwenBERT: evaluation protocol"))
    ax[0].set_ylabel(T("poet-level accuracy", "poet-level accuracy"))
    for i, v in enumerate([single, cv_mean]):
        ax[0].text(i, v+.02, f"{v:.2f}", ha="center")
    ax2 = ax[1].twinx()
    ax[1].plot(epochs, losses, "o-", color="#46a", label="train loss")
    ax2.plot(epochs, accs, "s--", color="#c44", label="train acc")
    ax[1].set_xlabel("epoch"); ax[1].set_ylabel("loss", color="#46a")
    ax2.set_ylabel("train accuracy", color="#c44")
    ax[1].set_title(T("微調訓練曲線（繁→簡後）",
                      "Fine-tuning curve (after Trad->Simp)"))
    ax[2].bar(range(1, len(fold_acc)+1), fold_acc, color="#7a4")
    ax[2].axhline(cv_mean, ls="--", c="k", label=f"mean {cv_mean:.2f}")
    ax[2].set_xlabel(T("折", "fold")); ax[2].set_ylim(0, 1)
    ax[2].set_title(T("各折 poet-level accuracy", "Per-fold poet-level accuracy"))
    ax[2].legend()
    save(fig, "fig09_transformer.png")


def fig10_length_control():
    df = sn_label(load_df())
    budget = int(df["n_chars"].quantile(0.25))
    res = {}
    for name, txt in [(T("整篇語料", "full corpus"), df["text"]),
                      (T(f"截至 {budget} 字", f"first {budget} chars"),
                       df["text"].str.slice(0, budget))]:
        le, y, p = _sn_cv_predict(df.assign(text=txt))
        res[name] = accuracy_score(y, p)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.bar(list(res.keys()), list(res.values()), color=["#46a", "#9ab"])
    ax.set_ylim(0, 0.8); ax.axhline(0.5, ls="--", c="gray")
    ax.set_ylabel(T("南/北 accuracy", "South/North accuracy"))
    ax.set_title(T("語料長度控制（幾乎不變 → 非長度假象）",
                   "Corpus-length control (stable -> not a length artifact)"))
    for i, v in enumerate(res.values()):
        ax.text(i, v+.01, f"{v:.2f}", ha="center")
    save(fig, "fig10_length_control.png")


def fig11_periphery():
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    p = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), X, y,
                          cv=StratifiedKFold(5, shuffle=True, random_state=42))
    rec = recall_score(y, p, average=None)
    order = list(le.classes_)
    dist = [haversine(CIRCUIT_COORDS[r], CIRCUIT_COORDS[CAP]) for r in order]
    rr = [rec[i] for i in range(len(order))]
    # No regression line: the association is non-significant (p>0.3) and reverses
    # sign without Jiangnan, so a fitted trend would over-state a distance effect.
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(dist, rr, s=80, color="purple")
    for r_, d, a in zip(order, dist, rr):
        ax.annotate(R(r_), (d, a), textcoords="offset points", xytext=(6, 4))
    ax.set_xlabel(T("離長安距離（km）", "distance from Chang'an (km)"))
    ax.set_ylabel(T("辨識率（recall）", "identifiability (recall)"))
    ax.set_title(T("各道辨識率 vs. 離首都距離",
                   "Per-circuit identifiability vs. distance from the capital"))
    save(fig, "fig11_periphery.png")


def fig11b_periphery_regline():
    # Supplementary/slide variant of fig11: adds the fitted regression line
    # (with r and its non-significant p in the legend) plus a dashed fit
    # excluding Jiangnan, whose leverage flips the slope sign. Place names
    # carry the Chinese circuit name in brackets. Not part of the paper set.
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    p = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), X, y,
                          cv=StratifiedKFold(5, shuffle=True, random_state=42))
    rec = recall_score(y, p, average=None)
    order = list(le.classes_)
    dist = np.array([haversine(CIRCUIT_COORDS[r], CIRCUIT_COORDS[CAP]) for r in order])
    rr = np.array([rec[i] for i in range(len(order))])

    r_all, p_all = pearsonr(dist, rr)
    mask = np.array([r_ != "江南道" for r_ in order])
    r_ex, p_ex = pearsonr(dist[mask], rr[mask])

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(dist, rr, s=90, color=SLIDE_RED, zorder=3)
    offsets = {"河南道": ((6, -16), "left"), "河東道": ((-8, 4), "right"),
               "江南道": ((-8, -18), "right")}
    for r_, d, a in zip(order, dist, rr):
        lbl = f"{PINYIN.get(r_, r_)}（{r_}）" if LANG == "en" else r_
        (dx, dy), ha = offsets.get(r_, ((6, 5), "left"))
        ax.annotate(lbl, (d, a), textcoords="offset points",
                    xytext=(dx, dy), ha=ha, fontsize=12, color=SLIDE_INK)
    xs = np.linspace(dist.min(), dist.max(), 100)
    z = np.polyfit(dist, rr, 1)
    ax.plot(xs, np.polyval(z, xs), color=SLIDE_RED, lw=2,
            label=T(f"全部（r={r_all:.2f}, p={p_all:.2f}，不顯著）",
                    f"all circuits (r={r_all:.2f}, p={p_all:.2f}, n.s.)"))
    z2 = np.polyfit(dist[mask], rr[mask], 1)
    ax.plot(xs, np.polyval(z2, xs), color=SLIDE_GRAY, lw=2, ls="--",
            label=T(f"不含江南（r={r_ex:.2f}, p={p_ex:.2f}）",
                    f"excl. Jiangnan（江南）(r={r_ex:.2f}, p={p_ex:.2f})"))
    ax.legend(loc="center left", fontsize=10.5, labelcolor=SLIDE_INK)
    ax.set_xlim(dist.min() - 80, dist.max() + 200)
    ax.set_xlabel(T("離長安距離（km）", "distance from Chang'an（長安）(km)"), fontsize=13)
    ax.set_ylabel(T("辨識率（recall）", "identifiability (recall)"), fontsize=13)
    _slide_axes(ax)
    save(fig, "fig11b_periphery_regline.png", transparent=True)


def _jn_families():
    """Family assignment, colors and EN glosses shared by fig13/fig14."""
    CAT = {}
    for f in ["img_mountain", "img_water", "煙霞", "溪上", "搖落"]:
        CAT[f] = "land"
    for f in ["謾", "只", "只有", "不是", "多少", "未可", "何言", "歸去",
              "好", "偏", "添", "片", "日又"]:
        CAT[f] = "colloq"
    for f in ["蘆", "萋", "茗", "牡丹", "朵", "鱗", "猩", "匡", "綿", "江南"]:
        CAT[f] = "flora"
    CCOL = {"land": "#2a8", "colloq": "#46a", "flora": "#a63c2a",
            "other": "#999"}
    GLOSS = {"img_mountain": T("山意象（特徵）", "mountain imagery"),
             "img_water": T("水意象（特徵）", "water imagery"),
             "season_spring": T("春季標記（特徵）", "spring markers"),
             "白露": "white dew",
             "謾": "in vain", "只": "only", "只有": "there is only",
             "不是": "is not", "多少": "how many", "未可": "not yet",
             "何言": "why say", "歸去": "going home", "好": "fine",
             "偏": "especially", "添": "adds", "片": "a sliver",
             "日又": "day, again", "煙霞": "mist and glow",
             "溪上": "on the stream", "搖落": "leaves falling",
             "蘆": "reeds", "萋": "lush grass", "茗": "tea",
             "牡丹": "peony", "朵": "blossom", "鱗": "fish scales",
             "猩": "gibbon-crimson", "匡": "Mt. Lu", "綿": "silk-soft",
             "江南": "Jiangnan itself", "約": "promise", "利": "gain",
             "律": "meter", "穿": "threads through", "魂夢": "soul-dream",
             "會": "meet", "關山": "frontier passes", "紛": "profuse",
             "衛": "guards", "使": "envoy", "回日": "day of return",
             "芙蓉": "lotus", "誰念": "who remembers", "文": "letters",
             "山長": "mountains stretch", "試": "examine", "賞": "bestow",
             "北": "north", "涓": "trickle"}
    return CAT, CCOL, GLOSS


def fig14_jiangnan_forest():
    # Traditional statistical presentation of the fig13 markers: Fisher
    # exact odds ratios on poet-level usage (JN vs rest) with Woolf 95% CIs
    # (Haldane 0.5 correction), per-feature p annotated. Descriptive only:
    # across all 8,013 features none passes BH-FDR at this sample size.
    from sklearn.linear_model import LogisticRegression
    from scipy.stats import fisher_exact
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, vec, _ = build_features(df["text"].tolist())
    names = list(vec.get_feature_names_out()) + feat.FEATURE_NAMES
    jn = list(le.classes_).index("江南道")
    mask = (y == jn)
    pres = np.asarray(X.todense()) > 0
    n_jn, n_ot = mask.sum(), (~mask).sum()
    w = LogisticRegression(max_iter=3000, class_weight="balanced")\
        .fit(X, (y == jn).astype(int)).coef_[0]
    order = np.argsort(w)[::-1]
    CAT, CCOL, GLOSS = _jn_families()

    def lbl(f):
        if f in feat.FEATURE_NAMES:
            return GLOSS.get(f, f)
        g = GLOSS.get(f)
        return f"{g}（{f}）" if (LANG == "en" and g) else f

    def stats(i):
        a = pres[mask, i].sum(); b = n_jn - a
        c = pres[~mask, i].sum(); d = n_ot - c
        _, p = fisher_exact([[a, b], [c, d]])
        a_, b_, c_, d_ = a + .5, b + .5, c + .5, d + .5
        lo = np.log((a_ * d_) / (b_ * c_))
        se = np.sqrt(1/a_ + 1/b_ + 1/c_ + 1/d_)
        return np.exp(lo), np.exp(lo - 1.96*se), np.exp(lo + 1.96*se), p

    rows = [(i, *stats(i)) for i in order[:16]]
    rows.sort(key=lambda r: r[1], reverse=True)
    rows_n = [(i, *stats(i)) for i in order[-10:]]
    rows_n.sort(key=lambda r: r[1], reverse=True)

    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    ypos, ylab, seen_fam = [], [], set()
    yc = 0
    groups = [(T("推向江南", "toward Jiangnan"), rows),
              (T("推離江南", "away from Jiangnan"), rows_n)]
    import matplotlib.transforms as mtransforms
    tr = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
    for gtitle, grows in groups:
        ax.text(-0.02, yc + 0.55, gtitle, transform=tr, fontsize=11,
                fontweight="bold", ha="right", va="center", color="#333")
        yc -= 0.4
        for i, or_, lo_, hi_, p_ in grows:
            fam = CAT.get(names[i], "other")
            col = CCOL[fam]
            ax.plot([lo_, hi_], [yc, yc], color=col, lw=1.6, zorder=2)
            ax.plot(or_, yc, "s", color=col, ms=6, zorder=3,
                    label=fam if fam not in seen_fam else None)
            seen_fam.add(fam)
            ypos.append(yc); ylab.append(lbl(names[i]))
            ax.text(1.02, yc, ("p<0.001" if p_ < 0.001 else f"p={p_:.3f}"),
                    transform=tr, fontsize=8, va="center", color="#555")
            yc -= 1
        yc -= 1.2
    ax.axvline(1, ls="--", c="gray", lw=1)
    ax.set_yticks(ypos); ax.set_yticklabels(ylab, fontsize=9)
    ax.set_xscale("log")
    ax.set_xticks([0.125, 0.25, 0.5, 1, 2, 4, 8])
    ax.set_xticklabels(["0.125", "0.25", "0.5", "1", "2", "4", "8"])
    ax.set_xlim(0.08, 12)
    ax.set_ylim(yc + 0.5, 1.6)
    ax.set_xlabel(T("勝算比（江南 vs 其他道，詩人層級使用率，log 尺度）",
                    "odds ratio (poet-level usage, JN vs rest, log scale)"))
    fam_names = {"land": T("山水/意象", "landscape & imagery"),
                 "colloq": T("口語語體", "colloquial diction"),
                 "flora": T("南方風物", "southern flora & things"),
                 "other": T("其他", "other")}
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, [fam_names[l] for l in labels], loc="upper left",
              fontsize=8)
    ax.set_title(T("江南標記:勝算比與 95% CI（Fisher 精確檢定）",
                   "Jiangnan markers: odds ratios with 95% CI (Fisher exact)"),
                 fontsize=13)
    fig.text(0.5, 0.012,
             T("Woolf CI（Haldane 0.5 校正）;各 p 值為描述性——全部 8,013 個"
               "特徵經 BH-FDR 校正後無單一特徵顯著（見正文）",
               "Woolf CIs (Haldane 0.5 correction); per-feature p-values are "
               "descriptive — across all 8,013 features none passes BH-FDR "
               "(see text)"),
             ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig14_jiangnan_forest.png", tight=False)


def fig13_jiangnan_markers():
    # What makes Jiangnan legible. Feature *selection* uses binary
    # Jiangnan-vs-rest LogReg weights (six-circuit poet set, same filter as
    # fig11), but the plotted quantity is model-agnostic: the difference in
    # poet-level usage share (JN minus rest). Robustness reported in the
    # footer: place-name ablation, family-level Mann-Whitney tests on fixed
    # lexicons, and a repeated split-half generalization check. Individual
    # n-grams do NOT survive FDR at n=219 (see validate_jiangnan.py) — the
    # signal is distributed; the bars are its most readable representatives.
    from sklearn.linear_model import LogisticRegression
    from scipy.stats import mannwhitneyu
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, vec, _ = build_features(df["text"].tolist())
    names = list(vec.get_feature_names_out()) + feat.FEATURE_NAMES
    jn = list(le.classes_).index("江南道")
    yb = (y == jn).astype(int)
    mask = yb.astype(bool)
    Xd = np.asarray(X.todense())
    pres = Xd > 0          # for domain features: share above corpus mean
    w = LogisticRegression(max_iter=3000,
                           class_weight="balanced").fit(X, yb).coef_[0]

    CAT, CCOL, GLOSS = _jn_families()

    def lbl(f):
        if f in feat.FEATURE_NAMES:
            return GLOSS.get(f, f)
        g = GLOSS.get(f)
        return f"{g}（{f}）" if (LANG == "en" and g) else f

    delta = pres[mask].mean(0) - pres[~mask].mean(0)   # usage share diff
    order = np.argsort(w)[::-1]
    top_p = sorted(order[:16], key=lambda i: delta[i])
    top_n = sorted(order[-10:], key=lambda i: delta[i], reverse=True)

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 6.4),
                           gridspec_kw={"width_ratios": [1.15, 1]})
    for a, idxs, title in [
            (ax[0], top_p, T("推向江南的特徵", "pushing toward Jiangnan")),
            (ax[1], top_n, T("推離江南的特徵", "pushing away from Jiangnan"))]:
        cols = [CCOL[CAT.get(names[i], "other")] for i in idxs]
        a.barh(range(len(idxs)), [delta[i] * 100 for i in idxs],
               color=cols, height=0.7)
        a.set_yticks(range(len(idxs)))
        a.set_yticklabels([lbl(names[i]) for i in idxs], fontsize=9)
        a.axvline(0, c="k", lw=0.8)
        a.set_xlabel(T("使用率差（江南 - 其他道，百分點）",
                       "usage-share difference (JN - rest, pp)"))
        a.set_title(title)
    handles = [plt.Rectangle((0, 0), 1, 1, color=CCOL[k]) for k in
               ["land", "colloq", "flora", "other"]]
    ax[0].legend(handles, [T("山水/意象", "landscape & imagery"),
                           T("口語語體", "colloquial diction"),
                           T("南方風物", "southern flora & things"),
                           T("其他", "other")],
                 loc="lower right", fontsize=8)

    # Place-name ablation (multiclass, same protocol as fig11).
    PLACE = set("吳越楚湘江湖溪浙淮楓橘蓮荷")
    nchar = len(vec.get_feature_names_out())
    drop = {i for i in range(nchar) if any(c in PLACE for c in names[i])}
    keep_idx = np.array([i for i in range(X.shape[1]) if i not in drop])
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    rec_f = recall_score(y, cross_val_predict(
        LinearSVC(class_weight="balanced", C=0.5), X, y, cv=skf),
        average=None)[jn]
    rec_a = recall_score(y, cross_val_predict(
        LinearSVC(class_weight="balanced", C=0.5), X[:, keep_idx], y, cv=skf),
        average=None)[jn]

    # Family-level tests on FIXED lexicons (one Mann-Whitney per family,
    # not 8k per-feature tests). img_* features are a priori (features.py);
    # the two lexicons are fixed word lists broader than the plotted bars.
    COLLOQ_LEX = ["只", "只有", "不是", "多少", "未可", "何言", "好", "偏",
                  "添", "謾", "歸去", "莫", "休", "爭得", "如今", "無端"]
    FLORA_LEX = ["蘆", "萋", "茗", "茶", "牡丹", "朵", "鱗", "猩", "猿",
                 "橘", "楓", "蓮", "荷", "苔", "梅"]
    name_idx = {n: i for i, n in enumerate(names)}

    def fam_p(lex):
        cols = [name_idx[t] for t in lex if t in name_idx]
        score = pres[:, cols].mean(1)
        return mannwhitneyu(score[mask], score[~mask],
                            alternative="greater").pvalue

    land_cols = [name_idx["img_mountain"], name_idx["img_water"]]
    land_score = Xd[:, land_cols].mean(1)
    p_land = mannwhitneyu(land_score[mask], land_score[~mask],
                          alternative="greater").pvalue
    p_coll, p_flor = fam_p(COLLOQ_LEX), fam_p(FLORA_LEX)

    # Repeated split-half: select top-30 markers on one half, test whether
    # their usage score separates JN on the held-out half (no double dipping).
    from sklearn.linear_model import LogisticRegression as LR
    sh_p, sh_auc = [], []
    for seed in range(20):
        tr, te = next(iter(StratifiedKFold(
            2, shuffle=True, random_state=seed).split(X, yb)))
        w_tr = LR(max_iter=2000, class_weight="balanced")\
            .fit(X[tr], yb[tr]).coef_[0]
        top30 = np.argsort(w_tr)[::-1][:30]
        sc = pres[te][:, top30].mean(1)
        mte = mask[te]
        res = mannwhitneyu(sc[mte], sc[~mte], alternative="greater")
        sh_p.append(res.pvalue)
        sh_auc.append(res.statistic / (mte.sum() * (~mte).sum()))
    sh_p_med, sh_auc_med = np.median(sh_p), np.median(sh_auc)

    fig.suptitle(T("江南為何可辨識：分散訊號中最可讀的標記",
                   "What makes Jiangnan legible: readable markers of a "
                   "distributed signal"), fontsize=13)
    fig.text(0.5, 0.075,
             T(f"地名消融:剔除全部含「{''.join(sorted(PLACE))}」的 "
               f"{len(drop)} 個 n-gram,江南 recall {rec_f:.2f} → "
               f"{rec_a:.2f} — 並非地名洩漏",
               f"Place-name ablation: dropping all {len(drop)} n-grams "
               f"containing 「{''.join(sorted(PLACE))}」 leaves recall "
               f"unchanged ({rec_f:.2f} → {rec_a:.2f}) — not name leakage"),
             ha="center", fontsize=8.5, style="italic")
    def fp(p):
        return "<0.001" if p < 0.001 else f"={p:.3f}"

    fig.text(0.5, 0.045,
             T(f"家族檢定（Mann-Whitney,固定詞表）:山水意象 p{fp(p_land)}"
               f" · 口語語體 p{fp(p_coll)} · 南方風物 p{fp(p_flor)};"
               f"僅取 top-30 標記跨半遷移很弱(中位 AUC={sh_auc_med:.2f})",
               f"Family tests (Mann-Whitney, fixed lexicons): landscape "
               f"p{fp(p_land)} · colloquial p{fp(p_coll)} · flora "
               f"p{fp(p_flor)}; top-30 markers alone transfer weakly across "
               f"halves (median AUC {sh_auc_med:.2f})"),
             ha="center", fontsize=8.5, style="italic")
    fig.text(0.5, 0.015,
             T("長條為模型無關的使用率差(特徵由 LogReg 選出);方向跨模型"
               "(top-50 重疊 41/50)與 bootstrap(≥99%)皆穩定;"
               "單一 n-gram 不過 FDR — 訊號是分散式的",
               "Bars show model-agnostic usage differences; direction stable "
               "across models (41/50 top-50 overlap) and bootstraps (≥99%); "
               "no single n-gram passes FDR — the signal is distributed"),
             ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=[0, 0.115, 1, 0.95])
    save(fig, "fig13_jiangnan_markers.png", tight=False)


def fig15_permutation_test():
    # Null distribution of S/N accuracy under label permutation (B=1000,
    # LinearSVC, same 5-fold protocol). Null draws are cached to .npy so
    # regeneration is cheap; delete the cache to recompute.
    cache = os.path.join(HERE, "perm_null_sn.npy")
    df = sn_label(load_df())
    y = LabelEncoder().fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    obs = accuracy_score(y, cross_val_predict(
        LinearSVC(class_weight="balanced", C=0.5), X, y, cv=skf))
    if os.path.exists(cache):
        null = np.load(cache)
    else:
        rng = np.random.RandomState(42)
        B = 1000
        null = np.empty(B)
        for b in range(B):
            yp = rng.permutation(y)
            null[b] = accuracy_score(yp, cross_val_predict(
                LinearSVC(class_weight="balanced", C=0.5), X, yp, cv=skf))
        np.save(cache, null)
    p = (1 + (null >= obs).sum()) / (len(null) + 1)
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.hist(null, bins=30, color="#9ab", edgecolor="white")
    ax.axvline(obs, color="darkred", lw=2.5)
    ax.text(obs - 0.004, ax.get_ylim()[1] * 0.95,
            T(f"觀察值 {obs:.3f}", f"observed {obs:.3f}"),
            color="darkred", ha="right", va="top", fontsize=11)
    ax.text(null.mean(), ax.get_ylim()[1] * 0.6,
            T(f"重排 null\n(B={len(null)})", f"permuted null\n(B={len(null)})"),
            ha="center", fontsize=10, color="#456")
    ax.set_xlabel(T("南/北 accuracy（LinearSVC，5 折）",
                    "South/North accuracy (LinearSVC, 5-fold)"))
    ax.set_ylabel(T("次數", "count"))
    nge = int((null >= obs).sum())
    ax.set_title(T(f"標籤重排檢定:p = {p:.3f}"
                   f"（{len(null)} 次重排中僅 {nge} 次 ≥ 觀察值）",
                   f"Label-permutation test: p = {p:.3f} "
                   f"({nge}/{len(null)} permutations ≥ observed)"))
    save(fig, "fig15_permutation.png")


def fig16_era_ci():
    # Honest version of fig04: within-era CV accuracy with bootstrap 95% CIs.
    # All pairwise Fisher tests are non-significant (min p = 0.06) — the
    # monotone trend is suggestive, not established.
    df = sn_label(load_df())
    years = load_years()
    df["era"] = df["poet"].map(lambda p: era_of(years[p]) if p in years else None)
    sub = df.dropna(subset=["era"])
    rng = np.random.RandomState(42)
    names, accs, los, his, ns = [], [], [], [], []
    for era, _, _ in ERAS:
        e = sub[sub.era == era]
        le, ye, pe = _sn_cv_predict(e)
        vals = np.empty(2000)
        yt = np.asarray(ye); pp = np.asarray(pe)
        for b in range(2000):
            i = rng.randint(0, len(yt), len(yt))
            vals[b] = (yt[i] == pp[i]).mean()
        names.append(E(era)); accs.append((yt == pp).mean())
        lo, hi = np.percentile(vals, [2.5, 97.5])
        los.append(lo); his.append(hi); ns.append(len(e))
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    xs = np.arange(len(names))
    ax.errorbar(xs, accs, yerr=[np.array(accs) - los, np.array(his) - accs],
                fmt="o-", ms=9, lw=2, capsize=5, color="darkred")
    ax.axhline(0.5, ls="--", c="gray", label=T("亂猜", "chance"))
    for x, a, n_ in zip(xs, accs, ns):
        ax.text(x + 0.06, a, f"{a:.2f}\n(n={n_})", fontsize=9, va="center")
    ax.set_xticks(xs); ax.set_xticklabels(names)
    ax.set_ylim(0.15, 1.0)
    ax.set_ylabel(T("南/北 accuracy", "South/North accuracy"))
    ax.set_title(T("逐期可分性與 bootstrap 95% CI（兩兩差異均不顯著,最小 p=0.06）",
                   "Separability by era with bootstrap 95% CIs\n"
                   "(no pairwise difference significant; min Fisher p = 0.06)"))
    ax.legend(loc="upper left")
    save(fig, "fig16_era_ci.png")


def fig17_ablation():
    # Left: feature-set ablation (char n-grams / domain / combined).
    # Right: function-character-only vs content-character-only n-grams.
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    from scipy.sparse import hstack, csr_matrix
    from sklearn.linear_model import LogisticRegression as _LR
    df = sn_label(load_df())
    y = LabelEncoder().fit_transform(df["label"])
    texts = df["text"].tolist()
    skf = StratifiedKFold(5, shuffle=True, random_state=42)

    def acc(Xv, model=None):
        model = model or LinearSVC(class_weight="balanced", C=0.5)
        return accuracy_score(y, cross_val_predict(model, Xv, y, cv=skf))

    char_vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 2), min_df=3,
                               max_features=8000, sublinear_tf=True)
    Xc = char_vec.fit_transform(texts)
    Xd = csr_matrix(StandardScaler().fit_transform(feat.vectorize(texts)))
    sets = [(T("僅字元 n-gram", "char n-grams\nonly"), acc(Xc)),
            (T("僅可讀特徵", "domain features\nonly"), acc(Xd)),
            (T("合併", "combined"), acc(hstack([Xc, Xd]).tocsr()))]

    FUNC = ("之乎者也而何其於于以為不無有是自相與且若乃焉哉矣耳此彼安孰即則"
            "雖然故遂復更未曾莫勿非豈但惟唯只又亦皆俱共還仍尚猶或每誰爾汝吾"
            "我君所能可得應當須欲將已經從向對如同像被把")
    vocab = char_vec.get_feature_names_out()
    fi = [i for i, t in enumerate(vocab) if all(c in FUNC for c in t)]
    ci = [i for i, t in enumerate(vocab) if all(c not in FUNC for c in t)]
    def lr():
        return _LR(max_iter=2000, class_weight="balanced")
    fc = [(T(f"僅虛字\n({len(fi)} n-gram)", f"function chars only\n({len(fi)} n-grams)"),
           acc(Xc[:, fi], lr())),
          (T(f"僅實字\n({len(ci)} n-gram)", f"content chars only\n({len(ci)} n-grams)"),
           acc(Xc[:, ci], lr())),
          (T("全部", "all n-grams"), acc(Xc, lr()))]

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    for a, data, title, hl in [
            (ax[0], sets, T("特徵集消融（SVC）", "Feature-set ablation (SVC)"), 0),
            (ax[1], fc, T("虛字 vs 實字（LogReg）",
                          "Function vs content characters (LogReg)"), 0)]:
        labs = [d[0] for d in data]; vals = [d[1] for d in data]
        best = int(np.argmax(vals))
        cols = ["#46a" if i != best else "#a63c2a" for i in range(len(vals))]
        a.bar(labs, vals, color=cols, width=0.55)
        a.axhline(0.5, ls="--", c="gray", lw=1)
        a.set_ylim(0, 0.8)
        a.set_ylabel(T("南/北 accuracy", "South/North accuracy"))
        a.set_title(title)
        for i, v in enumerate(vals):
            a.text(i, v + 0.012, f"{v:.3f}", ha="center", fontsize=10)
    fig.text(0.5, 0.012,
             T("可讀特徵單獨≈亂猜、併入 n-gram 反而略降——它們服務解釋而非準確率;"
               "純虛字 n-gram 即達 0.60 → 訊號在語體,不只在題材",
               "Domain features alone ≈ chance and slightly hurt when added — "
               "they serve interpretation, not accuracy; function characters "
               "alone reach 0.60 → the signal is stylistic, not only topical"),
             ha="center", fontsize=9, style="italic")
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    save(fig, "fig17_ablation.png", tight=False)


def fig18_prefecture_mantel():
    # Prefecture-level distance decay using CHGIS/TGAZ coordinates
    # (tang_prefecture_coords.csv). Scatter: pairwise linguistic vs
    # geographic distance for prefectures with >=5 poets; annotation reports
    # the threshold dependence (>=2 n.s. -> >=5/>=8 significant).
    import csv as _csv
    from gen_prefecture_coords import poet_prefectures
    coords = {}
    with open(os.path.join(HERE, "tang_prefecture_coords.csv"),
              encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            coords[row["prefecture"]] = (float(row["lon"]), float(row["lat"]))
    pp = poet_prefectures()
    df = load_df()
    df = df[df["poet"].map(lambda q: pp.get(q) in coords)].reset_index(drop=True)
    df["pref"] = df["poet"].map(pp)

    def mantel_for(min_poets):
        vc = df["pref"].value_counts()
        sub = df[df["pref"].isin(vc[vc >= min_poets].index)].reset_index(drop=True)
        units = sorted(sub["pref"].unique())
        X, _, _ = build_features(sub["text"].tolist())
        Xd = np.asarray(X.todense())
        c = np.vstack([Xd[(sub["pref"] == u).to_numpy()].mean(0)
                       for u in units])
        c /= (np.linalg.norm(c, axis=1, keepdims=True) + 1e-12)
        ling = 1 - c @ c.T
        geo = np.array([[haversine(coords[a], coords[b]) for b in units]
                        for a in units])
        r, p = mantel_p(geo, ling)
        return units, geo, ling, r, p, len(sub)

    u2, _, _, r2, p2, n2 = mantel_for(2)
    u5, geo5, ling5, r5, p5, n5 = mantel_for(5)
    u8, _, _, r8, p8, n8 = mantel_for(8)
    iu = np.triu_indices(len(u5), 1)
    gx, ly = geo5[iu], ling5[iu]
    fig, ax = plt.subplots(figsize=(7, 5.2))
    ax.scatter(gx, ly, alpha=.75, color="#a63c2a", s=45)
    z = np.polyfit(gx, ly, 1)
    xs = np.linspace(gx.min(), gx.max(), 50)
    ax.plot(xs, np.polyval(z, xs), ls="--", color="#2e2723", lw=1.8,
            label=T(f"每州 ≥5 位詩人:r={r5:.2f}, Mantel p={p5:.3f}",
                    f">=5 poets/prefecture: r={r5:.2f}, Mantel p={p5:.3f}"))
    ax.set_xlabel(T("州府間地理距離（km,CHGIS 座標）",
                    "geographic distance between prefectures (km, CHGIS)"))
    ax.set_ylabel(T("語言距離（1 − cosine）", "linguistic distance (1 - cosine)"))
    ax.set_title(T(f"府級距離衰減（{len(u5)} 州,{n5} 位詩人,"
                   f"{len(gx)} 對）",
                   f"Prefecture-level distance decay "
                   f"({len(u5)} prefectures, {n5} poets, {len(gx)} pairs)"))
    ax.legend(loc="upper left", fontsize=9)
    fig.text(0.5, 0.045,
             T(f"門檻依賴:全部州(≥2 人,{len(u2)} 州) r={r2:.2f} 不顯著"
               f"(質心噪音);≥8 人({len(u8)} 州) r={r8:.2f}, p={p8:.3f}",
               f"Threshold dependence: all prefectures (>=2 poets, {len(u2)} "
               f"units) r={r2:.2f} n.s. (centroid noise); >=8 poets "
               f"({len(u8)} units) r={r8:.2f}, p={p8:.3f}"),
             ha="center", fontsize=8.5, style="italic")
    fig.text(0.5, 0.015,
             T("道級基線:r=0.40, Mantel p≈0.09",
               "Circuit-level baseline: r=0.40, Mantel p≈0.09"),
             ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=[0, 0.075, 1, 1])
    save(fig, "fig18_prefecture_mantel.png", tight=False)


def fig19_map_recall():
    # Results on the map: one dot per Tang prefecture (CHGIS coordinates),
    # sized by number of dataset poets, colored by the per-circuit
    # identifiability (recall) from the six-circuit task (fig11 protocol).
    # Prefectures whose circuit is not in that task are drawn hollow/gray.
    # China outline: simplified GeoJSON (cached to china_boundary.geojson).
    import csv as _csv
    import json as _json
    import urllib.request
    from collections import Counter
    from gen_prefecture_coords import poet_prefectures

    bpath = os.path.join(HERE, "china_boundary.geojson")
    if not os.path.exists(bpath):
        url = ("https://raw.githubusercontent.com/johan/world.geo.json/"
               "master/countries/CHN.geo.json")
        with urllib.request.urlopen(url, timeout=30) as r:
            open(bpath, "wb").write(r.read())
    gj = _json.load(open(bpath, encoding="utf-8"))
    geom = gj["features"][0]["geometry"]
    rings = ([geom["coordinates"]] if geom["type"] == "Polygon"
             else geom["coordinates"])

    coords = {}
    with open(os.path.join(HERE, "tang_prefecture_coords.csv"),
              encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            coords[row["prefecture"]] = (float(row["lon"]), float(row["lat"]))
    pp = poet_prefectures()
    dfa = load_df()
    dfa = dfa[dfa["poet"].map(lambda q: pp.get(q) in coords)]
    pref_n = Counter(dfa["poet"].map(pp))
    pref_circuit = {}
    for _, row in dfa.iterrows():
        pref_circuit.setdefault(pp[row["poet"]], Counter())[row["region"]] += 1

    # per-circuit recall, same protocol as fig11
    dfc = apply_task(load_df(), "circuit")
    keep = dfc["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    dfc = dfc[dfc["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); yc = le.fit_transform(dfc["label"])
    Xc, _, _ = build_features(dfc["text"].tolist())
    pc = cross_val_predict(LinearSVC(class_weight="balanced", C=0.5), Xc, yc,
                           cv=StratifiedKFold(5, shuffle=True, random_state=42))
    rec = dict(zip(le.classes_, recall_score(yc, pc, average=None)))

    fig, ax = plt.subplots(figsize=(9.2, 7.6))
    for poly in rings:
        for ring in poly:
            xs = [pt[0] for pt in ring]; ys = [pt[1] for pt in ring]
            ax.plot(xs, ys, color="#c9c2b8", lw=1.0, zorder=1)
    cmap = plt.get_cmap("YlOrRd")
    import matplotlib.colors as mcolors
    norm_ = mcolors.Normalize(vmin=0, vmax=0.75)
    for p, n in sorted(pref_n.items(), key=lambda kv: -kv[1]):
        lon, lat = coords[p]
        circ = pref_circuit[p].most_common(1)[0][0]
        s = 18 + n * 16
        if circ in rec:
            ax.scatter(lon, lat, s=s, color=cmap(norm_(rec[circ])),
                       edgecolor="#2e2723", lw=0.5, zorder=3)
        else:
            ax.scatter(lon, lat, s=s, facecolor="none", edgecolor="#8c8478",
                       lw=1.0, zorder=2)
    ax.scatter(*CIRCUIT_COORDS["關內道"], marker="*", s=260, color="#2e2723",
               zorder=4)
    ax.annotate(T("長安", "Chang'an 長安"), CIRCUIT_COORDS["關內道"],
                textcoords="offset points", xytext=(8, -14), fontsize=10,
                fontweight="bold", color="#2e2723")
    ax.annotate(T("江南道 recall 0.71", "Jiangnan 江南 — recall 0.71"),
                (120.6, 27.6), fontsize=11, color="#a63c2a",
                fontweight="bold", ha="center")
    ax.annotate(T("京畿諸道互相混淆\n(recall 0.06–0.17)",
                  "capital circuits blur\n(recall 0.06–0.17)"),
                (106.2, 38.6), fontsize=10, color="#555", ha="center")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_)
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label(T("所屬道辨識率（recall,六道任務）",
                   "circuit identifiability (recall, six-circuit task)"))
    for n_, lbl_ in [(1, "1"), (5, "5"), (15, "15")]:
        ax.scatter([], [], s=18 + n_ * 16, facecolor="#ddd",
                   edgecolor="#2e2723", lw=0.5, label=lbl_)
    ax.legend(title=T("詩人數/州", "poets per prefecture"), loc="lower left",
              fontsize=9, title_fontsize=9)
    ax.set_xlim(97, 127); ax.set_ylim(19.5, 42.5)
    ax.set_aspect(1 / np.cos(np.radians(31)))
    ax.set_xlabel(T("經度", "longitude")); ax.set_ylabel(T("緯度", "latitude"))
    ax.set_title(T("結果地圖:各州詩人（CHGIS 座標）與所屬道辨識率",
                   "Results on the map: poets by Tang prefecture (CHGIS), "
                   "colored by circuit identifiability"))
    fig.text(0.5, 0.012,
             T("空心點:所屬道不在六道任務中(樣本過少);點大小=資料集詩人數",
               "hollow points: circuit not in the six-circuit task (too few "
               "poets); dot size = number of dataset poets"),
             ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig19_map_recall.png", tight=False)


def _china_rings():
    """Simplified China boundary rings, cached to china_boundary.geojson."""
    import json as _json
    import urllib.request
    bpath = os.path.join(HERE, "china_boundary.geojson")
    if not os.path.exists(bpath):
        url = ("https://raw.githubusercontent.com/johan/world.geo.json/"
               "master/countries/CHN.geo.json")
        with urllib.request.urlopen(url, timeout=30) as r:
            open(bpath, "wb").write(r.read())
    geom = _json.load(open(bpath, encoding="utf-8"))["features"][0]["geometry"]
    return ([geom["coordinates"]] if geom["type"] == "Polygon"
            else geom["coordinates"])


def fig20_char_maps():
    # Dialect-atlas style small multiples: one mini-map per marker character,
    # each prefecture dot colored by the share of its poets who use that
    # character at least once (dot size = poet count). Southern markers on
    # the top row, northern markers on the bottom row.
    import csv as _csv
    from collections import defaultdict
    from gen_prefecture_coords import poet_prefectures

    coords = {}
    with open(os.path.join(HERE, "tang_prefecture_coords.csv"),
              encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            coords[row["prefecture"]] = (float(row["lon"]), float(row["lat"]))
    pp = poet_prefectures()
    dfa = load_df()
    dfa = dfa[dfa["poet"].map(lambda q: pp.get(q) in coords)].reset_index(drop=True)
    dfa["pref"] = dfa["poet"].map(pp)

    CHARS = [("謾", T("謾（口語「空自」·南)", "謾 in vain · southern colloq.")),
             ("茗", T("茗（茶·南）", "茗 tea · southern")),
             ("猩", T("猩（猩紅/猿·南）", "猩 gibbon-crimson · southern")),
             ("文", T("文（文翰·北）", "文 letters · northern")),
             ("衛", T("衛（宿衛·北）", "衛 guards · northern")),
             ("關山", T("關山（邊塞·北）", "關山 frontier passes · northern"))]

    counts_all = dfa["pref"].value_counts()
    prefs = sorted(counts_all[counts_all >= 2].index)   # drop 0/1-noise
    counts = {p: int(counts_all[p]) for p in prefs}
    rings = _china_rings()
    cmap = plt.get_cmap("YlOrRd")
    import matplotlib.colors as mcolors

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.6))
    for ax, (ch, label) in zip(axes.ravel(), CHARS):
        share = {}
        for p in prefs:
            sub = dfa[dfa["pref"] == p]
            share[p] = sub["text"].str.contains(ch, regex=False).mean()
        vmax = max(0.15, max(share.values()))
        norm_ = mcolors.Normalize(vmin=0, vmax=vmax)
        for poly in rings:
            for ring in poly:
                ax.plot([pt[0] for pt in ring], [pt[1] for pt in ring],
                        color="#d5cfc6", lw=0.7, zorder=1)
        for p in sorted(prefs, key=lambda q: -counts[q]):
            lon, lat = coords[p]
            ax.scatter(lon, lat, s=10 + counts[p] * 9,
                       color=cmap(norm_(share[p])),
                       edgecolor="#6b625a", lw=0.4, zorder=3)
        ax.scatter(*CIRCUIT_COORDS["關內道"], marker="*", s=90,
                   color="#2e2723", zorder=4)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_)
        cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
        cb.ax.tick_params(labelsize=7)
        ax.set_xlim(97, 127); ax.set_ylim(19.5, 42.5)
        ax.set_aspect(1 / np.cos(np.radians(31)))
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(label, fontsize=11)
    fig.suptitle(T("標記字的地理分布:各州使用該字的詩人比例（★=長安）",
                   "Marker characters on the map: share of each prefecture's "
                   "poets using the character (★ = Chang'an)"), fontsize=13)
    fig.text(0.5, 0.012,
             T("上排:江南標記;下排:北方標記。僅顯示 ≥2 位詩人的州;"
               "點大小=詩人數;顏色=使用比例(各面板色階獨立)",
               "Top row: Jiangnan markers; bottom row: northern markers. "
               "Prefectures with >=2 poets only; dot size = poets; "
               "color = usage share (per-panel scale)"),
             ha="center", fontsize=9, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    save(fig, "fig20_char_maps.png", tight=False)


def _pref_data(min_poets=2):
    """(coords dict, dataset df restricted to located poets, with 'pref')."""
    import csv as _csv
    from gen_prefecture_coords import poet_prefectures
    coords = {}
    with open(os.path.join(HERE, "tang_prefecture_coords.csv"),
              encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            coords[row["prefecture"]] = (float(row["lon"]), float(row["lat"]))
    pp = poet_prefectures()
    dfa = load_df()
    dfa = dfa[dfa["poet"].map(lambda q: pp.get(q) in coords)].reset_index(drop=True)
    dfa["pref"] = dfa["poet"].map(pp)
    vc = dfa["pref"].value_counts()
    dfa = dfa[dfa["pref"].isin(vc[vc >= min_poets].index)].reset_index(drop=True)
    return coords, dfa


def _map_frame(ax):
    for poly in _china_rings():
        for ring in poly:
            ax.plot([pt[0] for pt in ring], [pt[1] for pt in ring],
                    color="#d5cfc6", lw=0.8, zorder=1)
    ax.set_xlim(97, 127); ax.set_ylim(19.5, 42.5)
    ax.set_aspect(1 / np.cos(np.radians(31)))
    ax.set_xticks([]); ax.set_yticks([])


def fig21_isogloss():
    # Isogloss-style two-character contrast: for each prefecture (>=2 poets)
    # the log-odds of poets using the southern marker 謾 vs the northern
    # marker 文 (Haldane 0.5). Red = 謾-leaning, blue = 文-leaning —
    # the dialect-atlas "one map, one contrast" presentation.
    import matplotlib.colors as mcolors
    CH_S, CH_N = "謾", "文"
    coords, dfa = _pref_data(min_poets=2)
    prefs = sorted(set(dfa["pref"]))

    def logodds(sub):
        n = len(sub)
        a = sub["text"].str.contains(CH_S, regex=False).sum()
        b = sub["text"].str.contains(CH_N, regex=False).sum()
        return (np.log((a + .5) / (n - a + .5))
                - np.log((b + .5) / (n - b + .5)))

    # centre on the corpus-wide balance: 文 is globally far more common
    # than 謾, so the isogloss contrast is each prefecture's DEVIATION
    # from the overall log-odds, not the raw value.
    base = logodds(dfa)
    vals, ns = {}, {}
    for p in prefs:
        sub = dfa[dfa["pref"] == p]
        vals[p] = logodds(sub) - base
        ns[p] = len(sub)
    lim = max(abs(v) for v in vals.values())
    norm_ = mcolors.Normalize(vmin=-lim, vmax=lim)
    cmap = plt.get_cmap("RdBu_r")
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    _map_frame(ax)
    for p in sorted(prefs, key=lambda q: -ns[q]):
        lon, lat = coords[p]
        ax.scatter(lon, lat, s=22 + ns[p] * 14, color=cmap(norm_(vals[p])),
                   edgecolor="#4a443e", lw=0.5, zorder=3)
    ax.scatter(*CIRCUIT_COORDS["關內道"], marker="*", s=230, color="#2e2723",
               zorder=4)
    ax.annotate(T("長安", "Chang'an"), CIRCUIT_COORDS["關內道"],
                textcoords="offset points", xytext=(8, -14), fontsize=10,
                fontweight="bold")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_)
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label(T(f"相對 log-odds:偏{CH_S}（紅） vs 偏{CH_N}（藍）",
                   f"relative log-odds: {CH_S}-leaning (red) vs "
                   f"{CH_N}-leaning (blue)"))
    ax.set_title(T(f"等語線式對比:南方口語「{CH_S}」 vs 北方文翰「{CH_N}」"
                   f"（每州 ≥2 位詩人）",
                   f"Isogloss-style contrast: southern colloquial {CH_S} vs "
                   f"northern {CH_N} 'letters' (prefectures with ≥2 poets)"))
    fig.text(0.5, 0.012,
             T("點大小=詩人數;顏色=該州兩字使用勝算比對數,相對全語料基準"
               "(Haldane 0.5 校正)",
               "Dot size = poets; color = log-odds of using each character, "
               "relative to the corpus-wide balance (Haldane 0.5)"),
             ha="center", fontsize=9, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig21_isogloss.png", tight=False)


def fig22_chars_on_map():
    # Humanistic opener: each circuit's top-3 discriminative characters
    # (multiclass LinearSVC weights, n-gram features only) printed AT the
    # circuit's location — the characters are the figure.
    dfc = apply_task(load_df(), "circuit")
    keep = dfc["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    dfc = dfc[dfc["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); yc = le.fit_transform(dfc["label"])
    Xc, vec, _ = build_features(dfc["text"].tolist())
    names = list(vec.get_feature_names_out())
    uni = [i for i, t in enumerate(names) if len(t) == 1]   # unigrams only
    clf = LinearSVC(class_weight="balanced", C=0.5).fit(Xc, yc)
    SOUTH_COL, NORTH_COL = "#a63c2a", "#2f5a8f"
    OFFS = {"江南道": (0.8, -1.8), "淮南道": (3.0, 0.2), "河南道": (-0.2, -1.9),
            "河北道": (2.4, 1.2), "河東道": (-2.6, 1.5), "關內道": (-1.6, -2.0)}
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    _map_frame(ax)
    for k, circ in enumerate(le.classes_):
        w = clf.coef_[k]
        top3 = [names[i] for i in sorted(uni, key=lambda j: -w[j])[:3]]
        lon, lat = CIRCUIT_COORDS[circ]
        dx, dy = OFFS.get(circ, (0, 1.0))
        col = SOUTH_COL if circ in SOUTH else NORTH_COL
        ax.scatter(lon, lat, s=30, color=col, zorder=3)
        ax.text(lon + dx, lat + dy + 0.55, " ".join(top3), fontsize=21,
                color=col, ha="center", fontweight="bold", zorder=4)
        ax.text(lon + dx, lat + dy - 0.35, R(circ), fontsize=9.5,
                color="#6b625a", ha="center", zorder=4)
    ax.scatter(*CIRCUIT_COORDS["關內道"], marker="*", s=230,
               color="#2e2723", zorder=5)
    ax.set_title(T("每道最具鑑別力的三個字（六道任務,SVC 權重）",
                   "Each circuit's three most discriminative characters "
                   "(six-circuit task, SVC weights)"))
    fig.text(0.5, 0.012,
             T("紅=南方道,藍=北方道;字由多分類 SVC 權重選出(僅 n-gram 特徵)"
               "——描述性呈現,個別字未經 FDR 認證",
               "Red = southern, blue = northern circuits; characters chosen "
               "by multiclass SVC weight (n-gram features only) — "
               "descriptive, not FDR-certified individually"),
             ha="center", fontsize=9, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig22_chars_on_map.png", tight=False)


def fig23_confidence_map():
    # Prefecture-level refinement of fig19: share of each prefecture's poets
    # correctly classified in the South/North CV (LogReg, 5-fold).
    import matplotlib.colors as mcolors
    coords, _ = _pref_data(min_poets=2)
    from gen_prefecture_coords import poet_prefectures
    pp = poet_prefectures()
    dfs = sn_label(load_df())
    y = LabelEncoder().fit_transform(dfs["label"])
    X, _, _ = build_features(dfs["text"].tolist())
    pred = cross_val_predict(
        LogisticRegression(max_iter=2000, class_weight="balanced"),
        X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    dfs = dfs.reset_index(drop=True)
    dfs["correct"] = pred == y
    dfs["pref"] = dfs["poet"].map(pp)
    dfs = dfs[dfs["pref"].map(lambda q: q in coords)]
    vc = dfs["pref"].value_counts()
    dfs = dfs[dfs["pref"].isin(vc[vc >= 2].index)]
    prefs = sorted(set(dfs["pref"]))
    cmap = plt.get_cmap("RdYlGn")
    norm_ = mcolors.Normalize(vmin=0, vmax=1)
    fig, ax = plt.subplots(figsize=(8.6, 7.2))
    _map_frame(ax)
    for p in sorted(prefs, key=lambda q: -vc[q]):
        sub = dfs[dfs["pref"] == p]
        lon, lat = coords[p]
        ax.scatter(lon, lat, s=22 + len(sub) * 14,
                   color=cmap(norm_(sub["correct"].mean())),
                   edgecolor="#4a443e", lw=0.5, zorder=3)
    ax.scatter(*CIRCUIT_COORDS["關內道"], marker="*", s=230, color="#2e2723",
               zorder=4)
    ax.annotate(T("長安", "Chang'an"), CIRCUIT_COORDS["關內道"],
                textcoords="offset points", xytext=(8, -14), fontsize=10,
                fontweight="bold")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_)
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label(T("南/北分類正確率（該州詩人）",
                   "share of prefecture's poets correctly classified (S/N)"))
    ax.set_title(T("模型信心地圖:各州詩人的南/北分類正確率（LogReg,5 折 CV）",
                   "Model-confidence map: South/North classification accuracy "
                   "by prefecture (LogReg, 5-fold CV)"))
    fig.text(0.5, 0.012,
             T("每州 ≥2 位詩人;點大小=詩人數(南/北任務,fig19 的府級細化)",
               "Prefectures with ≥2 poets; dot size = poets "
               "(S/N task — prefecture-level refinement of fig19)"),
             ha="center", fontsize=9, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    save(fig, "fig23_confidence_map.png", tight=False)


def fig12_hier_comparison():
    # Results from transformer_hier.py (one consistent pytorch291 GPU run,
    # south/north, StratifiedKFold(5), poet-level — same protocol as classical).
    feats = ["TF-IDF", "BERT(frozen)", "BERT+TF-IDF"]
    acc = {"LogReg": [0.603, 0.674, 0.653], "MLP": [0.674, 0.653, 0.636]}
    feats_lbl = feats if LANG == "zh" else feats
    x = np.arange(len(feats)); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x-w/2, acc["LogReg"], w, label="LogReg", color="#46a")
    ax.bar(x+w/2, acc["MLP"], w, label="MLP", color="#c44")
    ax.axhline(0.674, ls="--", c="green",
               label=T("最佳古典 0.67", "best classical 0.67"))
    ax.axhline(0.5, ls=":", c="gray")
    ax.set_xticks(x); ax.set_xticklabels(feats_lbl)
    ax.set_ylim(0, 0.85); ax.set_ylabel(T("南/北 accuracy", "South/North accuracy"))
    ax.set_title(T("公平比較:階層式 BERT vs TF-IDF（同一 5 折）",
                   "Fair comparison: hierarchical BERT vs TF-IDF (same 5-fold)"))
    ax.legend()
    for i in range(len(feats)):
        ax.text(i-w/2, acc["LogReg"][i]+.01, f"{acc['LogReg'][i]:.2f}",
                ha="center", fontsize=8)
        ax.text(i+w/2, acc["MLP"][i]+.01, f"{acc['MLP'][i]:.2f}",
                ha="center", fontsize=8)
    save(fig, "fig12_hier_comparison.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()
    LANG = args.lang
    FIGDIR = os.path.join(HERE, args.outdir or ("figures_en" if LANG == "en" else "figures"))
    os.makedirs(FIGDIR, exist_ok=True)
    # CJK-capable font (covers Latin too; needed for fig08 Chinese-character data).
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "Noto Sans CJK JP", "AR PL UMing CN"]
    plt.rcParams["axes.unicode_minus"] = False

    print(f"Writing {LANG} figures to {FIGDIR}/")
    for fn in [fig06_region_distribution, fig02_confusion, fig03_distance_decay,
               fig04_era_evolution, fig05_misclass_by_era, fig07_domain_radar,
               fig08_discriminative_chars, fig10_length_control, fig11_periphery,
               fig09_transformer, fig12_hier_comparison, fig13_jiangnan_markers,
               fig14_jiangnan_forest, fig15_permutation_test, fig16_era_ci,
               fig17_ablation, fig18_prefecture_mantel, fig19_map_recall,
               fig20_char_maps, fig21_isogloss, fig22_chars_on_map,
               fig23_confidence_map, fig01_model_comparison]:
        try:
            fn()
        except Exception as e:
            print(f"  !! {fn.__name__} failed: {e}")
    print("Done.")
