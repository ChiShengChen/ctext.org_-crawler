#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細的姓名匹配調試
檢查具體的匹配問題
"""

import pandas as pd
import os
import re

def extract_poet_name_fixed(name_str):
    """修復的詩人姓名提取函數"""
    name_str = str(name_str)
    
    # 處理包含編號的格式：如 "117. 薛濤: 77 首"
    # 先去除作品數量部分
    name_str = re.sub(r':\s*\d+\s*首.*$', '', name_str)
    
    # 提取姓名部分，去除編號
    name_match = re.search(r'(\d+\.\s*)?(.+)', name_str)
    if name_match:
        return name_match.group(2).strip()
    
    return name_str.strip()

def detailed_name_matching_debug():
    """詳細的姓名匹配調試"""
    print("=" * 80)
    print("🔍 詳細的姓名匹配調試")
    print("=" * 80)
    
    # 1. 載入地理標籤數據
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    df = pd.read_csv(poet_geo_file)
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    print(f"✅ 女性詩人總數: {len(female_df)} 人")
    
    # 2. 載入N-gram數據
    ngram_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv'
    ngram_df = pd.read_csv(ngram_file)
    print(f"✅ N-gram數據總行數: {len(ngram_df)}")
    
    # 3. 檢查重要女性詩人的具體情況
    important_poets = ['薛濤', '魚玄機', '武則天', '李冶', '上官昭容', '徐賢妃']
    
    print(f"\n📋 重要女性詩人詳細檢查:")
    print("=" * 60)
    
    for poet in important_poets:
        print(f"\n🔍 檢查 {poet}:")
        
        # 檢查在地理標籤數據中的情況
        geo_matches = female_df[female_df['詩人'].str.contains(poet, case=False, na=False)]
        if not geo_matches.empty:
            print(f"  地理標籤數據中找到 {len(geo_matches)} 條記錄:")
            for _, row in geo_matches.iterrows():
                original_name = row['詩人']
                extracted_name = extract_poet_name_fixed(original_name)
                print(f"    原始: {original_name}")
                print(f"    提取: {extracted_name}")
        else:
            print(f"  地理標籤數據中未找到")
        
        # 檢查在N-gram數據中的情況
        ngram_matches = ngram_df[ngram_df['詩人'] == poet]
        if not ngram_matches.empty:
            print(f"  N-gram數據中找到 {len(ngram_matches)} 條記錄")
            print(f"    詩人姓名: {ngram_matches['詩人'].iloc[0]}")
            print(f"    詞頻總數: {ngram_matches['詞頻'].sum()}")
        else:
            print(f"  N-gram數據中未找到")
        
        # 檢查匹配情況
        if not geo_matches.empty and not ngram_matches.empty:
            extracted_names = geo_matches['詩人'].apply(extract_poet_name_fixed)
            if poet in extracted_names.values:
                print(f"  ✅ 匹配成功")
            else:
                print(f"  ❌ 匹配失敗")
                print(f"    提取的姓名: {extracted_names.unique()}")
        else:
            print(f"  ❌ 數據不完整")
    
    # 4. 檢查所有女性詩人的匹配情況
    print(f"\n📊 所有女性詩人匹配統計:")
    print("=" * 60)
    
    # 提取所有女性詩人姓名
    female_df['extracted_name'] = female_df['詩人'].apply(extract_poet_name_fixed)
    female_poet_names = set(female_df['extracted_name'].unique())
    ngram_poet_names = set(ngram_df['詩人'].unique())
    
    matched_poets = female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = female_poet_names - ngram_poet_names
    
    print(f"女性詩人總數: {len(female_poet_names)}")
    print(f"N-gram詩人總數: {len(ngram_poet_names)}")
    print(f"匹配成功: {len(matched_poets)}")
    print(f"匹配失敗: {len(unmatched_poets)}")
    print(f"匹配率: {len(matched_poets)/len(female_poet_names)*100:.1f}%")
    
    # 5. 顯示匹配成功的詩人
    print(f"\n✅ 匹配成功的女性詩人:")
    for poet in sorted(matched_poets):
        print(f"  - {poet}")
    
    # 6. 顯示匹配失敗的詩人
    print(f"\n❌ 匹配失敗的女性詩人:")
    for poet in sorted(unmatched_poets):
        print(f"  - {poet}")
    
    # 7. 檢查是否有類似的姓名
    print(f"\n🔍 匹配失敗詩人的類似姓名檢查:")
    for poet in sorted(unmatched_poets):
        similar_poets = [ngram_poet for ngram_poet in ngram_poet_names 
                        if poet in ngram_poet or ngram_poet in poet]
        if similar_poets:
            print(f"  {poet}: {similar_poets}")
        else:
            print(f"  {poet}: 無類似姓名")

def main():
    """主函數"""
    detailed_name_matching_debug()

if __name__ == "__main__":
    main()
