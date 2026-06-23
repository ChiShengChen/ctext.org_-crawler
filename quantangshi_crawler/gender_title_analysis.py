#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
男女詩人詩題詞頻分析
只統計詩歌標題，不包含內容
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import re
import os

def load_poet_gender_data():
    """載入詩人性別數據"""
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    # 提取詩人名字
    def extract_poet_name(text):
        if pd.isna(text):
            return "未知"
        text_str = str(text)
        
        # 處理格式如 "1. 白居易: 2600 首"
        if re.match(r'^\s*\d+\.\s*', text_str):
            text_str = re.sub(r'^\s*\d+\.\s*', '', text_str)
        
        if ':' in text_str:
            return text_str.split(':')[0].strip()
        
        return text_str.strip()
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 提取詩歌數量
    def extract_poem_count(poet_info):
        if pd.isna(poet_info):
            return 0
        poet_str = str(poet_info)
        match = re.search(r':\s*(\d+)\s*首', poet_str)
        if match:
            try:
                return int(match.group(1))
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

def analyze_gender_title_ngrams(ngram_file, df, ngram_type):
    """分析性別詩題 n-gram 特徵"""
    print(f"正在分析詩題 {ngram_type} 數據...")
    
    # 載入 n-gram 數據
    ngram_df = pd.read_csv(ngram_file)
    
    # 創建詩人-性別映射
    poet_gender_map = {}
    for _, row in df.iterrows():
        poet_name = row['poet_name']
        gender = row['gender_clean']
        poem_count = row['poem_count']
        poet_gender_map[poet_name] = {
            'gender': gender,
            'poem_count': poem_count
        }
    
    # 為每個 n-gram 記錄添加性別信息
    ngram_df['gender'] = ngram_df['詩人'].map(lambda x: poet_gender_map.get(x, {}).get('gender', '未知'))
    ngram_df['poem_count'] = ngram_df['詩人'].map(lambda x: poet_gender_map.get(x, {}).get('poem_count', 0))
    
    # 檢查著名詩人
    famous_poets = ['白居易', '杜甫', '李白', '魚玄機', '薛濤']
    print(f"\n檢查 {ngram_type} 中著名詩人詩題匹配情況:")
    for poet in famous_poets:
        poet_data = ngram_df[ngram_df['詩人'] == poet]
        if len(poet_data) > 0:
            gender = poet_data['gender'].iloc[0]
            poem_count = poet_data['poem_count'].iloc[0]
            total_freq = poet_data['詞頻'].sum()
            print(f"  {poet}: {poem_count}首詩, {gender}性, 詩題總詞頻 {total_freq:,}")
        else:
            print(f"  {poet}: 未找到")
    
    # 按性別分組統計
    gender_stats = {}
    
    for gender in ['男', '女', '未知']:
        gender_data = ngram_df[ngram_df['gender'] == gender]
        
        if len(gender_data) == 0:
            continue
        
        # 計算該性別的總詞頻
        total_freq = gender_data['詞頻'].sum()
        
        # 按字詞分組
        word_freq = gender_data.groupby('字詞')['詞頻'].sum().reset_index()
        word_freq = word_freq.sort_values('詞頻', ascending=False)
        
        # 取前500個字詞
        top_500 = word_freq.head(500)
        
        # 獲取該性別的所有詩人名單
        poets_in_gender = gender_data[['詩人', 'poem_count']].drop_duplicates()
        poets_in_gender = poets_in_gender.sort_values('poem_count', ascending=False)
        
        gender_stats[gender] = {
            'total_freq': total_freq,
            'unique_ngrams': len(gender_data),
            'top_500': top_500,
            'poets': poets_in_gender
        }
    
    return gender_stats

