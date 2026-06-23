# -*- coding: utf-8 -*-
"""
Step 2 — Domain-specific feature extraction.

Beyond surface n-grams, the paper calls for interpretable features grounded in
classical Chinese literary categories. This module turns each poet's aggregated
text into a small, named feature vector:

  * Imagery categories  山 / 川 / 草木 / 鳥獸 / 天體  (traditional 意象 classes)
  * Seasonal & temporal markers                      四季 / 時間
  * Allusion density                                  典故 (canon + historical figures)

Each feature is a relative frequency (per character), so poets with very
different corpus sizes stay comparable. Returns an OrderedDict per poet, plus a
helper to vectorize a whole dataframe.
"""
from collections import OrderedDict

import numpy as np

# --- Imagery lexicons (山川草木鳥獸天體) ----------------------------------
IMAGERY = {
    "img_mountain": list("山岳峰嶺巖崖巒岫崗陵阜峽壑"),      # 山 mountains
    "img_water": list("江河水川溪流泉湖海波濤瀾潮津渡浦灣瀨"),  # 川 waters
    "img_plant": list("花草木松柏竹梅蘭菊柳荷蓮桃李楊葉枝芳藤蕪"),  # 草木 vegetation
    "img_animal": list("鳥獸馬牛羊虎龍鳳鶴雁鶯燕鴉鵲魚蟬猿鹿犬鷗"),  # 鳥獸 fauna
    "img_celestial": list("天日月星雲霞風雨雪霜露雷霧虹辰曦暉"),    # 天體 sky
}

# --- Seasonal / temporal markers ----------------------------------------
SEASONAL = {
    "season_spring": list("春"),
    "season_summer": list("夏暑"),
    "season_autumn": list("秋"),
    "season_winter": list("冬寒"),
    "time_marker": list("朝暮晨昏晝夜旦夕曉午宵"),
}

# --- Allusion / erudition proxy -----------------------------------------
# Density of references to the classical canon and to historic figures/places —
# a stand-in for 典故 (allusion) usage.
ALLUSION_CANON = list("經詩書禮易春秋傳史子曰孔孟莊老聖賢")
ALLUSION_FIGURES = [
    "堯", "舜", "禹", "湯", "周公", "孔", "孟", "莊", "老", "屈原",
    "項羽", "劉邦", "蕭何", "張良", "韓信", "諸葛", "曹", "謝安",
    "陶潛", "陶淵明", "嵇康", "阮籍", "司馬", "班", "揚雄", "賈誼",
]


def extract(text):
    """Return an OrderedDict of named, length-normalized features for one poet."""
    feats = OrderedDict()
    n = max(len(text), 1)

    for groups in (IMAGERY, SEASONAL):
        for name, chars in groups.items():
            charset = set(chars)
            count = sum(1 for ch in text if ch in charset)
            feats[name] = count / n

    canon = set(ALLUSION_CANON)
    feats["allusion_canon"] = sum(1 for ch in text if ch in canon) / n
    feats["allusion_figures"] = sum(text.count(f) for f in ALLUSION_FIGURES) / n

    # Lexical richness: distinct chars / total chars (a 古體 vs 近體 style proxy).
    feats["type_token_ratio"] = len(set(text)) / n
    return feats


FEATURE_NAMES = list(extract("山水").keys())


def vectorize(texts):
    """Stack domain features for a sequence of texts into an (N, F) array."""
    return np.array([list(extract(t).values()) for t in texts], dtype=float)


if __name__ == "__main__":
    import pandas as pd
    import os
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "dataset.csv"))
    print("Feature names:", FEATURE_NAMES)
    sample = df.head(3)
    for _, row in sample.iterrows():
        print(f"\n{row['poet']} ({row['region']}):")
        for k, v in extract(row["text"]).items():
            print(f"  {k:18s} {v:.4f}")
