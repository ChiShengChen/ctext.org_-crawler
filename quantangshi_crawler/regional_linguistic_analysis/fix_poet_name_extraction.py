#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復詩人姓名提取問題
正確提取詩人姓名，確保與N-gram數據匹配
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

def load_all_female_poets_data_fixed():
    """使用修復的姓名提取函數載入所有女性詩人數據"""
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    
    if not os.path.exists(poet_geo_file):
        print(f"❌ 地理標籤文件不存在: {poet_geo_file}")
        return None
    
    df = pd.read_csv(poet_geo_file)
    print(f"✅ 載入地理標籤文件: {len(df)} 行")
    
    # 使用修復的姓名提取函數
    df['poet_name'] = df['詩人'].apply(extract_poet_name_fixed)
    
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

def test_fixed_name_extraction():
    """測試修復的姓名提取"""
    print("=" * 80)
    print("🔧 測試修復的姓名提取")
    print("=" * 80)
    
    # 測試用例
    test_cases = [
        "117. 薛濤: 77 首",
        "149. 魚玄機: 48 首", 
        "151. 武則天: 46 首",
        "262. 李冶: 18 首",
        "385. 上官昭容: 7 首",
        "419. 徐賢妃: 6 首",
        "2090. 花蕊夫人: 1 首",
        "2456. 楊貴妃: 1 首"
    ]
    
    print("📋 姓名提取測試:")
    for test_case in test_cases:
        extracted = extract_poet_name_fixed(test_case)
        print(f"原始: {test_case}")
        print(f"提取: {extracted}")
        print()

def analyze_fixed_matching():
    """分析修復後的匹配情況"""
    print("=" * 80)
    print("🔍 分析修復後的匹配情況")
    print("=" * 80)
    
    # 1. 載入修復後的女性詩人數據
    all_female_df = load_all_female_poets_data_fixed()
    if all_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 檢查匹配情況
    all_female_poet_names = set(all_female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_data['1gram']['詩人'].unique())
    
    matched_poets = all_female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = all_female_poet_names - ngram_poet_names
    
    print(f"\n📊 修復後的匹配分析:")
    print(f"    所有女性詩人: {len(all_female_poet_names)} 人")
    print(f"    N-gram詩人: {len(ngram_poet_names)} 人")
    print(f"    匹配詩人: {len(matched_poets)} 人")
    print(f"    不匹配詩人: {len(unmatched_poets)} 人")
    print(f"    匹配率: {len(matched_poets)/len(all_female_poet_names)*100:.1f}%")
    
    # 4. 檢查重要女性詩人是否匹配
    important_female_poets = ['薛濤', '魚玄機', '武則天', '李冶', '上官昭容', '徐賢妃', '花蕊夫人', '楊貴妃']
    
    print(f"\n📋 重要女性詩人匹配檢查:")
    for poet in important_female_poets:
        if poet in matched_poets:
            print(f"✅ {poet} - 匹配成功")
        else:
            print(f"❌ {poet} - 匹配失敗")
    
    # 5. 顯示不匹配的詩人
    if unmatched_poets:
        print(f"\n📋 仍然不匹配的女性詩人:")
        for poet in sorted(unmatched_poets):
            print(f"  - {poet}")
    
    return all_female_df, ngram_data, matched_poets

def main():
    """主函數"""
    # 測試修復的姓名提取
    test_fixed_name_extraction()
    
    # 分析修復後的匹配情況
    analyze_fixed_matching()

if __name__ == "__main__":
    main()
