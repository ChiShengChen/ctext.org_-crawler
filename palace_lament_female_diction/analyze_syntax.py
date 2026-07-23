# -*- coding: utf-8 -*-
"""
Sentence-pattern (句式) and part-of-speech / function-word (詞性・虛詞) analysis
across the same groups as analyze_diction.

No reliable Classical-Chinese POS tagger is bundled (stanza-lzh absent; jieba/
spaCy are modern-Chinese models that mis-tag 文言). We therefore use two
文言-appropriate, transparent devices:

  句式 (structural, from the 句-segmented corpus):
    - 詩形       %五言 / %七言 / %雜言 (dominant clause length per poem)
    - 平均句長    mean clause length
    - 篇幅       mean clauses per poem
    - 疊字率      AA reduplication per 100 chars
    - 問句率      clauses containing an interrogative per 100 clauses

  詞性・虛詞 (curated Classical-Chinese function-word classes, per 10k chars):
    人稱代詞(一/二/三)、疑問詞、否定詞、副詞、連介詞、語氣助詞、方位詞、時間詞

Groups reused from analyze_diction: G1m 代言 / G3l 閨怨 / G3d 宮詞 / G2 女詩人.

Usage:  python3 analyze_syntax.py
"""
import os
import argparse
import collections

import corpus
import analyze_diction as A

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
C_GROUPS = ["#3b6ea5", "#c8553d", "#e0a458", "#5b8c5a"]   # 代言/閨怨/宮詞/女詩人

INTERROGATIVE = set("何誰安焉寧豈胡奚曷孰")
POS_CLASSES = collections.OrderedDict([
    ("一人稱 (1st-pers)", set("我吾余予妾儂朕")),
    ("二人稱 (2nd-pers)", set("君爾汝卿子若")),
    ("三/指示 (3rd/dem)", set("其之彼此是伊渠厥")),
    ("疑問 (interrog)",   set("何誰安焉寧豈胡奚曷孰")),
    ("否定 (negation)",   set("不無未莫非勿毋靡")),
    ("副詞 (adverb)",     set("猶尚已復更但唯惟皆俱空自獨還祇只方將漸")),
    ("連介詞 (conj/prep)", set("與及而則以於于為向從因隨")),
    ("語氣助詞 (particle)", set("兮矣也乎哉耳歟耶邪焉")),
    ("方位 (locative)",   set("上下中內外前後東西南北")),
    ("時間 (temporal)",   set("昔今曾嘗忽漸長永朝暮夜晝")),
])


def poem_form(rec):
    lens = [len(c) for c in rec["clauses"] if 2 <= len(c) <= 12]
    if not lens:
        return "雜言"
    mode = collections.Counter(lens).most_common(1)[0][0]
    return {5: "五言", 7: "七言"}.get(mode, "雜言")


def reduplication_count(text):
    return sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1])


def syntax_profile(records):
    n_poems = len(records)
    forms = collections.Counter(poem_form(r) for r in records)
    clause_lens, n_clauses, chars = [], 0, 0
    redup, q_clauses, tot_clauses = 0, 0, 0
    for r in records:
        cls = [c for c in r["clauses"] if c]
        n_clauses += len(cls)
        tot_clauses += len(cls)
        chars += len(r["text"])
        redup += reduplication_count(r["text"])
        for c in cls:
            clause_lens.append(len(c))
            if any(ch in INTERROGATIVE for ch in c):
                q_clauses += 1
    chars = max(chars, 1)
    return {
        "n_poems": n_poems,
        "pct_5": 100 * forms["五言"] / max(n_poems, 1),
        "pct_7": 100 * forms["七言"] / max(n_poems, 1),
        "pct_misc": 100 * forms["雜言"] / max(n_poems, 1),
        "mean_clause_len": sum(clause_lens) / max(len(clause_lens), 1),
        "clauses_per_poem": n_clauses / max(n_poems, 1),
        "redup_per100": 100 * redup / chars,
        "q_per100cl": 100 * q_clauses / max(tot_clauses, 1),
    }


def pos_profile(records):
    joined = "".join(r["text"] for r in records)
    n = max(len(joined), 1)
    return {name: sum(joined.count(ch) for ch in chars) / n * 1e4
            for name, chars in POS_CLASSES.items()}


