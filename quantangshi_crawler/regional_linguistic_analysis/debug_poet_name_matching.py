#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試詩人姓名匹配問題
檢查為什麼重要的女性詩人沒有被匹配到
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

def debug_poet_name_matching():
    """調試詩人姓名匹配問題"""
    print("=" * 80)
    print("🔍 調試詩人姓名匹配問題")
    print("=" * 80)
    
    # 1. 載入所有女性詩人數據
    all_female_df = load_all_female_poets_data()
    if all_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 檢查重要女性詩人的姓名
    important_female_poets = ['薛濤', '魚玄機', '武則天', '李冶', '上官昭容', '徐賢妃', '花蕊夫人', '楊貴妃']
    
    print(f"\n📋 重要女性詩人姓名檢查:")
    print("=" * 60)
    
    for poet in important_female_poets:
        # 檢查在地理標籤數據中的姓名
        geo_match = all_female_df[all_female_df['poet_name'].str.contains(poet, case=False, na=False)]
        if not geo_match.empty:
            print(f"✅ {poet} 在地理標籤數據中:")
            for _, row in geo_match.iterrows():
                print(f"   原始姓名: {row['詩人']}")
                print(f"   提取姓名: {row['poet_name']}")
                print(f"   背景: {row['背景']}")
                print(f"   地域: {row['Geography']}")
        else:
            print(f"❌ {poet} 在地理標籤數據中未找到")
        
        # 檢查在N-gram數據中的姓名
        ngram_match = ngram_data['1gram'][ngram_data['1gram']['詩人'].str.contains(poet, case=False, na=False)]
        if not ngram_match.empty:
            print(f"✅ {poet} 在N-gram數據中:")
            unique_poets = ngram_match['詩人'].unique()
            for ngram_poet in unique_poets:
                print(f"   N-gram姓名: {ngram_poet}")
        else:
            print(f"❌ {poet} 在N-gram數據中未找到")
        
        print()
    
    # 4. 檢查姓名匹配問題
    print(f"\n🔍 姓名匹配問題分析:")
    print("=" * 60)
    
    all_female_poet_names = set(all_female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_data['1gram']['詩人'].unique())
    
    print(f"地理標籤數據中的女性詩人: {len(all_female_poet_names)} 人")
    print(f"N-gram數據中的詩人: {len(ngram_poet_names)} 人")
    
    # 找到匹配和不匹配的詩人
    matched_poets = all_female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = all_female_poet_names - ngram_poet_names
    
    print(f"匹配的詩人: {len(matched_poets)} 人")
    print(f"不匹配的詩人: {len(unmatched_poets)} 人")
    
    # 檢查不匹配的詩人
    print(f"\n📋 不匹配的女性詩人詳細分析:")
    for poet in sorted(unmatched_poets):
        # 檢查是否有類似的姓名在N-gram數據中
        similar_poets = [ngram_poet for ngram_poet in ngram_poet_names 
                        if poet in ngram_poet or ngram_poet in poet]
        
        print(f"❌ {poet}")
        if similar_poets:
            print(f"   可能的匹配: {similar_poets}")
        else:
            print(f"   沒有找到類似的姓名")
    
    # 5. 檢查N-gram數據中的女性詩人
    print(f"\n📋 N-gram數據中的女性詩人:")
    print("=" * 60)
    
    # 檢查N-gram數據中是否有女性詩人
    female_poets_in_ngram = []
    for poet in ngram_poet_names:
        # 檢查這個詩人是否在女性詩人名單中
        if any(female_poet in poet for female_poet in important_female_poets):
            female_poets_in_ngram.append(poet)
    
    print(f"N-gram數據中的女性詩人: {len(female_poets_in_ngram)} 人")
    for poet in female_poets_in_ngram:
        print(f"  - {poet}")

def main():
    """主函數"""
    debug_poet_name_matching()

if __name__ == "__main__":
    main()
