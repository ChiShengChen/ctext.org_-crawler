# 專案結構說明

```
ctext.org_-crawler/
├── README.md                    # 主要說明文件
├── requirements.txt             # Python 依賴
├── run_crawler.sh              # 運行腳本
├── ctext_books.csv             # 書籍列表數據
│
├── api_crawler/                # API 爬蟲模組
│   ├── README.md              # API 爬蟲說明
│   ├── book_downloader.py     # 主要下載器
│   ├── crawler.py             # 通用爬蟲類
│   ├── get_book_list.py       # 獲取書籍列表
│   └── test_api.py            # API 測試工具
│
├── quantangshi_crawler/        # 全唐詩爬蟲模組
│   ├── README.md              # 全唐詩爬蟲說明
│   ├── improved_crawler.py    # 改進版爬蟲 (推薦)
│   ├── quantangshi_crawler_v2.py  # v2 版本爬蟲
│   ├── simple_quantangshi_crawler.py  # 簡化版爬蟲
│   ├── retry_failed_volumes.py # 重試失敗卷工具
│   ├── config.json            # 基本配置
│   ├── config_example.json    # 配置範例
│   ├── improved_config.json   # 改進配置 (推薦)
│   ├── failed_volumes.json    # 失敗卷記錄
│   └── quantangshi_volumes/   # 爬取的詩歌文件
│       ├── 全唐詩_第001卷.txt
│       ├── 全唐詩_第002卷.txt
│       └── ...
│
└── docs/                      # 文檔目錄
    ├── README.md              # 原始說明文件
    ├── README_book_downloader.md  # 書籍下載器說明
    ├── README_quantangshi.md     # 全唐詩爬蟲說明
    ├── QUICK_START.md            # 快速開始指南
    └── SUMMARY.md                # 總結文檔
```

## 模組說明

### 1. API 爬蟲模組 (`api_crawler/`)
- **用途**: 通過 ctext.org 的 API 爬取所有文檔
- **主要文件**: `book_downloader.py`
- **功能**: 批量下載、編碼處理、錯誤重試

### 2. 全唐詩爬蟲模組 (`quantangshi_crawler/`)
- **用途**: 專門爬取全唐詩內容
- **主要文件**: `improved_crawler.py` (推薦)
- **功能**: 反檢測、重試機制、驗證碼處理

### 3. 文檔目錄 (`docs/`)
- **用途**: 存放所有說明文檔
- **內容**: 使用指南、配置說明、故障排除

## 推薦使用順序

1. **API 爬蟲**: 先使用 API 爬蟲獲取書籍列表和下載文檔
2. **全唐詩爬蟲**: 使用改進版爬蟲爬取全唐詩
3. **重試工具**: 對失敗的卷進行重試

## 配置文件

- `improved_config.json`: 全唐詩爬蟲的推薦配置
- `config.json`: 基本配置
- `failed_volumes.json`: 記錄失敗的卷，便於重試 