def make_figures(groups, syn, pos):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "Noto Sans CJK JP",
                                       "Noto Sans CJK SC", "AR PL UMing CN"]
    plt.rcParams["axes.unicode_minus"] = False
    os.makedirs(FIGDIR, exist_ok=True)
    names = list(groups)

    def save(fig, name):
        fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, name), dpi=130)
        plt.close(fig); print(f"  saved figures/{name}")

    # fig5 詩形分布 (stacked)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    p5 = [syn[n]["pct_5"] for n in names]
    p7 = [syn[n]["pct_7"] for n in names]
    pm = [syn[n]["pct_misc"] for n in names]
    ax.bar(names, p5, label="五言", color="#3b6ea5")
    ax.bar(names, p7, bottom=p5, label="七言", color="#c8553d")
    ax.bar(names, pm, bottom=[a + b for a, b in zip(p5, p7)], label="雜言", color="#999")
    ax.set_ylabel("% of poems"); ax.set_title("詩形分布(五言 / 七言 / 雜言)")
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(.5, 1.02))
    save(fig, "fig5_poem_form.png")

    # fig6 虛詞類 heatmap (row-normalized colour, raw annotations)
    cats = list(POS_CLASSES)
    M = np.array([[pos[n][c] for n in names] for c in cats])
    Mn = (M - M.min(1, keepdims=True)) / (M.ptp(1, keepdims=True) + 1e-9)
    fig, ax = plt.subplots(figsize=(7.4, 6))
    ax.imshow(Mn, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, fontsize=10)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([c.split(" (")[0] for c in cats], fontsize=10)
    for i in range(len(cats)):
        for j in range(len(names)):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=9,
                    color="#222" if Mn[i, j] < .6 else "white")
    ax.set_title("詞性・虛詞類(每萬字;色階為列內相對高低)")
    save(fig, "fig6_function_words.png")

    # fig7 語域標記 grouped bar (per-10k function-word markers)
    markers = ["二人稱 (2nd-pers)", "一人稱 (1st-pers)", "疑問 (interrog)",
               "語氣助詞 (particle)", "時間 (temporal)"]
    x = np.arange(len(markers)); w = 0.8 / len(names)
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    for i, n in enumerate(names):
        ax.bar(x + i * w, [pos[n][m] for m in markers], w, label=n, color=C_GROUPS[i])
    ax.set_xticks(x + w * (len(names) - 1) / 2)
    ax.set_xticklabels([m.split(" (")[0] for m in markers], fontsize=10)
    ax.set_ylabel("每萬字次數"); ax.set_title("語域標記:人稱・疑問・語氣・時間")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "fig7_register_markers.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", action="store_true", help="also write fig5–7")
    args = ap.parse_args()
    recs = corpus.load_records_structured()
    g = A.build_groups(recs=recs)
    groups = collections.OrderedDict([
        ("G1m 代言", g["G1m"]), ("G3l 閨怨", g["G3l"]),
        ("G3d 宮詞", g["G3d"]), ("G2 女詩人", g["G2"]),
    ])

    syn = {name: syntax_profile(recs_) for name, recs_ in groups.items()}
    pos = {name: pos_profile(recs_) for name, recs_ in groups.items()}

    print("=== 句式 (sentence patterns) ===")
    metrics = [("詩數", "n_poems", "{:.0f}"),
               ("五言%", "pct_5", "{:.0f}"), ("七言%", "pct_7", "{:.0f}"),
               ("雜言%", "pct_misc", "{:.0f}"),
               ("平均句長", "mean_clause_len", "{:.2f}"),
               ("句數/首", "clauses_per_poem", "{:.1f}"),
               ("疊字/100字", "redup_per100", "{:.2f}"),
               ("問句/100句", "q_per100cl", "{:.2f}")]
    print("  " + "指標".ljust(14) + "".join(k.ljust(11) for k in groups))
    for label, key, fmt in metrics:
        print("  " + label.ljust(14) +
              "".join(fmt.format(syn[k][key]).ljust(11) for k in groups))

    print("\n=== 詞性・虛詞 (每萬字次數) ===")
    print("  " + "詞類".ljust(20) + "".join(k.ljust(11) for k in groups))
    for cls in POS_CLASSES:
        print("  " + cls.ljust(20) +
              "".join(f"{pos[k][cls]:>6.1f}".ljust(11) for k in groups))

    if args.figures:
        make_figures(groups, syn, pos)
    _write_report(groups, syn, pos, metrics)


def _write_report(groups, syn, pos, metrics):
    L = ["# 宮怨詩 vs 女性詩人 — 句式・詞性用法報告\n",
         "由 `analyze_syntax.py` 產生。文言無可靠 POS 標註器,故以結構特徵(句式)"
         "與古漢語虛詞詞類(詞性)分析,皆可解釋、可重現。\n",
         "## 句式 (sentence patterns)\n",
         "| 指標 | " + " | ".join(groups) + " |",
         "|" + "---|" * (len(groups) + 1)]
    for label, key, fmt in metrics:
        L.append(f"| {label} | " + " | ".join(fmt.format(syn[k][key]) for k in groups) + " |")
    L += ["\n## 詞性・虛詞 (每萬字次數)\n",
          "| 詞類 | " + " | ".join(groups) + " |",
          "|" + "---|" * (len(groups) + 1)]
    for cls in POS_CLASSES:
        L.append(f"| {cls} | " + " | ".join(f"{pos[k][cls]:.1f}" for k in groups) + " |")
    L += ["\n> ⚠️ G3l(閨怨 n≈11)、G3d(宮詞 n≈8)樣本小,句式/虛詞比率波動大,屬 suggestive。"]
    with open(os.path.join(HERE, "syntax_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\nSaved -> syntax_report.md")


if __name__ == "__main__":
    main()
