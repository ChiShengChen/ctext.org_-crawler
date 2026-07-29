# -*- coding: utf-8 -*-
"""
Diction contrast: palace-lament poems (宮怨詩, largely male ventriloquism) vs.
poems by female poets (女性詩人), plus female-authored self-voice split into
documentary palace verse (宮詞記事) and lyrical boudoir lament (閨怨抒情).

Data source (the curated list already carries a 性別 column):
  data/data_index/*.csv   columns 作者,性別,題目,...   -- the palace-lament list
  data/female_poets.txt   extra Tang female poets to broaden G2 (augmentation)

Groups:
  G1  宮怨詩            -- palace-lament poems matched to the corpus
  G1m 宮怨詩・代言       -- G1 rows whose 性別 == 男
  G2  女性詩人(全部)    -- ALL corpus poems by female poets
  G3  女性自述(宮/閨)   -- female self-voice palace/boudoir poems
        G3d 宮詞記事    -- documentary palace verse (宮詞 / 題…詩)
        G3l 閨怨抒情    -- lyrical boudoir/palace lament (閨怨/春怨/長門…)

Contrasts: G1 vs G2 (genre vs female authorship); G1m vs G3l (male ventriloquism
vs female self-voiced lament, same lament mode); G3d vs G3l (documentary vs
lyrical female self-voice). Distinctive terms via Monroe et al. (2008) weighted
log-odds with an informative Dirichlet prior (the whole《全唐詩》as background).

Usage:  python3 analyze_diction.py [--top 25]
"""
import os
import csv
import glob
import argparse
import collections
from math import log, sqrt

import corpus

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PALACE_DIR = os.path.join(DATA, "data_index")
FEMALE_AUG = os.path.join(DATA, "female_poets.txt")

LEXICAL_FIELDS = collections.OrderedDict([
    ("怨情 (lament)",       list("怨愁恨悲淚泣啼寂寞孤斷腸憂哀")),
    ("時序 (time/season)",  list("秋春夜月風霜寒曉暮昏更漏年")),
    ("宮殿空間 (palace space)", list("宮殿樓臺闕簾幕階砌苔井戶窗庭牆")),
    ("服飾器物 (adornment)",    list("羅綺紈扇鏡妝黛粉釵鈿衣裳金玉")),
    ("君恩 (favour)",       list("君恩寵幸顧承歡愛專新舊棄")),
])

# Female self-voice subgenre detection from the poem TITLE.
LYRIC_KW = ["閨怨", "閨情", "春怨", "秋怨", "宮怨", "長門", "長信", "昭陽",
            "團扇", "秋扇", "婕妤", "倢伃", "妾", "相思", "望夫", "搗衣",
            "怨歌", "恨", "別離", "離思"]
DOC_KW = ["宮詞", "宮中"]                  # palace-documentary title markers
DOC_LEAF = ("葉", "苑", "宮", "掖", "內")   # 題X: keep 紅葉題詩-type palace inscriptions only


def female_subgenre(title):
    """'lyric' (閨怨抒情) / 'doc' (宮詞記事) / None from a title.
    'doc' is deliberately narrow: 宮詞/宮中, or a 題… inscription that carries a
    palace marker (紅葉題詩 legends). Plain 題寺/題景 and 應制 banquet poems are
    NOT documentary and fall through to None (they leave G3)."""
    t = title or ""
    if any(k in t for k in LYRIC_KW):
        return "lyric"
    if any(k in t for k in DOC_KW):
        return "doc"
    if t.startswith("題") and any(k in t for k in DOC_LEAF):
        return "doc"
    return None


