#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全部女性詩人完整統計分析
分析所有女性詩人（不管有沒有地域標籤）的詞頻統計
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

def analyze_all_female_poets():
    """分析所有女性詩人"""
    print("=" * 80)
    print("🔍 所有女性詩人完整N-gram分析")
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
    
    # 4. 按社會階級分析1-gram
    print("\n" + "=" * 60)
    print("📈 按社會階級分析所有女性詩人1-gram")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = all_female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併社會階級信息
        class_merged = matched_df.merge(
            all_female_df[['poet_name', 'social_class', '背景', 'region_status']], 
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
                
                # 統計有地域標籤和沒有地域標籤的詩人
                has_region = class_data[class_data['region_status'] == 'Has Region']['詩人'].nunique()
                no_region = class_data[class_data['region_status'] == 'No Region']['詩人'].nunique()
                
                print(f"\n✅ {social_class} 所有女性詩人統計:")
                print(f"    詩人數量: {class_data['詩人'].nunique():,} 人 (有地域: {has_region} 人, 無地域: {no_region} 人)")
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
    
    # 5. 按地域標籤狀態分析
    print(f"\n" + "=" * 60)
    print("📈 按地域標籤狀態分析所有女性詩人1-gram")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        matched_poets = all_female_poet_names.intersection(set(df['詩人'].unique()))
        
        # 篩選匹配詩人的數據
        matched_df = df[df['詩人'].isin(matched_poets)]
        
        # 合併地域標籤信息
        region_merged = matched_df.merge(
            all_female_df[['poet_name', 'region_status', 'social_class']], 
            left_on='詩人', 
            right_on='poet_name', 
            how='left'
        )
        
        # 按地域標籤狀態分組統計
        for region_status in ['Has Region', 'No Region']:
            region_data = region_merged[region_merged['region_status'] == region_status]
            if not region_data.empty:
                unique_words = region_data['字詞'].nunique()
                total_freq = region_data['詞頻'].sum()
                avg_freq = total_freq / unique_words if unique_words > 0 else 0
                
                print(f"\n✅ {region_status} 女性詩人統計:")
                print(f"    詩人數量: {region_data['詩人'].nunique():,} 人")
                print(f"    唯一詞彙: {unique_words:,} 個")
                print(f"    總詞頻: {total_freq:,} 次")
                print(f"    平均詞頻: {avg_freq:.2f} 次")
                
                # 前20個高頻字
                top_words = region_data.nlargest(20, '詞頻')
                print(f"    前20個高頻字:")
                for i, (_, row) in enumerate(top_words.iterrows(), 1):
                    print(f"      {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
                
                # 社會階級分布
                class_dist = region_data['social_class'].value_counts()
                print(f"    社會階級分布:")
                for class_name, count in class_dist.items():
                    print(f"      {class_name}: {count} 人")

def generate_complete_female_poets_report():
    """生成所有女性詩人完整分析報告"""
    print("=" * 80)
    print("📝 生成所有女性詩人完整分析報告")
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
    report_content.append("# 所有女性詩人完整分析報告")
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
    
    # 按社會階級詳細分析
    for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
        class_data = all_female_df[all_female_df['social_class'] == social_class]
        if not class_data.empty:
            report_content.append(f"## 🏛️ {social_class} 女性詩人")
            report_content.append("")
            report_content.append(f"**詩人數量**: {len(class_data)} 人")
            
            # 地域標籤分布
            has_region_class = len(class_data[class_data['region_status'] == 'Has Region'])
            no_region_class = len(class_data[class_data['region_status'] == 'No Region'])
            report_content.append(f"**地域標籤分布**: 有地域 {has_region_class} 人, 無地域 {no_region_class} 人")
            report_content.append("")
            
            # 詩人名單（前20個）
            report_content.append("### 詩人名單")
            report_content.append("")
            for i, (_, row) in enumerate(class_data.head(20).iterrows(), 1):
                report_content.append(f"{i}. **{row['poet_name']}**")
                if pd.notna(row['背景']):
                    report_content.append(f"   - 背景: {row['背景']}")
                if pd.notna(row['Geography']):
                    report_content.append(f"   - 地域: {row['Geography']}")
                report_content.append("")
            
            if len(class_data) > 20:
                report_content.append(f"... 還有 {len(class_data) - 20} 位詩人")
                report_content.append("")
            
            # N-gram分析
            if '1gram' in ngram_data:
                df = ngram_data['1gram']
                matched_poets_class = all_female_poet_names.intersection(set(df['詩人'].unique()))
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
    report_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/所有女性詩人完整分析報告.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"✅ 報告已保存至: {report_file}")

def main():
    """主函數"""
    # 分析所有女性詩人
    analyze_all_female_poets()
    
    # 生成完整報告
    generate_complete_female_poets_report()

if __name__ == "__main__":
    main()
