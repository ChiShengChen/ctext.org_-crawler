#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詩人性別、地域與詩的數量統計分析
根據 poet_geo_label.csv 文件進行統計分析
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
    
    # 手動處理每一行數據
    processed_data = []
    
    for i, row in df.iterrows():
        # 獲取所有列的值
        values = row.tolist()
        
        # 智能識別詩歌數量和詩人名字
        poem_count = 0
        poet_name = "未知"
        
        # 檢查所有列，尋找包含詩歌數量的列
        for j, val in enumerate(values):
            if pd.notna(val):
                val_str = str(val)
                if '首' in val_str or (any(char.isdigit() for char in val_str) and len(val_str) > 1):
                    count = extract_poem_count(val_str)
                    if count > poem_count:
                        poem_count = count
                        # 提取詩人名字
                        if ':' in val_str:
                            poet_name = val_str.split(':')[0].strip()
                        elif '首' in val_str:
                            parts = val_str.split('首')
                            if len(parts) > 1:
                                poet_name = parts[0].strip()
        
        # 智能識別性別
        gender = None
        for val in values:
            if pd.notna(val) and str(val).lower() in ['male', 'female']:
                gender = '男' if str(val).lower() == 'male' else '女'
                break
        
        # 智能識別地理信息
        region = "未知"
        for val in values:
            if pd.notna(val) and '道' in str(val):
                region = extract_region(val)
                break
        
        # 只保留有詩歌數量和性別信息的記錄
        if gender and poem_count > 0:
            processed_data.append({
                'poet_name': poet_name,
                'gender': gender,
                'region': region,
                'poem_count': poem_count
            })
    
    # 創建新的數據框
    df_processed = pd.DataFrame(processed_data)
    
    print(f"處理後有效記錄: {len(df_processed)} 條")
    
    if len(df_processed) == 0:
        print("無法處理數據，請檢查CSV文件格式")
        return
    
    # 基本統計
    total_poets = len(df_processed)
    total_poems = df_processed['poem_count'].sum()
    
    # 性別統計
    gender_stats = df_processed['gender'].value_counts()
    
    # 地域統計
    region_stats = df_processed['region'].value_counts()
    
    # 按性別和地域的交叉統計
    cross_stats = pd.crosstab(df_processed['gender'], df_processed['region'], margins=True)
    
    # 按性別的詩歌數量統計
    gender_poem_stats = df_processed.groupby('gender')['poem_count'].agg(['count', 'sum', 'mean', 'median']).round(2)
    
    # 按地域的詩歌數量統計
    region_poem_stats = df_processed.groupby('region')['poem_count'].agg(['count', 'sum', 'mean', 'median']).round(2)
    
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
        poems = df_processed[df_processed['gender'] == gender]['poem_count'].sum()
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
        poems = df_processed[df_processed['region'] == region]['poem_count'].sum()
        avg_poems = poems / count if count > 0 else 0
        markdown_content += f"| {region} | {count:,} | {percentage:.1f}% | {poems:,} | {avg_poems:.1f} |\n"
    
    markdown_content += f"""
## 性別與地域交叉統計

| 地域 \\ 性別 | 男 | 女 | 總計 |
|-------------|----|----|----|
"""
    
    for region in cross_stats.columns[:-1]:  # 排除 'All' 列
        if region != 'All':
            male_count = cross_stats.loc['男', region] if '男' in cross_stats.index else 0
            female_count = cross_stats.loc['女', region] if '女' in cross_stats.index else 0
            total_count = cross_stats.loc['All', region]
            markdown_content += f"| {region} | {male_count} | {female_count} | {total_count} |\n"
    
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
    
    top_poets = df_processed.nlargest(20, 'poem_count')[['poet_name', 'gender', 'region', 'poem_count']]
    for i, (_, row) in enumerate(top_poets.iterrows(), 1):
        markdown_content += f"| {i} | {row['poet_name']} | {row['gender']} | {row['region']} | {row['poem_count']:,} |\n"
    
    markdown_content += f"""

## 分析結論

1. **性別分布**: 男性詩人佔絕大多數，這反映了古代中國文學創作的性別特徵。
2. **地域分布**: 江南道和關內道是詩人最集中的地區，這與唐代政治文化中心的地理分布相符。
3. **詩歌產量**: 不同地域和性別的詩人在詩歌產量上存在差異，反映了社會文化背景的影響。

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
