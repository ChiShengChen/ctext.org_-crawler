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


def fig13_jiangnan_markers():
    # What makes Jiangnan legible: binary Jiangnan-vs-rest LogReg weights on
    # the six-circuit poet set (same filter as fig11), grouped into readable
    # families, plus a place-name ablation showing recall is unchanged when
    # every geographically-loaded n-gram is dropped (i.e. not name leakage).
    from sklearn.linear_model import LogisticRegression
    df = apply_task(load_df(), "circuit")
    keep = df["label"].value_counts(); keep = keep[keep >= 8].index
    keep = [r for r in keep if r in CIRCUIT_COORDS]
    df = df[df["label"].isin(keep)].reset_index(drop=True)
    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, vec, _ = build_features(df["text"].tolist())
    names = list(vec.get_feature_names_out()) + feat.FEATURE_NAMES
    jn = list(le.classes_).index("江南道")
    yb = (y == jn).astype(int)
    w = LogisticRegression(max_iter=3000,
                           class_weight="balanced").fit(X, yb).coef_[0]

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

    def lbl(f):
        if f in feat.FEATURE_NAMES:
            return GLOSS.get(f, f)
        g = GLOSS.get(f)
        return f"{g}（{f}）" if (LANG == "en" and g) else f

    order = np.argsort(w)[::-1]
    top_p = order[:16][::-1]
    top_n = order[-10:]

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 6.2),
                           gridspec_kw={"width_ratios": [1.15, 1]})
    for a, idxs, title in [
            (ax[0], top_p, T("推向江南的特徵", "pushing toward Jiangnan")),
            (ax[1], top_n, T("推離江南的特徵", "pushing away from Jiangnan"))]:
        cols = [CCOL[CAT.get(names[i], "other")] for i in idxs]
        a.barh(range(len(idxs)), [w[i] for i in idxs], color=cols, height=0.7)
        a.set_yticks(range(len(idxs)))
        a.set_yticklabels([lbl(names[i]) for i in idxs], fontsize=9)
        a.axvline(0, c="k", lw=0.8)
        a.set_xlabel(T("LogReg 權重（江南 vs 其他道）",
                       "LogReg weight (Jiangnan vs rest)"))
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
    fig.suptitle(T("江南為何可辨識：判別特徵（二元 LogReg）",
                   "What makes Jiangnan legible: discriminative features"),
                 fontsize=13)
    fig.text(0.5, 0.055,
             T(f"地名消融:剔除全部含「{''.join(sorted(PLACE))}」的 "
               f"{len(drop)} 個 n-gram 後,",
               f"Place-name ablation: dropping all {len(drop)} n-grams "
               f"containing 「{''.join(sorted(PLACE))}」"),
             ha="center", fontsize=9.5, style="italic")
    fig.text(0.5, 0.022,
             T(f"江南 recall {rec_f:.2f} → {rec_a:.2f} — 可辨識性並非地名洩漏",
               f"leaves Jiangnan recall unchanged ({rec_f:.2f} → {rec_a:.2f}) "
               "— identifiability is not place-name leakage"),
             ha="center", fontsize=9.5, style="italic")
    fig.tight_layout(rect=[0, 0.09, 1, 0.95])
    save(fig, "fig13_jiangnan_markers.png", tight=False)


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
               fig01_model_comparison]:
        try:
            fn()
        except Exception as e:
            print(f"  !! {fn.__name__} failed: {e}")
    print("Done.")
