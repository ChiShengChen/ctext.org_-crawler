# -*- coding: utf-8 -*-
"""
Step 1 — Build the poet-level dataset for regional-origin prediction.

Reads the《全唐詩》volume text files and the CBDB-derived geo label table,
aggregates every poem under its author, attaches the author's 道 (Tang
administrative circuit) as the regional label, filters out poets with too
few surviving poems or no clear geographic attribution, and writes a single
poet-level table to dataset.csv.

Output columns: poet, region, n_poems, n_chars, text
"""
import os
import re
import csv
import glob
import argparse
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOLUMES = os.path.join(
    HERE, "..", "quantangshi_crawler", "quantangshi_volumes"
)
DEFAULT_GEO = os.path.join(
    HERE, "..", "quantangshi_crawler", "poet_geo_label.csv"
)

# Poem entries inside a volume look like:
#   12. 某某曲辭：標題
#      作者: 王維
#      內容:
#   <line>
#   <line>
#   ------------------------------
ENTRY_SPLIT = re.compile(r"-{20,}")
AUTHOR_RE = re.compile(r"作者:\s*(.+)")
# Trailing role markers attached to author names in the source (白居易著, 王維等).
AUTHOR_SUFFIX = re.compile(r"[著撰等作]+$")
CJK = re.compile(r"[一-鿿]")


def normalize_author(name):
    return AUTHOR_SUFFIX.sub("", name.strip()).strip()


def parse_volume(path):
    """Yield (author, poem_text) for every poem in one volume file."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    for block in ENTRY_SPLIT.split(raw):
        m = AUTHOR_RE.search(block)
        if not m:
            continue
        author = normalize_author(m.group(1))
        if not author or author == "佚名":
            continue
        # Content is everything after the "內容:" marker.
        idx = block.find("內容:")
        if idx == -1:
            continue
        body = block[idx + len("內容:"):]
        # Each verse line is often prefixed with a repeated "標題:" marker from
        # the crawler; keep only the part after the last colon on each line.
        verses = []
        for line in body.splitlines():
            if "：" in line:
                line = line.rsplit("：", 1)[-1]
            elif ":" in line:
                line = line.rsplit(":", 1)[-1]
            verses.append(line)
        text = "".join(CJK.findall("".join(verses)))
        if len(text) < 4:
            continue
        yield author, text


def load_poems(volumes_dir):
    """author -> list of poem strings, aggregated across all volumes."""
    poems = collections.defaultdict(list)
    files = sorted(glob.glob(os.path.join(volumes_dir, "*.txt")))
    for path in files:
        for author, text in parse_volume(path):
            poems[author].append(text)
    return poems


def load_regions(geo_path):
    """poet name -> 道 (circuit). Uses the first 道 found in the Geography cell."""
    regions = {}
    with open(geo_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 7:
                continue
            name_m = re.match(r"\s*\d+\.\s*(.+?):\s*\d+\s*首", row[0])
            if not name_m:
                continue
            name = name_m.group(1).strip()
            geo = row[6]
            dao_m = re.search(r"唐朝--([^-]+?道)", geo)
            if not dao_m:
                continue
            regions[name] = dao_m.group(1)
    return regions


def build(volumes_dir, geo_path, out_path, min_poems=5):
    poems = load_poems(volumes_dir)
    regions = load_regions(geo_path)
    print(f"Parsed poems for {len(poems)} authors across volumes.")
    print(f"Loaded regional labels for {len(regions)} poets.")

    rows = []
    matched = collections.Counter()
    for poet, region in regions.items():
        author_poems = poems.get(poet)
        if not author_poems or len(author_poems) < min_poems:
            continue
        text = "".join(author_poems)
        rows.append({
            "poet": poet,
            "region": region,
            "n_poems": len(author_poems),
            "n_chars": len(text),
            "text": text,
        })
        matched[region] += 1

    rows.sort(key=lambda r: r["n_poems"], reverse=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["poet", "region", "n_poems", "n_chars", "text"]
        )
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} poets (>= {min_poems} poems) to {out_path}")
    print("\nRegion distribution:")
    for region, n in matched.most_common():
        print(f"  {n:4d}  {region}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--volumes", default=DEFAULT_VOLUMES)
    ap.add_argument("--geo", default=DEFAULT_GEO)
    ap.add_argument("--out", default=os.path.join(HERE, "dataset.csv"))
    ap.add_argument("--min-poems", type=int, default=5)
    args = ap.parse_args()
    build(args.volumes, args.geo, args.out, args.min_poems)
