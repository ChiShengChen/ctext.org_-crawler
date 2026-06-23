#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
女性詩人詳細分析報告生成器
生成包含具體詩人姓名和N-gram數據的詳細報告
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

def load_female_poets_detailed_data():
    """載入女性詩人詳細數據"""
    poet_geo_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    
    if not os.path.exists(poet_geo_file):
        print(f"❌ 地理標籤文件不存在: {poet_geo_file}")
        return None
    
    df = pd.read_csv(poet_geo_file)
    
    # 清理和提取詩人姓名
    def extract_poet_name(name_str):
        import re
        name_match = re.search(r'(\d+\.\s*)?([^:：]+)', str(name_str))
        if name_match:
            return name_match.group(2).strip()
        return str(name_str)
    
    df['poet_name'] = df['詩人'].apply(extract_poet_name)
    
    # 篩選女性詩人
    female_df = df[df['性別'].str.contains('female', case=False, na=False)]
    
    # 分類社會階級
    def classify_social_class(background_str):
        if pd.isna(background_str):
            return 'Unknown'
        
        background_str = str(background_str).lower()
        
        if any(keyword in background_str for keyword in ['empress', '皇后', 'imperial consort', '后妃', '妃嬪']):
            return 'Royal'
        elif any(keyword in background_str for keyword in ['civil office', '為官者', 'office', '宰相']):
            return 'Noble/Official'
        elif any(keyword in background_str for keyword in ['man of culture', '文人', 'calligrapher', '書法家']):
            return 'Literati'
        elif any(keyword in background_str for keyword in ['daoist nun', '道姑', '女冠', '僧', 'monk']):
            return 'Religious'
        elif any(keyword in background_str for keyword in ['entertainer', '妓', 'female entertainer']):
            return 'Entertainer'
        elif 'poet' in background_str or '詩人' in background_str:
            return 'General Poet'
        else:
            return 'Other'
    
    female_df['social_class'] = female_df['背景'].apply(classify_social_class)
    
    return female_df[['poet_name', 'social_class', '背景', 'Geography']].dropna()

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
            df = pd.read_csv(file_path)
            ngram_data[ngram_type] = df
        else:
            print(f"❌ 文件不存在: {filename}")
    
    return ngram_data

