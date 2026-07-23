# -*- coding: utf-8 -*-
"""
Export the original text (原文, punctuation kept) of every poem in the study,
one file per poem, under poems/<group>/. Groups exported:
  poems/G1_宮怨詩/   all palace-lament poems (321)
  poems/G2_女詩人/   all poems by female poets (214)
Female palace-lament poems appear in both folders (convenience). A manifest.csv
maps each file to author / title / gender / groups.

Run:  python3 export_poems.py
"""
import os
import re
import csv

import corpus
import analyze_diction as A

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "poems")
_BAD = re.compile(r'[\\/:*?"<>|\n\r\t]+')


def sanitize(s):
    return _BAD.sub("_", s).strip()[:50]


def dump(records, subdir):
    d = os.path.join(OUT, subdir)
    os.makedirs(d, exist_ok=True)
    manifest = []
    ordered = sorted(records, key=lambda r: (r["author"], r["title"]))
    for i, r in enumerate(ordered, 1):
        body = r.get("raw") or "\n".join(r.get("clauses", [])) or r["text"]
        fn = f"{i:03d}_{sanitize(r['author'])}_{sanitize(r['title'])}.txt"
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            f.write(f"{r['author']}《{r['title']}》\n")
            f.write("=" * 28 + "\n")
            f.write(body.rstrip() + "\n")
        manifest.append((subdir, fn, r["author"], r["title"],
                         r.get("gender", ""), len(r["text"])))
    return manifest


def main():
    recs = corpus.load_records_structured()
    g = A.build_groups(recs=recs)
    rows = []
    rows += dump(g["G1"], "G1_宮怨詩")
    rows += dump(g["G2"], "G2_女詩人")
    with open(os.path.join(OUT, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["folder", "file", "author", "title", "gender", "n_chars"])
        w.writerows(rows)
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write("# 詩作原文（poems/）\n\n"
                "各詩原文（保留標點與分行），由 `export_poems.py` 從《全唐詩》語料匯出。\n\n"
                f"- `G1_宮怨詩/`：宮怨詩名單比對到語料者（{len(g['G1'])} 首）\n"
                f"- `G2_女詩人/`：女性詩人全部詩（{len(g['G2'])} 首）\n"
                "- `manifest.csv`：檔案 → 作者／題目／性別／字數 對照\n\n"
                "女性所作宮怨詩會同時出現在兩個資料夾。分群旗標見上層 "
                "`group_membership.csv`。\n")
    print(f"exported {len(rows)} files under poems/ (G1 {len(g['G1'])}, G2 {len(g['G2'])})")


if __name__ == "__main__":
    main()
