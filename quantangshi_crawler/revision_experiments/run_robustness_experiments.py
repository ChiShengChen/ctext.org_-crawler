#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run robustness experiments promised in the revision:
- Fixed-length resampling TTR (unigram & bigram)
- HD-D lexical diversity (unigram & bigram) from frequency counts
- MTLD (order-sensitive) approximated by averaging random shuffles of the multiset
- Neutral control set calibration for the rank-based gender preference score
- Sub-corpus consistency checks (time period / region / background class)

Outputs CSV tables and (small) PNG figures under:
  quantangshi_crawler/revision_experiments/output/
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler"
POET_META_PATH = os.path.join(BASE_DIR, "poet_geo_label.csv")
NGRAM_DIR = os.path.join(BASE_DIR, "analysis_result/analysis_results_no_title/author_ngram_csvs")
GRAM_PATHS = {
    "1gram": os.path.join(NGRAM_DIR, "merged_1gram_詞頻統計.csv"),
    "2gram": os.path.join(NGRAM_DIR, "merged_2gram_詞頻統計.csv"),
}

OUT_DIR = os.path.join(BASE_DIR, "revision_experiments", "output")
os.makedirs(OUT_DIR, exist_ok=True)


def _clean_gender(raw: str) -> str:
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return "Unknown"
    s = str(raw).strip().lower()
    if "female" in s:
        return "Female"
    if "male" in s and "female" not in s:
        return "Male"
    return "Unknown"


def _extract_birth_year(birth_death: str) -> Optional[int]:
    """
    birth-death examples: "772-846", "699-761", "?-881", "726?-790?"
    """
    if birth_death is None or (isinstance(birth_death, float) and np.isnan(birth_death)):
        return None
    s = str(birth_death)
    m = re.search(r"(\d{3,4})\s*[-–]\s*(\d{3,4}|\?)", s)
    if not m:
        m = re.search(r"(\d{3,4})", s)
        if not m:
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _period_from_birth_year(y: Optional[int]) -> str:
    # Coarse buckets (commonly used in Tang studies)
    if y is None:
        return "Unknown"
    if y <= 712:
        return "Early Tang"
    if y <= 765:
        return "High Tang"
    if y <= 835:
        return "Mid Tang"
    if y <= 907:
        return "Late Tang"
    return "Post-Tang/Unknown"


def _extract_region(geo: str) -> str:
    """
    Geography examples:
    "唐朝--河東道--太原--太谷(Taigu)/唐朝--關內道--華州--下邽(Xiagui)"
    Returns the first '道' segment if available.
    """
    if geo is None or (isinstance(geo, float) and np.isnan(geo)):
        return "Unknown"
    s = str(geo).strip()
    if not s:
        return "Unknown"
    first = s.split("/")[0]
    parts = [p.strip() for p in first.split("--") if p.strip()]
    if len(parts) >= 2:
        return parts[1]
    return "Unknown"


def _coarse_class(background: str) -> str:
    """
    Very coarse mapping from 背景 to a few categories.
    """
    if background is None or (isinstance(background, float) and np.isnan(background)):
        return "Unknown"
    s = str(background).lower()
    if "僧" in s or "monk" in s or "buddhist" in s:
        return "Monk"
    if "道士" in s or "daoist" in s:
        return "Daoist"
    if "office" in s or "為官" in s or "宰相" in s or "官" in s:
        return "Official"
    if "recluse" in s or "隱士" in s:
        return "Recluse"
    if "poet" in s or "詩人" in s:
        return "Poet/Man of letters"
    return "Other/Unknown"


def load_poet_metadata() -> pd.DataFrame:
    df = pd.read_csv(POET_META_PATH)

    # Normalize poet name: remove leading numbering and trailing poem counts.
    def extract_poet_name(name_str: str) -> str:
        m = re.search(r"(\d+\.\s*)?([^:：]+)", str(name_str))
        return (m.group(2) if m else str(name_str)).strip()

    df["poet_name"] = df["詩人"].apply(extract_poet_name)
    df["gender"] = df["性別"].apply(_clean_gender)
    df["birth_year"] = df["birth-death"].apply(_extract_birth_year)
    df["period"] = df["birth_year"].apply(_period_from_birth_year)
    df["region"] = df["Geography"].apply(_extract_region)
    df["class_coarse"] = df["背景"].apply(_coarse_class)

    return df[["poet_name", "gender", "birth_year", "period", "region", "class_coarse"]]


