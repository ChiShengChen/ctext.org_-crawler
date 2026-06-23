# ctext.org 爬蟲與唐詩計算分析專案

> 從 [ctext.org](https://ctext.org) 爬取中國古典文獻，並以《全唐詩》為核心，
> 進行詞頻分析、詩人籍貫預測與詩人關係網路的計算研究。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-Academic%20use-lightgrey)
![Domain](https://img.shields.io/badge/domain-Digital%20Humanities-purple)
![Corpus](https://img.shields.io/badge/corpus-%E5%85%A8%E5%94%90%E8%A9%A9%20900%20%E5%8D%B7-red)

**主題標籤**：`digital-humanities` · `chinese-poetry` · `quan-tang-shi` · `web-scraping`
· `ctext` · `nlp` · `text-mining` · `ngram-analysis` · `machine-learning`
· `quantum-machine-learning` · `classical-chinese`

---

## 專案總覽

本倉庫從「資料爬取 → 文本分析 → 機器學習」三個層面，建構一條完整的唐詩數位人文研究管線：

| 模組 | 用途 | 主要技術 |
|------|------|----------|
| [`api_crawler/`](api_crawler/) | 透過 ctext.org **API** 批量下載任意古典文獻 | requests、編碼處理、斷點續傳 |
| [`quantangshi_crawler/`](quantangshi_crawler/) | 專門爬取**《全唐詩》900 卷**，並做 n-gram 詞頻統計 | 反檢測爬蟲、n-gram、TF-IDF |
| [`gender_poem_predictor/`](gender_poem_predictor/) | 僅憑詩作預測詩人**地理出身（唐代「道」）** | scikit-learn、字元 n-gram、領域特徵 |
| [`quantum_tangshi_relation_predict/`](quantum_tangshi_relation_predict/) | 以**量子神經網路**預測詩人社交關係 | 量子圖神經網路、PennyLane |
| [`bencao_gangmu/`](bencao_gangmu/) | 已下載之古典文獻範例（論語、孟子、詩經…） | — |

完整目錄樹見 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)。

---

## 快速開始

```bash
pip install -r requirements.txt
```

### 1. API 爬蟲 — 下載任意古籍

```bash
cd api_crawler
python get_book_list.py                 # 取得書籍列表
python book_downloader.py --book "論語"  # 下載單一書籍
python book_downloader.py --list books.txt  # 批量下載
```

### 2. 全唐詩爬蟲

```bash
cd quantangshi_crawler
python improved_crawler.py --start 1 --end 50 --delay 5.0  # 改進版（推薦）
python retry_failed_volumes.py --delay 15.0               # 重試失敗卷
```

### 3. 詩人籍貫預測（機器學習）

```bash
cd gender_poem_predictor
python build_dataset.py   # 建立詩人層級語料 → dataset.csv（357 位詩人、10 個道）
python train.py           # 交叉驗證評估 + 可解釋性分析
```

### 4. 量子神經網路詩人關係預測

```bash
cd quantum_tangshi_relation_predict
python experiment_runner.py   # 154 詩人節點、180 關係邊的關係預測實驗
```

---

## 各模組功能特點

### API 爬蟲 (`api_crawler/`)
- ✅ API 批量下載、自動編碼處理、繁體轉換
- ✅ 智能錯誤處理與斷點續傳

### 全唐詩爬蟲 (`quantangshi_crawler/`)
- ✅ 智能反檢測、重試與驗證碼偵測機制
- ✅ 分批爬取策略與詳細統計
- ✅ 1–7 gram 作者詞頻統計（見 `analysis_result/`）

### 籍貫預測 (`gender_poem_predictor/`)
- ✅ 結合《全唐詩》文本與 CBDB 籍貫資料建立資料集
- ✅ 字元 n-gram TF-IDF + 意象／季節／典故等領域特徵
- ✅ 交叉驗證、混淆矩陣、距離衰減等可解釋性圖表
- 📄 含可投稿 arXiv 的 LaTeX 論文（`paper/`，未納入版控）

### 量子關係預測 (`quantum_tangshi_relation_predict/`)
- ✅ 將量子圖神經網路應用於詩人社交關係預測
- ✅ 完整實驗報告與設計文件

---

## 配置與使用建議

### 全唐詩爬蟲配置（`improved_config.json`）
- `delay_seconds`：請求延遲（建議 5–10 秒）
- `max_volumes_per_run`：每次最大卷數（建議 20–50）
- `retry_attempts` / `retry_delay_seconds`：重試次數與間隔

### 爬取策略
1. 採保守設定（每次 20 卷、延遲 10 秒），分批爬取避免被阻擋
2. 定期重試失敗的卷，夜間爬取效果更佳

---

## 注意事項

1. **尊重網站**：避免過於頻繁的請求，遵守 `robots.txt`
2. **遵守條款**：注意 ctext.org 的使用條款與版權規定
3. **備份資料**：定期保存已爬取的數據

### 常見問題
- 驗證碼／HTTP 403：增加延遲、使用更保守設定，必要時考慮代理
- 解析失敗：檢查網站結構是否變動，更新解析規則

---

## 開發者資訊

本專案僅供**學術研究與文化保護**用途。請確保遵守相關網站的使用條款與版權規定。
