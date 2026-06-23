#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修復詩人姓名匹配問題
使用最簡單直接的方法解決匹配問題
"""

import pandas as pd
import os
import re

def extract_poet_name_simple(name_str):
    """最簡單的詩人姓名提取函數"""
    name_str = str(name_str)
    
    # 直接去除編號和作品數量
    # 匹配模式：數字. 姓名: 數量首
    match = re.search(r'\d+\.\s*([^:：]+)', name_str)
    if match:
        return match.group(1).strip()
    
    return name_str.strip()

def create_final_corrected_analysis():
    """創建最終修正的分析"""
    print("=" * 80)
    print("🔧 最終修正的女性詩人N-gram分析")
    print("=" * 80)
    
    # 1. 載入地理標籤數據
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    df = pd.read_csv(poet_geo_file)
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)].copy()
    print(f"✅ 女性詩人總數: {len(female_df)} 人")
    
    # 使用最簡單的姓名提取函數
    female_df['poet_name'] = female_df['詩人'].apply(extract_poet_name_simple)
    
    # 2. 載入N-gram數據
    ngram_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv'
    ngram_df = pd.read_csv(ngram_file)
    print(f"✅ N-gram數據總行數: {len(ngram_df)}")
    
    # 3. 檢查匹配情況
    female_poet_names = set(female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_df['詩人'].unique())
    
    matched_poets = female_poet_names.intersection(ngram_poet_names)
    unmatched_poets = female_poet_names - ngram_poet_names
    
    print(f"\n📊 最終匹配分析:")
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
    
    # 7. 生成修正後的合併N-gram分析
    print(f"\n📈 修正後的合併N-gram分析:")
    print("=" * 60)
    
    # 載入所有N-gram數據
    ngram_dir = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs'
    ngram_files = {
        '1gram': 'merged_1gram_詞頻統計.csv',
        '2gram': 'merged_2gram_詞頻統計.csv',
        '4gram': 'merged_4gram_詞頻統計.csv'
    }
    
    for ngram_type, filename in ngram_files.items():
        file_path = os.path.join(ngram_dir, filename)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
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
    
    return female_df, matched_poets

def main():
    """主函數"""
    create_final_corrected_analysis()

if __name__ == "__main__":
    main()