def iter_ngram_chunks(path: str, usecols: List[str], chunksize: int = 200_000) -> Iterable[pd.DataFrame]:
    for chunk in pd.read_csv(path, usecols=usecols, chunksize=chunksize):
        yield chunk


@dataclass(frozen=True)
class GroupKey:
    gender: str
    period: str = "ALL"
    region: str = "ALL"
    class_coarse: str = "ALL"


def aggregate_counts(
    gram: str,
    meta: pd.DataFrame,
    group_by: Tuple[str, ...],
    min_gender: Optional[str] = None,
) -> Dict[Tuple, pd.Series]:
    """
    Aggregate frequency counts into a dict:
      group_key_tuple -> Series(word -> count)

    group_by can include: "gender", "period", "region", "class_coarse"
    """
    assert gram in GRAM_PATHS
    path = GRAM_PATHS[gram]
    usecols = ["字詞", "詩人", "詞頻"]

    poet_to_meta = meta.set_index("poet_name")[["gender", "period", "region", "class_coarse"]]

    agg: Dict[Tuple, Dict[str, int]] = {}

    chunk_i = 0
    for chunk in iter_ngram_chunks(path, usecols=usecols):
        chunk_i += 1
        if chunk_i % 10 == 0:
            print(f"  - {gram} read {chunk_i} chunks...", flush=True)
        chunk = chunk.rename(columns={"詩人": "poet_name"})
        chunk = chunk.merge(poet_to_meta, left_on="poet_name", right_index=True, how="left")
        chunk["gender"] = chunk["gender"].fillna("Unknown")
        chunk["period"] = chunk["period"].fillna("Unknown")
        chunk["region"] = chunk["region"].fillna("Unknown")
        chunk["class_coarse"] = chunk["class_coarse"].fillna("Unknown")

        if min_gender is not None:
            chunk = chunk[chunk["gender"] == min_gender]
        if chunk.empty:
            continue

        # Build grouping
        gb_cols = list(group_by) + ["字詞"]
        grouped = chunk.groupby(gb_cols, as_index=False)["詞頻"].sum()

        for _, row in grouped.iterrows():
            key = tuple(row[c] for c in group_by)
            word = row["字詞"]
            count = int(row["詞頻"])
            if key not in agg:
                agg[key] = {}
            agg[key][word] = agg[key].get(word, 0) + count

    # Convert to Series
    out: Dict[Tuple, pd.Series] = {}
    for k, d in agg.items():
        s = pd.Series(d, dtype="int64")
        s = s.sort_values(ascending=False)
        out[k] = s
    return out


def ttr_from_counts(counts: pd.Series) -> float:
    total = int(counts.sum())
    if total <= 0:
        return float("nan")
    return float(counts.shape[0] / total)


