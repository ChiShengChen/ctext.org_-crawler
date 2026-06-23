#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詩人性別、地域與詩的數量統計分析
根據修正後的 poet_geo_label.csv 文件進行統計分析
包含所有詩人，包括沒有標注性別的詩人
"""

import pandas as pd
import re
import numpy as np
from collections import Counter

def extract_poem_count(text):
    """從文本中提取詩歌數量"""
    if pd.isna(text):
        return 0
    
    text_str = str(text)
    
    # 查找所有數字
    numbers = re.findall(r'(\d+(?:,\d+)*)', text_str)
    if numbers:
        # 取最大的數字（通常是詩歌數量）
        max_num = 0
        for num_str in numbers:
            num = int(num_str.replace(',', ''))
            if num > max_num:
                max_num = num
        return max_num
    
    return 0

def extract_poet_name(text):
    """從文本中提取詩人名字"""
    if pd.isna(text):
        return "未知"
    
    text_str = str(text)
    
    # 提取詩人名字
    if ':' in text_str:
        return text_str.split(':')[0].strip()
    elif '首' in text_str:
        parts = text_str.split('首')
        if len(parts) > 1:
            return parts[0].strip()
    
    return text_str.strip()

def extract_region(geography):
    """從地理信息中提取主要地域"""
    if pd.isna(geography):
        return "未知"
    
    geo_str = str(geography)
    
    # 提取主要地域
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

def main():
    # 讀取 CSV 文件
    print("正在讀取數據...")
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    print(f"總共讀取 {len(df)} 條詩人記錄")
    
    # 提取詩歌數量
    df['poem_count'] = df['詩人'].apply(extract_poem_count)
    
    # 提取詩人名字
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 提取地域信息
    df['region'] = df['Geography'].apply(extract_region)
    
    # 清理性別數據，保留所有記錄
    df['gender_clean'] = df['性別'].str.strip().str.lower()
    df['gender_clean'] = df['gender_clean'].replace({'male': '男', 'female': '女'})
    
    # 將無效的性別標記為"未知"
    df['gender_clean'] = df['gender_clean'].where(df['gender_clean'].isin(['男', '女']), '未知')
    
    print(f"處理後記錄: {len(df)} 條")
    
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
    
    markdown_content += f"""

## 分析結論

1. **性別分布**: 男性詩人佔絕大多數，這反映了古代中國文學創作的性別特徵。
2. **地域分布**: 江南道和關內道是詩人最集中的地區，這與唐代政治文化中心的地理分布相符。
3. **詩歌產量**: 不同地域和性別的詩人在詩歌產量上存在差異，反映了社會文化背景的影響。
4. **數據完整性**: 包含所有詩人記錄，包括沒有標注性別的詩人，提供更全面的統計分析。

---
*統計時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存 Markdown 文件
    with open('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_statistics_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("統計分析完成！")
    print(f"Markdown 報告已保存至: poet_statistics_report.md")
    
    # 顯示基本統計信息
    print(f"\n基本統計:")
    print(f"總詩人數: {total_poets:,}")
    print(f"總詩歌數: {total_poems:,}")
    print(f"平均每人詩歌數: {total_poems/total_poets:.1f}")
    
    print(f"\n性別分布:")
    for gender in gender_stats.index:
        count = gender_stats[gender]
        percentage = (count / total_poets) * 100
        print(f"{gender}: {count:,} 人 ({percentage:.1f}%)")
    
    print(f"\n地域分布 (前10名):")
    for region in region_stats.head(10).index:
        count = region_stats[region]
        percentage = (count / total_poets) * 100
        print(f"{region}: {count:,} 人 ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
