#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
所有女性詩人合併N-gram分析
將所有女性詩人的N-gram數據合併計算，並列出所有詩人
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np
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
    
    all_female_df['social_class'] = all_female_df['背景'].apply(classify_social_class)
    
    # 添加地域標籤分類
    def classify_region_status(geography_str):
        if pd.isna(geography_str) or geography_str == '' or 'Unknown' in str(geography_str):
            return 'No Region'
        else:
            return 'Has Region'
    
    all_female_df['region_status'] = all_female_df['Geography'].apply(classify_region_status)
    
    # 顯示社會階級分布
    print(f"\n📊 所有女性詩人社會階級分布:")
    class_counts = all_female_df['social_class'].value_counts()
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count} 人")
    
    # 顯示地域標籤分布
    print(f"\n📊 所有女性詩人地域標籤分布:")
    region_counts = all_female_df['region_status'].value_counts()
    for region_status, count in region_counts.items():
        print(f"  {region_status}: {count} 人")
    
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
            print(f"   - 唯一詞組: {df['字詞'].nunique():,}")
        else:
            print(f"❌ 文件不存在: {filename}")
    
    return ngram_data

def analyze_combined_female_poets():
    """分析所有女性詩人合併的N-gram數據"""
    print("=" * 80)
    print("🔍 所有女性詩人合併N-gram分析")
    print("=" * 80)
    
    # 1. 載入所有女性詩人數據
    all_female_df = load_all_female_poets_data()
    if all_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 找到匹配的女性詩人
    all_female_poet_names = set(all_female_df['poet_name'].unique())
    
    print(f"\n📊 所有女性詩人匹配分析:")
    for ngram_type, df in ngram_data.items():
        ngram_poet_names = set(df['詩人'].unique())
        matched_poets = all_female_poet_names.intersection(ngram_poet_names)
        
        print(f"  {ngram_type.upper()}:")
        print(f"    所有女性詩人: {len(all_female_poet_names):,} 人")
        print(f"    N-gram詩人: {len(ngram_poet_names):,} 人")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    匹配率: {len(matched_poets)/len(all_female_poet_names)*100:.1f}%")
    
    # 4. 合併所有女性詩人的N-gram數據
    print("\n" + "=" * 60)
    print("📈 所有女性詩人合併N-gram統計")
    print("=" * 60)
    
    for ngram_type, df in ngram_data.items():
        matched_poets = all_female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併所有女性詩人的詞頻
        combined_freq = matched_df.groupby('字詞')['詞頻'].sum().reset_index()
        combined_freq = combined_freq.sort_values('詞頻', ascending=False)
        
        unique_words = len(combined_freq)
        total_freq = combined_freq['詞頻'].sum()
        avg_freq = total_freq / unique_words if unique_words > 0 else 0
        
        print(f"\n✅ {ngram_type.upper()} 合併統計:")
        print(f"    匹配詩人: {len(matched_poets):,} 人")
        print(f"    唯一詞彙: {unique_words:,} 個")
        print(f"    總詞頻: {total_freq:,} 次")
        print(f"    平均詞頻: {avg_freq:.2f} 次")
        
        # 前30個高頻詞彙
        top_words = combined_freq.head(30)
        print(f"    前30個高頻{ngram_type}:")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
    
    return all_female_df, ngram_data, all_female_poet_names