def resample_ttr(
    counts: pd.Series,
    L: int,
    K: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Multinomial resampling of tokens from type-frequency distribution.
    Returns K TTR values for samples of length L.
    """
    if counts.empty:
        return np.array([], dtype=float)
    probs = counts.values.astype(float)
    probs = probs / probs.sum()

    # Draw K samples: multinomial(K x V) could be huge; do loop but vectorize unique count.
    ttrs = np.empty(K, dtype=float)
    V = len(probs)

    for i in range(K):
        draw = rng.multinomial(L, probs)
        uniq = int((draw > 0).sum())
        ttrs[i] = uniq / float(L)
    return ttrs


def hdd_from_counts(counts: pd.Series, sample_size: int = 42) -> float:
    """
    HD-D (Hypergeometric Distribution Diversity) for token multiset.
    Based on McCarthy & Jarvis (2010): sum over types of P(type occurs >=1 in sample).

    For each type with frequency f in population of size N:
      P(type absent) = C(N-f, n)/C(N, n)
      P(present) = 1 - P(absent)
    HD-D = sum P(present) / n
    """
    N = int(counts.sum())
    n = int(sample_size)
    if N <= 0 or n <= 0:
        return float("nan")
    if N < n:
        n = N
    # Use log-gamma for combinations to stay stable.
    from math import lgamma, exp

    def logC(a: int, b: int) -> float:
        if b < 0 or b > a:
            return float("-inf")
        return lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)

    log_den = logC(N, n)
    probs_present = 0.0
    for f in counts.values.astype(int):
        if f <= 0:
            continue
        if N - f < n:
            # must appear
            probs_present += 1.0
            continue
        log_abs = logC(N - f, n) - log_den
        p_abs = exp(log_abs)
        probs_present += (1.0 - p_abs)
    return probs_present / float(n)


def mtld_approx_from_counts(
    counts: pd.Series,
    rng: np.random.Generator,
    text_len: int = 10_000,
    replications: int = 30,
    ttr_threshold: float = 0.72,
) -> float:
    """
    MTLD needs token order. We approximate by:
    - sampling a token sequence of length text_len from the distribution
    - randomly shuffling (via permutation of sampled indices)
    - computing MTLD forward
    - averaging across replications
    """
    if counts.empty:
        return float("nan")
    # Build token ids distribution
    probs = counts.values.astype(float)
    probs = probs / probs.sum()
    V = len(probs)
    L = int(text_len)
    if L <= 0:
        return float("nan")

    # Pre-sample indices once per replication (already random order)
    mtlds: List[float] = []
    for _ in range(replications):
        idx = rng.choice(V, size=L, replace=True, p=probs)
        # Compute MTLD forward
        factor_count = 0.0
        token_count = 0
        types = set()
        for i in idx:
            token_count += 1
            types.add(int(i))
            ttr = len(types) / token_count
            if ttr <= ttr_threshold:
                factor_count += 1.0
                token_count = 0
                types = set()
        if token_count > 0:
            # partial factor
            ttr = len(types) / token_count
            if ttr == 1.0:
                partial = 0.0
            else:
                partial = (1.0 - ttr) / (1.0 - ttr_threshold)
            factor_count += partial
        if factor_count == 0:
            mtlds.append(float("nan"))
        else:
            mtlds.append(L / factor_count)
    return float(np.nanmean(mtlds))


def rank_based_scores(counts: pd.Series, max_rank: int = 500) -> pd.Series:
    """
    Rank -> 0..100 score. Rank starts at 1.
    """
    top = counts.sort_values(ascending=False).head(max_rank)
    ranks = pd.Series(np.arange(1, len(top) + 1), index=top.index, dtype=float)
    score = (max_rank - ranks) / max_rank * 100.0
    return score


def preference_score_from_counts(male_counts: pd.Series, female_counts: pd.Series, max_rank: int = 500) -> pd.DataFrame:
    male_score = rank_based_scores(male_counts, max_rank=max_rank)
    female_score = rank_based_scores(female_counts, max_rank=max_rank)

    vocab = male_score.index.union(female_score.index)
    df = pd.DataFrame(index=vocab)
    df["score_male"] = male_score.reindex(vocab).fillna(0.0)
    df["score_female"] = female_score.reindex(vocab).fillna(0.0)

    # Exclusives within top lists (as per original definition)
    male_only = df["score_male"].gt(0) & df["score_female"].eq(0)
    female_only = df["score_female"].gt(0) & df["score_male"].eq(0)
    df.loc[male_only, ["score_male"]] = 100.0
    df.loc[female_only, ["score_female"]] = 100.0

    df["preference"] = df["score_male"] - df["score_female"]
    return df.sort_values("preference", ascending=False)


def build_neutral_control(
    male_counts: pd.Series,
    female_counts: pd.Series,
    min_total: int = 200,
    ratio_band: float = 0.10,
) -> pd.Index:
    """
    Tokens with near-balanced relative frequencies across genders.
    ratio_band=0.10 means within [0.9,1.1] after normalization by total tokens.
    """
    vocab = male_counts.index.union(female_counts.index)
    m = male_counts.reindex(vocab).fillna(0).astype(float)
    f = female_counts.reindex(vocab).fillna(0).astype(float)
    mN = m.sum()
    fN = f.sum()
    if mN == 0 or fN == 0:
        return pd.Index([])
    pm = m / mN
    pf = f / fN
    total = m + f
    ok_total = total >= float(min_total)
    ratio = pm / (pf + 1e-18)
    ok_ratio = (ratio >= (1.0 - ratio_band)) & (ratio <= (1.0 + ratio_band))
    return vocab[ok_total & ok_ratio]


def main():
    rng = np.random.default_rng(20260317)
    meta = load_poet_metadata()

    # ========== 1) Aggregate counts by gender for unigram & bigram ==========
    print("Aggregating counts by gender (this may take a while)...", flush=True)
    uni_by_gender = aggregate_counts("1gram", meta, group_by=("gender",))
    bi_by_gender = aggregate_counts("2gram", meta, group_by=("gender",))

    male_uni = uni_by_gender.get(("Male",), pd.Series(dtype="int64"))
    female_uni = uni_by_gender.get(("Female",), pd.Series(dtype="int64"))
    male_bi = bi_by_gender.get(("Male",), pd.Series(dtype="int64"))
    female_bi = bi_by_gender.get(("Female",), pd.Series(dtype="int64"))

    # ========== 2) Resampling TTR tables ==========
    def run_resampling_table(counts_m: pd.Series, counts_f: pd.Series, gram_label: str) -> pd.DataFrame:
        rows = []
        for L in [500, 1000, 2000, 5000]:
            K = 500  # runtime-friendly but still stable
            for gender, counts in [("Men", counts_m), ("Women", counts_f)]:
                ttrs = resample_ttr(counts, L=L, K=K, rng=rng)
                rows.append(
                    {
                        "gram": gram_label,
                        "L": L,
                        "K": K,
                        "gender": gender,
                        "ttr_mean": float(np.mean(ttrs)),
                        "ttr_p2_5": float(np.quantile(ttrs, 0.025)),
                        "ttr_p97_5": float(np.quantile(ttrs, 0.975)),
                    }
                )
        return pd.DataFrame(rows)

    uni_resample = run_resampling_table(male_uni, female_uni, "unigram")
    bi_resample = run_resampling_table(male_bi, female_bi, "bigram")
    resample_df = pd.concat([uni_resample, bi_resample], ignore_index=True)
    resample_path = os.path.join(OUT_DIR, "resampling_ttr_summary.csv")
    resample_df.to_csv(resample_path, index=False)
    print("Wrote", resample_path, flush=True)

    # ========== 3) HD-D and MTLD (approx) ==========
    diversity_rows = []
    for gram_label, m_counts, f_counts in [
        ("unigram", male_uni, female_uni),
        ("bigram", male_bi, female_bi),
    ]:
        for gender, counts in [("Men", m_counts), ("Women", f_counts)]:
            diversity_rows.append(
                {
                    "gram": gram_label,
                    "gender": gender,
                    "total_tokens": int(counts.sum()),
                    "unique_types": int(counts.shape[0]),
                    "ttr_raw": float(ttr_from_counts(counts)),
                    "hdd_42": float(hdd_from_counts(counts, sample_size=42)),
                    "mtld_approx": float(mtld_approx_from_counts(counts, rng=rng, text_len=10000, replications=20)),
                }
            )
    diversity_df = pd.DataFrame(diversity_rows)
    diversity_path = os.path.join(OUT_DIR, "lexical_diversity_summary.csv")
    diversity_df.to_csv(diversity_path, index=False)
    print("Wrote", diversity_path, flush=True)

    # ========== 4) Neutral control calibration ==========
    # Unigram
    uni_pref = preference_score_from_counts(male_uni, female_uni, max_rank=500)
    uni_neutral = build_neutral_control(male_uni, female_uni, min_total=200, ratio_band=0.10)
    uni_neutral_scores = uni_pref.loc[uni_pref.index.intersection(uni_neutral), "preference"]
    # Bigram
    bi_pref = preference_score_from_counts(male_bi, female_bi, max_rank=500)
    # Bigrams are sparser; use a lower frequency threshold for the neutral set.
    bi_neutral = build_neutral_control(male_bi, female_bi, min_total=10, ratio_band=0.10)
    bi_neutral_scores = bi_pref.loc[bi_pref.index.intersection(bi_neutral), "preference"]

    calib_rows = []
    for gram_label, s in [("unigram", uni_neutral_scores), ("bigram", bi_neutral_scores)]:
        if s.empty:
            continue
        calib_rows.append(
            {
                "gram": gram_label,
                "neutral_n": int(s.shape[0]),
                "abs_pref_p95": float(np.quantile(np.abs(s.values), 0.95)),
                "abs_pref_p99": float(np.quantile(np.abs(s.values), 0.99)),
                "abs_pref_median": float(np.median(np.abs(s.values))),
            }
        )
    calib_df = pd.DataFrame(calib_rows)
    calib_path = os.path.join(OUT_DIR, "neutral_control_calibration.csv")
    calib_df.to_csv(calib_path, index=False)
    print("Wrote", calib_path, flush=True)

    # ========== 5) Sub-corpus consistency checks ==========
    # We implement (time period) + (region) + (class_coarse), each with gender split.
    consistency_rows = []

    def consistency_for_dimension(gram: str, dim: str, topN: int = 200):
        # Aggregate once per (gram, dim) instead of repeatedly.
        grouped = aggregate_counts(gram, meta, group_by=(dim, "gender"))

        # collect per subcorpus preference lists
        sub_pref: Dict[str, pd.Series] = {}
        for dv in sorted({k[0] for k in grouped.keys()}):
            m = grouped.get((dv, "Male"), pd.Series(dtype="int64"))
            f = grouped.get((dv, "Female"), pd.Series(dtype="int64"))
            if m.sum() == 0 or f.sum() == 0:
                continue
            sub_pref[dv] = preference_score_from_counts(m, f, max_rank=500)["preference"]
        if not sub_pref:
            return

        # Use precomputed global preference (by gender) for candidate selection.
        if gram == "1gram":
            global_pref = uni_pref["preference"]
        elif gram == "2gram":
            global_pref = bi_pref["preference"]
        else:
            return

        candidates = global_pref.iloc[np.argsort(-np.abs(global_pref.values))].head(topN).index

        for tok in candidates:
            signs = []
            mags = []
            for dv, pref in sub_pref.items():
                if tok not in pref.index:
                    continue
                val = float(pref.loc[tok])
                if val == 0:
                    continue
                signs.append(np.sign(val))
                mags.append(abs(val))
            min_support = 2 if gram == "2gram" else 3
            if len(signs) < min_support:
                continue
            # consistency: proportion of same sign as global
            gsign = np.sign(float(global_pref.get(tok, 0.0)))
            if gsign == 0:
                continue
            same = sum(1 for s in signs if s == gsign)
            consistency = same / len(signs)
            consistency_rows.append(
                {
                    "gram": gram,
                    "dimension": dim,
                    "token": tok,
                    "global_sign": "Male" if gsign > 0 else "Female",
                    "subcorpora_with_token": len(signs),
                    "consistency_rate": float(consistency),
                    "median_abs_pref": float(np.median(mags)),
                }
            )

    for gram in ["1gram", "2gram"]:
        for dim in ["period", "region", "class_coarse"]:
            print(f"Computing consistency: {gram} x {dim} ...")
            consistency_for_dimension(gram, dim, topN=200)

    cons_df = pd.DataFrame(consistency_rows)
    cons_path = os.path.join(OUT_DIR, "subcorpus_consistency.csv")
    cons_df.to_csv(cons_path, index=False)
    print("Wrote", cons_path, flush=True)

    print("\nAll experiments completed.", flush=True)


if __name__ == "__main__":
    main()

