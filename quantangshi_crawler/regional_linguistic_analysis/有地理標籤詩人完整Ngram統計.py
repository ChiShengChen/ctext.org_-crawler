#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有地理標籤詩人完整N-gram統計分析
生成詳細的統計報告
"""

import pandas as pd
import os
import re
import numpy as np
from datetime import datetime

def load_poet_data(poet_geo_path):
    """載入詩人地理標籤數據"""
    print("📚 載入詩人地理標籤數據...")
    poet_df = pd.read_csv(poet_geo_path)
    
    # 清理詩人姓名
    poet_df['poet_name'] = poet_df['詩人'].str.strip()
    # 移除序號和詩歌數量信息，只保留詩人姓名
    poet_df['poet_name'] = poet_df['poet_name'].str.replace(r'^\s*\d+\.\s*', '', regex=True)  # 移除序號
    poet_df['poet_name'] = poet_df['poet_name'].str.replace(r':\s*\d+.*$', '', regex=True)  # 移除詩歌數量
    poet_df['poet_name'] = poet_df['poet_name'].str.replace(r'[（(].*?[）)]', '', regex=True)  # 移除括號內容
    poet_df['poet_name'] = poet_df['poet_name'].str.strip()
    
    # 提取地域信息
    poet_df['region'] = poet_df['Geography'].str.strip()
    
    print(f"✅ 載入詩人數據: {len(poet_df)} 筆")
    print(f"✅ 唯一詩人: {poet_df['poet_name'].nunique()} 人")
    print(f"✅ 地域分布: {poet_df['region'].nunique()} 個地域")
    
    return poet_df

def load_ngram_data(ngram_dir):
    """載入N-gram數據"""
    print("\n📊 載入N-gram數據...")
    
    ngram_files = {
        '1gram': 'merged_1gram_詞頻統計.csv',
        '2gram': 'merged_2gram_詞頻統計.csv', 
        '4gram': 'merged_4gram_詞頻統計.csv'
    }
    
    ngram_data = {}
    for ngram_type, filename in ngram_files.items():
        file_path = os.path.join(ngram_dir, filename)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            ngram_data[ngram_type] = df
            print(f"✅ 載入 {ngram_type}: {len(df):,} 筆數據")
        else:
            print(f"❌ 未找到: {filename}")
    
    return ngram_data

def analyze_geo_poets_ngram():
    """分析有地理標籤詩人的N-gram統計"""
    print("🔍 開始分析有地理標籤詩人的N-gram統計...")
    
    # 文件路徑
    poet_geo_path = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    ngram_dir = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs'
    
    # 載入數據
    poet_data = load_poet_data(poet_geo_path)
    ngram_data = load_ngram_data(ngram_dir)
    
    # 匹配詩人
    geo_poets = set(poet_data['poet_name'].unique())
    ngram_poets = set(ngram_data['1gram']['詩人'].unique())
    matched_poets = geo_poets.intersection(ngram_poets)
    
    print(f"\n🎯 詩人匹配結果:")
    print(f"✅ 地理標籤詩人: {len(geo_poets):,} 人")
    print(f"✅ N-gram詩人: {len(ngram_poets):,} 人") 
    print(f"✅ 匹配詩人: {len(matched_poets):,} 人")
    print(f"✅ 匹配率: {len(matched_poets)/len(geo_poets)*100:.1f}%")
    
    # 分析各N-gram類型
    results = {}
    
    for ngram_type in ['1gram', '2gram', '4gram']:
        if ngram_type not in ngram_data:
            continue
            
        print(f"\n📈 分析 {ngram_type}...")
        
        # 篩選有地理標籤的詩人數據
        filtered_df = ngram_data[ngram_type][ngram_data[ngram_type]['詩人'].isin(matched_poets)]
        
        # 基本統計
        total_unique = filtered_df['字詞'].nunique()
        total_freq = filtered_df['詞頻'].sum()
        avg_freq = total_freq / total_unique if total_unique > 0 else 0
        
        # 詞頻分布
        freq_stats = filtered_df['詞頻'].describe()
        
        # 前100個高頻詞
        top_100 = filtered_df.nlargest(100, '詞頻')
        
        results[ngram_type] = {
            'total_unique': total_unique,
            'total_freq': total_freq,
            'avg_freq': avg_freq,
            'freq_stats': freq_stats,
            'top_100': top_100,
            'filtered_df': filtered_df
        }
        
        print(f"✅ {ngram_type} 統計完成")
        print(f"   - 總詞組數: {total_unique:,} 個")
        print(f"   - 總詞頻: {total_freq:,} 次")
        print(f"   - 平均詞頻: {avg_freq:.2f} 次")
    
    return results, matched_poets

def generate_detailed_report(results, matched_poets):
    """生成詳細報告"""
    print("\n📝 生成詳細報告...")
    
    # 生成各N-gram的詳細報告
    for ngram_type in ['1gram', '2gram', '4gram']:
        if ngram_type not in results:
            continue
            
        data = results[ngram_type]
        filename = f"有地理標籤詩人_{ngram_type}_完整統計報告.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 有地理標籤詩人 {ngram_type.upper()} 完整統計報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**分析對象**: {len(matched_poets):,} 位有地理標籤的詩人\n\n")
            
            # 基本統計
            f.write("## 📊 基本統計\n\n")
            f.write(f"- **總詞組數**: {data['total_unique']:,} 個\n")
            f.write(f"- **總詞頻**: {data['total_freq']:,} 次\n")
            f.write(f"- **平均詞頻**: {data['avg_freq']:.2f} 次\n")
            f.write(f"- **最高詞頻**: {data['freq_stats']['max']:.0f} 次\n")
            f.write(f"- **最低詞頻**: {data['freq_stats']['min']:.0f} 次\n\n")
            
            # 詞頻分布統計
            f.write("## 📈 詞頻分布統計\n\n")
            f.write(f"- **最小值**: {data['freq_stats']['min']:.0f}\n")
            f.write(f"- **25%分位數**: {data['freq_stats']['25%']:.2f}\n")
            f.write(f"- **中位數**: {data['freq_stats']['50%']:.2f}\n")
            f.write(f"- **75%分位數**: {data['freq_stats']['75%']:.2f}\n")
            f.write(f"- **最大值**: {data['freq_stats']['max']:.0f}\n")
            f.write(f"- **標準差**: {data['freq_stats']['std']:.2f}\n\n")
            
            # 前100個高頻詞
            f.write("## 🔤 前100個高頻詞組\n\n")
            for i, (_, row) in enumerate(data['top_100'].iterrows(), 1):
                f.write(f"  {i:2d}. **{row['字詞']}** - {row['詞頻']:,} 次\n")
            
            f.write(f"\n---\n")
            f.write(f"**數據來源**: 全唐詩N-gram分析結果\n")
            f.write(f"**分析方法**: 有地理標籤詩人完整統計\n")
        
        print(f"✅ 已生成: {filename}")
    
    # 生成總結報告
    summary_filename = "有地理標籤詩人_Ngram_完整統計總結.md"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("# 有地理標籤詩人 N-gram 完整統計總結報告\n\n")
        f.write(f"**生成時間**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"**分析對象**: {len(matched_poets):,} 位有地理標籤的詩人\n\n")
        
        f.write("## 📊 統計摘要\n\n")
        
        for ngram_type in ['1gram', '2gram', '4gram']:
            if ngram_type not in results:
                continue
                
            data = results[ngram_type]
            f.write(f"### {ngram_type.upper()}\n")
            f.write(f"- **總詞組數**: {data['total_unique']:,} 個\n")
            f.write(f"- **總詞頻**: {data['total_freq']:,} 次\n")
            f.write(f"- **平均詞頻**: {data['avg_freq']:.2f} 次\n\n")
        
        f.write("## 📁 生成的文件\n\n")
        for ngram_type in ['1gram', '2gram', '4gram']:
            if ngram_type in results:
                f.write(f"{len([f for f in [ngram_type] if f in results])}. **有地理標籤詩人_{ngram_type}_完整統計報告.md** - {ngram_type}完整統計\n")
        
        f.write(f"\n---\n\n")
        f.write(f"**生成時間**: {datetime.now().strftime('%Y年%m月%d日')}\n")
        f.write(f"**數據來源**: 全唐詩N-gram分析結果\n")
        f.write(f"**分析方法**: 有地理標籤詩人完整統計分析\n")
    
    print(f"✅ 已生成總結報告: {summary_filename}")

def main():
    """主函數"""
    print("🚀 開始有地理標籤詩人完整N-gram統計分析...")
    
    try:
        # 分析統計
        results, matched_poets = analyze_geo_poets_ngram()
        
        # 生成報告
        generate_detailed_report(results, matched_poets)
        
        print(f"\n🎉 分析完成！")
        print(f"📊 匹配詩人數量: {len(matched_poets):,} 人")
        
        for ngram_type in ['1gram', '2gram', '4gram']:
            if ngram_type in results:
                data = results[ngram_type]
                print(f"📈 {ngram_type}: {data['total_unique']:,} 個詞組, {data['total_freq']:,} 次詞頻")
        
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
