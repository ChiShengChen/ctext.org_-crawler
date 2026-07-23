# -*- coding: utf-8 -*-
"""
Figures for the palace-lament / female-poet diction study. Mirrors the style of
`../poet_origin_predictor/make_figures.py` (matplotlib, CJK font, dpi 130).

  fig1_genre_terms      宮怨詩 vs 女性詩人   最具區辨力字詞(diverging bar)
  fig2_voice_terms      男性代言 vs 女性閨怨抒情  區辨字詞
  fig3_lexical_fields   四組 × 五語彙場  分組長條圖
  fig4_subgenre_terms   宮詞記事 vs 閨怨抒情  區辨字詞

Usage:  python3 make_figures.py [--lang zh|en] [--top 15]
"""
import os
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import analyze_diction as A

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
LANG = "zh"

# Two-sided palette: 宮怨/男性代言 (cool) vs 女性 (warm).
C_PALACE, C_FEMALE = "#3b6ea5", "#c8553d"
C_FIELDS = ["#3b6ea5", "#c8553d", "#e0a458", "#5b8c5a"]   # 代言/閨怨/宮詞/女詩人


def T(zh, en):
    return en if LANG == "en" else zh


def save(fig, name):
    os.makedirs(FIGDIR, exist_ok=True)
    p = os.path.join(FIGDIR, name)
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print(f"  saved {os.path.relpath(p, HERE)}")


def diverging_terms(a_side, b_side, name_a, name_b, title, fname, top):
    """a_side: (term, z) with z>0 distinctive of A; b_side: z<0 distinctive of B."""
    items = list(b_side[:top])[::-1] + list(a_side[:top])[::-1]
    terms = [w for w, _ in items]
    zs = [z for _, z in items]
    colors = [C_PALACE if z > 0 else C_FEMALE for z in zs]
    fig, ax = plt.subplots(figsize=(7.2, max(4, 0.34 * len(items) + 1)))
    ax.barh(range(len(items)), zs, color=colors, edgecolor="none")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(terms, fontsize=11)
    ax.axvline(0, color="#444", lw=.8)
    ax.set_xlabel(T("加權 log-odds z（← 偏 {} ｜ 偏 {} →）".format(name_b, name_a),
                    "weighted log-odds z  (← {}  |  {} →)".format(name_b, name_a)))
    ax.set_title(title)
    # legend proxies
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=C_PALACE, label=name_a),
                       Patch(color=C_FEMALE, label=name_b)],
              loc="lower right", frameon=False, fontsize=9)
    save(fig, fname)


def fig_lexical_fields(profs, top=None):
    fields = list(A.LEXICAL_FIELDS.keys())
    labels_zh = [f.split(" (")[0] for f in fields]
    labels_en = [f.split("(")[1].rstrip(")") for f in fields]
    labels = labels_en if LANG == "en" else labels_zh
    groups = list(profs.keys())
    import numpy as np
    x = np.arange(len(fields)); w = 0.8 / len(groups)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for i, gname in enumerate(groups):
        vals = [profs[gname][f] for f in fields]
        ax.bar(x + i * w, vals, w, label=gname, color=C_FIELDS[i % len(C_FIELDS)])
    ax.set_xticks(x + w * (len(groups) - 1) / 2)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(T("每萬字出現次數", "occurrences per 10k chars"))
    ax.set_title(T("宮怨語彙場：四組對照", "Palace-lament lexical fields across groups"))
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig3_lexical_fields.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    global LANG, FIGDIR
    LANG = args.lang
    FIGDIR = os.path.join(HERE, "figures_en" if LANG == "en" else "figures")

    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "Noto Sans CJK JP",
                                       "Noto Sans CJK SC", "AR PL UMing CN"]
    plt.rcParams["axes.unicode_minus"] = False

    g = A.build_groups()
    bg = A.counts(g["recs"])
    c = {k: A.counts(g[k]) for k in ("G1", "G2", "G1m", "G3d", "G3l")}
    print(f"groups: G1={len(g['G1'])} G1m={len(g['G1m'])} G2={len(g['G2'])} "
          f"G3d={len(g['G3d'])} G3l={len(g['G3l'])}")

    a1, b1 = A.weighted_logodds(c["G1"], c["G2"], bg, top=args.top)
    diverging_terms(a1, b1, T("宮怨詩", "palace-lament"), T("女性詩人", "female poets"),
                    T("宮怨詩 vs 女性詩人：最具區辨力字詞",
                      "Palace-lament vs. female poets: distinctive terms"),
                    "fig1_genre_terms.png", args.top)

    if g["G1m"] and g["G3l"]:
        a2, b2 = A.weighted_logodds(c["G1m"], c["G3l"], bg, top=args.top)
        diverging_terms(a2, b2, T("男性代言", "male ventriloquism"),
                        T("女性閨怨", "female self-voice"),
                        T("男性代言 vs 女性閨怨抒情（n 小，示意）",
                          "Male ventriloquism vs. female lament (small n)"),
                        "fig2_voice_terms.png", args.top)

    if g["G3d"] and g["G3l"]:
        a4, b4 = A.weighted_logodds(c["G3d"], c["G3l"], bg, top=args.top)
        diverging_terms(a4, b4, T("宮詞記事", "documentary"), T("閨怨抒情", "lyrical lament"),
                        T("女性自述：宮詞記事 vs 閨怨抒情",
                          "Female self-voice: documentary vs. lyrical"),
                        "fig4_subgenre_terms.png", args.top)

    import collections
    profs = collections.OrderedDict()
    profs[T("代言", "ventriloquism")] = A.field_profile(g["G1m"])
    profs[T("閨怨", "lyric lament")] = A.field_profile(g["G3l"])
    profs[T("宮詞", "documentary")] = A.field_profile(g["G3d"])
    profs[T("女詩人", "female poets")] = A.field_profile(g["G2"])
    fig_lexical_fields(profs)


if __name__ == "__main__":
    main()
