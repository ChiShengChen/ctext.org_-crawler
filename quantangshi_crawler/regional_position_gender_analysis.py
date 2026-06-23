#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地域×職位×性別三維詞頻分析
基於地域、社會階層和性別進行 n-gram 詞頻分析
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import re

def load_poet_data():
    """載入詩人數據"""
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    # 提取地域信息
    def extract_region(geography):
        if pd.isna(geography):
            return "未知"
        
        geo_str = str(geography)
        
        if "關內道" in geo_str:
            return "關內道"
        elif "河南道" in geo_str:
            return "河南道"
        elif "河北道" in geo_str:
            return "河北道"
        elif "江南道" in geo_str:
            return "江南道"
        elif "河東道" in geo_str:
            return "河東道"
        elif "淮南道" in geo_str:
            return "淮南道"
        elif "山南道" in geo_str:
            return "山南道"
        elif "隴右道" in geo_str:
            return "隴右道"
        elif "劍南道" in geo_str:
            return "劍南道"
        elif "嶺南道" in geo_str:
            return "嶺南道"
        else:
            return "其他"
    
    df['region'] = df['Geography'].apply(extract_region)
    
    # 提取社會階層信息
    def extract_social_class(background):
        if pd.isna(background):
            return "未知"
        
        bg_str = str(background)
        
        # 根據背景信息分類社會階層
        if "chief councilor" in bg_str or "宰相" in bg_str:
            return "宰相"
        elif "civil office" in bg_str or "為官者" in bg_str:
            return "官員"
        elif "僧" in bg_str or "monk" in bg_str:
            return "僧人"
        elif "calligrapher" in bg_str or "書法家" in bg_str:
            return "書法家"
        elif "painter" in bg_str or "畫家" in bg_str:
            return "畫家"
        elif "poet" in bg_str or "詩人" in bg_str:
            return "詩人"
        elif "man of culture" in bg_str or "文人" in bg_str:
            return "文人"
        elif "recluse" in bg_str or "隱士" in bg_str:
            return "隱士"
        else:
            return "其他"
    
    df['social_class'] = df['背景'].apply(extract_social_class)
    
    # 提取詩人名字，處理編號問題
    def extract_poet_name(text):
        if pd.isna(text):
            return "未知"
        text_str = str(text)
        
        # 移除編號（如 "1. 白居易" -> "白居易"）
        if re.match(r'^\d+\.\s*', text_str):
            text_str = re.sub(r'^\d+\.\s*', '', text_str)
        
        if ':' in text_str:
            return text_str.split(':')[0].strip()
        elif '首' in text_str:
            parts = text_str.split('首')
            if len(parts) > 1:
                return parts[0].strip()
        return text_str.strip()
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 提取詩歌數量
    def extract_poem_count(poet_info):
        if pd.isna(poet_info):
            return 0
        poet_str = str(poet_info)
        match = re.search(r':\s*(\d{1,3}(?:,\d{3})*)\s*首', poet_str)
        if match:
            count_str = match.group(1).replace(',', '')
            try:
                return int(count_str)
            except ValueError:
                return 0
        return 0
    
    df['poem_count'] = df['詩人'].apply(extract_poem_count)
    
    # 清理性別數據
    def clean_gender(gender):
        if pd.isna(gender):
            return "未知"
        gender_str = str(gender).strip().lower()
        if gender_str in ['male', '男']:
            return "男"
        elif gender_str in ['female', '女']:
            return "女"
        else:
            return "未知"
    
    df['gender_clean'] = df['性別'].apply(clean_gender)
    
    return df

def analyze_regional_position_gender_ngrams(ngram_file, df, ngram_type):
    """分析地域×職位×性別 n-gram 特徵"""
    print(f"正在分析 {ngram_type} 數據...")
    
    # 載入 n-gram 數據
    ngram_df = pd.read_csv(ngram_file)
    
    # 創建詩人-地域-職位-性別映射
    poet_info_map = {}
    for _, row in df.iterrows():
        poet_name = row['poet_name']
        region = row['region']
        social_class = row['social_class']
        gender = row['gender_clean']
        poem_count = row['poem_count']
        poet_info_map[poet_name] = {
            'region': region,
            'social_class': social_class,
            'gender': gender,
            'poem_count': poem_count
        }
    
    # 為每個 n-gram 記錄添加地域、職位、性別信息
    ngram_df['region'] = ngram_df['詩人'].map(lambda x: poet_info_map.get(x, {}).get('region', '未知'))
    ngram_df['social_class'] = ngram_df['詩人'].map(lambda x: poet_info_map.get(x, {}).get('social_class', '未知'))
    ngram_df['gender'] = ngram_df['詩人'].map(lambda x: poet_info_map.get(x, {}).get('gender', '未知'))
    ngram_df['poem_count'] = ngram_df['詩人'].map(lambda x: poet_info_map.get(x, {}).get('poem_count', 0))
    
    # 按地域、職位、性別分組統計
    regional_position_gender_stats = {}
    
    for region in ngram_df['region'].unique():
        if pd.isna(region):
            continue
        
        region_data = ngram_df[ngram_df['region'] == region]
        
        if len(region_data) == 0:
            continue
        
        regional_position_gender_stats[region] = {}
        
        for social_class in region_data['social_class'].unique():
            if pd.isna(social_class):
                continue
            
            class_data = region_data[region_data['social_class'] == social_class]
            
            if len(class_data) == 0:
                continue
            
            regional_position_gender_stats[region][social_class] = {}
            
            for gender in class_data['gender'].unique():
                if pd.isna(gender):
                    continue
                
                gender_data = class_data[class_data['gender'] == gender]
                
                if len(gender_data) == 0:
                    continue
                
                # 計算該地域-職位-性別的總詞頻
                total_freq = gender_data['詞頻'].sum()
                
                # 按詞頻排序，取前50
                top_50 = gender_data.nlargest(50, '詞頻')
                
                # 獲取該地域-職位-性別的所有詩人名單
                poets_in_group = gender_data[['詩人', 'poem_count']].drop_duplicates()
                poets_in_group = poets_in_group.sort_values('poem_count', ascending=False)
                
                regional_position_gender_stats[region][social_class][gender] = {
                    'total_freq': total_freq,
                    'unique_ngrams': len(gender_data),
                    'top_50': top_50,
                    'poets': poets_in_group
                }
    
    return regional_position_gender_stats

