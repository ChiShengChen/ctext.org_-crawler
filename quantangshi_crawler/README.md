# 全唐詩爬蟲模組

這個模組專門用於爬取 ctext.org 上的全唐詩內容，並提供數據分析和Web API服務。

## 🎉 項目完成狀態

✅ **已完成**: 成功爬取全唐詩900卷，共42280首詩歌，2535位作者  
📊 **數據分析**: 提供完整的統計分析和可視化  
🌐 **Web API**: 提供RESTful API接口  
📈 **可視化**: 生成統計圖表和報告  

## 文件說明

### 主要爬蟲
- `advanced_crawler.py` - 高級反檢測爬蟲 (最新版本)
- `improved_crawler.py` - 改進版爬蟲 (推薦使用)
- `quantangshi_crawler_v2.py` - 全唐詩爬蟲 v2.0
- `simple_quantangshi_crawler.py` - 簡化版爬蟲

### 數據分析工具
- `data_analysis.py` - 數據分析和可視化工具
- `extract_authors_clean.py` - 作者提取和清理工具
- `authors_list_clean.txt` - 清理後的作者列表
- `authors_python_list_clean.py` - Python格式作者列表

### Web API
- `web_api.py` - Flask Web API服務器
- 提供RESTful API接口查詢詩歌數據

### 工具腳本
- `retry_failed_volumes.py` - 重試失敗的卷

### 配置文件
- `config.json` - 基本配置
- `improved_config.json` - 改進配置 (推薦)
- `advanced_config.json` - 高級配置
- `failed_volumes.json` - 失敗卷記錄

### 數據目錄
- `quantangshi_volumes/` - 爬取的詩歌文件 (900卷)

## 使用方法

### 1. 基本爬取

```bash
# 使用高級爬蟲 (推薦)
python advanced_crawler.py --start 1 --end 50 --delay 5.0

# 使用改進版爬蟲
python improved_crawler.py --start 1 --end 50 --delay 5.0

# 使用 v2 版本
python quantangshi_crawler_v2.py
```

### 2. 數據分析

```bash
# 運行數據分析
python data_analysis.py

# 提取作者列表
python extract_authors_clean.py
```

### 3. 啟動Web API

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動API服務器
python web_api.py
```

然後訪問 http://localhost:5000 查看API文檔

### 4. 重試失敗的卷

```bash
python retry_failed_volumes.py --delay 15.0
```

### 5. 分批爬取策略

```bash
# 第一批：1-50卷
python advanced_crawler.py --start 1 --end 50 --delay 5.0

# 等待後，第二批：51-100卷
python advanced_crawler.py --start 51 --end 100 --delay 5.0
```

## Web API 使用

### API端點

- `GET /api/random` - 獲取隨機詩歌
- `GET /api/search?q=關鍵詞` - 搜索詩歌
- `GET /api/author/作者名` - 按作者獲取詩歌
- `GET /api/volume/卷號` - 按卷號獲取詩歌
- `GET /api/authors` - 獲取作者列表
- `GET /api/stats` - 獲取統計信息

### 使用示例

```javascript
// 獲取隨機詩歌
fetch('/api/random')
  .then(response => response.json())
  .then(data => console.log(data));

// 搜索詩歌
fetch('/api/search?q=春天')
  .then(response => response.json())
  .then(data => console.log(data));

// 獲取李白的詩歌
fetch('/api/author/李白')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 配置說明

### advanced_config.json 主要設置

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

## 數據統計

### 最活躍的作者 (前10名)
1. 白居易 - 2639首
2. 杜甫 - 1157首
3. 李白 - 881首
4. 齊己 - 780首
5. 劉禹錫 - 700首
6. 元稹 - 591首
7. 李商隱 - 555首
8. 貫休 - 551首
9. 韋應物 - 550首
10. 陸龜蒙 - 518首

### 數據質量
- 總詩歌數: 42,280首
- 總作者數: 2,535位
- 總卷數: 900卷
- 平均每位作者詩歌數: 16.7首
- 只出現一次的作者: 1,356人

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

### 4. Web API 無法啟動
- 確保已安裝 Flask: `pip install flask`
- 檢查端口是否被佔用
- 查看錯誤日誌

## 建議策略

### 保守策略 (推薦)
```bash
# 每次只爬取 20 卷，延遲 10 秒
python advanced_crawler.py --start 1 --end 20 --delay 10.0
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

## 下一步開發

1. **數據庫存儲**: 將數據存入SQLite/PostgreSQL
2. **機器學習**: 詩歌風格分析、作者識別
3. **Web界面**: 完整的詩歌瀏覽網站
4. **移動應用**: 詩歌學習APP
5. **API優化**: 添加緩存、分頁、搜索優化

## 注意事項

1. **尊重網站**: 不要過於頻繁地請求
2. **遵守 robots.txt**: 檢查網站的爬蟲政策
3. **備份數據**: 定期保存已爬取的數據
4. **監控進度**: 定期檢查爬取狀態
5. **數據使用**: 僅供學習和研究使用

## 貢獻

歡迎提交Issue和Pull Request來改進這個項目！

## 許可證

本項目僅供學習和研究使用，請遵守相關法律法規。 