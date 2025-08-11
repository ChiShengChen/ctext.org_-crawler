#!/usr/bin/env python3
"""
測試改進版全唐詩爬蟲
"""

import sys
import os
from improved_crawler import ImprovedQuantangshiCrawler

def test_crawler():
    """測試爬蟲功能"""
    print("🧪 開始測試改進版爬蟲...")
    
    # 使用改進的配置文件
    config_file = "improved_config.json"
    
    # 創建爬蟲實例
    crawler = ImprovedQuantangshiCrawler(
        config_file=config_file,
        output_dir="test_output",
        delay=1.0  # 較短的延遲用於測試
    )
    
    # 測試單個卷
    print("\n📖 測試獲取第87卷...")
    poems, status = crawler.fetch_volume_with_retry(87)
    
    if status == "success":
        print(f"✅ 測試成功！獲取到 {len(poems)} 首詩")
        # 保存測試結果
        crawler.save_volume_to_file(poems, 87)
        
        # 顯示前幾首詩的標題
        print("\n📝 前5首詩的標題:")
        for i, poem in enumerate(poems[:5], 1):
            title = poem.get('title', '未知標題')
            author = poem.get('author', '未知作者')
            print(f"  {i}. {title} - {author}")
            
    elif status == "captcha":
        print("⚠️  遇到驗證碼，這是正常的防護機制")
    else:
        print(f"❌ 測試失敗: {status}")
    
    print("\n🎯 測試完成！")

if __name__ == "__main__":
    test_crawler() 