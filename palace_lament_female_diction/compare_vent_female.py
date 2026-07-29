# -*- coding: utf-8 -*-
"""
Focused two-group comparison: 代言 (G1m, male-ventriloquized palace-lament) vs
女詩人 (G2, all poems by female poets). Redraws figures for just these two groups
and writes a report. Both are large (256 vs 214), so this is the most robust
contrast in the study (it avoids the small-n G3 subgroups).

Figures (zh -> figures_cmp/, en -> figures_cmp_en/):
  cmp1_terms      distinctive terms, 代言 vs 女詩人 (diverging log-odds)
  cmp2_fields     five palace-lament lexical fields, grouped bar
  cmp3_form       poem form (五言/七言/雜言), stacked
  cmp4_funcwords  function-word classes, grouped horizontal bar

Usage:  python3 compare_vent_female.py
"""
import os
import collections

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import corpus
import analyze_diction as A
import analyze_syntax as S
import make_figures as MF

HERE = os.path.dirname(os.path.abspath(__file__))
C_VENT, C_FEM = "#3b6ea5", "#c8553d"


def build():
    recs = corpus.load_records_structured()
    g = A.build_groups(recs=recs)
    return g["recs"], g["G1m"], g["G2"]


def figures(lang, recs, vent, fem):
    en = lang == "en"
    figdir = os.path.join(HERE, "figures_cmp_en" if en else "figures_cmp")
    os.makedirs(figdir, exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "Noto Sans CJK JP",
                                       "Noto Sans CJK SC", "AR PL UMing CN"]
    plt.rcParams["axes.unicode_minus"] = False
    T = lambda zh, e: e if en else zh
    NV, NF = T("代言", "male poets"), T("女詩人", "female poets")

    def save(fig, name):
        fig.tight_layout(); fig.savefig(os.path.join(figdir, name), dpi=130)
        plt.close(fig); print(f"  saved {os.path.basename(figdir)}/{name}")

    bg = A.counts(recs)
    cv, cf = A.counts(vent), A.counts(fem)

    # cmp1 distinctive terms (diverging)
    a_side, b_side = A.weighted_logodds(cv, cf, bg, top=20)
    items = list(b_side)[::-1] + list(a_side)[::-1]
    terms = [w for w, _ in items]
    zs = [z for _, z in items]
    labels = [MF.gloss_label(w) for w in terms] if en else terms
    colors = [C_VENT if z > 0 else C_FEM for z in zs]
    fig, ax = plt.subplots(figsize=(9.0 if en else 7.2, 0.34 * len(items) + 1))
    ax.barh(range(len(items)), zs, color=colors, edgecolor="none")
    ax.set_yticks(range(len(items))); ax.set_yticklabels(labels, fontsize=10 if en else 11)
    ax.axvline(0, color="#444", lw=.8)
    ax.set_xlabel(T(f"加權 log-odds z（← 偏 {NF} ｜ 偏 {NV} →）",
                    f"weighted log-odds z  (← {NF}  |  {NV} →)"))
    ax.set_title(T("代言 vs 女詩人：最具區辨力字詞",
                   "Ventriloquism vs. female poets: distinctive terms"))
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=C_VENT, label=NV), Patch(color=C_FEM, label=NF)],
              loc="lower right", frameon=False, fontsize=9)
    save(fig, "cmp1_terms.png")

    # cmp2 lexical fields (grouped bar)
    fields = list(A.LEXICAL_FIELDS)
    pv, pf = A.field_profile(vent), A.field_profile(fem)
    lab = [f.split("(")[1].rstrip(")") if en else f.split(" (")[0] for f in fields]
    x = np.arange(len(fields)); w = 0.38
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.bar(x - w/2, [pv[f] for f in fields], w, label=NV, color=C_VENT)
    ax.bar(x + w/2, [pf[f] for f in fields], w, label=NF, color=C_FEM)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=10)
    ax.set_ylabel(T("每萬字次數", "per 10k chars"))
    ax.set_title(T("宮怨語彙場：代言 vs 女詩人", "Lexical fields: ventriloquism vs. female poets"))
    ax.legend(frameon=False)
    save(fig, "cmp2_fields.png")

    # cmp3 poem form (stacked)
    sv, sf = S.syntax_profile(vent), S.syntax_profile(fem)
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    gl = [NV, NF]
    p5 = [sv["pct_5"], sf["pct_5"]]; p7 = [sv["pct_7"], sf["pct_7"]]
    pm = [sv["pct_misc"], sf["pct_misc"]]
    ax.bar(gl, p5, label=T("五言", "5-syllable"), color="#3b6ea5")
    ax.bar(gl, p7, bottom=p5, label=T("七言", "7-syllable"), color="#c8553d")
    ax.bar(gl, pm, bottom=[a+b for a, b in zip(p5, p7)], label=T("雜言", "mixed"), color="#999")
    ax.set_ylabel("% of poems")
    ax.set_title(T("詩形分布", "Poem form"))
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(.5, 1.02))
    save(fig, "cmp3_form.png")

    # cmp4 function-word classes (grouped horizontal bar)
    cats = list(S.POS_CLASSES)
    qv, qf = S.pos_profile(vent), S.pos_profile(fem)
    ylab = [c.split("(")[1].rstrip(")") if en else c.split(" (")[0] for c in cats]
    y = np.arange(len(cats)); h = 0.38
    fig, ax = plt.subplots(figsize=(7.6, 6))
    ax.barh(y + h/2, [qv[c] for c in cats], h, label=NV, color=C_VENT)
    ax.barh(y - h/2, [qf[c] for c in cats], h, label=NF, color=C_FEM)
    ax.set_yticks(y); ax.set_yticklabels(ylab, fontsize=10); ax.invert_yaxis()
    ax.set_xlabel(T("每萬字次數", "per 10k chars"))
    ax.set_title(T("詞性・虛詞類：代言 vs 女詩人", "Function-word classes: vent. vs. female"))
    ax.legend(frameon=False)
    save(fig, "cmp4_funcwords.png")

    return dict(terms=(a_side, b_side), fields=(pv, pf), syn=(sv, sf), pos=(qv, qf))


def main():
    recs, vent, fem = build()
    print(f"G1m 代言 = {len(vent)} 首 / G2 女詩人 = {len(fem)} 首")
    data = figures("zh", recs, vent, fem)
    figures("en", recs, vent, fem)

    pv, pf = data["fields"]; sv, sf = data["syn"]; qv, qf = data["pos"]
    print("\n=== 語彙場 (每萬字) ===")
    for f in A.LEXICAL_FIELDS:
        print(f"  {f:20s} 代言 {pv[f]:6.1f} | 女詩人 {pf[f]:6.1f}")
    print("\n=== 句式 ===")
    for lab, k in [("五言%", "pct_5"), ("七言%", "pct_7"), ("問句/100句", "q_per100cl"),
                   ("疊字/100字", "redup_per100")]:
        print(f"  {lab:12s} 代言 {sv[k]:6.2f} | 女詩人 {sf[k]:6.2f}")
    print("\n=== 詞性・虛詞 (每萬字) ===")
    for c in S.POS_CLASSES:
        print(f"  {c:20s} 代言 {qv[c]:6.1f} | 女詩人 {qf[c]:6.1f}")


if __name__ == "__main__":
    main()
