#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
綜合詩人分析：結合基本統計與 n-gram 詞頻分析
"""

import pandas as pd
import numpy as np
from collections import Counter
import re

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
    def extract_poem_count(text):
        if pd.isna(text):
            return 0
        text_str = str(text)
        if '首' in text_str:
            if ':' in text_str:
                after_colon = text_str.split(':')[1]
                numbers = re.findall(r'(\d+(?:,\d+)*)', after_colon)
                if numbers:
                    return int(numbers[0].replace(',', ''))
            else:
                numbers = re.findall(r'(\d+(?:,\d+)*)\s*首', text_str)
                if numbers:
                    return int(numbers[0].replace(',', ''))
        return 0
    
    df['poem_count'] = df['詩人'].apply(extract_poem_count)
    
    # 清理性別數據
    df['gender_clean'] = df['性別'].str.strip().str.lower()
    df['gender_clean'] = df['gender_clean'].replace({'male': '男', 'female': '女'})
    df['gender_clean'] = df['gender_clean'].where(df['gender_clean'].isin(['男', '女']), '未知')
    
    return df

def analyze_ngrams(ngram_file, poet_region_map):
    """分析 n-gram 數據"""
    print(f"正在分析 {ngram_file}...")
    
    # 載入 n-gram 數據
    df = pd.read_csv(ngram_file)
    
    # 為每個 n-gram 記錄添加地域信息
    df['region'] = df['詩人'].map(poet_region_map).fillna('未知')
    
    # 計算總詞頻
    total_freq = df['詞頻'].sum()
    
    # 按詞頻排序，取前100
    top_100 = df.nlargest(100, '詞頻')
    
    return {
        'total_freq': total_freq,
        'unique_ngrams': len(df),
        'top_100': top_100
    }

def generate_comprehensive_report():
    """生成綜合報告"""
    
    # 載入詩人數據
    print("載入詩人數據...")
    df = load_poet_geo_data()
    
    # 創建詩人-地域映射
    poet_region_map = dict(zip(df['poet_name'], df['region']))
    
    # 基本統計
    total_poets = len(df)
    total_poems = df['poem_count'].sum()
    
    # 性別統計
    gender_stats = df['gender_clean'].value_counts()
    
    # 地域統計
    region_stats = df['region'].value_counts()
    
    # 按性別和地域的交叉統計
    cross_stats = pd.crosstab(df['gender_clean'], df['region'], margins=True)
    
    # 按性別的詩歌數量統計
    gender_poem_stats = df.groupby('gender_clean')['poem_count'].agg(['count', 'sum', 'mean', 'median']).round(2)
    
    # 按地域的詩歌數量統計
    region_poem_stats = df.groupby('region')['poem_count'].agg(['count', 'sum', 'mean', 'median']).round(2)
    
    # 分析 n-gram 數據
    print("分析 1-gram 數據...")
    ngram_1gram = analyze_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_1gram_詞頻統計.csv',
        poet_region_map
    )
    
    print("分析 2-gram 數據...")
    ngram_2gram = analyze_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_2gram_詞頻統計.csv',
        poet_region_map
    )
    
    print("分析 4-gram 數據...")
    ngram_4gram = analyze_ngrams(
        '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs/merged_4gram_詞頻統計.csv',
        poet_region_map
    )
    
    # 生成 Markdown 報告
    markdown_content = f"""# 詩人性別、地域與詩的數量統計分析

## 基本統計

- **總詩人數**: {total_poets:,} 人
- **總詩歌數**: {total_poems:,} 首
- **平均每人詩歌數**: {total_poems/total_poets:.1f} 首

## 性別分布

| 性別 | 人數 | 百分比 | 詩歌總數 | 平均每人詩歌數 |
|------|------|--------|----------|----------------|
"""
    
    for gender in gender_stats.index:
        count = gender_stats[gender]
        percentage = (count / total_poets) * 100
        poems = df[df['gender_clean'] == gender]['poem_count'].sum()
        avg_poems = poems / count if count > 0 else 0
        markdown_content += f"| {gender} | {count:,} | {percentage:.1f}% | {poems:,} | {avg_poems:.1f} |\n"
    
    markdown_content += f"""
## 地域分布