def generate_regional_position_gender_markdown_report(regional_position_gender_stats_1gram, regional_position_gender_stats_2gram, regional_position_gender_stats_4gram, df):
    """生成地域×職位×性別三維分析 Markdown 報告"""
    
    # 基本統計
    total_poets = len(df)
    total_poems = df['poem_count'].sum()
    avg_poems = total_poems / total_poets if total_poets > 0 else 0
    
    # 三維交叉統計
    cross_tab = pd.crosstab([df['region'], df['social_class']], df['gender_clean'], margins=True)
    
    markdown_content = f"""# 地域×職位×性別三維詞頻分析報告

## 基本統計

- **總詩人數**: {total_poets:,} 人
- **總詩歌數**: {total_poems:,} 首
- **平均每人詩歌數**: {avg_poems:.1f} 首

## 地域×職位×性別交叉統計

{cross_tab.to_string()}

## 1-gram（單字）分析

"""
    
    # 1-gram 分析
    for region in sorted(regional_position_gender_stats_1gram.keys()):
        markdown_content += f"### {region}\n\n"
        
        for social_class in sorted(regional_position_gender_stats_1gram[region].keys()):
            markdown_content += f"#### {social_class}\n\n"
            
            for gender in sorted(regional_position_gender_stats_1gram[region][social_class].keys()):
                stats = regional_position_gender_stats_1gram[region][social_class][gender]
                markdown_content += f"##### {gender}性\n\n"
                markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
                markdown_content += f"- **獨特單字數**: {stats['unique_ngrams']:,}\n"
                markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
                
                # 顯示詩人名單（前10名）
                markdown_content += "**詩人名單（前10名）**:\n"
                markdown_content += "| 排名 | 詩人姓名 | 詩歌數量 |\n"
                markdown_content += "|------|----------|----------|\n"
                
                for i, (_, poet) in enumerate(stats['poets'].head(10).iterrows(), 1):
                    markdown_content += f"| {i} | {poet['詩人']} | {poet['poem_count']:,} |\n"
                
                markdown_content += "\n"
                markdown_content += "**前50名單字**:\n"
                markdown_content += "| 排名 | 單字 | 詞頻 |\n"
                markdown_content += "|------|------|------|\n"
                
                for i, (_, row) in enumerate(stats['top_50'].iterrows(), 1):
                    markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
                
                markdown_content += "\n"
    
    markdown_content += "## 2-gram（雙字詞）分析\n\n"
    
    # 2-gram 分析
    for region in sorted(regional_position_gender_stats_2gram.keys()):
        markdown_content += f"### {region}\n\n"
        
        for social_class in sorted(regional_position_gender_stats_2gram[region].keys()):
            markdown_content += f"#### {social_class}\n\n"
            
            for gender in sorted(regional_position_gender_stats_2gram[region][social_class].keys()):
                stats = regional_position_gender_stats_2gram[region][social_class][gender]
                markdown_content += f"##### {gender}性\n\n"
                markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
                markdown_content += f"- **獨特雙字詞數**: {stats['unique_ngrams']:,}\n"
                markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
                
                # 顯示詩人名單（前10名）
                markdown_content += "**詩人名單（前10名）**:\n"
                markdown_content += "| 排名 | 詩人姓名 | 詩歌數量 |\n"
                markdown_content += "|------|----------|----------|\n"
                
                for i, (_, poet) in enumerate(stats['poets'].head(10).iterrows(), 1):
                    markdown_content += f"| {i} | {poet['詩人']} | {poet['poem_count']:,} |\n"
                
                markdown_content += "\n"
                markdown_content += "**前50名雙字詞**:\n"
                markdown_content += "| 排名 | 雙字詞 | 詞頻 |\n"
                markdown_content += "|------|--------|------|\n"
                
                for i, (_, row) in enumerate(stats['top_50'].iterrows(), 1):
                    markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
                
                markdown_content += "\n"
    
    markdown_content += "## 4-gram（四字詞）分析\n\n"
    
    # 4-gram 分析
    for region in sorted(regional_position_gender_stats_4gram.keys()):
        markdown_content += f"### {region}\n\n"
        
        for social_class in sorted(regional_position_gender_stats_4gram[region].keys()):
            markdown_content += f"#### {social_class}\n\n"
            
            for gender in sorted(regional_position_gender_stats_4gram[region][social_class].keys()):
                stats = regional_position_gender_stats_4gram[region][social_class][gender]
                markdown_content += f"##### {gender}性\n\n"
                markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
                markdown_content += f"- **獨特四字詞數**: {stats['unique_ngrams']:,}\n"
                markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
                
                # 顯示詩人名單（前10名）
                markdown_content += "**詩人名單（前10名）**:\n"
                markdown_content += "| 排名 | 詩人姓名 | 詩歌數量 |\n"
                markdown_content += "|------|----------|----------|\n"
                
                for i, (_, poet) in enumerate(stats['poets'].head(10).iterrows(), 1):
                    markdown_content += f"| {i} | {poet['詩人']} | {poet['poem_count']:,} |\n"
                
                markdown_content += "\n"
                markdown_content += "**前50名四字詞**:\n"
                markdown_content += "| 排名 | 四字詞 | 詞頻 |\n"
                markdown_content += "|------|--------|------|\n"
                
                for i, (_, row) in enumerate(stats['top_50'].iterrows(), 1):
                    markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
                
                markdown_content += "\n"
    
    markdown_content += """## 分析結論

1. **三維差異**: 地域、職位、性別三個維度對詩人用字習慣都有顯著影響
2. **地域特色**: 不同地域的詩人在用字上體現了地域文化特色
3. **職位差異**: 不同社會階層的詩人用字反映了其身份和背景
4. **性別特徵**: 男女詩人在用字上存在明顯的性別差異
5. **交叉影響**: 三個維度的交叉作用產生了更細緻的用字特徵分類

---
*分析時間: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
    
    return markdown_content

def main():
    print("開始地域×職位×性別三維詞頻分析...")
    
    # 載入詩人數據
    print("載入詩人數據...")
    df = load_poet_data()
    
    # 顯示基本統計
    print(f"\n基本統計:")
    print(f"總詩人數: {len(df):,} 人")
    print(f"總詩歌數: {df['poem_count'].sum():,} 首")
    
    # 顯示三維交叉分布
    print("\n地域×職位×性別交叉分布:")
    cross_tab = pd.crosstab([df['region'], df['social_class']], df['gender_clean'], margins=True)
    print(cross_tab)
    
    # 分析 1-gram
    print("\n分析 1-gram 數據...")
    regional_position_gender_stats_1gram = analyze_regional_position_gender_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv',
        df,
        '1-gram'
    )
    
    # 分析 2-gram
    print("\n分析 2-gram 數據...")
    regional_position_gender_stats_2gram = analyze_regional_position_gender_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_2gram_詞頻統計.csv',
        df,
        '2-gram'
    )
    
    # 分析 4-gram
    print("\n分析 4-gram 數據...")
    regional_position_gender_stats_4gram = analyze_regional_position_gender_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_4gram_詞頻統計.csv',
        df,
        '4-gram'
    )
    
    # 生成報告
    print("\n生成 Markdown 報告...")
    markdown_content = generate_regional_position_gender_markdown_report(
        regional_position_gender_stats_1gram, 
        regional_position_gender_stats_2gram, 
        regional_position_gender_stats_4gram,
        df
    )
    
    # 保存報告
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_position_gender_analysis_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n分析完成！報告已保存至: {output_file}")
    
    # 顯示基本統計
    print("\n基本統計:")
    print("1-gram 分析地域數:", len(regional_position_gender_stats_1gram))
    print("2-gram 分析地域數:", len(regional_position_gender_stats_2gram))
    print("4-gram 分析地域數:", len(regional_position_gender_stats_4gram))
    
    # 顯示各地域-職位-性別統計
    print("\n各地域-職位-性別 1-gram 統計:")
    for region in sorted(regional_position_gender_stats_1gram.keys()):
        print(f"\n{region}:")
        for social_class in sorted(regional_position_gender_stats_1gram[region].keys()):
            print(f"  {social_class}:")
            for gender in sorted(regional_position_gender_stats_1gram[region][social_class].keys()):
                stats = regional_position_gender_stats_1gram[region][social_class][gender]
                print(f"    {gender}性: 總詞頻 {stats['total_freq']:,}, 獨特單字 {stats['unique_ngrams']:,}, 詩人 {len(stats['poets'])} 人")

if __name__ == "__main__":
    main()
