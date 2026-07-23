# -*- coding: utf-8 -*-
"""
Dump the exact group definitions and full membership to files:
  group_membership.csv   one row per poem, with a flag for every group
  group_definitions.md   human-readable definitions, set overlaps, listings,
                         and the data caveats found during review.

Run:  python3 dump_groups.py
"""
import os
import csv
import collections

import corpus
import analyze_diction as A
import analyze_syntax as SYN

HERE = os.path.dirname(os.path.abspath(__file__))


def poem_form(rec):
    lens = [len(c) for c in rec.get("clauses", []) if 2 <= len(c) <= 12]
    if not lens:
        return "雜言"
    mode = collections.Counter(lens).most_common(1)[0][0]
    return {5: "五言", 7: "七言"}.get(mode, "雜言")


def main():
    recs = corpus.load_records_structured()
    g = A.build_groups(recs=recs)
    K = A._key
    sets = {name: set(K(r) for r in g[name])
            for name in ("G1", "G1m", "G2", "G3", "G3d", "G3l")}

    # universe of poems = G1 ∪ G2, keep one record each (prefer one carrying gender)
    uni = {}
    for name in ("G1", "G2"):
        for r in g[name]:
            uni.setdefault(K(r), r)

    # ---- membership CSV --------------------------------------------------
    rows = []
    for k, r in uni.items():
        rows.append({
            "author": r["author"], "title": r["title"],
            "gender": r.get("gender", ""), "n_chars": len(r["text"]),
            "form": poem_form(r),
            "G1_宮怨詩": int(k in sets["G1"]),
            "G1m_代言": int(k in sets["G1m"]),
            "G2_女詩人": int(k in sets["G2"]),
            "G3_女性自述": int(k in sets["G3"]),
            "G3d_宮詞記事": int(k in sets["G3d"]),
            "G3l_閨怨抒情": int(k in sets["G3l"]),
        })
    rows.sort(key=lambda x: (-x["G1_宮怨詩"], x["author"], x["title"]))
    cols = ["author", "title", "gender", "n_chars", "form", "G1_宮怨詩",
            "G1m_代言", "G2_女詩人", "G3_女性自述", "G3d_宮詞記事", "G3l_閨怨抒情"]
    with open(os.path.join(HERE, "group_membership.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    # ---- definitions markdown -------------------------------------------
    def tbl(records, cols3=True):
        L = ["| 作者 | 題目 | 字數 |", "|---|---|--:|"] if cols3 else \
            ["| 作者 | 題目 | 性別 | 字數 |", "|---|---|:-:|--:|"]
        for r in sorted(records, key=lambda x: (-len(x["text"]), x["author"])):
            if cols3:
                L.append(f"| {r['author']} | {r['title']} | {len(r['text'])} |")
            else:
                L.append(f"| {r['author']} | {r['title']} | {r.get('gender','')} | {len(r['text'])} |")
        return L

    def author_summary(records):
        c = collections.Counter(r["author"] for r in records)
        ch = collections.Counter()
        for r in records:
            ch[r["author"]] += len(r["text"])
        L = ["| 作者 | 詩數 | 字數 |", "|---|--:|--:|"]
        for a, n in c.most_common():
            L.append(f"| {a} | {n} | {ch[a]} |")
        return L

    na = lambda name: len(set(r["author"] for r in g[name]))
    L = []
    L.append("# 分群定義與成員明細\n")
    L.append("由 `dump_groups.py` 產生。完整逐首資料見 `group_membership.csv`"
             "（一首一列，每組一個 0/1 旗標）。\n")

    L.append("## 一、分群定義\n")
    L.append("| 組別 | 定義 | 詩數 | 作者數 |")
    L.append("|---|---|--:|--:|")
    L.append(f"| **G1 宮怨詩** | 宮怨詩名單（`data/data_index/*.csv`，欄位 作者,性別,題目）"
             f"每首，經標題正規化比對到語料者 | {len(g['G1'])} | {na('G1')} |")
    L.append(f"| **G1m 代言** | G1 中 `性別 == 男`（男性代言） | {len(g['G1m'])} | {na('G1m')} |")
    L.append(f"| **G2 女詩人** | 語料中作者 ∈（名單 `性別==女` ∪ `data/female_poets.txt` 補入）"
             f"之全部詩 | {len(g['G2'])} | {na('G2')} |")
    L.append(f"| **G3 女性自述** | （G1 中 `性別==女`）∪（G2 中標題含宮/閨題材關鍵字者） "
             f"| {len(g['G3'])} | {na('G3')} |")
    L.append(f"| **G3d 宮詞記事** | G3 中標題判為記事（見下關鍵字） | {len(g['G3d'])} | {na('G3d')} |")
    L.append(f"| **G3l 閨怨抒情** | G3 中標題判為抒情（見下關鍵字） | {len(g['G3l'])} | {na('G3l')} |")
    L.append("")
    L.append("**子類關鍵字（標題比對）**")
    L.append(f"- 閨怨抒情（lyric）：{'、'.join(A.LYRIC_KW)}")
    L.append(f"- 宮詞記事（doc）：{'、'.join(A.DOC_KW)}、或「題」開頭")
    L.append("- 判定順序：先 lyric 後 doc；G1 女性列若兩者皆非，預設 lyric（名單本為宮怨）。\n")

    L.append("## 二、集合關係\n")
    L.append("| 關係 | 值 |")
    L.append("|---|---|")
    L.append(f"| G3d ∩ G3l | {len(sets['G3d'] & sets['G3l'])}（兩子類互斥）|")
    L.append(f"| G3d ⊆ G2 | {len(sets['G3d'] & sets['G2'])}/{len(sets['G3d'])} |")
    L.append(f"| G3l ⊆ G2 | {len(sets['G3l'] & sets['G2'])}/{len(sets['G3l'])} |")
    L.append(f"| G3 ⊆ G2 | {len(sets['G3'] & sets['G2'])}/{len(sets['G3'])} |")
    L.append(f"| G3d ∩ G1m（代言）| {len(sets['G3d'] & sets['G1m'])} |")
    L.append(f"| G3l ∩ G1m（代言）| {len(sets['G3l'] & sets['G1m'])} |")
    L.append(f"| G3d ∩ G1（宮怨名單）| {len(sets['G3d'] & sets['G1'])} |")
    L.append(f"| G3l ∩ G1（宮怨名單）| {len(sets['G3l'] & sets['G1'])} |")
    L.append("")

    L.append("## 三、女性自述明細（G3 = 19）\n")
    L.append("### G3d 宮詞記事（8）")
    L += tbl(g["G3d"])
    L.append("")
    L.append("### G3l 閨怨抒情（11）")
    L += tbl(g["G3l"])
    L.append("")

    L.append("## 四、代言（G1m）作者彙總\n")
    L += author_summary(g["G1m"])
    L.append("")
    L.append("## 五、女詩人（G2）作者彙總\n")
    L += author_summary(g["G2"])
    L.append("")

    L.append("## 六、資料 caveat\n")
    hy = [r for r in g["G3d"] if r["author"] == "花蕊夫人"]
    hy_chars = sum(len(r["text"]) for r in hy)
    g3d_chars = sum(len(r["text"]) for r in g["G3d"])
    L.append(f"- **G3d 宮詞記事以字數計，{100*hy_chars/max(g3d_chars,1):.0f}% 為花蕊夫人《宮詞》**"
             f"（{hy_chars} / {g3d_chars} 字）；log-odds/語彙場按字加權，故該組≈花蕊夫人一人。")
    L.append("- **關鍵字誤抓**：G3d 內 `薛濤 題竹郎廟`、`魚玄機 題隱霧亭/題任處士創資福寺` 為"
             "題寺題景之作，非宮廷記事（被 `題` 開頭誤納）；`鮑君徽 奉和…應制` 為宮廷應制。"
             "真正宮詞記事僅花蕊夫人《宮詞》+ 3 首宮人題葉詩。")
    L.append("- **小樣本**：G3l n=11、G3d n=8，比率與 z 值波動大，結論屬 suggestive。")
    L.append("- **名單未比對 45 筆**（作者不在語料/語料未爬到之卷）見 `unmatched_list.csv`。")

    with open(os.path.join(HERE, "group_definitions.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print(f"wrote group_membership.csv ({len(rows)} poems) and group_definitions.md")


if __name__ == "__main__":
    main()