# ---- name-list loading --------------------------------------------------
def load_palace_rows(palace_dir):
    rows = []
    for f in sorted(glob.glob(os.path.join(palace_dir, "*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for rec in csv.reader(fh):
                if len(rec) < 3:
                    continue
                a = corpus.normalize_author(rec[0])
                g = rec[1].strip()
                t = corpus.normalize_title(rec[2])
                if not a or a == "作者" or not t:
                    continue
                rows.append((a, g, t))
    return rows


def load_augment(path):
    names = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    names.add(corpus.normalize_author(line))
    return names


# ---- title matching -----------------------------------------------------
def build_index(recs):
    by_author = collections.defaultdict(list)
    for r in recs:
        by_author[r["author"]].append(r)
    return by_author


def _key(r):
    return (r["volume"], r["author"], r["title"], r["text"][:12])


def match_rows(rows, by_author):
    seen, tiers, unmatched = {}, collections.Counter(), []
    for a, g, t in rows:
        pool = by_author.get(a)
        if not pool:
            tiers["author_missing"] += 1
            unmatched.append((a, g, t, "author_missing"))
            continue
        nt, ct = corpus.title_norm(t), corpus.title_core(t)
        hits = []
        for r in pool:
            rt = r["title"]
            if rt == t or corpus.title_norm(rt) == nt:
                hits.append(r)
            elif len(ct) >= 2:
                rc = corpus.title_core(rt)
                if rc and (rc == ct or rc.startswith(ct) or ct.startswith(rc)):
                    hits.append(r)
        if not hits:
            tiers["title_miss"] += 1
            unmatched.append((a, g, t, "title_miss"))
            continue
        tiers["matched"] += 1
        for r in hits:
            k = _key(r)
            if k not in seen:
                rr = dict(r); rr["gender"] = g
                seen[k] = rr
    return list(seen.values()), tiers, unmatched


def build_groups(recs=None):
    """Return a dict of all poem groups plus metadata. Reused by make_figures
    and analyze_syntax. Pass recs=corpus.load_records_structured() to carry the
    per-poem 'clauses' through to the groups."""
    rows = load_palace_rows(PALACE_DIR)
    aug = load_augment(FEMALE_AUG)
    if recs is None:
        recs = corpus.load_records()
    by_author = build_index(recs)

    G1, tiers, unmatched = match_rows(rows, by_author)
    G1m = [r for r in G1 if r["gender"] == "男"]

    female_from_list = sorted({a for a, g, t in rows if g == "女"})
    female_authors = set(female_from_list) | aug
    G2 = [r for r in recs if r["author"] in female_authors]

    # G3: female self-voice palace/boudoir poems, with a subgenre tag.
    g3 = {}
    for r in G1:                       # curated 女 palace-lament rows
        if r["gender"] == "女":
            sg = female_subgenre(r["title"]) or "lyric"   # curated 宮怨 -> lyric
            rr = dict(r); rr["subgenre"] = sg
            g3[_key(r)] = rr
    for r in G2:                       # keyword-expanded female poems
        sg = female_subgenre(r["title"])
        if sg and _key(r) not in g3:
            rr = dict(r); rr["subgenre"] = sg
            g3[_key(r)] = rr
    G3 = list(g3.values())
    G3d = [r for r in G3 if r["subgenre"] == "doc"]
    G3l = [r for r in G3 if r["subgenre"] == "lyric"]

    return dict(recs=recs, G1=G1, G1m=G1m, G2=G2, G3=G3, G3d=G3d, G3l=G3l,
                rows=rows, tiers=tiers, unmatched=unmatched,
                female_from_list=female_from_list, aug=aug)


# ---- Monroe weighted log-odds -------------------------------------------
def tokens(text):
    return list(text) + [text[i:i+2] for i in range(len(text) - 1)]


def counts(records):
    c = collections.Counter()
    for r in records:
        c.update(tokens(r["text"]))
    return c


def weighted_logodds(c1, c2, prior, top=25, min_count=5):
    n1, n2 = sum(c1.values()), sum(c2.values())
    a0 = sum(prior.values())
    out = []
    for w in (set(c1) | set(c2)):
        if c1[w] + c2[w] < min_count:
            continue
        aw = prior.get(w, 0) + 0.5
        l1 = log((c1[w] + aw) / (n1 + a0 - c1[w] - aw))
        l2 = log((c2[w] + aw) / (n2 + a0 - c2[w] - aw))
        z = (l1 - l2) / sqrt(1.0 / (c1[w] + aw) + 1.0 / (c2[w] + aw))
        out.append((w, z))
    out.sort(key=lambda x: x[1])
    return out[-top:][::-1], out[:top]     # (group1-distinctive, group2-distinctive)


def field_profile(records):
    joined = "".join(r["text"] for r in records)
    n = max(len(joined), 1)
    return {fld: sum(joined.count(ch) for ch in chars) / n * 1e4
            for fld, chars in LEXICAL_FIELDS.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    g = build_groups()
    if not g["rows"]:
        print(f"!! No list rows under {os.path.relpath(PALACE_DIR, HERE)}/")
        return
    G1, G1m, G2, G3, G3d, G3l = (g[k] for k in ("G1", "G1m", "G2", "G3", "G3d", "G3l"))

    na = lambda G: len(set(r["author"] for r in G))
    print(f"list rows: {len(g['rows'])}  |  match tiers: {dict(g['tiers'])}")
    print(f"G1 宮怨詩            : {len(G1)} poems, {na(G1)} authors")
    print(f"G1m 宮怨詩・代言(男) : {len(G1m)} poems")
    print(f"G2 女性詩人(全部)    : {len(G2)} poems, {na(G2)} authors "
          f"(名單女{len(g['female_from_list'])} + 補入{len(g['aug'] - set(g['female_from_list']))})")
    print(f"G3 女性自述(宮/閨)   : {len(G3)} poems, {na(G3)} authors "
          f"→ 宮詞記事 {len(G3d)} / 閨怨抒情 {len(G3l)}")

    background = counts(g["recs"])
    c1, c2, c1m, c3d, c3l = (counts(G) for G in (G1, G2, G1m, G3d, G3l))

    def show(title, ca, cb, na_, nb_):
        a_side, b_side = weighted_logodds(ca, cb, background, top=args.top)
        print(f"\n=== {title} ===")
        print(f"  ▶ {na_} 偏用: " + " ".join(f"{w}({z:+.1f})" for w, z in a_side))
        print(f"  ▶ {nb_} 偏用: " + " ".join(f"{w}({z:+.1f})" for w, z in b_side))
        return a_side, b_side

    con_genre = show("G1 宮怨詩 vs G2 女性詩人(全部)", c1, c2, "宮怨詩", "女性詩人")
    con_voice = show("G1m 男性代言 vs G3l 女性閨怨抒情", c1m, c3l, "男性代言", "女性閨怨") \
        if G3l and G1m else None
    con_sub = show("G3d 宮詞記事 vs G3l 閨怨抒情", c3d, c3l, "宮詞記事", "閨怨抒情") \
        if G3d and G3l else None

    print("\n=== 宮怨語彙場 (每萬字次數) ===")
    profs = collections.OrderedDict()
    profs["G1m 代言"] = field_profile(G1m)
    profs["G3l 閨怨"] = field_profile(G3l)
    profs["G3d 宮詞"] = field_profile(G3d)
    profs["G2 女詩人"] = field_profile(G2)
    print("  " + "field".ljust(24) + "".join(k.ljust(12) for k in profs))
    for fld in LEXICAL_FIELDS:
        print("  " + fld.ljust(24) + "".join(f"{profs[k][fld]:>7.1f}".ljust(12) for k in profs))

    _write_report(g, con_genre, con_voice, con_sub, profs, args.top)


def _write_report(g, con_genre, con_voice, con_sub, profs, top):
    G1, G1m, G2, G3, G3d, G3l = (g[k] for k in ("G1", "G1m", "G2", "G3", "G3d", "G3l"))
    na = lambda G: len(set(r["author"] for r in G))
    L = ["# 宮怨詩 vs 女性詩人 — 用語差異報告\n",
         "由 `analyze_diction.py` 產生。區辨詞:Monroe et al. (2008) 加權 log-odds "
         "(informative Dirichlet prior = 全唐詩全集),z 值愈大愈偏用該詞。\n",
         "## 組別\n",
         "| 組別 | 說明 | 詩數 | 作者數 |", "|---|---|--:|--:|",
         f"| G1 | 宮怨詩(名單，已比對語料) | {len(G1)} | {na(G1)} |",
         f"| G1m | 宮怨詩・男性代言 | {len(G1m)} | {na(G1m)} |",
         f"| G2 | 女性詩人全部詩 | {len(G2)} | {na(G2)} |",
         f"| G3 | 女性自述(宮/閨) | {len(G3)} | {na(G3)} |",
         f"| G3d | ├ 宮詞記事 | {len(G3d)} | {na(G3d)} |",
         f"| G3l | └ 閨怨抒情 | {len(G3l)} | {na(G3l)} |",
         f"\n名單比對:{dict(g['tiers'])}(未中 {len(g['unmatched'])} 筆，見 `unmatched_list.csv`)。",
         f"G2 女性作者 = 名單女性 {len(g['female_from_list'])} 位 + 補入 "
         f"{len(g['aug'] - set(g['female_from_list']))} 位。\n"]
    ag, bg = con_genre
    L += ["## 對照一:宮怨詩 vs 女性詩人(全部)\n",
          "**宮怨詩偏用**:" + " ".join(f"`{w}`" for w, _ in ag),
          "\n**女性詩人偏用**:" + " ".join(f"`{w}`" for w, _ in bg)]
    if con_voice:
        av, bv = con_voice
        L += ["\n## 對照二:男性代言 vs 女性閨怨抒情(同哀怨體)\n",
              "**男性代言偏用**:" + " ".join(f"`{w}`" for w, _ in av),
              "\n**女性閨怨偏用**:" + " ".join(f"`{w}`" for w, _ in bv)]
    if con_sub:
        ad, al = con_sub
        L += ["\n## 對照三:女性自述 — 宮詞記事 vs 閨怨抒情\n",
              "**宮詞記事偏用**:" + " ".join(f"`{w}`" for w, _ in ad),
              "\n**閨怨抒情偏用**:" + " ".join(f"`{w}`" for w, _ in al)]
    L += ["\n## 宮怨語彙場(每萬字次數)\n",
          "| 語彙場 | " + " | ".join(profs) + " |",
          "|" + "---|" * (len(profs) + 1)]
    for fld in LEXICAL_FIELDS:
        L.append(f"| {fld} | " + " | ".join(f"{profs[k][fld]:.1f}" for k in profs) + " |")
    with open(os.path.join(HERE, "diction_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(HERE, "unmatched_list.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["author", "gender", "title", "reason"])
        w.writerows(g["unmatched"])
    print("\nSaved report -> diction_report.md ; unmatched -> unmatched_list.csv")


if __name__ == "__main__":
    main()
