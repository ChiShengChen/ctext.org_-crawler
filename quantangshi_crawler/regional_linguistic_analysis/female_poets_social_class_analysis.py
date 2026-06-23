#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
女性詩人社會階級分析
分析不同社會階級女性詩人的用字習慣差異
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

def load_female_poets_data():
    """載入女性詩人數據並分類社會階級"""
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
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    print(f"✅ 女性詩人總數: {len(female_df)} 人")
    
    # 分類社會階級
    def classify_social_class(background_str):
        if pd.isna(background_str):
            return 'Unknown'
        
        background_str = str(background_str).lower()
        
        # 皇室階級
        if any(keyword in background_str for keyword in ['empress', '皇后', 'imperial consort', '后妃', '妃嬪']):
            return 'Royal'
        
        # 貴族/官員階級
        elif any(keyword in background_str for keyword in ['civil office', '為官者', 'office', '宰相']):
            return 'Noble/Official'
        
        # 文人階級
        elif any(keyword in background_str for keyword in ['man of culture', '文人', 'calligrapher', '書法家']):
            return 'Literati'
        
        # 宗教階級
        elif any(keyword in background_str for keyword in ['daoist nun', '道姑', '女冠', '僧', 'monk']):
            return 'Religious'
        
        # 娛樂階級
        elif any(keyword in background_str for keyword in ['entertainer', '妓', 'female entertainer']):
            return 'Entertainer'
        
        # 一般詩人
        elif 'poet' in background_str or '詩人' in background_str:
            return 'General Poet'
        
        # 其他
        else:
            return 'Other'
    
    female_df['social_class'] = female_df['背景'].apply(classify_social_class)
    
    print(f"✅ 女性詩人社會階級分布:")
    class_counts = female_df['social_class'].value_counts()
    for social_class, count in class_counts.items():
        print(f"    {social_class}: {count} 人")
    
    return female_df[['poet_name', 'social_class', '背景']].dropna()

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
        else:
            print(f"❌ 文件不存在: {filename}")
    
    return ngram_data

def analyze_female_poets_by_social_class():
    """按社會階級分析女性詩人"""
    print("=" * 80)
    print("🔍 女性詩人社會階級N-gram分析")
    print("=" * 80)
    
    # 1. 載入女性詩人數據
    female_df = load_female_poets_data()
    if female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 找到匹配的女性詩人
    female_poet_names = set(female_df['poet_name'].unique())
    
    print(f"\n📊 女性詩人匹配分析:")
    for ngram_type, df in ngram_data.items():
        ngram_poet_names = set(df['詩人'].unique())
        matched_poets = female_poet_names.intersection(ngram_poet_names)
        
        print(f"  {ngram_type.upper()}:")
        print(f"    女性詩人: {len(female_poet_names):,} 人")
        print(f"    N-gram詩人: {len(ngram_poet_names):,} 人")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    匹配率: {len(matched_poets)/len(female_poet_names)*100:.1f}%")
    
    # 4. 按社會階級分析1-gram
    print(f"\n" + "=" * 60)
    print("📈 按社會階級分析女性詩人1-gram")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            female_df, 
            left_on='詩人', 
            right_on='poet_name', 
            how='left'
        )
        
        # 按社會階級分組統計
        for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
            class_data = class_merged[class_merged['social_class'] == social_class]
            if not class_data.empty:
                unique_words = class_data['字詞'].nunique()
                total_freq = class_data['詞頻'].sum()
                avg_freq = total_freq / unique_words if unique_words > 0 else 0
                
                print(f"\n✅ {social_class} 女性詩人統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人")
                print(f"    唯一詞彙: {unique_words:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前15個高頻字
                top_words = class_data.nlargest(15, '詞頻')
                print(f"    前15個高頻字:")
                for i, (_, row) in enumerate(top_words.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
                
                # 顯示背景信息
                backgrounds = class_data['背景'].unique()
                print(f"    背景標籤: {', '.join(backgrounds[:3])}{'...' if len(backgrounds) > 3 else ''}")
    
    # 5. 按社會階級分析2-gram
    print(f"\n" + "=" * 60)
    print("📈 按社會階級分析女性詩人2-gram")
    print("=" * 60)
    
    if '2gram' in ngram_data:
        df = ngram_data['2gram']
        matched_poets = female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            female_df, 
            left_on='詩人', 
            right_on='poet_name', 
            how='left'
        )
        
        # 按社會階級分組統計
        for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
            class_data = class_merged[class_merged['social_class'] == social_class]
            if not class_data.empty:
                unique_phrases = class_data['字詞'].nunique()
                total_freq = class_data['詞頻'].sum()
                avg_freq = total_freq / unique_phrases if unique_phrases > 0 else 0
                
                print(f"\n✅ {social_class} 女性詩人2-gram統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人")
                print(f"    唯一詞組: {unique_phrases:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前10個高頻詞組
                top_phrases = class_data.nlargest(10, '詞頻')
                print(f"    前10個高頻2-gram:")
                for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    # 6. 社會階級差異分析
    print(f"\n" + "=" * 60)
    print("📋 社會階級差異分析")
    print("=" * 60)
    
    # 生成社會階級差異報告
    print("✅ 女性詩人社會階級N-gram分析完成！")
    print("✅ 可以分析不同社會階級女性詩人的用字習慣差異")
    print("✅ 為女性文學史和社會階級研究提供數據支持")
    
    # 顯示各階級的特徵詞彙
    print(f"\n🎯 各社會階級特徵詞彙分析:")
    print("  - Royal: 皇室用詞，可能偏向宮廷、政治")
    print("  - Noble/Official: 貴族官員用詞，可能偏向正式、文雅")
    print("  - Literati: 文人用詞，可能偏向文學、藝術")
    print("  - Religious: 宗教用詞，可能偏向宗教、修行")
    print("  - Entertainer: 娛樂用詞，可能偏向情感、表演")
    print("  - General Poet: 一般詩人用詞，可能偏向日常、自然")

def main():
    """主函數"""
    try:
        analyze_female_poets_by_social_class()
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
