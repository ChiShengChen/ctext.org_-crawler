# -*- coding: utf-8 -*-
"""
Analysis #6 — Reading the model's MISTAKES as literary history.

A poet whose verse the classifier confidently assigns to the "wrong" region is
not just an error: often the poem reflects where the poet actually lived, served,
or was exiled to, rather than the ancestral seat recorded as their origin. This
script surfaces those cases and checks them against biography.

For the south/north task we take out-of-fold predictions with probabilities,
rank the confident misclassifications, and for each poet parse EVERY location in
the CBDB geography cell (many list an ancestral seat 郡望 plus an actual residence).
We then test a concrete hypothesis:

  When the model is "wrong", does its prediction match a SECONDARY location of
  the poet (where they really lived) rather than the labelled birthplace?

If so, the model is tracking lived geography, and the "error" is biographically
meaningful — a human-in-the-loop hypothesis generator, exactly the paper's theme.

Usage:  python3 analysis_misclassification.py [--top 20]
"""
import os
import re
import csv
import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict

import build_dataset as bd
from train import SOUTH, NORTH, build_features

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))


def side(dao):
    return "南" if dao in SOUTH else ("北" if dao in NORTH else None)


def load_bio():
    """poet -> dict(years, career, official_era, locations=[(dao, place), ...])."""
    bio = {}
    with open(bd.DEFAULT_GEO, encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            m = re.match(r"\s*\d+\.\s*(.+?):\s*\d+\s*首", row[0])
            if not m or len(row) < 7:
                continue
            name = m.group(1).strip()
            geo = row[6]
            # Split the cell into location segments and parse each.
            locs = []
            for seg in re.split(r"[/,，、]", geo):
                dm = re.search(r"唐朝--([^-]+?道)--.*?--?([^\-/,，、()]+)", seg)
                if not dm:
                    dm = re.search(r"唐朝--([^-]+?道)", seg)
                    if not dm:
                        continue
                    locs.append((dm.group(1), ""))
                else:
                    locs.append((dm.group(1), dm.group(2).strip()))
            # dedupe preserving order
            seen, uniq = set(), []
            for d, p in locs:
                if (d, p) not in seen:
                    seen.add((d, p)); uniq.append((d, p))
            bio[name] = {
                "years": (row[3] or "").strip(),
                "career": (row[7] if len(row) > 7 else "").strip(),
                "official_era": (row[8] if len(row) > 8 else "").strip(),
                "locations": uniq,
            }
    return bio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--min-poems", type=int, default=10)
    args = ap.parse_args()

    df = pd.read_csv(os.path.join(HERE, "dataset.csv"))
    df = df[df["n_poems"] >= args.min_poems].copy()
    df["label"] = df["region"].map(
        lambda r: "南" if r in SOUTH else ("北" if r in NORTH else None))
    df = df.dropna(subset=["label"]).reset_index(drop=True)

    le = LabelEncoder(); y = le.fit_transform(df["label"])
    X, _, _ = build_features(df["text"].tolist())
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    proba = cross_val_predict(clf, X, y, cv=skf, method="predict_proba")
    pred_idx = proba.argmax(1)
    df["pred"] = le.inverse_transform(pred_idx)
    df["conf"] = proba.max(1)
    df["wrong"] = df["pred"] != df["label"]

    bio = load_bio()

    # Hypothesis test: among confident errors, how often does the prediction
    # match a SECONDARY location (lived elsewhere)?
    wrong = df[df["wrong"]].copy()
    explained = 0
    for _, row in wrong.iterrows():
        b = bio.get(row["poet"], {})
        alt_sides = {side(d) for d, _ in b.get("locations", [])[1:]}
        if row["pred"] in alt_sides:
            explained += 1
    n_multi = sum(1 for _, row in wrong.iterrows()
                  if len({side(d) for d, _ in bio.get(row["poet"], {}).get("locations", [])}) > 1)

    acc = (~df["wrong"]).mean()
    print(f"Poets: {len(df)} | south/north CV accuracy {acc:.3f} | "
          f"misclassified {len(wrong)}")
    print(f"\nOf {len(wrong)} errors, {n_multi} have >1 distinct region on record; "
          f"{explained} have the PREDICTED side among their secondary locations.")
    print("  -> these 'errors' align with where the poet also lived/served, "
          "not their labelled origin.\n")

    # Error direction by era: are southern poets mis-read as northern mainly in
    # the early/high Tang, when the court (northern) idiom dominated?
    def era_of(yrs):
        m = re.search(r"(\d{3,4})\s*-\s*(\d{3,4})", yrs or "")
        if not m:
            return None
        mid = (int(m.group(1)) + int(m.group(2))) // 2
        for nm, lo, hi in [("初唐", 0, 712), ("盛唐", 713, 765),
                           ("中唐", 766, 835), ("晚唐", 836, 907)]:
            if lo <= mid <= hi:
                return nm
        return None
    print("=== Error direction by era ===")
    rows = []
    for _, row in wrong.iterrows():
        e = era_of(bio.get(row["poet"], {}).get("years", ""))
        if e:
            rows.append((e, f"{row['label']}→{row['pred']}"))
    if rows:
        ed = pd.DataFrame(rows, columns=["era", "dir"])
        tab = pd.crosstab(ed["era"], ed["dir"]).reindex(
            ["初唐", "盛唐", "中唐", "晚唐"]).dropna(how="all")
        print(tab.to_string())
        print("  (南→北 = southern poet read as northern, i.e. court-idiom pull)\n")

    print(f"=== Top {args.top} most confident misclassifications ===")
    head = wrong.sort_values("conf", ascending=False).head(args.top)
    for _, row in head.iterrows():
        b = bio.get(row["poet"], {})
        locs = "; ".join(f"{d}{('·'+p) if p else ''}[{side(d)}]"
                         for d, p in b.get("locations", []))
        flag = "  <= 預測命中其它居地" if row["pred"] in {
            side(d) for d, _ in b.get("locations", [])[1:]} else ""
        print(f"\n• {row['poet']}  標記={row['label']} 預測={row['pred']} "
              f"(conf {row['conf']:.2f}){flag}")
        print(f"    生卒 {b.get('years','?')} | 任官 {b.get('official_era','')}".rstrip())
        print(f"    地理: {locs}")
        career = b.get("career", "")
        if career:
            print(f"    背景: {career[:70]}")

    # Save full error table for closer reading.
    out = os.path.join(HERE, "misclassified_poets.csv")
    cols = ["poet", "label", "pred", "conf", "n_poems"]
    save = wrong.sort_values("conf", ascending=False)[cols].copy()
    save["years"] = save["poet"].map(lambda p: bio.get(p, {}).get("years", ""))
    save["locations"] = save["poet"].map(
        lambda p: " | ".join(f"{d}{('·'+pl) if pl else ''}"
                             for d, pl in bio.get(p, {}).get("locations", [])))
    save.to_csv(out, index=False)
    print(f"\nSaved full error table -> {out}")


if __name__ == "__main__":
    main()
