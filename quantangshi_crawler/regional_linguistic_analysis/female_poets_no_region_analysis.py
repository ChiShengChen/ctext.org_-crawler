#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沒有地域標籤的女性詩人詞頻分析
分析沒有地理標籤的女性詩人的用字習慣
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np
import re

def load_female_poets_no_region_data():
    """載入沒有地域標籤的女性詩人數據"""
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
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    print(f"✅ 女性詩人總數: {len(female_df)} 人")
    
    # 篩選沒有地域標籤的女性詩人
    no_region_female = female_df[
        (female_df['Geography'].isna()) | 
        (female_df['Geography'] == '') |
        (female_df['Geography'].str.contains('Unknown', case=False, na=True))
    ]
    
    print(f"✅ 沒有地域標籤的女性詩人: {len(no_region_female)} 人")
    
    # 分類社會階級
    def classify_social_class(background_str):
        if pd.isna(background_str):
            return 'Unknown'
        
        background_str = str(background_str).lower()
        
        # 皇室階級
        if any(keyword in background_str for keyword in ['empress', '皇后', 'imperial consort', '后妃', '妃嬪']):
            return 'Royal'
        
        # 貴族/官員階級
        if any(keyword in background_str for keyword in ['civil office', '為官者', 'office:', '宰相', 'chief councilor']):
            return 'Noble/Official'
        
        # 文人階級
        if any(keyword in background_str for keyword in ['man of culture', '文人', 'wenren', 'skilled at writing', '工於文']):
            return 'Literati'
        
        # 宗教階級
        if any(keyword in background_str for keyword in ['monk', '僧', 'nun', '道姑', '女冠', 'daoist']):
            return 'Religious'
        
        # 娛樂階級
        if any(keyword in background_str for keyword in ['entertainer', '妓', '歌', '舞', '表演']):
            return 'Entertainer'
        
        # 一般詩人
        if 'poet' in background_str or '詩人' in background_str:
            return 'General Poet'
        
        return 'Other'
    
    no_region_female['social_class'] = no_region_female['背景'].apply(classify_social_class)
    
    # 顯示社會階級分布
    print(f"\n📊 沒有地域標籤的女性詩人社會階級分布:")
    class_counts = no_region_female['social_class'].value_counts()
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count} 人")
    
    return no_region_female

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