def generate_complete_combined_report():
    """生成所有女性詩人合併分析報告"""
    print("=" * 80)
    print("📝 生成所有女性詩人合併分析報告")
    print("=" * 80)
    
    # 1. 載入所有女性詩人數據
    all_female_df = load_all_female_poets_data()
    if all_female_df is None:
        return
    
    # 2. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 3. 生成報告內容
    report_content = []
    report_content.append("# 所有女性詩人合併N-gram分析報告")
    report_content.append("")
    report_content.append("## 📊 概述")
    report_content.append("")
    report_content.append(f"- **所有女性詩人總數**: {len(all_female_df)} 人")
    
    # 統計有N-gram數據的女性詩人
    all_female_poet_names = set(all_female_df['poet_name'].unique())
    ngram_poet_names = set(ngram_data['1gram']['詩人'].unique()) if '1gram' in ngram_data else set()
    matched_poets = all_female_poet_names.intersection(ngram_poet_names)
    report_content.append(f"- **有N-gram數據的女性詩人**: {len(matched_poets)} 人")
    
    # 地域標籤統計
    has_region_count = len(all_female_df[all_female_df['region_status'] == 'Has Region'])
    no_region_count = len(all_female_df[all_female_df['region_status'] == 'No Region'])
    report_content.append(f"- **有地域標籤的女性詩人**: {has_region_count} 人")
    report_content.append(f"- **沒有地域標籤的女性詩人**: {no_region_count} 人")
    report_content.append("")
    
    # 社會階級分布
    report_content.append("## 🏛️ 社會階級分布")
    report_content.append("")
    class_counts = all_female_df['social_class'].value_counts()
    for class_name, count in class_counts.items():
        report_content.append(f"- **{class_name}**: {count} 人")
    report_content.append("")
    
    # 地域標籤分布
    report_content.append("## 🌍 地域標籤分布")
    report_content.append("")
    region_counts = all_female_df['region_status'].value_counts()
    for region_status, count in region_counts.items():
        report_content.append(f"- **{region_status}**: {count} 人")
    report_content.append("")
    
    # 所有女性詩人名單
    report_content.append("## 👥 所有女性詩人名單")
    report_content.append("")
    
    # 按社會階級分組列出所有詩人
    for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
        class_data = all_female_df[all_female_df['social_class'] == social_class]
        if not class_data.empty:
            report_content.append(f"### {social_class} 女性詩人 ({len(class_data)} 人)")
            report_content.append("")
            
            for i, (_, row) in enumerate(class_data.iterrows(), 1):
                report_content.append(f"{i}. **{row['poet_name']}**")
                if pd.notna(row['背景']):
                    report_content.append(f"   - 背景: {row['背景']}")
                if pd.notna(row['Geography']):
                    report_content.append(f"   - 地域: {row['Geography']}")
                report_content.append("")
            
            report_content.append("---")
            report_content.append("")
    
    # 合併N-gram分析
    report_content.append("## 📈 合併N-gram分析")
    report_content.append("")
    
    for ngram_type, df in ngram_data.items():
        matched_poets = all_female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併所有女性詩人的詞頻
        combined_freq = matched_df.groupby('字詞')['詞頻'].sum().reset_index()
        combined_freq = combined_freq.sort_values('詞頻', ascending=False)
        
        unique_words = len(combined_freq)
        total_freq = combined_freq['詞頻'].sum()
        avg_freq = total_freq / unique_words if unique_words > 0 else 0
        
        report_content.append(f"### {ngram_type.upper()} 合併統計")
        report_content.append("")
        report_content.append(f"- **匹配詩人**: {len(matched_poets)} 人")
        report_content.append(f"- **唯一詞彙**: {unique_words:,} 個")
        report_content.append(f"- **總詞頻**: {total_freq:,} 次")
        report_content.append(f"- **平均詞頻**: {avg_freq:.2f} 次")
        report_content.append("")
        
        # 前30個高頻詞彙
        top_words = combined_freq.head(30)
        report_content.append(f"**前30個高頻{ngram_type}**:")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            report_content.append(f" {i:2d}. **{row['字詞']}** - {row['詞頻']:,} 次")
        report_content.append("")
        report_content.append("---")
        report_content.append("")
    
    # 保存報告
    report_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/所有女性詩人合併N-gram分析報告.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"✅ 報告已保存至: {report_file}")

def main():
    """主函數"""
    # 分析所有女性詩人合併N-gram
    analyze_combined_female_poets()
    
    # 生成合併分析報告
    generate_complete_combined_report()

if __name__ == "__main__":
    main()