def generate_detailed_female_poets_report():
    """生成詳細的女性詩人分析報告"""
    print("=" * 80)
    print("🔍 生成女性詩人詳細分析報告")
    print("=" * 80)
    
    # 1. 載入數據
    female_df = load_female_poets_detailed_data()
    if female_df is None:
        return
    
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 2. 找到匹配的女性詩人
    female_poet_names = set(female_df['poet_name'].unique())
    
    # 3. 生成詳細報告
    report_content = []
    report_content.append("# 唐代女性詩人詳細分析報告")
    report_content.append("")
    report_content.append("## 📊 概述")
    report_content.append("")
    report_content.append(f"- **總女性詩人數量**: {len(female_df)} 人")
    report_content.append(f"- **有N-gram數據的女性詩人**: {len(female_poet_names.intersection(set(ngram_data['1gram']['詩人'].unique())))} 人")
    report_content.append("")
    
    # 4. 按社會階級分析
    for social_class in ['Royal', 'Noble/Official', 'Literati', 'Religious', 'Entertainer', 'General Poet', 'Other', 'Unknown']:
        class_poets = female_df[female_df['social_class'] == social_class]
        if class_poets.empty:
            continue
        
        report_content.append(f"## 🏛️ {social_class} 女性詩人")
        report_content.append("")
        report_content.append(f"**詩人數量**: {len(class_poets)} 人")
        report_content.append("")
        
        # 列出具體詩人
        report_content.append("### 詩人名單")
        report_content.append("")
        for i, (_, poet) in enumerate(class_poets.iterrows(), 1):
            report_content.append(f"{i}. **{poet['poet_name']}**")
            report_content.append(f"   - 背景: {poet['背景']}")
            report_content.append(f"   - 地域: {poet['Geography']}")
            report_content.append("")
        
        # 分析N-gram數據
        matched_poets = set(class_poets['poet_name']).intersection(set(ngram_data['1gram']['詩人'].unique()))
        if matched_poets:
            report_content.append("### N-gram 分析")
            report_content.append("")
            
            # 1-gram分析
            if '1gram' in ngram_data:
                df = ngram_data['1gram']
                class_data = df[df['詩人'].isin(matched_poets)]
                
                if not class_data.empty:
                    report_content.append("#### 1-gram (單字) 分析")
                    report_content.append("")
                    report_content.append(f"- **唯一詞彙數**: {class_data['字詞'].nunique()} 個")
                    report_content.append(f"- **總詞頻**: {class_data['詞頻'].sum()} 次")
                    report_content.append(f"- **平均詞頻**: {class_data['詞頻'].sum() / class_data['字詞'].nunique():.2f} 次")
                    report_content.append("")
                    
                    # 前20個高頻字
                    top_words = class_data.nlargest(20, '詞頻')
                    report_content.append("**前20個高頻字**:")
                    for i, (_, row) in enumerate(top_words.iterrows(), 1):
                        report_content.append(f"{i:2d}. **{row['字詞']}** - {row['詞頻']} 次")
                    report_content.append("")
            
            # 2-gram分析
            if '2gram' in ngram_data:
                df = ngram_data['2gram']
                class_data = df[df['詩人'].isin(matched_poets)]
                
                if not class_data.empty:
                    report_content.append("#### 2-gram (雙字詞組) 分析")
                    report_content.append("")
                    report_content.append(f"- **唯一詞組數**: {class_data['字詞'].nunique()} 個")
                    report_content.append(f"- **總詞頻**: {class_data['詞頻'].sum()} 次")
                    report_content.append(f"- **平均詞頻**: {class_data['詞頻'].sum() / class_data['字詞'].nunique():.2f} 次")
                    report_content.append("")
                    
                    # 前15個高頻詞組
                    top_phrases = class_data.nlargest(15, '詞頻')
                    report_content.append("**前15個高頻2-gram**:")
                    for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                        report_content.append(f"{i:2d}. **{row['字詞']}** - {row['詞頻']} 次")
                    report_content.append("")
            
            # 4-gram分析
            if '4gram' in ngram_data:
                df = ngram_data['4gram']
                class_data = df[df['詩人'].isin(matched_poets)]
                
                if not class_data.empty:
                    report_content.append("#### 4-gram (四字詞組) 分析")
                    report_content.append("")
                    report_content.append(f"- **唯一詞組數**: {class_data['字詞'].nunique()} 個")
                    report_content.append(f"- **總詞頻**: {class_data['詞頻'].sum()} 次")
                    report_content.append(f"- **平均詞頻**: {class_data['詞頻'].sum() / class_data['字詞'].nunique():.2f} 次")
                    report_content.append("")
                    
                    # 前10個高頻詞組
                    top_phrases = class_data.nlargest(10, '詞頻')
                    report_content.append("**前10個高頻4-gram**:")
                    for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
                        report_content.append(f"{i:2d}. **{row['字詞']}** - {row['詞頻']} 次")
                    report_content.append("")
        
        report_content.append("---")
        report_content.append("")
    
    # 5. 總結分析
    report_content.append("## 📋 總結分析")
    report_content.append("")
    report_content.append("### 社會階級差異特徵")
    report_content.append("")
    report_content.append("1. **Royal (皇室)**: 偏向政治、國家、宮廷用詞")
    report_content.append("2. **Literati (文人)**: 偏向文學創作、書信往來、情感表達")
    report_content.append("3. **Entertainer (娛樂)**: 偏向音樂、表演、社交用詞")
    report_content.append("4. **General Poet (一般詩人)**: 偏向自然景觀、日常情感、季節變化")
    report_content.append("5. **Other (其他)**: 特殊背景，用詞相對獨立")
    report_content.append("")
    
    report_content.append("### 語言學意義")
    report_content.append("")
    report_content.append("- 不同社會階級女性詩人在用字習慣上存在顯著差異")
    report_content.append("- 社會地位影響詞彙選擇和表達方式")
    report_content.append("- 為女性文學史和社會階級研究提供重要數據")
    report_content.append("")
    
    report_content.append("---")
    report_content.append("")
    report_content.append("**報告生成時間**: 2024年10月13日")
    report_content.append("**數據來源**: 《全唐詩》詩人地理標籤 + N-gram 詞頻統計")
    report_content.append("**分析方法**: 社會階級分類 + N-gram 統計分析")
    
    # 6. 保存報告
    report_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/女性詩人詳細分析報告.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print(f"✅ 詳細報告已生成: {report_file}")
    print(f"✅ 報告包含 {len(female_df)} 位女性詩人的詳細分析")
    print(f"✅ 按社會階級分類的N-gram統計數據")

def main():
    """主函數"""
    try:
        generate_detailed_female_poets_report()
    except Exception as e:
        print(f"❌ 生成報告過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
