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

def extract_poem_count(poet_info):
    """從詩人信息中提取詩歌數量"""
    if pd.isna(poet_info):
        return 0
    
    poet_str = str(poet_info)
    
    # 查找數字
    numbers = re.findall(r'(\d+(?:,\d+)*)', poet_str)
    if numbers:
        count_str = numbers[0].replace(',', '')
        try:
            return int(count_str)
        except ValueError:
            return 0
    
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
    
    # 重新命名列
    df.columns = ['poet_info', 'poem_count_raw', 'gender_raw', 'birth_death', 'col4', 'col5', 'geography', 'background', 'official_years', 'col9', 'col10']
    
    # 提取詩歌數量 - 從第一列提取
    df['poem_count'] = df['poet_info'].apply(extract_poem_count)
    
    # 提取地域信息
    df['region'] = df['geography'].apply(extract_region)
    
    # 清理性別數據 - 從第二列提取
    df['gender_clean'] = df['poem_count_raw'].str.strip().str.lower()
    df['gender_clean'] = df['gender_clean'].replace({'male': '男', 'female': '女'})
    
    # 如果第二列不是性別，則從第三列提取
    if not df['gender_clean'].isin(['男', '女']).any():
        df['gender_clean'] = df['gender_raw'].str.strip().str.lower()
        df['gender_clean'] = df['gender_clean'].replace({'male': '男', 'female': '女'})
    
    # 過濾掉無效的性別數據
    df = df[df['gender_clean'].isin(['男', '女'])]
    
    print(f"過濾後有效記錄: {len(df)} 條")
    
    if len(df) == 0:
        print("沒有找到有效的性別數據，嘗試其他方法...")
        
        # 重新讀取並手動處理
        df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
        
        # 創建新的數據框
        processed_data = []
        
        for i, row in df.iterrows():
            poet_info = str(row.iloc[0])  # 第一列
            gender_info = str(row.iloc[1])  # 第二列
            geography_info = str(row.iloc[6]) if len(row) > 6 else "未知"  # 第7列
            
            # 提取詩歌數量
            poem_count = extract_poem_count(poet_info)
            
            # 提取性別
            gender = "男" if gender_info.lower() == "male" else "女" if gender_info.lower() == "female" else None
            
            # 提取地域
            region = extract_region(geography_info)
            
            if gender and poem_count > 0:
                processed_data.append({
                    'poet_name': poet_info.split(':')[0].strip() if ':' in poet_info else poet_info,
                    'gender': gender,
                    'region': region,
                    'poem_count': poem_count
                })
        
        df = pd.DataFrame(processed_data)
        print(f"處理後有效記錄: {len(df)} 條")
    
    if len(df) == 0:
        print("無法處理數據，請檢查CSV文件格式")
        return
    
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
    
    top_poets = df.nlargest(20, 'poem_count')[['poet_info', 'gender_clean', 'region', 'poem_count']]
    for i, (_, row) in enumerate(top_poets.iterrows(), 1):
        poet_name = str(row['poet_info']).split(':')[0].strip() if ':' in str(row['poet_info']) else str(row['poet_info'])
        markdown_content += f"| {i} | {poet_name} | {row['gender_clean']} | {row['region']} | {row['poem_count']:,} |\n"
    
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
