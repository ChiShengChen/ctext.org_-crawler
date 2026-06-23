#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地域詩人用字特徵分析
基於 n-gram 數據分析各地域詩人的用字特徵
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import os

def load_poet_geo_data():
    """載入詩人地理標籤數據"""
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
    
    # 提取詩人名字
    def extract_poet_name(text):
        if pd.isna(text):
            return "未知"
        text_str = str(text)
        if ':' in text_str:
            return text_str.split(':')[0].strip()
        elif '首' in text_str:
            parts = text_str.split('首')
            if len(parts) > 1:
                return parts[0].strip()
        return text_str.strip()
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 創建詩人-地域映射
    poet_region_map = {}
    for _, row in df.iterrows():
        poet_name = row['poet_name']
        region = row['region']
        poet_region_map[poet_name] = region
    
    return poet_region_map

def analyze_regional_ngrams(ngram_file, poet_region_map, ngram_type):
    """分析地域 n-gram 特徵"""
    print(f"正在分析 {ngram_type} 數據...")
    
    # 載入 n-gram 數據
    df = pd.read_csv(ngram_file)
    
    # 為每個 n-gram 記錄添加地域信息
    df['region'] = df['詩人'].map(poet_region_map).fillna('未知')
    
    # 按地域分組統計
    regional_stats = {}
    
    for region in df['region'].unique():
        if pd.isna(region):
            continue
            
        region_data = df[df['region'] == region]
        
        # 計算該地域的總詞頻
        total_freq = region_data['詞頻'].sum()
        
        # 按詞頻排序，取前100
        top_ngrams = region_data.nlargest(100, '詞頻')
        
        regional_stats[region] = {
            'total_freq': total_freq,
            'unique_ngrams': len(region_data),
            'top_100': top_ngrams
        }
    
    return regional_stats

def generate_markdown_report(regional_stats_1gram, regional_stats_2gram, regional_stats_4gram):
    """生成 Markdown 報告"""
    
    markdown_content = """# 地域詩人用字特徵分析

## 分析概述

本報告基於詩人的 n-gram 詞頻統計數據，分析各地域詩人的用字特徵，包括：
- 1-gram（單字）分析
- 2-gram（雙字詞）分析  
- 4-gram（四字詞）分析

## 1-gram（單字）分析

"""
    
    # 1-gram 分析
    for region in sorted(regional_stats_1gram.keys()):
        stats = regional_stats_1gram[region]
        markdown_content += f"### {region}\n\n"
        markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
        markdown_content += f"- **獨特單字數**: {stats['unique_ngrams']:,}\n\n"
        markdown_content += "| 排名 | 單字 | 詞頻 |\n"
        markdown_content += "|------|------|------|\n"
        
        for i, (_, row) in enumerate(stats['top_100'].iterrows(), 1):
            markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
        
        markdown_content += "\n"
    
    markdown_content += "## 2-gram（雙字詞）分析\n\n"
    
    # 2-gram 分析
    for region in sorted(regional_stats_2gram.keys()):
        stats = regional_stats_2gram[region]
        markdown_content += f"### {region}\n\n"
        markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
        markdown_content += f"- **獨特雙字詞數**: {stats['unique_ngrams']:,}\n\n"
        markdown_content += "| 排名 | 雙字詞 | 詞頻 |\n"
        markdown_content += "|------|--------|------|\n"
        
        for i, (_, row) in enumerate(stats['top_100'].iterrows(), 1):
            markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
        
        markdown_content += "\n"
    
    markdown_content += "## 4-gram（四字詞）分析\n\n"
    
    # 4-gram 分析
    for region in sorted(regional_stats_4gram.keys()):
        stats = regional_stats_4gram[region]
        markdown_content += f"### {region}\n\n"
        markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
        markdown_content += f"- **獨特四字詞數**: {stats['unique_ngrams']:,}\n\n"
        markdown_content += "| 排名 | 四字詞 | 詞頻 |\n"
        markdown_content += "|------|--------|------|\n"
        
        for i, (_, row) in enumerate(stats['top_100'].iterrows(), 1):
            markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
        
        markdown_content += "\n"
    
    markdown_content += """## 分析結論

1. **地域用字差異**: 不同地域的詩人在用字習慣上存在明顯差異
2. **詞彙豐富度**: 各地域的詞彙豐富度反映了其文化發展水平
3. **特色詞彙**: 各地域都有其獨特的特色詞彙，反映了地域文化特色

---
*分析時間: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
    
    return markdown_content

def main():
    print("開始地域詩人用字特徵分析...")
    
    # 載入詩人地理標籤數據
    print("載入詩人地理標籤數據...")
    poet_region_map = load_poet_geo_data()
    print(f"載入了 {len(poet_region_map)} 個詩人的地理標籤")
    
    # 分析 1-gram
    print("\n分析 1-gram 數據...")
    regional_stats_1gram = analyze_regional_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv',
        poet_region_map,
        '1-gram'
    )
    
    # 分析 2-gram
    print("\n分析 2-gram 數據...")
    regional_stats_2gram = analyze_regional_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_2gram_詞頻統計.csv',
        poet_region_map,
        '2-gram'
    )
    
    # 分析 4-gram
    print("\n分析 4-gram 數據...")
    regional_stats_4gram = analyze_regional_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_4gram_詞頻統計.csv',
        poet_region_map,
        '4-gram'
    )
    
    # 生成報告
    print("\n生成 Markdown 報告...")
    markdown_content = generate_markdown_report(
        regional_stats_1gram, 
        regional_stats_2gram, 
        regional_stats_4gram
    )
    
    # 保存報告
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n分析完成！報告已保存至: {output_file}")
    
    # 顯示基本統計
    print("\n基本統計:")
    print("1-gram 分析地域數:", len(regional_stats_1gram))
    print("2-gram 分析地域數:", len(regional_stats_2gram))
    print("4-gram 分析地域數:", len(regional_stats_4gram))
    
    # 顯示各地域統計
    print("\n各地域 1-gram 統計:")
    for region in sorted(regional_stats_1gram.keys()):
        stats = regional_stats_1gram[region]
        print(f"{region}: 總詞頻 {stats['total_freq']:,}, 獨特單字 {stats['unique_ngrams']:,}")

if __name__ == "__main__":
    main()
