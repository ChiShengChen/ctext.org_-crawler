# 全唐詩爬蟲調試總結

## 問題分析

### 主要問題
1. **CAPTCHA 驗證碼檢測**: 網站檢測到自動化請求，顯示驗證碼
2. **HTTP 403 錯誤**: 服務器拒絕請求
3. **長時間延遲**: 原始策略等待時間過長（30+秒）

### 測試結果

#### 成功案例
- ✅ **第87卷**: 成功獲取94首詩
- ✅ **改進版爬蟲**: 使用requests庫和會話管理，減少延遲

#### 失敗案例
- ❌ **第88卷**: 持續遇到CAPTCHA和403錯誤
- ❌ **第43-60卷**: 大量CAPTCHA問題

## 解決方案

### 1. 已實現的改進

#### 改進版爬蟲 (`improved_crawler.py`)
- ✅ 使用 `requests.Session()` 進行會話管理
- ✅ 智能延遲策略（減少等待時間）
- ✅ 會話輪換機制
- ✅ 更好的錯誤處理
- ✅ 隨機請求頭

#### 高級爬蟲 (`advanced_crawler.py`)
- ✅ 會話池管理
- ✅ 多線程安全的會話輪換
- ✅ 更先進的反檢測機制
- ✅ 指數退避重試策略

### 2. 推薦使用策略

#### 對於正常卷（如第87卷）
```bash
# 使用改進版爬蟲
python improved_crawler.py --start 87 --end 87 --delay 2.0 --config improved_config.json
```

#### 對於問題卷（如第88卷）
```bash
# 使用高級爬蟲，更長的延遲
python advanced_crawler.py --start 88 --end 88 --delay 5.0 --config advanced_config.json
```

### 3. 配置文件優化

#### 改進版配置 (`improved_config.json`)
```json
{
    "crawler_settings": {
        "delay_seconds": 2.0,
        "max_retries": 3,
        "max_requests_per_session": 15
    }
}
```

#### 高級配置 (`advanced_config.json`)
```json
{
    "crawler_settings": {
        "delay_seconds": 3.0,
        "max_retries": 5,
        "session_pool_size": 4,
        "max_requests_per_session": 8
    }
}
```

## 使用建議

### 1. 分批處理
- 將900卷分成小批次（10-20卷）
- 每批次之間休息較長時間（30分鐘以上）

### 2. 時間策略
- 避免在高峰時段爬取
- 考慮在深夜或凌晨進行大規模爬取

### 3. 重試策略
- 對於CAPTCHA問題，等待更長時間（1-2小時）
- 使用不同的IP地址（如果可能）

### 4. 監控和記錄
- 記錄失敗的卷
- 定期重試失敗的卷
- 使用 `retry_failed_volumes.py` 腳本

## 腳本使用指南

### 測試爬蟲
```bash
python test_crawler.py
```

### 爬取指定範圍
```bash
# 小範圍測試
python improved_crawler.py --start 87 --end 90 --delay 2.0

# 大範圍爬取
python advanced_crawler.py --start 1 --end 50 --delay 3.0
```

### 重試失敗的卷
```bash
python retry_failed_volumes.py --file failed_volumes.json
```

## 技術細節

### 反檢測機制
1. **會話管理**: 維護多個會話，輪換使用
2. **請求頭隨機化**: 隨機選擇User-Agent和其他頭部
3. **延遲策略**: 智能延遲，避免規律性
4. **錯誤處理**: 針對不同錯誤類型採用不同策略

### 內容提取
- 使用BeautifulSoup解析HTML
- 支持多種詩歌格式
- 自動清理和格式化內容

## 注意事項

1. **遵守robots.txt**: 尊重網站的爬取規則
2. **合理延遲**: 避免對服務器造成過大負擔
3. **備份數據**: 定期保存已爬取的數據
4. **監控進度**: 記錄成功和失敗的統計信息

## 未來改進方向

1. **代理支持**: 集成代理池以繞過IP限制
2. **驗證碼處理**: 集成驗證碼識別服務
3. **分布式爬取**: 支持多機器協同爬取
4. **數據庫存儲**: 使用數據庫而非文件存儲
5. **Web界面**: 提供Web管理界面 