# -*- coding: utf-8 -*-
"""
Shared corpus loader for the palace-lament / female-poet diction study.

Parses the《全唐詩》volume text files into per-poem records, keeping the TITLE
as well as the author and text (the origin-predictor loader drops titles; here we
need them to match the palace-lament poem list). Reuses the same author-suffix
and per-line title-prefix cleaning conventions as
`../poet_origin_predictor/build_dataset.py`.

A record is a dict: {"author": str, "title": str, "text": str, "volume": str}.
"""
import os
import re
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOLUMES = os.path.join(HERE, "..", "quantangshi_crawler", "quantangshi_volumes")

ENTRY_SPLIT = re.compile(r"-{20,}")
AUTHOR_RE = re.compile(r"作者:\s*(.+)")
TITLE_RE = re.compile(r"^\s*\d+\.\s*(.+?)\s*$", re.M)   # "12. 標題"
AUTHOR_SUFFIX = re.compile(r"[著撰等作]+$")
CJK = re.compile(r"[一-鿿]")


def normalize_author(name):
    return AUTHOR_SUFFIX.sub("", name.strip()).strip()


# ---- title normalisation (for matching a curated poem list to the corpus) ----
# 樂府 category prefixes that appear before the real title as "類-題".
YUEFU_PREFIX = ["雜曲歌辭", "相和歌辭", "橫吹曲辭", "鼓吹曲辭", "舞曲歌辭",
                "琴曲歌辭", "雜歌謠辭", "近代曲辭", "郊廟歌辭", "清商曲辭",
                "燕射歌辭", "舞曲歌辭"]
# Variant characters seen between the list and the corpus.
_TITLE_VARIANTS = str.maketrans({"倢": "婕", "伃": "妤", "臺": "台", "牀": "床",
                                 "粧": "妝", "羣": "群", "峯": "峰"})
_CNUM = "一二三四五六七八九十百千兩"
_SPLIT_SUB = re.compile(r"[-－(（]")          # first-line / paren subtitle
_SUFFIX_QI = re.compile(r"其[%s]+$" % _CNUM)
_SUFFIX_CNT = re.compile(r"[%s]+首$" % _CNUM)


def title_norm(t):
    """Strip 樂府 prefix, first-line/paren subtitle, and unify variants."""
    t = (t or "").translate(_TITLE_VARIANTS).strip()
    for y in YUEFU_PREFIX:
        if t.startswith(y + "-") or t.startswith(y + "－"):
            t = t.split("-", 1)[-1].split("－", 1)[-1]
            break
    return _SPLIT_SUB.split(t, 1)[0].strip()


def title_core(t):
    """title_norm minus 其X / X首 / 上下 counters, for fuzzy prefix matching."""
    t = title_norm(t)
    t = _SUFFIX_QI.sub("", t)
    t = _SUFFIX_CNT.sub("", t)
    return t.rstrip("上下").strip()


def normalize_title(title):
    # Titles sometimes carry a repeated "標題：" prefix from the crawler.
    t = title.strip()
    if "：" in t:
        t = t.rsplit("：", 1)[-1]
    elif ":" in t:
        t = t.rsplit(":", 1)[-1]
    return t.strip()


def _clean_body(body):
    verses = []
    for line in body.splitlines():
        if "：" in line:
            line = line.rsplit("：", 1)[-1]
        elif ":" in line:
            line = line.rsplit(":", 1)[-1]
        verses.append(line)
    return "".join(CJK.findall("".join(verses)))


def parse_volume(path):
    """Yield poem records for one volume file."""
    vol = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    for block in ENTRY_SPLIT.split(raw):
        m = AUTHOR_RE.search(block)
        if not m:
            continue
        author = normalize_author(m.group(1))
        if not author or author == "佚名":
            continue
        tm = TITLE_RE.search(block)
        title = normalize_title(tm.group(1)) if tm else ""
        idx = block.find("內容:")
        if idx == -1:
            continue
        text = _clean_body(block[idx + len("內容:"):])
        if len(text) < 4:
            continue
        yield {"author": author, "title": title, "text": text, "volume": vol}


def load_records(volumes_dir=DEFAULT_VOLUMES):
    """All poem records across every volume."""
    records = []
    for path in sorted(glob.glob(os.path.join(volumes_dir, "*.txt"))):
        records.extend(parse_volume(path))
    return records


# ---- structured variant (keeps 句 boundaries for syntax analysis) --------
CLAUSE_SPLIT = re.compile(r"[，。！？、；.!?,;]+")


def parse_volume_structured(path):
    """Like parse_volume but also returns 'clauses': the poem split into 句
    (CJK-only clauses), preserving verse structure for line-length analysis."""
    vol = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    for block in ENTRY_SPLIT.split(raw):
        m = AUTHOR_RE.search(block)
        if not m:
            continue
        author = normalize_author(m.group(1))
        if not author or author == "佚名":
            continue
        tm = TITLE_RE.search(block)
        title = normalize_title(tm.group(1)) if tm else ""
        idx = block.find("內容:")
        if idx == -1:
            continue
        clauses, raw_lines = [], []
        for line in block[idx + len("內容:"):].splitlines():
            # drop the repeated 標題： prefix the crawler prepends to verse lines
            if "：" in line:
                line = line.rsplit("：", 1)[-1]
            elif ":" in line:
                line = line.rsplit(":", 1)[-1]
            line = line.strip()
            if line:
                raw_lines.append(line)          # original text: punctuation kept
            for piece in CLAUSE_SPLIT.split(line):
                cl = "".join(CJK.findall(piece))
                if cl:
                    clauses.append(cl)
        text = "".join(clauses)
        if len(text) < 4:
            continue
        yield {"author": author, "title": title, "text": text,
               "clauses": clauses, "raw": "\n".join(raw_lines), "volume": vol}


def load_records_structured(volumes_dir=DEFAULT_VOLUMES):
    records = []
    for path in sorted(glob.glob(os.path.join(volumes_dir, "*.txt"))):
        records.extend(parse_volume_structured(path))
    return records


if __name__ == "__main__":
    recs = load_records()
    by_author = collections.Counter(r["author"] for r in recs)
    print(f"parsed {len(recs)} poems by {len(by_author)} authors "
          f"from {DEFAULT_VOLUMES}")
    print("e.g.", recs[0]["author"], "/", recs[0]["title"], "/",
          recs[0]["text"][:20], "...")
