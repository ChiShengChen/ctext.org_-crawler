# -*- coding: utf-8 -*-
"""
Build a Tang prefecture -> (lon, lat) table for the poets in dataset.csv,
using the CHGIS/TGAZ gazetteer API (Harvard & Fudan), then run the
prefecture-level Mantel test (linguistic vs geographic distance).

Prefecture names come from ../quantangshi_crawler/poet_geo_label.csv
(field 6: 唐朝--道--州--縣(pinyin)). For each unique prefecture we query
  https://chgis.hudci.org/tgaz/placename?fmt=json&n=<name>
and keep the POINT whose attested year-span overlaps the Tang (618-907)
the longest, preferring 州/府/郡 feature types.

Outputs tang_prefecture_coords.csv and prints the Mantel result.
"""
import csv
import json
import re
import time
import urllib.parse
import urllib.request
import os

import numpy as np

import make_figures as m
from train import build_features

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, "..", "quantangshi_crawler", "poet_geo_label.csv")
OUT = os.path.join(HERE, "tang_prefecture_coords.csv")
TANG = (618, 907)
ALIAS = {"和縣": "和州", "關輔": "京兆", "河南": "河南府",
         "京兆": "京兆府", "太原": "太原府", "成都": "成都府",
         "恆州": "恒州"}
# Manual fixes: TGAZ rows with corrupt lon=0, or homonymous prefectures
# where the longest-overlap match lands in the wrong region (checked against
# standard historical geography; modern seats in parentheses).
OVERRIDE = {
    "江州": (115.99, 29.71),   # 九江
    "泉州": (118.68, 24.91),
    "澧州": (111.76, 29.63),   # 澧縣
    "越州": (120.58, 30.00),   # 紹興
    "蒲州": (110.33, 34.84),   # 永濟（河中）
    "齊州": (117.02, 36.67),   # 濟南
    "涿州": (115.97, 39.49),
    "婺州": (119.65, 29.08),   # 金華
    "恆州": (114.57, 38.15),   # 正定
}
# China bounding box sanity check for gazetteer points.
BBOX = (73.0, 136.0, 17.0, 54.0)


def norm(p):
    p = re.sub(r"[（(].*?[)）]", "", p)
    p = re.split(r"[,，、;；]", p)[0].strip()
    return p


def poet_prefectures():
    df = m.load_df()
    poets = set(df["poet"])
    out = {}
    with open(GEO, encoding="utf-8") as f:
        r = csv.reader(f); next(r)
        for row in r:
            mm = re.match(r"\s*\d+\.\s*(.+?):\s*\d+\s*首", row[0])
            if not mm or len(row) < 7:
                continue
            name = mm.group(1).strip()
            if name not in poets:
                continue
            parts = row[6].split("/")[0].split("--")
            if len(parts) >= 3:
                out[name] = norm(parts[2])
    return out


def tgaz(name):
    url = ("https://chgis.hudci.org/tgaz/placename?fmt=json&n="
           + urllib.parse.quote(name))
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def tang_overlap(years):
    mm = re.match(r"\s*(-?\d+)\s*~\s*(-?\d+)", years or "")
    if not mm:
        return 0
    a, b = int(mm.group(1)), int(mm.group(2))
    return max(0, min(b, TANG[1]) - max(a, TANG[0]))


def resolve(name):
    """Return (lon, lat, matched_name, years) or None."""
    tried = [name]
    if name in ALIAS:
        tried.append(ALIAS[name])
    tried += [name + "府", name + "郡"]
    for q in tried:
        try:
            data = tgaz(q)
        except Exception:
            time.sleep(1)
            continue
        best, best_ov = None, 0
        for pl in data.get("placenames", []):
            ft = pl.get("feature type", "")
            if not any(t in ft for t in ("州", "府", "郡")):
                continue
            ov = tang_overlap(pl.get("years", ""))
            if ov <= 0:
                continue
            xy = pl.get("xy coordinates", "")
            try:
                lon, lat = [float(v) for v in xy.split(",")[:2]]
            except Exception:
                continue
            if not (BBOX[0] <= lon <= BBOX[1] and BBOX[2] <= lat <= BBOX[3]):
                continue
            if ov > best_ov:
                best, best_ov = (lon, lat, pl.get("name", q),
                                 pl.get("years", "")), ov
        if best:
            return best
        time.sleep(0.2)
    return None


def main():
    pp = poet_prefectures()
    prefs = sorted(set(pp.values()))
    print(f"{len(pp)} poets with prefecture; {len(prefs)} unique prefectures")
    coords, misses = {}, []
    for i, p in enumerate(prefs):
        if p in OVERRIDE:
            lon, lat = OVERRIDE[p]
            coords[p] = (lon, lat, p, "manual")
            print(f"  [{i+1}/{len(prefs)}] {p}: {lon:.2f},{lat:.2f} (manual)")
            continue
        res = resolve(p)
        if res:
            coords[p] = res
            print(f"  [{i+1}/{len(prefs)}] {p}: {res[0]:.2f},{res[1]:.2f} "
                  f"({res[2]} {res[3]})")
        else:
            misses.append(p)
            print(f"  [{i+1}/{len(prefs)}] {p}: MISS")
        time.sleep(0.25)
    print("misses:", misses)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["prefecture", "lon", "lat", "matched", "years"])
        for p, (lon, lat, mn, yr) in sorted(coords.items()):
            wtr.writerow([p, lon, lat, mn, yr])
    print(f"wrote {OUT} ({len(coords)} prefectures)")

    # ---- prefecture-level Mantel --------------------------------------
    df = m.load_df()
    df = df[df["poet"].map(lambda q: pp.get(q) in coords)].reset_index(drop=True)
    df["pref"] = df["poet"].map(pp)
    for min_poets in (2, 3):
        vc = df["pref"].value_counts()
        keep = vc[vc >= min_poets].index
        sub = df[df["pref"].isin(keep)].reset_index(drop=True)
        units = sorted(sub["pref"].unique())
        X, _, _ = build_features(sub["text"].tolist())
        Xd = np.asarray(X.todense())
        cents = np.vstack([Xd[(sub["pref"] == u).to_numpy()].mean(0)
                           for u in units])
        cents /= (np.linalg.norm(cents, axis=1, keepdims=True) + 1e-12)
        ling = 1 - cents @ cents.T
        geo = np.array([[m.haversine(coords[a][:2], coords[b][:2])
                         for b in units] for a in units])
        r, p_mantel = m.mantel_p(geo, ling)
        print(f"\nPrefecture-level Mantel (>= {min_poets} poets/prefecture): "
              f"{len(units)} prefectures, {len(sub)} poets, "
              f"{len(units)*(len(units)-1)//2} pairs")
        print(f"  r = {r:.3f}, Mantel p = {p_mantel:.4f}")
        print(f"  (circuit-level baseline: r = 0.40, Mantel p ≈ 0.09)")


if __name__ == "__main__":
    main()
