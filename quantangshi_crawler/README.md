# 全唐詩爬蟲模組

這個模組專門用於爬取 ctext.org 上的全唐詩內容。

## 文件說明

### 主要爬蟲
- `quantangshi_crawler_v2.py` - 全唐詩爬蟲 v2.0 (主要版本)
- `improved_crawler.py` - 改進版爬蟲 (推薦使用)
- `simple_quantangshi_crawler.py` - 簡化版爬蟲

### 工具腳本
- `retry_failed_volumes.py` - 重試失敗的卷

### 配置文件
- `config.json` - 基本配置
- `improved_config.json` - 改進配置 (推薦)
- `failed_volumes.json` - 失敗卷記錄

### 數據目錄
- `quantangshi_volumes/` - 爬取的詩歌文件

## 使用方法

### 1. 基本爬取

```bash
# 使用改進版爬蟲 (推薦)
python improved_crawler.py --start 1 --end 50 --delay 5.0

# 使用 v2 版本
python quantangshi_crawler_v2.py
```

### 2. 重試失敗的卷

```bash
python retry_failed_volumes.py --delay 15.0
```

### 3. 分批爬取策略

```bash
# 第一批：1-50卷
python improved_crawler.py --start 1 --end 50 --delay 5.0

# 等待後，第二批：51-100卷
python improved_crawler.py --start 51 --end 100 --delay 5.0
```

## 配置說明

### improved_config.json 主要設置

```json
{
  "crawler_settings": {
    "delay_seconds": 5.0,           // 請求延遲
    "max_volumes_per_run": 20,      // 每次運行最大卷數
    "retry_attempts": 3,            // 重試次數
    "retry_delay_seconds": 15       // 重試間隔
  }
}
```

## 常見問題

### 1. 驗證碼阻擋
- 增加延遲時間到 10-15 秒
- 使用更保守的設置
- 分批爬取，避免連續請求

### 2. HTTP 403 錯誤
- 更長的延遲時間 (15-30 秒)
- 更換 User-Agent
- 考慮使用代理

### 3. 解析失敗
- 檢查網站結構是否變化
- 更新解析規則
- 保存原始 HTML 進行分析

## 建議策略

### 保守策略 (推薦)
```bash
# 每次只爬取 20 卷，延遲 10 秒
python improved_crawler.py --start 1 --end 20 --delay 10.0
```

### 夜間爬取
- 在網站流量較少的時間段進行
- 使用更長的延遲時間

## 輸出格式

每卷詩歌保存為單獨的 txt 文件：

```
全唐詩 第X卷
==================================================

1. 詩歌標題
   作者: 作者名
   內容:
詩歌內容...
------------------------------

2. 詩歌標題
   作者: 作者名
   內容:
詩歌內容...
------------------------------
```

## 注意事項

1. **尊重網站**: 不要過於頻繁地請求
2. **遵守 robots.txt**: 檢查網站的爬蟲政策
3. **備份數據**: 定期保存已爬取的數據
4. **監控進度**: 定期檢查爬取狀態 