| 地域 | 詩人數 | 百分比 | 詩歌總數 | 平均每人詩歌數 |
|------|--------|--------|----------|----------------|
"""
    
    for region in region_stats.index:
        count = region_stats[region]
        percentage = (count / total_poets) * 100
        poems = df[df['region'] == region]['poem_count'].sum()
        avg_poems = poems / count if count > 0 else 0
        markdown_content += f"| {region} | {count:,} | {percentage:.1f}% | {poems:,} | {avg_poems:.1f} |\n"
    
    markdown_content += f"""
## 性別與地域交叉統計

| 地域 \\ 性別 | 男 | 女 | 未知 | 總計 |
|-------------|----|----|----|----|
"""
    
    for region in cross_stats.columns[:-1]:  # 排除 'All' 列
        if region != 'All':
            male_count = cross_stats.loc['男', region] if '男' in cross_stats.index else 0
            female_count = cross_stats.loc['女', region] if '女' in cross_stats.index else 0
            unknown_count = cross_stats.loc['未知', region] if '未知' in cross_stats.index else 0
            total_count = cross_stats.loc['All', region]
            markdown_content += f"| {region} | {male_count} | {female_count} | {unknown_count} | {total_count} |\n"
    
    markdown_content += f"""
## 詳細統計表

### 按性別統計
"""
    
    markdown_content += gender_poem_stats.to_markdown()
    
    markdown_content += f"""

### 按地域統計
"""
    
    markdown_content += region_poem_stats.to_markdown()
    
    markdown_content += f"""

## 前20名詩歌數量最多的詩人

| 排名 | 詩人 | 性別 | 地域 | 詩歌數量 |
|------|------|------|------|----------|
"""
    
    top_poets = df.nlargest(20, 'poem_count')[['poet_name', 'gender_clean', 'region', 'poem_count']]
    for i, (_, row) in enumerate(top_poets.iterrows(), 1):
        markdown_content += f"| {i} | {row['poet_name']} | {row['gender_clean']} | {row['region']} | {row['poem_count']:,} |\n"
    
    # 添加 n-gram 分析
    markdown_content += f"""

## 全部詩人詞頻統計分析

### 1-gram（單字）前100名詞頻統計

- **總詞頻**: {ngram_1gram['total_freq']:,}
- **獨特單字數**: {ngram_1gram['unique_ngrams']:,}

| 排名 | 單字 | 詞頻 |
|------|------|------|
"""
    
    for i, (_, row) in enumerate(ngram_1gram['top_100'].iterrows(), 1):
        markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
    
    markdown_content += f"""

### 2-gram（雙字詞）前100名詞頻統計

- **總詞頻**: {ngram_2gram['total_freq']:,}
- **獨特雙字詞數**: {ngram_2gram['unique_ngrams']:,}

| 排名 | 雙字詞 | 詞頻 |
|------|--------|------|
"""
    
    for i, (_, row) in enumerate(ngram_2gram['top_100'].iterrows(), 1):
        markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
    
    markdown_content += f"""

### 4-gram（四字詞）前100名詞頻統計

- **總詞頻**: {ngram_4gram['total_freq']:,}
- **獨特四字詞數**: {ngram_4gram['unique_ngrams']:,}

| 排名 | 四字詞 | 詞頻 |
|------|--------|------|
"""
    
    for i, (_, row) in enumerate(ngram_4gram['top_100'].iterrows(), 1):
        markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
    
    markdown_content += f"""

## 分析結論

1. **性別分布**: 男性詩人佔絕大多數，這反映了古代中國文學創作的性別特徵。
2. **地域分布**: 江南道和關內道是詩人最集中的地區，這與唐代政治文化中心的地理分布相符。
3. **詩歌產量**: 不同地域和性別的詩人在詩歌產量上存在差異，反映了社會文化背景的影響。
4. **數據完整性**: 包含所有詩人記錄，包括沒有標注性別的詩人，提供更全面的統計分析。
5. **詞頻分析**: 通過 n-gram 分析揭示了詩人用字的整體特徵和偏好。

---
*統計時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return markdown_content

def main():
    print("開始綜合詩人分析...")
    
    # 生成綜合報告
    markdown_content = generate_comprehensive_report()
    
    # 保存報告
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_statistics_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n綜合分析完成！報告已保存至: {output_file}")
    
    # 顯示基本統計
    print("\n分析完成，包含：")
    print("- 詩人基本統計")
    print("- 性別分布分析")
    print("- 地域分布分析")
    print("- 1-gram 前100名詞頻統計")
    print("- 2-gram 前100名詞頻統計")
    print("- 4-gram 前100名詞頻統計")

if __name__ == "__main__":
    main()
