# 全唐詩爬蟲 - 快速開始指南

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install requests beautifulsoup4 lxml urllib3
```

### 2. 測試運行
```bash
python3 simple_quantangshi_crawler.py --test
```

### 3. 完整爬取
```bash
python3 simple_quantangshi_crawler.py
```

## 📁 文件說明

- `simple_quantangshi_crawler.py` - 主要爬蟲程序
- `quantangshi_crawler_v2.py` - 高級版本爬蟲
- `requirements.txt` - 依賴包列表
- `run_crawler.sh` - 快速啟動腳本
- `README_quantangshi.md` - 詳細說明文檔

## 🎯 主要功能

✅ **每卷輸出單獨txt文件**  
✅ **自動檢測驗證碼**  
✅ **智能延遲避免反爬蟲**  
✅ **詳細統計和摘要**  
✅ **支持斷點續爬**  

## 📊 輸出示例

```
quantangshi_volumes/
├── 全唐詩_第001卷.txt
├── 全唐詩_第002卷.txt
├── ...
├── 全唐詩_第900卷.txt
└── 爬取摘要.txt
```

## ⚡ 常用命令

```bash
# 測試模式 (前5卷)
python3 simple_quantangshi_crawler.py --test

# 爬取指定範圍
python3 simple_quantangshi_crawler.py --start 1 --end 100

# 調整延遲
python3 simple_quantangshi_crawler.py --delay 3.0

# 使用啟動腳本
./run_crawler.sh
```

## ⚠️ 注意事項

1. 請合理設置延遲時間，避免對服務器造成負擔
2. 遇到驗證碼時，爬蟲會自動記錄並繼續
3. 僅供學習和研究使用
4. 遵守網站使用條款

## 🆘 遇到問題？

1. **驗證碼頻繁出現** → 增加延遲時間
2. **連接超時** → 檢查網絡連接
3. **提取內容為空** → 檢查網頁結構是否變化

## 📞 支持

如有問題，請查看 `README_quantangshi.md` 獲取詳細說明。 