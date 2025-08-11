#!/usr/bin/env python3
"""
重試失敗的卷 - 改進版
使用改進的爬蟲重新嘗試獲取之前失敗的卷
"""

import json
import os
import sys
from improved_crawler import ImprovedQuantangshiCrawler

def load_failed_volumes(filename="failed_volumes.json"):
    """載入失敗的卷列表"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('failed_volumes', [])
    except FileNotFoundError:
        print(f"⚠️  文件 {filename} 不存在")
        return []
    except json.JSONDecodeError:
        print(f"⚠️  文件 {filename} 格式錯誤")
        return []

def save_failed_volumes(failed_volumes, filename="failed_volumes.json"):
    """保存失敗的卷列表"""
    data = {
        "failed_volumes": failed_volumes,
        "total_failed": len(failed_volumes)
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 已保存失敗卷列表到 {filename}")

def retry_failed_volumes():
    """重試失敗的卷"""
    print("🔄 開始重試失敗的卷...")
    
    # 載入失敗的卷
    failed_volumes = load_failed_volumes()
    
    if not failed_volumes:
        print("✅ 沒有需要重試的卷")
        return
    
    print(f"📋 找到 {len(failed_volumes)} 個失敗的卷")
    
    # 按狀態分組
    captcha_volumes = [v for v in failed_volumes if v.get('status') == 'captcha']
    http_403_volumes = [v for v in failed_volumes if 'http_error_403' in v.get('status', '')]
    other_failed = [v for v in failed_volumes if v.get('status') not in ['captcha'] and 'http_error_403' not in v.get('status', '')]
    
    print(f"   - 驗證碼問題: {len(captcha_volumes)} 卷")
    print(f"   - 403錯誤: {len(http_403_volumes)} 卷")
    print(f"   - 其他錯誤: {len(other_failed)} 卷")
    
    # 創建改進的爬蟲實例
    crawler = ImprovedQuantangshiCrawler(
        config_file="improved_config.json",
        output_dir="quantangshi_volumes",
        delay=2.0
    )
    
    # 重試列表
    still_failed = []
    success_count = 0
    
    # 優先重試非驗證碼問題的卷
    retry_order = other_failed + http_403_volumes + captcha_volumes
    
    for i, volume_info in enumerate(retry_order, 1):
        volume_num = volume_info['volume']
        original_status = volume_info['status']
        
        print(f"\n🔄 重試第 {volume_num} 卷 ({i}/{len(retry_order)})")
        print(f"   原始狀態: {original_status}")
        
        # 檢查是否已經存在文件
        filename = f"全唐詩_第{volume_num:03d}卷.txt"
        filepath = os.path.join(crawler.output_dir, filename)
        
        if os.path.exists(filepath):
            print(f"   ⚠️  文件已存在，跳過")
            continue
        
        # 重試獲取
        poems, status = crawler.fetch_volume_with_retry(volume_num)
        
        if status == "success":
            print(f"   ✅ 重試成功！獲取到 {len(poems)} 首詩")
            crawler.save_volume_to_file(poems, volume_num)
            success_count += 1
        else:
            print(f"   ❌ 重試失敗: {status}")
            still_failed.append({
                'volume': volume_num,
                'status': status,
                'description': f"重試失敗: {status}",
                'original_status': original_status
            })
    
    # 保存仍然失敗的卷
    if still_failed:
        save_failed_volumes(still_failed, "still_failed_volumes.json")
        print(f"\n❌ 仍有 {len(still_failed)} 個卷失敗")
    else:
        print(f"\n🎉 所有重試的卷都成功了！")
    
    print(f"✅ 重試成功: {success_count} 卷")
    print(f"❌ 重試失敗: {len(still_failed)} 卷")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="重試失敗的卷")
    parser.add_argument("--file", type=str, default="failed_volumes.json", 
                       help="失敗卷列表文件")
    parser.add_argument("--config", type=str, default="improved_config.json",
                       help="爬蟲配置文件")
    
    args = parser.parse_args()
    
    # 檢查文件是否存在
    if not os.path.exists(args.file):
        print(f"❌ 文件 {args.file} 不存在")
        return
    
    retry_failed_volumes()

if __name__ == "__main__":
    main() 