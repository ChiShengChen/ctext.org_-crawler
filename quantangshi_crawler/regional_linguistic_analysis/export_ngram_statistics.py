#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
導出N-gram統計數據
將1-gram、2-gram、4-gram的全部用字與數量統計分別存成3份文件
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

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

def export_ngram_statistics():
    """導出N-gram統計數據到3份文件"""
    print("=" * 80)
    print("🔍 導出N-gram統計數據")
    print("=" * 80)
    
    # 1. 載入N-gram數據
    ngram_data = load_ngram_data()
    if not ngram_data:
        return
    
    # 2. 導出1-gram統計
    if '1gram' in ngram_data:
        print(f"\n📊 導出1-gram統計...")
        df = ngram_data['1gram']
        
        # 基本統計
        total_unique_words = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_words if total_unique_words > 0 else 0
        
        # 生成統計報告
        report_content = []
        report_content.append("# 1-gram (單字) 完整統計報告")
        report_content.append("")
        report_content.append("## 📊 基本統計")
        report_content.append("")
        report_content.append(f"- **總用字數**: {total_unique_words:,} 個")
        report_content.append(f"- **總詞頻**: {total_frequency:,} 次")
        report_content.append(f"- **平均詞頻**: {avg_frequency:.2f} 次")
        report_content.append(f"- **最高詞頻**: {df['詞頻'].max():,} 次")
        report_content.append(f"- **最低詞頻**: {df['詞頻'].min():,} 次")
        report_content.append("")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        report_content.append("## 📈 詞頻分布統計")
        report_content.append("")
        report_content.append(f"- **最小值**: {freq_stats['min']:.0f}")
        report_content.append(f"- **25%分位數**: {freq_stats['25%']:.0f}")
        report_content.append(f"- **中位數**: {freq_stats['50%']:.0f}")
        report_content.append(f"- **75%分位數**: {freq_stats['75%']:.0f}")
        report_content.append(f"- **最大值**: {freq_stats['max']:.0f}")
        report_content.append(f"- **標準差**: {freq_stats['std']:.2f}")
        report_content.append("")
        
        # 前100個高頻字
        top_words = df.nlargest(100, '詞頻')
        report_content.append("## 🔤 前100個高頻1-gram")
        report_content.append("")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            report_content.append(f"{i:3d}. **{row['字詞']}** - {row['詞頻']:,} 次")
        report_content.append("")
        
        # 保存文件
        output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/1gram_完整統計報告.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"✅ 1-gram統計已保存: {output_file}")
    
    # 3. 導出2-gram統計
    if '2gram' in ngram_data:
        print(f"\n📊 導出2-gram統計...")
        df = ngram_data['2gram']
        
        # 基本統計
        total_unique_phrases = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_phrases if total_unique_phrases > 0 else 0
        
        # 生成統計報告
        report_content = []
        report_content.append("# 2-gram (雙字詞組) 完整統計報告")
        report_content.append("")
        report_content.append("## 📊 基本統計")
        report_content.append("")
        report_content.append(f"- **總詞組數**: {total_unique_phrases:,} 個")
        report_content.append(f"- **總詞頻**: {total_frequency:,} 次")
        report_content.append(f"- **平均詞頻**: {avg_frequency:.2f} 次")
        report_content.append(f"- **最高詞頻**: {df['詞頻'].max():,} 次")
        report_content.append(f"- **最低詞頻**: {df['詞頻'].min():,} 次")
        report_content.append("")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        report_content.append("## 📈 詞頻分布統計")
        report_content.append("")
        report_content.append(f"- **最小值**: {freq_stats['min']:.0f}")
        report_content.append(f"- **25%分位數**: {freq_stats['25%']:.0f}")
        report_content.append(f"- **中位數**: {freq_stats['50%']:.0f}")
        report_content.append(f"- **75%分位數**: {freq_stats['75%']:.0f}")
        report_content.append(f"- **最大值**: {freq_stats['max']:.0f}")
        report_content.append(f"- **標準差**: {freq_stats['std']:.2f}")
        report_content.append("")
        
        # 前100個高頻詞組
        top_phrases = df.nlargest(100, '詞頻')
        report_content.append("## 🔤 前100個高頻2-gram")
        report_content.append("")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            report_content.append(f"{i:3d}. **{row['字詞']}** - {row['詞頻']:,} 次")
        report_content.append("")
        
        # 保存文件
        output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/2gram_完整統計報告.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"✅ 2-gram統計已保存: {output_file}")
    
    # 4. 導出4-gram統計
    if '4gram' in ngram_data:
        print(f"\n📊 導出4-gram統計...")
        df = ngram_data['4gram']
        
        # 基本統計
        total_unique_phrases = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_phrases if total_unique_phrases > 0 else 0
        
        # 生成統計報告
        report_content = []
        report_content.append("# 4-gram (四字詞組) 完整統計報告")
        report_content.append("")
        report_content.append("## 📊 基本統計")
        report_content.append("")
        report_content.append(f"- **總詞組數**: {total_unique_phrases:,} 個")
        report_content.append(f"- **總詞頻**: {total_frequency:,} 次")
        report_content.append(f"- **平均詞頻**: {avg_frequency:.2f} 次")
        report_content.append(f"- **最高詞頻**: {df['詞頻'].max():,} 次")
        report_content.append(f"- **最低詞頻**: {df['詞頻'].min():,} 次")
        report_content.append("")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        report_content.append("## 📈 詞頻分布統計")
        report_content.append("")
        report_content.append(f"- **最小值**: {freq_stats['min']:.0f}")
        report_content.append(f"- **25%分位數**: {freq_stats['25%']:.0f}")
        report_content.append(f"- **中位數**: {freq_stats['50%']:.0f}")
        report_content.append(f"- **75%分位數**: {freq_stats['75%']:.0f}")
        report_content.append(f"- **最大值**: {freq_stats['max']:.0f}")
        report_content.append(f"- **標準差**: {freq_stats['std']:.2f}")
        report_content.append("")
        
        # 前100個高頻詞組
        top_phrases = df.nlargest(100, '詞頻')
        report_content.append("## 🔤 前100個高頻4-gram")
        report_content.append("")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            report_content.append(f"{i:3d}. **{row['字詞']}** - {row['詞頻']:,} 次")
        report_content.append("")
        
        # 保存文件
        output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/4gram_完整統計報告.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"✅ 4-gram統計已保存: {output_file}")
    
    # 5. 生成總結報告
    print(f"\n📋 生成總結報告...")
    summary_content = []
    summary_content.append("# N-gram 完整統計總結報告")
    summary_content.append("")
    summary_content.append("## 📊 統計摘要")
    summary_content.append("")
    
    for ngram_type in ['1gram', '2gram', '4gram']:
        if ngram_type in ngram_data:
            df = ngram_data[ngram_type]
            total_unique = df['字詞'].nunique()
            total_freq = df['詞頻'].sum()
            avg_freq = total_freq / total_unique
            
            summary_content.append(f"### {ngram_type.upper()}")
            summary_content.append(f"- **總詞組數**: {total_unique:,} 個")
            summary_content.append(f"- **總詞頻**: {total_freq:,} 次")
            summary_content.append(f"- **平均詞頻**: {avg_freq:.2f} 次")
            summary_content.append("")
    
    summary_content.append("## 📁 生成的文件")
    summary_content.append("")
    summary_content.append("1. **1gram_完整統計報告.md** - 1-gram完整統計")
    summary_content.append("2. **2gram_完整統計報告.md** - 2-gram完整統計")
    summary_content.append("3. **4gram_完整統計報告.md** - 4-gram完整統計")
    summary_content.append("")
    summary_content.append("---")
    summary_content.append("")
    summary_content.append("**生成時間**: 2024年10月13日")
    summary_content.append("**數據來源**: 全唐詩N-gram分析結果")
    summary_content.append("**分析方法**: 完整統計分析")
    
    # 保存總結報告
    summary_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis/Ngram_完整統計總結.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_content))
    
    print(f"✅ 總結報告已保存: {summary_file}")
    print(f"\n🎯 所有N-gram統計數據已成功導出！")

def main():
    """主函數"""
    try:
        export_ngram_statistics()
    except Exception as e:
        print(f"❌ 導出過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
