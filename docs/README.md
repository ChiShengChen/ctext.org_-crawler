# 全唐詩爬蟲使用說明

## 失敗原因分析

根據你的日誌，爬蟲失敗主要有以下幾種情況：

### 1. 驗證碼阻擋 (Captcha)
- **影響範圍**: 第43-47, 49-59卷
- **原因**: 網站檢測到爬蟲行為，要求輸入驗證碼
- **解決方案**: 
  - 增加請求延遲
  - 使用更真實的瀏覽器請求頭
  - 分批爬取，避免連續請求

### 2. HTTP 403 錯誤 (Forbidden)
- **影響範圍**: 第60-71卷
- **原因**: 網站直接拒絕訪問
- **解決方案**:
  - 更長的延遲時間
  - 更換IP地址
  - 使用代理服務器

### 3. 內容驗證失敗
- **影響範圍**: 第10卷
- **原因**: 頁面內容不符合預期格式
- **解決方案**: 調整內容驗證規則

## 改進方案

### 1. 使用改進版爬蟲

```bash
# 使用更保守的設置
python improved_crawler.py --start 1 --end 50 --delay 5.0 --config improved_config.json
```

### 2. 重試失敗的卷

```bash
# 重試失敗的卷，使用更長的延遲
python retry_failed_volumes.py --delay 15.0
```

### 3. 分批爬取策略

```bash
# 第一批：1-50卷
python improved_crawler.py --start 1 --end 50 --delay 5.0

# 等待一段時間後，第二批：51-100卷
python improved_crawler.py --start 51 --end 100 --delay 5.0
```

## 配置文件說明

### improved_config.json
- `delay_seconds`: 請求延遲（建議5-10秒）
- `max_volumes_per_run`: 每次運行最大卷數（建議20-50）
- `retry_attempts`: 重試次數
- `retry_delay_seconds`: 重試間隔

## 建議的爬取策略

### 1. 保守策略（推薦）
```bash
# 每次只爬取20卷，延遲10秒
python improved_crawler.py --start 1 --end 20 --delay 10.0
```

### 2. 夜間爬取
- 在網站流量較少的時間段進行爬取
- 使用更長的延遲時間

### 3. 使用代理
- 考慮使用代理服務器輪換IP
- 避免單一IP被封鎖

## 監控和調試

### 1. 檢查失敗原因
```bash
# 查看失敗卷列表
cat failed_volumes.json
```

### 2. 調試模式
在配置文件中設置：
```json
{
  "output_format": {
    "verbose_logging": true,
    "save_debug_content": true
  }
}
```

## 注意事項

1. **尊重網站**: 不要過於頻繁地請求
2. **遵守robots.txt**: 檢查網站的爬蟲政策
3. **備份數據**: 定期保存已爬取的數據
4. **監控進度**: 定期檢查爬取狀態

## 故障排除

### 如果遇到大量403錯誤
1. 增加延遲時間到15-30秒
2. 更換User-Agent
3. 考慮使用代理

### 如果遇到驗證碼
1. 暫停爬取1-2小時
2. 手動訪問網站確認
3. 使用更保守的設置重新開始

### 如果解析失敗
1. 檢查網站結構是否變化
2. 更新解析規則
3. 保存原始HTML進行分析
