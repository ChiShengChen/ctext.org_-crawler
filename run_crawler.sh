#!/bin/bash

# 全唐詩爬蟲快速啟動腳本

echo "全唐詩爬蟲 v2.0"
echo "=================="

# 檢查Python是否安裝
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python3，請先安裝 Python3"
    exit 1
fi

# 檢查依賴是否安裝
echo "檢查依賴..."
python3 -c "import requests, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安裝依賴..."
    pip3 install -r requirements.txt
fi

# 顯示使用選項
echo ""
echo "請選擇運行模式:"
echo "1) 測試模式 (爬取前5卷)"
echo "2) 完整爬取 (爬取所有900卷)"
echo "3) 自定義範圍"
echo "4) 查看幫助"
echo ""

read -p "請輸入選項 (1-4): " choice

case $choice in
    1)
        echo "啟動測試模式..."
        python3 simple_quantangshi_crawler.py --test
        ;;
    2)
        echo "啟動完整爬取模式..."
        echo "警告: 這將爬取所有900卷，可能需要很長時間"
        read -p "確認繼續? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            python3 simple_quantangshi_crawler.py
        else
            echo "已取消"
        fi
        ;;
    3)
        read -p "請輸入開始卷號: " start_vol
        read -p "請輸入結束卷號: " end_vol
        read -p "請輸入輸出目錄 (默認: quantangshi_volumes): " output_dir
        output_dir=${output_dir:-quantangshi_volumes}
        echo "啟動自定義爬取模式..."
        python3 simple_quantangshi_crawler.py --start $start_vol --end $end_vol --output $output_dir
        ;;
    4)
        echo ""
        echo "使用說明:"
        echo "python3 simple_quantangshi_crawler.py [選項]"
        echo ""
        echo "選項:"
        echo "  --start N       開始卷號 (默認: 1)"
        echo "  --end N         結束卷號 (默認: 900)"
        echo "  --output DIR    輸出目錄 (默認: quantangshi_volumes)"
        echo "  --delay N       請求延遲秒數 (默認: 2.0)"
        echo "  --test          測試模式 (只爬取前5卷)"
        echo ""
        echo "示例:"
        echo "  python3 simple_quantangshi_crawler.py --test"
        echo "  python3 simple_quantangshi_crawler.py --start 1 --end 100"
        echo "  python3 simple_quantangshi_crawler.py --delay 3.0"
        ;;
    *)
        echo "無效選項"
        exit 1
        ;;
esac

echo ""
echo "爬取完成！請查看輸出目錄中的文件。" 