def analyze_no_region_female_poets():
    """分析沒有地域標籤的女性詩人"""
    print("=" * 80)
    print("🔍 沒有地域標籤的女性詩人N-gram分析")
    print("=" * 80)
    
    # 1. 載入沒有地域標籤的女性詩人數據
    no_region_female_df = load_female_poets_no_region_data()
    if no_region_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 找到匹配的女性詩人
    no_region_poet_names = set(no_region_female_df['poet_name'].unique())
    
    print(f"\n📊 沒有地域標籤的女性詩人匹配分析:")
    for ngram_type, df in ngram_data.items():
        ngram_poet_names = set(df['詩人'].unique())
        matched_poets = no_region_poet_names.intersection(ngram_poet_names)
        
        print(f"  {ngram_type.upper()}:")
        print(f"    沒有地域標籤女性詩人: {len(no_region_poet_names):,} 人")
        print(f"    N-gram詩人: {len(ngram_poet_names):,} 人")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    匹配率: {len(matched_poets)/len(no_region_poet_names)*100:.1f}%")
    
    # 4. 按社會階級分析1-gram
    print("\n" + "=" * 60)
    print("📈 按社會階級分析沒有地域標籤的女性詩人1-gram")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = no_region_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            no_region_female_df[['poet_name', 'social_class', '背景']], 
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
                
                print(f"\n✅ {social_class} 沒有地域標籤女性詩人統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人")
                print(f"    唯一詞彙: {unique_words:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前20個高頻字
                top_words = class_data.nlargest(20, '詞頻')
                print(f"    前20個高頻字:")
                for i, (_, row) in enumerate(top_words.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
                
                # 顯示背景信息
                backgrounds = class_data['背景'].dropna().unique()
                if len(backgrounds) > 0:
                    print(f"    背景標籤: {', '.join(backgrounds[:3])}{'...' if len(backgrounds) > 3 else ''}")
                else:
                    print(f"    背景標籤: 無")
    
    # 5. 按社會階級分析2-gram
    print(f"\n" + "=" * 60)
    print("📈 按社會階級分析沒有地域標籤的女性詩人2-gram")
    print("=" * 60)
    
    if '2gram' in ngram_data:
        df = ngram_data['2gram']
        matched_poets = no_region_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            no_region_female_df[['poet_name', 'social_class', '背景']], 
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
                
                print(f"\n✅ {social_class} 沒有地域標籤女性詩人2-gram統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人")
                print(f"    唯一詞組: {unique_phrases:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前15個高頻詞組
                top_phrases = class_data.nlargest(15, '詞頻')
                print(f"    前15個高頻2-gram:")
                for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    # 6. 按社會階級分析4-gram
    print(f"\n" + "=" * 60)
    print("📈 按社會階級分析沒有地域標籤的女性詩人4-gram")
    print("=" * 60)
    
    if '4gram' in ngram_data:
        df = ngram_data['4gram']
        matched_poets = no_region_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            no_region_female_df[['poet_name', 'social_class', '背景']], 
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
                
                print(f"\n✅ {social_class} 沒有地域標籤女性詩人4-gram統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人")
                print(f"    唯一詞組: {unique_phrases:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前10個高頻詞組
                top_phrases = class_data.nlargest(10, '詞頻')
                print(f"    前10個高頻4-gram:")
                for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")

def generate_no_region_female_poets_report():
    """生成沒有地域標籤的女性詩人分析報告"""
    print("=" * 80)
    print("📝 生成沒有地域標籤的女性詩人分析報告")
    print("=" * 80)
    
    # 1. 載入沒有地域標籤的女性詩人數據
    no_region_female_df = load_female_poets_no_region_data()
    if no_region_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 生成報告內容
    report_content = []
    report_content.append("# 沒有地域標籤的女性詩人詳細分析報告")
    report_content.append("")
    report_content.append("## 📊 概述")
    report_content.append("")
    report_content.append(f"- **沒有地域標籤的女性詩人數量**: {len(no_region_female_df)} 人")
    
    # 統計有N-gram數據的女性詩人
    no_region_poet_names = set(no_region_female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_data['1gram']['詩人'].unique()) if '1gram' in ngram_data else set()
    matched_poets = no_region_poet_names.intersection(ngram_poet_names)
    report_content.append(f"- **有N-gram數據的沒有地域標籤女性詩人**: {len(matched_poets)} 人")
    report_content.append("")
    
    # 按社會階級分析
    for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
        class_data = no_region_female_df[no_region_female_df['social_class'] == social_class]
        if not class_data.empty:
            report_content.append(f"## 🏛️ {social_class} 沒有地域標籤女性詩人")
            report_content.append("")
            report_content.append(f"**詩人數量**: {len(class_data)} 人")
            report_content.append("")
            report_content.append("### 詩人名單")
            report_content.append("")
            
            for i, (_, row) in enumerate(class_data.iterrows(), 1):
                report_content.append(f"{i}. **{row['poet_name']}**")
                if pd.notna(row['背景']):
                    report_content.append(f"   - 背景: {row['背景']}")
                if pd.notna(row['Geography']):
                    report_content.append(f"   - 地域: {row['Geography']}")
                report_content.append("")
            
            # N-gram分析
            if '1gram' in ngram_data:
                df = ngram_data['1gram']
                matched_poets_class = no_region_poet_names.intersection(set(df['詩人'].unique()))
                class_poets = [name for name in matched_poets_class if name in class_data['poet_name'].values]
                
                if class_poets:
                    class_ngram_data = df[df['詩人'].isin(class_poets)]
                    
                    report_content.append("### N-gram 分析")
                    report_content.append("")
                    report_content.append("#### 1-gram (單字) 分析")
                    report_content.append("")
                    
                    unique_words = class_ngram_data['字詞'].nunique()
                    total_freq = class_ngram_data['詞頻'].sum()
                    avg_freq = total_freq / unique_words if unique_words > 0 else 0
                    
                    report_content.append(f"- **唯一詞彙數**: {unique_words} 個")
                    report_content.append(f"- **總詞頻**: {total_freq} 次")
                    report_content.append(f"- **平均詞頻**: {avg_freq:.2f} 次")
                    report_content.append("")
                    
                    # 前20個高頻字
                    top_words = class_ngram_data.nlargest(20, '詞頻')
                    report_content.append("**前20個高頻字**:")
                    for i, (_, row) in enumerate(top_words.iterrows(), 1):
                        report_content.append(f" {i:2d}. **{row['字詞']}** - {row['詞頻']} 次")
                    report_content.append("")
            
            report_content.append("---")
            report_content.append("")
    
    # 保存報告
    report_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/沒有地域標籤女性詩人詳細分析報告.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"✅ 報告已保存至: {report_file}")

def main():
    """主函數"""
    # 分析沒有地域標籤的女性詩人
    analyze_no_region_female_poets()
    
    # 生成詳細報告
    generate_no_region_female_poets_report()

if __name__ == "__main__":
    main()
