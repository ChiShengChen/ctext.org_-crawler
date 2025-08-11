#!/usr/bin/env python3
"""
調試測試腳本 - 測試單個卷的爬取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from improved_crawler import ImprovedQuantangshiCrawler

def test_single_volume(volume_num: int = 94):
    """測試單個卷的爬取"""
    print(f"🧪 開始測試第 {volume_num} 卷...")
    
    # 創建爬蟲實例
    crawler = ImprovedQuantangshiCrawler(
        config_file="config.json",
        output_dir="debug_output",
        delay=1.0  # 使用較短的延遲
    )
    
    try:
        # 測試獲取單個卷
        poems, status = crawler.fetch_volume_with_retry(volume_num)
        
        print(f"\n📊 測試結果:")
        print(f"   狀態: {status}")
        print(f"   詩歌數量: {len(poems) if poems else 0}")
        
        if poems:
            print(f"   第一首詩標題: {poems[0].get('title', 'N/A')}")
            print(f"   第一首詩作者: {poems[0].get('author', 'N/A')}")
            print(f"   第一首詩內容長度: {len(poems[0].get('content', ''))}")
            
            # 保存到文件
            crawler.save_volume_to_file(poems, volume_num)
            print(f"✅ 測試成功，已保存到 debug_output/")
        else:
            print(f"❌ 測試失敗: {status}")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

def test_connection():
    """測試基本連接"""
    print("🔗 測試基本連接...")
    
    import requests
    
    try:
        response = requests.get("https://ctext.org/quantangshi/94/zh", timeout=10)
        print(f"   狀態碼: {response.status_code}")
        print(f"   內容長度: {len(response.text)}")
        print(f"   響應頭: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 連接測試成功")
        else:
            print(f"⚠️  連接測試異常，狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="調試測試腳本")
    parser.add_argument("--volume", type=int, default=94, help="要測試的卷號")
    parser.add_argument("--connection", action="store_true", help="只測試連接")
    
    args = parser.parse_args()
    
    if args.connection:
        test_connection()
    else:
        test_connection()
        print("\n" + "="*50 + "\n")
        test_single_volume(args.volume) 