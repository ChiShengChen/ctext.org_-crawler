#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詩人性別N-gram分析
分析不同性別詩人的用字習慣差異
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

def load_gender_data():
    """載入詩人性別數據"""
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
    
    # 清理性別標籤
    def clean_gender(gender_str):
        if pd.isna(gender_str):
            return 'Unknown'
        gender_str = str(gender_str).strip().lower()
        if 'male' in gender_str and 'female' not in gender_str:
            return 'Male'
        elif 'female' in gender_str:
            return 'Female'
        else:
            return 'Unknown'
    
    df['gender_clean'] = df['性別'].apply(clean_gender)
    
    print(f"✅ 提取詩人姓名: {df['poet_name'].nunique()} 個唯一詩人")
    print(f"✅ 性別分布:")
    gender_counts = df['gender_clean'].value_counts()
    for gender, count in gender_counts.items():
        print(f"    {gender}: {count} 人")
    
    return df[['poet_name', 'gender_clean']].dropna()

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

def analyze_gender_ngram():
    """分析性別N-gram統計"""
    print("=" * 80)
    print("🔍 詩人性別N-gram分析")
    print("=" * 80)
    
    # 1. 載入性別數據
    gender_df = load_gender_data()
    if gender_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 找到匹配的詩人
    gender_poet_names = set(gender_df['poet_name'].unique())
    
    print(f"\n📊 詩人匹配分析:")
    for ngram_type, df in ngram_data.items():
        ngram_poet_names = set(df['詩人'].unique())
        matched_poets = gender_poet_names.intersection(ngram_poet_names)
        
        print(f"  {ngram_type.upper()}:")
        print(f"    性別標籤詩人: {len(gender_poet_names):,} 人")
        print(f"    N-gram詩人: {len(ngram_poet_names):,} 人")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    匹配率: {len(matched_poets)/len(gender_poet_names)*100:.1f}%")
    
    # 4. 按性別分析N-gram數據
    print(f"\n" + "=" * 60)
    print("📈 按性別分析1-gram統計")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = gender_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併性別信息
        gender_merged = matched_df.merge(
            gender_df, 
            left_on='詩人', 
            right_on='poet_name', 
            how='left'
        )
        
        # 按性別分組統計
        gender_stats = {}
        for gender in ['Male', 'Female', 'Unknown']:
            gender_data = gender_merged[gender_merged['gender_clean'] == gender]
            if not gender_data.empty:
                unique_words = gender_data['字詞'].nunique()
                total_freq = gender_data['詞頻'].sum()
                avg_freq = total_freq / unique_words if unique_words > 0 else 0
                
                gender_stats[gender] = {
                    'poets': gender_data['詩人'].nunique(),
                    'unique_words': unique_words,
                    'total_freq': total_freq,
                    'avg_freq': avg_freq
                }
                
                print(f"\n✅ {gender} 詩人統計:")
                print(f"    詩人數量: {gender_data['詩人'].nunique():,} 人")
                print(f"    唯一詞彙: {unique_words:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前10個高頻字
                top_words = gender_data.nlargest(10, '詞頻')
                print(f"    前10個高頻字:")
                for i, (_, row) in enumerate(top_words.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    print(f"\n" + "=" * 60)
    print("📈 按性別分析2-gram統計")
    print("=" * 60)
    
    if '2gram' in ngram_data:
        df = ngram_data['2gram']
        matched_poets = gender_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併性別信息
        gender_merged = matched_df.merge(
            gender_df, 
            left_on='詩人', 
            right_on='poet_name', 
            how='left'
        )
        
        # 按性別分組統計
        for gender in ['Male', 'Female', 'Unknown']:
            gender_data = gender_merged[gender_merged['gender_clean'] == gender]
            if not gender_data.empty:
                unique_phrases = gender_data['字詞'].nunique()
                total_freq = gender_data['詞頻'].sum()
                avg_freq = total_freq / unique_phrases if unique_phrases > 0 else 0
                
                print(f"\n✅ {gender} 詩人2-gram統計:")
                print(f"    詩人數量: {gender_data['詩人'].nunique():,} 人")
                print(f"    唯一詞組: {unique_phrases:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前10個高頻詞組
                top_phrases = gender_data.nlargest(10, '詞頻')
                print(f"    前10個高頻2-gram:")
                for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    print(f"\n" + "=" * 60)
    print("📋 性別差異總結")
    print("=" * 60)
    
    # 生成性別差異報告
    print("✅ 性別N-gram分析完成！")
    print("✅ 可以分析不同性別詩人的用字習慣差異")
    print("✅ 為性別語言學研究提供數據支持")

def main():
    """主函數"""
    try:
        analyze_gender_ngram()
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
