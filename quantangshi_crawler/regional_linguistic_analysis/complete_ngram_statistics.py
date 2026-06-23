#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整N-gram統計分析
統計1-gram、2-gram、4-gram的完整總用字數，不只是前50個
"""

import pandas as pd
import json
import os
from collections import Counter
import numpy as np

def load_ngram_data():
    """載入完整的N-gram數據"""
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
            print(f"載入 {ngram_type} 數據: {filename}")
            df = pd.read_csv(file_path)
            ngram_data[ngram_type] = df
            print(f"  - 總行數: {len(df):,}")
            print(f"  - 唯一詞組數: {df['字詞'].nunique():,}")
            print(f"  - 總詞頻: {df['詞頻'].sum():,}")
        else:
            print(f"警告: {filename} 不存在")
    
    return ngram_data

def analyze_complete_ngram_statistics():
    """分析完整的N-gram統計數據"""
    print("=" * 80)
    print("🔍 完整N-gram統計分析 - 不只是前50個")
    print("=" * 80)
    
    # 載入N-gram數據
    ngram_data = load_ngram_data()
    
    if not ngram_data:
        print("❌ 無法載入N-gram數據")
        return
    
    print("\n" + "=" * 60)
    print("📈 完整1-gram (單字) 統計")
    print("=" * 60)
    
    if '1gram' in ngram_data:
        df = ngram_data['1gram']
        
        # 基本統計
        total_unique_words = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_words if total_unique_words > 0 else 0
        
        print(f"✅ 完整1-gram 總用字數: {total_unique_words:,} 個")
        print(f"✅ 完整1-gram 總詞頻: {total_frequency:,} 次")
        print(f"✅ 完整1-gram 平均詞頻: {avg_frequency:.2f} 次")
        
        # 前20個高頻字
        top_words = df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻1-gram:")
        for i, (_, row) in enumerate(top_words.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        print(f"\n📊 詞頻分布統計:")
        print(f"  最小值: {freq_stats['min']:.0f}")
        print(f"  25%分位數: {freq_stats['25%']:.0f}")
        print(f"  中位數: {freq_stats['50%']:.0f}")
        print(f"  75%分位數: {freq_stats['75%']:.0f}")
        print(f"  最大值: {freq_stats['max']:.0f}")
        print(f"  標準差: {freq_stats['std']:.2f}")
    
    print("\n" + "=" * 60)
    print("📈 完整2-gram (雙字詞組) 統計")
    print("=" * 60)
    
    if '2gram' in ngram_data:
        df = ngram_data['2gram']
        
        # 基本統計
        total_unique_phrases = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_phrases if total_unique_phrases > 0 else 0
        
        print(f"✅ 完整2-gram 總詞組數: {total_unique_phrases:,} 個")
        print(f"✅ 完整2-gram 總詞頻: {total_frequency:,} 次")
        print(f"✅ 完整2-gram 平均詞頻: {avg_frequency:.2f} 次")
        
        # 前20個高頻詞組
        top_phrases = df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻2-gram:")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        print(f"\n📊 詞頻分布統計:")
        print(f"  最小值: {freq_stats['min']:.0f}")
        print(f"  25%分位數: {freq_stats['25%']:.0f}")
        print(f"  中位數: {freq_stats['50%']:.0f}")
        print(f"  75%分位數: {freq_stats['75%']:.0f}")
        print(f"  最大值: {freq_stats['max']:.0f}")
        print(f"  標準差: {freq_stats['std']:.2f}")
    
    print("\n" + "=" * 60)
    print("📈 完整4-gram (四字詞組) 統計")
    print("=" * 60)
    
    if '4gram' in ngram_data:
        df = ngram_data['4gram']
        
        # 基本統計
        total_unique_phrases = df['字詞'].nunique()
        total_frequency = df['詞頻'].sum()
        avg_frequency = total_frequency / total_unique_phrases if total_unique_phrases > 0 else 0
        
        print(f"✅ 完整4-gram 總詞組數: {total_unique_phrases:,} 個")
        print(f"✅ 完整4-gram 總詞頻: {total_frequency:,} 次")
        print(f"✅ 完整4-gram 平均詞頻: {avg_frequency:.2f} 次")
        
        # 前20個高頻詞組
        top_phrases = df.nlargest(20, '詞頻')
        print(f"\n📝 前20個高頻4-gram:")
        for i, (_, row) in enumerate(top_phrases.iterrows(), 1):
            print(f"  {i:2d}. {row['字詞']} - {row['詞頻']:,} 次")
        
        # 詞頻分布統計
        freq_stats = df['詞頻'].describe()
        print(f"\n📊 詞頻分布統計:")
        print(f"  最小值: {freq_stats['min']:.0f}")
        print(f"  25%分位數: {freq_stats['25%']:.0f}")
        print(f"  中位數: {freq_stats['50%']:.0f}")
        print(f"  75%分位數: {freq_stats['75%']:.0f}")
        print(f"  最大值: {freq_stats['max']:.0f}")
        print(f"  標準差: {freq_stats['std']:.2f}")
    
    print("\n" + "=" * 60)
    print("📋 完整統計總結")
    print("=" * 60)
    
    # 生成完整統計報告
    complete_stats = {}
    
    for ngram_type in ['1gram', '2gram', '4gram']:
        if ngram_type in ngram_data:
            df = ngram_data[ngram_type]
            complete_stats[ngram_type] = {
                'total_unique': df['字詞'].nunique(),
                'total_frequency': df['詞頻'].sum(),
                'avg_frequency': df['詞頻'].sum() / df['字詞'].nunique(),
                'max_frequency': df['詞頻'].max(),
                'min_frequency': df['詞頻'].min()
            }
    
    print("✅ 完整N-gram統計數據:")
    for ngram_type, stats in complete_stats.items():
        print(f"  {ngram_type.upper()}:")
        print(f"    總詞組數: {stats['total_unique']:,} 個")
        print(f"    總詞頻: {stats['total_frequency']:,} 次")
        print(f"    平均詞頻: {stats['avg_frequency']:.2f} 次")
        print(f"    最高詞頻: {stats['max_frequency']:,} 次")
        print(f"    最低詞頻: {stats['min_frequency']:,} 次")
        print()
    
    print("🎯 重要發現:")
    print("  - 這是不經過地域過濾的完整統計")
    print("  - 包含所有詩人的所有N-gram數據")
    print("  - 反映全唐詩的完整語言特徵")

def main():
    """主函數"""
    try:
        analyze_complete_ngram_statistics()
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
