# ctext.org 爬蟲專案

這個專案包含兩個主要模組，用於從 ctext.org 爬取中國古典文獻：

1. **API 爬蟲** - 通過 API 爬取所有文檔
2. **全唐詩爬蟲** - 專門爬取全唐詩內容

## 專案結構

```
ctext.org_-crawler/
├── api_crawler/           # API 爬蟲模組
│   ├── book_downloader.py
│   ├── crawler.py
│   ├── get_book_list.py
│   ├── test_api.py
│   └── README.md
├── quantangshi_crawler/   # 全唐詩爬蟲模組
│   ├── improved_crawler.py      # 改進版爬蟲 (推薦)
│   ├── quantangshi_crawler_v2.py
│   ├── simple_quantangshi_crawler.py
│   ├── retry_failed_volumes.py
│   ├── config.json
│   ├── improved_config.json
│   ├── failed_volumes.json
│   ├── quantangshi_volumes/     # 爬取的詩歌文件
│   └── README.md
├── docs/                  # 文檔目錄
│   ├── README_book_downloader.md
│   ├── README_quantangshi.md
│   ├── QUICK_START.md
│   └── SUMMARY.md
└── README.md             # 本文件
```

## 快速開始

### 1. API 爬蟲 (爬取所有文檔)

```bash
cd api_crawler

# 獲取書籍列表
python get_book_list.py

# 下載特定書籍
python book_downloader.py --book "論語"

# 批量下載
python book_downloader.py --list books.txt
```

### 2. 全唐詩爬蟲

```bash
cd quantangshi_crawler

# 使用改進版爬蟲 (推薦)
python improved_crawler.py --start 1 --end 50 --delay 5.0

# 重試失敗的卷
python retry_failed_volumes.py --delay 15.0
```

## 功能特點

### API 爬蟲
- ✅ 支持 API 批量下載
- ✅ 自動處理編碼問題
- ✅ 支持繁體中文轉換
- ✅ 智能錯誤處理
- ✅ 斷點續傳功能

### 全唐詩爬蟲
- ✅ 智能反檢測機制
- ✅ 重試機制
- ✅ 驗證碼檢測
- ✅ 分批爬取策略
- ✅ 詳細的統計信息

## 配置說明

### API 爬蟲配置
可以通過命令行參數設置：
- `--output`: 輸出目錄
- `--format`: 輸出格式 (txt, json, xml)
- `--encoding`: 編碼格式
- `--delay`: 請求延遲

### 全唐詩爬蟲配置
使用 `improved_config.json` 配置文件：
- `delay_seconds`: 請求延遲 (建議 5-10 秒)
- `max_volumes_per_run`: 每次運行最大卷數 (建議 20-50)
- `retry_attempts`: 重試次數
- `retry_delay_seconds`: 重試間隔

## 建議使用策略

### API 爬蟲
1. 先獲取書籍列表
2. 選擇需要的書籍
3. 批量下載

### 全唐詩爬蟲
1. 使用保守策略 (每次 20 卷，延遲 10 秒)
2. 分批爬取，避免被阻擋
3. 定期重試失敗的卷
4. 夜間爬取效果更好

## 注意事項

1. **尊重網站**: 不要過於頻繁地請求
2. **遵守 robots.txt**: 檢查網站的爬蟲政策
3. **備份數據**: 定期保存已爬取的數據
4. **監控進度**: 定期檢查爬取狀態
5. **遵守 API 限制**: 注意 API 的使用頻率限制

## 故障排除

### 常見問題
1. **驗證碼阻擋**: 增加延遲時間，使用更保守的設置
2. **HTTP 403 錯誤**: 更長的延遲時間，考慮使用代理
3. **解析失敗**: 檢查網站結構是否變化，更新解析規則

### 獲取幫助
- 查看各模組的 README.md 文件
- 檢查配置文件設置
- 查看錯誤日誌

## 開發者信息

這個專案專門用於學術研究和文化保護目的。請確保遵守相關網站的使用條款和版權規定。 