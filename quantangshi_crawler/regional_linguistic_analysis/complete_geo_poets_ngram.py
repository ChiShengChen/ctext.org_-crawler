#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有地理標籤詩人的完整N-gram統計
統計1,461位有地理標籤詩人的全部詩歌的完整N-gram數據
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

def load_geo_poets_data():
    """載入有地理標籤的詩人數據"""
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    
    if not os.path.exists(poet_geo_file):
        print(f"❌ 地理標籤文件不存在: {poet_geo_file}")
        return None
    
    df = pd.read_csv(poet_geo_file)
    print(f"✅ 載入地理標籤文件: {len(df)} 行")
    
    # 清理和提取詩人姓名
    def extract_poet_name(name_str):
        import re
        name_match = re.search(r'(\d+\.\s*)?([^:：]+)', str(name_str))
        if name_match:
            return name_match.group(2).strip()
        return str(name_str)
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 提取地域
    def extract_region(geo_str):
        if pd.isna(geo_str):
            return 'Unknown'
        geo_str = str(geo_str)
        if '關內道' in geo_str:
            return 'Guannei Dao'
        elif '江南道' in geo_str:
            return 'Jiangnan Dao'
        elif '河北道' in geo_str:
            return 'Hebei Dao'
        elif '河南道' in geo_str:
            return 'Henan Dao'
        elif '河東道' in geo_str:
            return 'Hedong Dao'
        elif '山南道' in geo_str:
            return 'Shannan Dao'
        elif '劍南道' in geo_str:
            return 'Jiannan Dao'
        elif '淮南道' in geo_str:
            return 'Huainan Dao'
        elif '隴右道' in geo_str:
            return 'Longyou Dao'
        elif '嶺南道' in geo_str:
            return 'Lingnan Dao'
        else:
            return 'Other'
    
    df['region'] = df['Geography'].apply(extract_region)
    
    print(f"✅ 提取詩人姓名: {df['poet_name'].nunique()} 個唯一詩人")
    print(f"✅ 地域分布: {df['region'].value_counts().to_dict()}")
    
    return df[['poet_name', 'region']].dropna()

def load_ngram_data():
    """載入N-gram數據"""
    ngram_dir = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs'
    
    ngram_files = {
        '1gram': 'merged_1gram_詞頻統計.csv',
        '2gram': 'merged_2gram_詞頻統計.csv',
        '4gram': 'merged_4gram_詞頻統計.csv'
    }
    
    ngram_data = {}
    
    for ngram_type, filename in ngram_files.items():
        file_path = os.path.join(ngram_dir, filename)
        if os.path.exists(file_path):
            print(f"✅ 載入 {ngram_type} 數據: {filename}")
            df = pd.read_csv(file_path)
            ngram_data[ngram_type] = df
            print(f"   - 總行數: {len(df):,}")
            print(f"   - 唯一詩人: {df['詩人'].nunique():,}")
            print(f"   - 唯一詞組: {df['字詞'].nunique():,}")
        else:
            print(f"❌ 文件不存在: {filename}")
    
    return ngram_data

