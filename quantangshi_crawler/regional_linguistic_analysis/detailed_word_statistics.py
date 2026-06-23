#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed Word Statistics Analysis
詳細用字統計分析
"""

import json
import pandas as pd
import numpy as np
from collections import Counter

def analyze_word_statistics():
    """分析詳細的用字統計"""
    
    # Load the analysis results
    with open('fixed_analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== 唐代詩人地域用字統計詳細分析 ===\n")
    
    # Analyze 1-gram statistics
    if '1gram_regional_matrix' in data:
        print("📊 1-gram (單字) 統計結果")
        print("=" * 50)
        
        matrix_data = data['1gram_regional_matrix']
        
        # Convert to DataFrame for easier analysis
        regions = []
        words_data = []
        
        for item in matrix_data:
            if 'region' in item and 'words' in item:
                regions.append(item['region'])
                words_data.append(item['words'])
        
        if regions and words_data:
            # Create DataFrame
            df = pd.DataFrame(words_data, index=regions)
            
            # Calculate statistics for each region
            for region in df.index:
                print(f"\n🗺️ {region}:")
                print("-" * 30)
                
                # Get non-zero word frequencies
                region_words = df.loc[region]
                non_zero_words = region_words[region_words > 0]
                
                if len(non_zero_words) > 0:
                    # Sort by frequency
                    sorted_words = non_zero_words.sort_values(ascending=False)
                    
                    print(f"總用字數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {non_zero_words.sum()} 次")
                    print(f"平均詞頻: {non_zero_words.mean():.2f} 次")
                    print(f"最高詞頻: {non_zero_words.max()} 次")
                    
                    print("\n前15個高頻字:")
                    for i, (word, freq) in enumerate(sorted_words.head(15).items()):
                        print(f"  {i+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無用字數據")
    
    # Analyze 2-gram statistics
    if '2gram_regional_matrix' in data:
        print("\n\n📊 2-gram (雙字詞組) 統計結果")
        print("=" * 50)
        
        matrix_data = data['2gram_regional_matrix']
        
        # Convert to DataFrame for easier analysis
        regions = []
        words_data = []
        
        for item in matrix_data:
            if 'region' in item and 'words' in item:
                regions.append(item['region'])
                words_data.append(item['words'])
        
        if regions and words_data:
            # Create DataFrame
            df = pd.DataFrame(words_data, index=regions)
            
            # Calculate statistics for each region
            for region in df.index:
                print(f"\n🗺️ {region}:")
                print("-" * 30)
                
                # Get non-zero word frequencies
                region_words = df.loc[region]
                non_zero_words = region_words[region_words > 0]
                
                if len(non_zero_words) > 0:
                    # Sort by frequency
                    sorted_words = non_zero_words.sort_values(ascending=False)
                    
                    print(f"總詞組數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {non_zero_words.sum()} 次")
                    print(f"平均詞頻: {non_zero_words.mean():.2f} 次")
                    print(f"最高詞頻: {non_zero_words.max()} 次")
                    
                    print("\n前10個高頻詞組:")
                    for i, (word, freq) in enumerate(sorted_words.head(10).items()):
                        print(f"  {i+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無詞組數據")
    
    # Analyze 4-gram statistics
    if '4gram_regional_matrix' in data:
        print("\n\n📊 4-gram (四字詞組) 統計結果")
        print("=" * 50)
        
        matrix_data = data['4gram_regional_matrix']
        
        # Convert to DataFrame for easier analysis
        regions = []
        words_data = []
        
        for item in matrix_data:
            if 'region' in item and 'words' in item:
                regions.append(item['region'])
                words_data.append(item['words'])
        
        if regions and words_data:
            # Create DataFrame
            df = pd.DataFrame(words_data, index=regions)
            
            # Calculate statistics for each region
            for region in df.index:
                print(f"\n🗺️ {region}:")
                print("-" * 30)
                
                # Get non-zero word frequencies
                region_words = df.loc[region]
                non_zero_words = region_words[region_words > 0]
                
                if len(non_zero_words) > 0:
                    # Sort by frequency
                    sorted_words = non_zero_words.sort_values(ascending=False)
                    
                    print(f"總詞組數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {non_zero_words.sum()} 次")
                    print(f"平均詞頻: {non_zero_words.mean():.2f} 次")
                    print(f"最高詞頻: {non_zero_words.max()} 次")
                    
                    print("\n前5個高頻詞組:")
                    for i, (word, freq) in enumerate(sorted_words.head(5).items()):
                        print(f"  {i+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無詞組數據")
    
    # Analyze clustering results
    if '1gram_clusters' in data:
        print("\n\n🔍 地域語言群組分析")
        print("=" * 50)
        
        clusters = data['1gram_clusters']
        
        # Group regions by cluster
        cluster_groups = {}
        for item in clusters:
            cluster_id = item['cluster']
            region = item['region']
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(region)
        
        for cluster_id, regions in cluster_groups.items():
            print(f"\n群組 {cluster_id}: {', '.join(regions)}")
            
            # Analyze characteristics of this cluster
            if len(regions) > 1:
                print(f"  包含 {len(regions)} 個地域")
                print(f"  地域: {', '.join(regions)}")
            else:
                print(f"  獨立地域: {regions[0]}")

def main():
    """Main function"""
    try:
        analyze_word_statistics()
    except Exception as e:
        print(f"分析過程中出現錯誤: {e}")
        print("請確保 fixed_analysis_results.json 文件存在且格式正確")

if __name__ == "__main__":
    main()