def generate_title_markdown_report(gender_stats_1gram, gender_stats_2gram, gender_stats_3gram, 
                                   gender_stats_4gram, gender_stats_5gram, gender_stats_6gram, 
                                   gender_stats_7gram, df):
    """生成詩題分析 Markdown 報告"""
    
    # 基本統計
    total_poets = len(df)
    total_poems = df['poem_count'].sum()
    avg_poems = total_poems / total_poets if total_poets > 0 else 0
    
    # 性別分布統計
    gender_counts = df['gender_clean'].value_counts()
    gender_poems = df.groupby('gender_clean')['poem_count'].sum()
    gender_avg = df.groupby('gender_clean')['poem_count'].mean()
    
    markdown_content = f"""# 男女詩人詩題詞頻分析報告

## 說明

本報告只統計詩歌標題的詞頻，不包含詩歌內容。

## 基本統計

- **總詩人數**: {total_poets:,} 人
- **總詩歌數**: {total_poems:,} 首
- **平均每人詩歌數**: {avg_poems:.1f} 首

## 性別分布

| 性別 | 人數 | 百分比 | 詩歌總數 | 平均每人詩歌數 |
|------|------|--------|----------|----------------|
"""
    
    for gender in ['男', '女', '未知']:
        if gender in gender_counts:
            count = gender_counts[gender]
            percentage = (count / total_poets) * 100
            poems = gender_poems.get(gender, 0)
            avg = gender_avg.get(gender, 0)
            markdown_content += f"| {gender} | {count:,} | {percentage:.1f}% | {poems:,} | {avg:.1f} |\n"
    
    markdown_content += "\n## 1-gram（單字）詩題分析\n\n"
    
    # 1-gram 分析
    for gender in ['男', '女', '未知']:
        if gender in gender_stats_1gram:
            stats = gender_stats_1gram[gender]
            markdown_content += f"### {gender}性詩人詩題\n\n"
            markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
            markdown_content += f"- **獨特單字數**: {stats['unique_ngrams']:,}\n"
            markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
            
            # 顯示詩人名單（前20名）
            markdown_content += "**詩人名單（前20名）**:\n"
            markdown_content += "| 排名 | 詩人姓名 | 詩歌數量 |\n"
            markdown_content += "|------|----------|----------|\n"
            
            for i, (_, poet) in enumerate(stats['poets'].head(20).iterrows(), 1):
                markdown_content += f"| {i} | {poet['詩人']} | {poet['poem_count']:,} |\n"
            
            markdown_content += "\n"
            markdown_content += "**詩題中前100名單字**:\n"
            markdown_content += "| 排名 | 單字 | 詞頻 |\n"
            markdown_content += "|------|------|------|\n"
            
            for i, (_, row) in enumerate(stats['top_500'].head(100).iterrows(), 1):
                markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
            
            markdown_content += "\n"
    
    markdown_content += "## 2-gram（雙字詞）詩題分析\n\n"
    
    # 2-gram 分析
    for gender in ['男', '女', '未知']:
        if gender in gender_stats_2gram:
            stats = gender_stats_2gram[gender]
            markdown_content += f"### {gender}性詩人詩題\n\n"
            markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
            markdown_content += f"- **獨特雙字詞數**: {stats['unique_ngrams']:,}\n"
            markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
            
            markdown_content += "**詩題中前100名雙字詞**:\n"
            markdown_content += "| 排名 | 雙字詞 | 詞頻 |\n"
            markdown_content += "|------|--------|------|\n"
            
            for i, (_, row) in enumerate(stats['top_500'].head(100).iterrows(), 1):
                markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
            
            markdown_content += "\n"

    # 3-gram 分析
    markdown_content += "## 3-gram（三字詞）詩題分析\n\n"
    for gender in ['男', '女', '未知']:
        if gender in gender_stats_3gram:
            stats = gender_stats_3gram[gender]
            markdown_content += f"### {gender}性詩人詩題\n\n"
            markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
            markdown_content += f"- **獨特三字詞數**: {stats['unique_ngrams']:,}\n"
            markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
            
            markdown_content += "**詩題中前100名三字詞**:\n"
            markdown_content += "| 排名 | 三字詞 | 詞頻 |\n"
            markdown_content += "|------|--------|------|\n"
            
            for i, (_, row) in enumerate(stats['top_500'].head(100).iterrows(), 1):
                markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
            
            markdown_content += "\n"
    
    markdown_content += "## 4-gram（四字詞）詩題分析\n\n"
    
    # 4-gram 分析
    for gender in ['男', '女', '未知']:
        if gender in gender_stats_4gram:
            stats = gender_stats_4gram[gender]
            markdown_content += f"### {gender}性詩人詩題\n\n"
            markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
            markdown_content += f"- **獨特四字詞數**: {stats['unique_ngrams']:,}\n"
            markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
            
            markdown_content += "**詩題中前100名四字詞**:\n"
            markdown_content += "| 排名 | 四字詞 | 詞頻 |\n"
            markdown_content += "|------|--------|------|\n"
            
            for i, (_, row) in enumerate(stats['top_500'].head(100).iterrows(), 1):
                markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
            
            markdown_content += "\n"

    # 5-7 gram (簡化版本)
    for n, gender_stats in [(5, gender_stats_5gram), (6, gender_stats_6gram), (7, gender_stats_7gram)]:
        if not gender_stats:
            continue
        
        gram_names = {5: '五字詞', 6: '六字詞', 7: '七字詞'}
        markdown_content += f"## {n}-gram（{gram_names[n]}）詩題分析\n\n"
        
        for gender in ['男', '女', '未知']:
            if gender in gender_stats:
                stats = gender_stats[gender]
                markdown_content += f"### {gender}性詩人詩題\n\n"
                markdown_content += f"- **總詞頻**: {stats['total_freq']:,}\n"
                markdown_content += f"- **獨特{gram_names[n]}數**: {stats['unique_ngrams']:,}\n"
                markdown_content += f"- **詩人數量**: {len(stats['poets'])}\n\n"
                
                markdown_content += f"**詩題中前50名{gram_names[n]}**:\n"
                markdown_content += f"| 排名 | {gram_names[n]} | 詞頻 |\n"
                markdown_content += "|------|--------|------|\n"
                
                for i, (_, row) in enumerate(stats['top_500'].head(50).iterrows(), 1):
                    markdown_content += f"| {i} | {row['字詞']} | {row['詞頻']:,} |\n"
                
                markdown_content += "\n"
    
    markdown_content += """## 分析結論

1. **詩題特色**: 詩題用字相較於詩歌內容更加簡練，反映了標題的功能性
2. **性別差異**: 男女詩人在詩題用字習慣上的差異可能反映不同的題材偏好
3. **常用詞彙**: 詩題常見詞彙如"春"、"秋"、"夜"、"行"、"送"等反映了唐詩常見題材
4. **數據完整性**: 包含所有性別標注的詩人，提供全面的詩題詞頻分析

---
*分析時間: """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
    
    return markdown_content

