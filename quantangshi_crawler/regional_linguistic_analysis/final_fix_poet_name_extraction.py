#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終修復詩人姓名提取問題
正確提取詩人姓名，確保與N-gram數據匹配
"""

import pandas as pd
import os
import re

def extract_poet_name_final(name_str):
    """最終修復的詩人姓名提取函數"""
    name_str = str(name_str)
    
    # 處理包含編號的格式：如 "117. 薛濤: 77 首"
    # 先去除作品數量部分
    name_str = re.sub(r':\s*\d+\s*首.*$', '', name_str)
    
    # 提取姓名部分，去除編號
    # 匹配模式：可選的編號 + 空格 + 姓名
    name_match = re.search(r'(\d+\.\s*)?(.+)', name_str)
    if name_match:
        # 返回第二個捕獲組（姓名部分），去除前後空格
        return name_match.group(2).strip()
    
    return name_str.strip()

def test_name_extraction():
    """測試姓名提取函數"""
    print("=" * 80)
    print("🔧 測試最終修復的姓名提取函數")
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
        "2456. 楊貴妃: 1 首",
        "279. 徐氏: 15 首",
        "424. 郎大家宋氏: 6 首"
    ]
    
    print("📋 姓名提取測試:")
    for test_case in test_cases:
        extracted = extract_poet_name_final(test_case)
        print(f"原始: {test_case}")
        print(f"提取: {extracted}")
        print()

def create_corrected_female_poets_analysis():
    """創建修正後的女性詩人分析"""
    print("=" * 80)
    print("🔍 創建修正後的女性詩人分析")
    print("=" * 80)
    
    # 1. 載入地理標籤數據
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    df = pd.read_csv(poet_geo_file)
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)].copy()
    print(f"✅ 女性詩人總數: {len(female_df)} 人")
    
    # 使用修正的姓名提取函數
    female_df['poet_name'] = female_df['詩人'].apply(extract_poet_name_final)
    
    # 2. 載入N-gram數據
    ngram_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv'
    ngram_df = pd.read_csv(ngram_file)
    print(f"✅ N-gram數據總行數: {len(ngram_df)}")
    
    # 3. 檢查匹配情況
    female_poet_names = set(female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_df['詩人'].unique())
    
    matched_poets = female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = female_poet_names - ngram_poet_names
    
    print(f"\n📊 修正後的匹配分析:")
    print(f"    女性詩人總數: {len(female_poet_names)} 人")
    print(f"    N-gram詩人總數: {len(ngram_poet_names)} 人")
    print(f"    匹配成功: {len(matched_poets)} 人")
    print(f"    匹配失敗: {len(unmatched_poets)} 人")
    print(f"    匹配率: {len(matched_poets)/len(female_poet_names)*100:.1f}%")
    
    # 4. 檢查重要女性詩人
    important_poets = ['薛濤', '魚玄機', '武則天', '李冶', '上官昭容', '徐賢妃', '花蕊夫人', '楊貴妃']
    
    print(f"\n📋 重要女性詩人匹配檢查:")
    for poet in important_poets:
        if poet in matched_poets:
            print(f"✅ {poet} - 匹配成功")
        else:
            print(f"❌ {poet} - 匹配失敗")
    
    # 5. 顯示匹配成功的詩人
    print(f"\n✅ 匹配成功的女性詩人 ({len(matched_poets)} 人):")
    for poet in sorted(matched_poets):
        print(f"  - {poet}")
    
    # 6. 顯示匹配失敗的詩人
    if unmatched_poets:
        print(f"\n❌ 匹配失敗的女性詩人 ({len(unmatched_poets)} 人):")
        for poet in sorted(unmatched_poets):
            print(f"  - {poet}")
    
    return female_df, ngram_df, matched_poets

def generate_corrected_combined_analysis():
    """生成修正後的合併分析"""
    print("=" * 80)
    print("📝 生成修正後的合併分析")
    print("=" * 80)
    
    # 1. 載入修正後的數據
    female_df, ngram_df, matched_poets = create_corrected_female_poets_analysis()
    
    # 2. 載入所有N-gram數據
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
            ngram_data[ngram_type] = pd.read_csv(file_path)
            print(f"✅ 載入 {ngram_type} 數據")
    
    # 3. 生成修正後的合併N-gram分析
    print(f"\n📈 修正後的合併N-gram分析:")
    print("=" * 60)
    
    for ngram_type, df in ngram_data.items():
        # 篩選匹配的女性詩人數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併所有女性詩人的詞頻
        combined_freq = matched_df.groupby('字詞')['詞頻'].sum().reset_index()
        combined_freq = combined_freq.sort_values('詞頻', ascending=False)
        
        unique_words = len(combined_freq)
        total_freq = combined_freq['詞頻'].sum()
        avg_freq = total_freq / unique_words if unique_words > 0 else 0
        
        print(f"\n✅ {ngram_type.upper()} 修正後統計:")
        print(f"    匹配詩人: {len(matched_poets)} 人")
        print(f"    唯一詞彙: {unique_words:,} 個")
        print(f"    總詞頻: {total_freq:,} 次")
        print(f"    平均詞頻: {avg_freq:.2f} 次")
        
        # 前20個高頻詞彙
        top_words = combined_freq.head(20)
        print(f"    前20個高頻{ngram_type}:")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")

def main():
    """主函數"""
    # 測試姓名提取函數
    test_name_extraction()
    
    # 生成修正後的合併分析
    generate_corrected_combined_analysis()

if __name__ == "__main__":
    main()
