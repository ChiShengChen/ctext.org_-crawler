#!/usr/bin/env python3
"""
演示工作解決方案
展示如何使用改進的爬蟲成功獲取全唐詩
"""

import os
import sys
from improved_crawler import ImprovedQuantangshiCrawler

def demo_working_solution():
    """演示工作解決方案"""
    print("🎯 全唐詩爬蟲 - 工作解決方案演示")
    print("=" * 50)
    
    # 創建改進的爬蟲實例
    crawler = ImprovedQuantangshiCrawler(
        config_file="improved_config.json",
        output_dir="demo_output",
        delay=2.0
    )
    
    # 測試已知可以工作的卷
    test_volumes = [87, 89, 90]  # 第88卷有問題，跳過
    
    print(f"📖 測試卷: {test_volumes}")
    print()
    
    success_count = 0
    total_poems = 0
    
    for volume in test_volumes:
        print(f"🔄 正在處理第 {volume} 卷...")
        
        # 檢查是否已存在文件
        filename = f"全唐詩_第{volume:03d}卷.txt"
        filepath = os.path.join(crawler.output_dir, filename)
        
        if os.path.exists(filepath):
            print(f"   ⚠️  文件已存在，跳過")
            continue
        
        # 獲取詩歌
        poems, status = crawler.fetch_volume_with_retry(volume)
        
        if status == "success":
            print(f"   ✅ 成功！獲取到 {len(poems)} 首詩")
            crawler.save_volume_to_file(poems, volume)
            success_count += 1
            total_poems += len(poems)
            
            # 顯示前3首詩的標題
            print("   📝 前3首詩:")
            for i, poem in enumerate(poems[:3], 1):
                title = poem.get('title', '未知標題')
                author = poem.get('author', '未知作者')
                print(f"      {i}. {title} - {author}")
        else:
            print(f"   ❌ 失敗: {status}")
        
        print()
    
    # 總結
    print("=" * 50)
    print("📊 演示結果:")
    print(f"   ✅ 成功處理: {success_count}/{len(test_volumes)} 卷")
    print(f"   📝 總詩歌數: {total_poems} 首")
    print(f"   💾 輸出目錄: {crawler.output_dir}")
    
    if success_count > 0:
        print("\n🎉 演示成功！改進的爬蟲可以正常工作。")
        print("\n💡 使用建議:")
        print("   1. 對於正常卷，使用 improved_crawler.py")
        print("   2. 對於問題卷，使用 advanced_crawler.py")
        print("   3. 分批處理，避免一次性爬取太多卷")
        print("   4. 定期重試失敗的卷")
    else:
        print("\n⚠️  演示失敗，可能需要調整配置或等待更長時間。")

def show_file_structure():
    """顯示文件結構"""
    print("\n📁 項目文件結構:")
    print("   improved_crawler.py      - 改進版爬蟲")
    print("   advanced_crawler.py      - 高級爬蟲")
    print("   improved_config.json     - 改進版配置")
    print("   advanced_config.json     - 高級配置")
    print("   test_crawler.py          - 測試腳本")
    print("   retry_failed_volumes.py  - 重試腳本")
    print("   DEBUG_SUMMARY.md         - 調試總結")

if __name__ == "__main__":
    demo_working_solution()
    show_file_structure() 