def main():
    print("開始男女詩人詩題詞頻分析...")
    
    # 載入詩人數據
    print("載入詩人數據...")
    df = load_poet_gender_data()
    
    # 檢查著名詩人
    famous_poets = ['白居易', '杜甫', '李白', '魚玄機', '薛濤']
    print("\n檢查著名詩人:")
    for poet in famous_poets:
        if poet in df['poet_name'].values:
            poem_count = df[df['poet_name'] == poet]['poem_count'].iloc[0]
            gender = df[df['poet_name'] == poet]['gender_clean'].iloc[0]
            print(f"{poet}: {poem_count}首詩, {gender}性")
        else:
            print(f"{poet}: 未找到")
    
    # 顯示性別分布
    gender_counts = df['gender_clean'].value_counts()
    print("\n性別分布:")
    for gender, count in gender_counts.items():
        print(f"{gender}: {count} 人")
    
    base_path = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/title_analysis/author_title_ngram_csvs/'
    
    # 分析 1-gram
    print("\n分析詩題 1-gram 數據...")
    gender_stats_1gram = analyze_gender_title_ngrams(
        base_path + 'merged_title_1gram_詞頻統計.csv',
        df,
        '1-gram'
    )
    
    # 分析 2-gram
    print("\n分析詩題 2-gram 數據...")
    gender_stats_2gram = analyze_gender_title_ngrams(
        base_path + 'merged_title_2gram_詞頻統計.csv',
        df,
        '2-gram'
    )
    
    # 分析 3-gram
    print("\n分析詩題 3-gram 數據...")
    gender_stats_3gram = analyze_gender_title_ngrams(
        base_path + 'merged_title_3gram_詞頻統計.csv',
        df,
        '3-gram'
    )
    
    # 分析 4-gram
    print("\n分析詩題 4-gram 數據...")
    gender_stats_4gram = analyze_gender_title_ngrams(
        base_path + 'merged_title_4gram_詞頻統計.csv',
        df,
        '4-gram'
    )
    
    # 分析 5-7 gram
    try:
        print("\n分析詩題 5-gram 數據...")
        gender_stats_5gram = analyze_gender_title_ngrams(
            base_path + 'merged_title_5gram_詞頻統計.csv',
            df,
            '5-gram'
        )
    except Exception as e:
        print(f"5-gram 資料缺失或讀取失敗: {e}")
        gender_stats_5gram = {}
    
    try:
        print("\n分析詩題 6-gram 數據...")
        gender_stats_6gram = analyze_gender_title_ngrams(
            base_path + 'merged_title_6gram_詞頻統計.csv',
            df,
            '6-gram'
        )
    except Exception as e:
        print(f"6-gram 資料缺失或讀取失敗: {e}")
        gender_stats_6gram = {}
    
    try:
        print("\n分析詩題 7-gram 數據...")
        gender_stats_7gram = analyze_gender_title_ngrams(
            base_path + 'merged_title_7gram_詞頻統計.csv',
            df,
            '7-gram'
        )
    except Exception as e:
        print(f"7-gram 資料缺失或讀取失敗: {e}")
        gender_stats_7gram = {}
    
    # 生成報告
    print("\n生成 Markdown 報告...")
    markdown_content = generate_title_markdown_report(
        gender_stats_1gram,
        gender_stats_2gram,
        gender_stats_3gram,
        gender_stats_4gram,
        gender_stats_5gram,
        gender_stats_6gram,
        gender_stats_7gram,
        df
    )
    
    # 保存報告
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/gender_title_analysis_report.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n分析完成！報告已保存至: {output_file}")
    
    # 顯示基本統計
    print("\n基本統計:")
    for gender in sorted(gender_stats_1gram.keys()):
        stats = gender_stats_1gram[gender]
        print(f"{gender}性: 詩題總詞頻 {stats['total_freq']:,}, 獨特單字 {stats['unique_ngrams']:,}, 詩人 {len(stats['poets'])} 人")

if __name__ == "__main__":
    main()

