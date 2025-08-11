# API 爬蟲模組

這個模組專門用於通過 ctext.org 的 API 爬取所有文檔。

## 文件說明

- `book_downloader.py` - 主要的書籍下載器
- `crawler.py` - 通用爬蟲類
- `get_book_list.py` - 獲取書籍列表
- `test_api.py` - API 測試工具

## 使用方法

### 1. 獲取書籍列表

```bash
python get_book_list.py
```

### 2. 下載特定書籍

```bash
python book_downloader.py --book "論語"
```

### 3. 批量下載

```bash
python book_downloader.py --list books.txt
```

## 功能特點

- ✅ 支持 API 批量下載
- ✅ 自動處理編碼問題
- ✅ 支持繁體中文轉換
- ✅ 智能錯誤處理
- ✅ 斷點續傳功能

## 配置選項

可以通過命令行參數或配置文件設置：

- `--output`: 輸出目錄
- `--format`: 輸出格式 (txt, json, xml)
- `--encoding`: 編碼格式
- `--delay`: 請求延遲

## 注意事項

1. 請遵守 API 使用限制
2. 建議設置適當的延遲時間
3. 大量下載時建議分批進行 