def analyze_geo_poets_complete_ngram():
    """分析有地理標籤詩人的完整N-gram統計"""
    print("=" * 80)
    print("🔍 有地理標籤詩人的完整N-gram統計分析")
    print("=" * 80)
    
    # 1. 載入地理標籤詩人數據
    geo_poets_df = load_geo_poets_data()
    if geo_poets_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 找到匹配的詩人
    geo_poet_names = set(geo_poets_df['poet_name'].unique())
    
    print(f"\n📊 詩人匹配分析:")
    for ngram_type, df in ngram_data.items():
        ngram_poet_names = set(df['詩人'].unique())
        matched_poets = geo_poet_names.intersection(ngram_poet_names)
        
        print(f"  {ngram_type.upper()}:")
        print(f"    地理標籤詩人: {len(geo_poet_names):,} 人")
        print(f"    N-gram詩人: {len(ngram_poet_names):,} 人")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    匹配率: {len(matched_poets)/len(geo_poet_names)*100:.1f}%")
    
    # 4. 統計匹配詩人的完整N-gram數據
    print(f"\n" + "=" * 60)
    print("📈 匹配詩人的完整1-gram統計")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = geo_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        print(f"✅ 匹配詩人數量: {len(matched_poets):,} 人")
        print(f"✅ 數據行數: {len(matched_df):,} 行")
        print(f"✅ 唯一詞彙數: {matched_df['字詞'].nunique():,} 個")
        print(f"✅ 總詞頻: {matched_df['詞頻'].sum():,} 次")
        print(f"✅ 平均詞頻: {matched_df['詞頻'].sum() / matched_df['字詞'].nunique():.2f} 次")
        
        # 前20個高頻字
        top_words = matched_df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻1-gram:")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
        
        # 詞頻分布
        freq_stats = matched_df['詞頻'].describe()
        print(f"\n📊 詞頻分布統計:")
        print(f"  最小值: {freq_stats['min']:.0f}")
        print(f"  25%分位數: {freq_stats['25%']:.0f}")
        print(f"  中位數: {freq_stats['50%']:.0f}")
        print(f"  75%分位數: {freq_stats['75%']:.0f}")
        print(f"  最大值: {freq_stats['max']:.0f}")
        print(f"  標準差: {freq_stats['std']:.2f}")
    
    print(f"\n" + "=" * 60)
    print("📈 匹配詩人的完整2-gram統計")
    print("=" * 60)
    
    if '2gram' in ngram_data:
        df = ngram_data['2gram']
        matched_poets = geo_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        print(f"✅ 匹配詩人數量: {len(matched_poets):,} 人")
        print(f"✅ 數據行數: {len(matched_df):,} 行")
        print(f"✅ 唯一詞組數: {matched_df['字詞'].nunique():,} 個")
        print(f"✅ 總詞頻: {matched_df['詞頻'].sum():,} 次")
        print(f"✅ 平均詞頻: {matched_df['詞頻'].sum() / matched_df['字詞'].nunique():.2f} 次")
        
        # 前20個高頻詞組
        top_phrases = matched_df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻2-gram:")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    print(f"\n" + "=" * 60)
    print("📈 匹配詩人的完整4-gram統計")
    print("=" * 60)
    
    if '4gram' in ngram_data:
        df = ngram_data['4gram']
        matched_poets = geo_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        print(f"✅ 匹配詩人數量: {len(matched_poets):,} 人")
        print(f"✅ 數據行數: {len(matched_df):,} 行")
        print(f"✅ 唯一詞組數: {matched_df['字詞'].nunique():,} 個")
        print(f"✅ 總詞頻: {matched_df['詞頻'].sum():,} 次")
        print(f"✅ 平均詞頻: {matched_df['詞頻'].sum() / matched_df['字詞'].nunique():.2f} 次")
        
        # 前20個高頻詞組
        top_phrases = matched_df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻4-gram:")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    print(f"\n" + "=" * 60)
    print("📋 完整統計總結")
    print("=" * 60)
    
    # 生成完整統計報告
    complete_stats = {}
    
    for ngram_type in ['1gram', '2gram', '4gram']:
        if ngram_type in ngram_data:
            df = ngram_data[ngram_type]
            matched_poets = geo_poet_names.intersection(set(df['詩人'].unique()))
            matched_df = df[df['詩人'].isin(matched_poets)]
            
            complete_stats[ngram_type] = {
                'matched_poets': len(matched_poets),
                'total_unique': matched_df['字詞'].nunique(),
                'total_frequency': matched_df['詞頻'].sum(),
                'avg_frequency': matched_df['詞頻'].sum() / matched_df['字詞'].nunique(),
                'max_frequency': matched_df['詞頻'].max(),
                'min_frequency': matched_df['詞頻'].min()
            }
    
    print("✅ 有地理標籤詩人的完整N-gram統計:")
    for ngram_type, stats in complete_stats.items():
        print(f"  {ngram_type.upper()}:")
        print(f"    匹配詩人: {stats['matched_poets']:,} 人")
        print(f"    總詞組數: {stats['total_unique']:,} 個")
        print(f"    總詞頻: {stats['total_frequency']:,} 次")
        print(f"    平均詞頻: {stats['avg_frequency']:.2f} 次")
        print(f"    最高詞頻: {stats['max_frequency']:,} 次")
        print(f"    最低詞頻: {stats['min_frequency']:,} 次")
        print()
    
    print("🎯 重要發現:")
    print("  - 這是有地理標籤詩人的完整統計")
    print("  - 包含所有詞彙，不只是前50個")
    print("  - 反映有地理標籤詩人的真實用字情況")

def main():
    """主函數"""
    try:
        analyze_geo_poets_complete_ngram()
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
