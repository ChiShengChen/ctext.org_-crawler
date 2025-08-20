# 全唐詩作者 N-gram 分析結果 (不包含標題)

## 概述

本目錄包含全唐詩作者 N-gram 分析結果，**只統計詩歌內容，不包含標題**。

## 目錄結構

```
analysis_results_no_title/
├── author_ngram_csvs/           # 每位作者的n-gram CSV文件
│   ├── 白居易_1gram_詞頻統計.csv
│   ├── 白居易_2gram_詞頻統計.csv
│   ├── 白居易_4gram_詞頻統計.csv
│   ├── 杜甫_1gram_詞頻統計.csv
│   └── ...
├── detailed_ngram_analysis_no_title.json  # 詳細的JSON分析結果
├── author_summary_no_title.csv            # 作者摘要統計
├── analysis_report_no_title.md            # 分析報告
└── README.md                              # 本文件
```

## 統計摘要

- **總作者數**: 2,460 位
- **總詩歌數**: 41,380 首
- **總字符數**: 2,819,637 (不包含標題)
- **平均每首詩**: 68.1 字符

### N-gram 統計

- **1-gram 總數**: 572,946
- **2-gram 總數**: 2,215,737
- **4-gram 總數**: 2,716,966

## 文件說明

### 1. author_ngram_csvs/
包含每位作者的 1-gram、2-gram、4-gram 詞頻統計 CSV 文件。

**文件命名格式**: `{作者名}_{n}gram_詞頻統計.csv`

**CSV 格式**:
```csv
排名,詞彙,出現次數
1,不,2551
2,人,1756
3,一,1600
...
```

**文件數量**: 7,380 個 CSV 文件 (2,460 位作者 × 3 種 n-gram)

### 2. detailed_ngram_analysis_no_title.json
包含所有作者的詳細 n-gram 統計數據，格式為 JSON。

**主要字段**:
- `metadata`: 元數據信息
- `author_statistics`: 每位作者的詳細統計

### 3. author_summary_no_title.csv
作者摘要統計表，包含每位作者的基本統計信息。

**字段說明**:
- `author`: 作者名稱
- `poem_count`: 詩歌數量
- `total_chars`: 總字符數 (不包含標題)
- `avg_chars_per_poem`: 平均每首詩字符數
- `unique_1gram`: 唯一 1-gram 數量
- `unique_2gram`: 唯一 2-gram 數量
- `unique_4gram`: 唯一 4-gram 數量
- `total_1gram`: 1-gram 總出現次數
- `total_2gram`: 2-gram 總出現次數
- `total_4gram`: 4-gram 總出現次數

### 4. analysis_report_no_title.md
詳細的分析報告，包含統計摘要和文件說明。

## 與原版對比

### 原版 (analysis_results/)
- 包含標題和內容的統計
- 總字符數: 3,089,451
- 標題字符佔比: 8.73%

### 本版 (analysis_results_no_title/)
- 只包含內容的統計
- 總字符數: 2,819,637
- 更準確反映詩歌創作量

## 使用建議

1. **研究詩歌內容**: 使用本版進行詩歌內容分析
2. **比較分析**: 與原版對比，了解標題對統計的影響
3. **詞頻研究**: 利用 n-gram 數據進行詞頻和語言模式分析
4. **作者風格**: 分析不同作者的用詞偏好和寫作風格

## 技術細節

- **文本清理**: 只保留中文字符，移除標點符號和數字
- **作者名稱**: 已清理，去掉末尾的"著"字
- **編碼**: UTF-8
- **生成時間**: 2025-08-20 22:40:22

## 注意事項

- 本分析只統計詩歌內容，不包含標題
- 已清理作者名稱，去掉末尾的"著"字
- 只保留中文字符，移除標點符號和數字
- 文件較大，建議使用適當的工具進行處理 