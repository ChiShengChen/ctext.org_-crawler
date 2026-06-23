#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查沒有N-gram數據的女性詩人
分析為什麼有些女性詩人沒有N-gram數據
"""

import pandas as pd
import os
import re

def load_all_female_poets_data():
    """載入所有女性詩人數據"""
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    
    if not os.path.exists(poet_geo_file):
        print(f"❌ 地理標籤文件不存在: {poet_geo_file}")
        return None
    
    df = pd.read_csv(poet_geo_file)
    print(f"✅ 載入地理標籤文件: {len(df)} 行")
    
    # 清理和提取詩人姓名
    def extract_poet_name(name_str):
        name_match = re.search(r'(\d+\.\s*)?([^:：]+)', str(name_str))
        if name_match:
            return name_match.group(2).strip()
        return str(name_str)
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 篩選所有女性詩人
    all_female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    print(f"✅ 所有女性詩人總數: {len(all_female_df)} 人")
    
    return all_female_df

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
        else:
            print(f"❌ 文件不存在: {filename}")
    
    return ngram_data

def check_poems_count():
    """檢查女性詩人的作品數量"""
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    
    df = pd.read_csv(poet_geo_file)
    
    # 清理和提取詩人姓名和作品數量
    def extract_poet_info(name_str):
        # 提取詩人姓名
        name_match = re.search(r'(\d+\.\s*)?([^:：]+)', str(name_str))
        if name_match:
            poet_name = name_match.group(2).strip()
        else:
            poet_name = str(name_str)
        
        # 提取作品數量
        poem_count_match = re.search(r'(\d+(?:,\d+)*)\s*首', str(name_str))
        if poem_count_match:
            poem_count = int(poem_count_match.group(1).replace(',', ''))
        else:
            poem_count = 0
        
        return poet_name, poem_count
    
    df[['poet_name', 'poem_count']] = df['詩人'].apply(lambda x: pd.Series(extract_poet_info(x)))
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    
    return female_df

def analyze_female_poets_without_ngram():
    """分析沒有N-gram數據的女性詩人"""
    print("=" * 80)
    print("🔍 檢查沒有N-gram數據的女性詩人")
    print("=" * 80)
    
    # 1. 載入所有女性詩人數據
    all_female_df = load_all_female_poets_data()
    if all_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 載入作品數量數據
    female_with_poems = check_poems_count()
    
    # 4. 找到匹配的女性詩人
    all_female_poet_names = set(all_female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_data['1gram']['詩人'].unique()) if '1gram' in ngram_data else set()
    matched_poets = all_female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = all_female_poet_names - ngram_poet_names
    
    print(f"\n📊 女性詩人匹配分析:")
    print(f"    所有女性詩人: {len(all_female_poet_names):,} 人")
    print(f"    有N-gram數據: {len(matched_poets):,} 人")
    print(f"    沒有N-gram數據: {len(unmatched_poets):,} 人")
    print(f"    匹配率: {len(matched_poets)/len(all_female_poet_names)*100:.1f}%")
    
    # 5. 分析沒有N-gram數據的女性詩人
    print(f"\n📋 沒有N-gram數據的女性詩人詳細分析:")
    print("=" * 60)
    
    unmatched_female = all_female_df[all_female_df['poet_name'].isin(unmatched_poets)]
    
    # 合併作品數量信息
    unmatched_with_poems = unmatched_female.merge(
        female_with_poems[['poet_name', 'poem_count']], 
        on='poet_name', 
        how='left'
    )
    
    # 按作品數量分組統計
    poem_count_stats = unmatched_with_poems['poem_count'].value_counts().sort_index()
    print(f"\n📊 沒有N-gram數據的女性詩人作品數量分布:")
    for count, num_poets in poem_count_stats.items():
        print(f"    {count} 首詩: {num_poets} 人")
    
    # 顯示沒有N-gram數據的女性詩人詳細信息
    print(f"\n📋 沒有N-gram數據的女性詩人名單:")
    for i, (_, row) in enumerate(unmatched_with_poems.iterrows(), 1):
        print(f"{i:2d}. **{row['poet_name']}**")
        print(f"    作品數量: {row['poem_count']} 首")
        if pd.notna(row['背景']):
            print(f"    背景: {row['背景']}")
        if pd.notna(row['Geography']):
            print(f"    地域: {row['Geography']}")
        print()
    
    # 6. 分析可能的原因
    print(f"\n🔍 沒有N-gram數據的可能原因分析:")
    print("=" * 60)
    
    # 統計不同作品數量的詩人
    zero_poems = len(unmatched_with_poems[unmatched_with_poems['poem_count'] == 0])
    one_poem = len(unmatched_with_poems[unmatched_with_poems['poem_count'] == 1])
    few_poems = len(unmatched_with_poems[unmatched_with_poems['poem_count'] <= 3])
    many_poems = len(unmatched_with_poems[unmatched_with_poems['poem_count'] > 3])
    
    print(f"1. **沒有作品 (0首)**: {zero_poems} 人")
    print(f"2. **只有1首詩**: {one_poem} 人")
    print(f"3. **作品很少 (≤3首)**: {few_poems} 人")
    print(f"4. **作品較多 (>3首)**: {many_poems} 人")
    
    # 檢查是否有作品但沒有N-gram數據的詩人
    has_poems_no_ngram = unmatched_with_poems[unmatched_with_poems['poem_count'] > 0]
    print(f"\n📊 有作品但沒有N-gram數據的女性詩人: {len(has_poems_no_ngram)} 人")
    
    if len(has_poems_no_ngram) > 0:
        print(f"\n📋 有作品但沒有N-gram數據的女性詩人名單:")
        for i, (_, row) in enumerate(has_poems_no_ngram.iterrows(), 1):
            print(f"{i:2d}. **{row['poet_name']}** - {row['poem_count']} 首詩")
    
    return unmatched_with_poems

def main():
    """主函數"""
    analyze_female_poets_without_ngram()

if __name__ == "__main__":
    main()
