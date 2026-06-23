#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
實際用字統計分析
基於修復版分析結果的詳細用字統計
"""

import json
import pandas as pd
import numpy as np
from collections import Counter

def analyze_actual_word_statistics():
    """分析實際的用字統計"""
    
    # Load the analysis results
    with open('fixed_analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== 唐代詩人地域用字統計實際分析 ===\n")
    
    # Analyze 1-gram statistics
    if '1gram_regional_matrix' in data:
        print("📊 1-gram (單字) 實際統計結果")
        print("=" * 60)
        
        matrix_data = data['1gram_regional_matrix']
        
        # Get region names from similarity matrix
        region_names = data['1gram_similarity_matrix'][0].keys()
        
        print(f"分析地域: {list(region_names)}")
        print(f"分析詞彙: 50個高頻單字")
        print(f"數據行數: {len(matrix_data)}")
        
        # Analyze each region's word usage
        for i, region_data in enumerate(matrix_data):
            if i < len(region_names):
                region_name = list(region_names)[i]
                print(f"\n🗺️ {region_name}:")
                print("-" * 40)
                
                # Get non-zero word frequencies
                non_zero_words = {word: freq for word, freq in region_data.items() if freq > 0}
                
                if non_zero_words:
                    # Sort by frequency
                    sorted_words = sorted(non_zero_words.items(), key=lambda x: x[1], reverse=True)
                    
                    print(f"總用字數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {sum(non_zero_words.values())} 次")
                    print(f"平均詞頻: {sum(non_zero_words.values()) / len(non_zero_words):.2f} 次")
                    print(f"最高詞頻: {max(non_zero_words.values())} 次")
                    
                    print("\n前15個高頻字:")
                    for j, (word, freq) in enumerate(sorted_words[:15]):
                        print(f"  {j+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無用字數據")
    
    # Analyze 2-gram statistics
    if '2gram_regional_matrix' in data:
        print("\n\n📊 2-gram (雙字詞組) 實際統計結果")
        print("=" * 60)
        
        matrix_data = data['2gram_regional_matrix']
        region_names = data['2gram_similarity_matrix'][0].keys()
        
        print(f"分析地域: {list(region_names)}")
        print(f"分析詞組: 50個高頻雙字詞組")
        print(f"數據行數: {len(matrix_data)}")
        
        # Analyze each region's word usage
        for i, region_data in enumerate(matrix_data):
            if i < len(region_names):
                region_name = list(region_names)[i]
                print(f"\n🗺️ {region_name}:")
                print("-" * 40)
                
                # Get non-zero word frequencies
                non_zero_words = {word: freq for word, freq in region_data.items() if freq > 0}
                
                if non_zero_words:
                    # Sort by frequency
                    sorted_words = sorted(non_zero_words.items(), key=lambda x: x[1], reverse=True)
                    
                    print(f"總詞組數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {sum(non_zero_words.values())} 次")
                    print(f"平均詞頻: {sum(non_zero_words.values()) / len(non_zero_words):.2f} 次")
                    print(f"最高詞頻: {max(non_zero_words.values())} 次")
                    
                    print("\n前10個高頻詞組:")
                    for j, (word, freq) in enumerate(sorted_words[:10]):
                        print(f"  {j+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無詞組數據")
    
    # Analyze 4-gram statistics
    if '4gram_regional_matrix' in data:
        print("\n\n📊 4-gram (四字詞組) 實際統計結果")
        print("=" * 60)
        
        matrix_data = data['4gram_regional_matrix']
        region_names = data['4gram_similarity_matrix'][0].keys()
        
        print(f"分析地域: {list(region_names)}")
        print(f"分析詞組: 50個高頻四字詞組")
        print(f"數據行數: {len(matrix_data)}")
        
        # Analyze each region's word usage
        for i, region_data in enumerate(matrix_data):
            if i < len(region_names):
                region_name = list(region_names)[i]
                print(f"\n🗺️ {region_name}:")
                print("-" * 40)
                
                # Get non-zero word frequencies
                non_zero_words = {word: freq for word, freq in region_data.items() if freq > 0}
                
                if non_zero_words:
                    # Sort by frequency
                    sorted_words = sorted(non_zero_words.items(), key=lambda x: x[1], reverse=True)
                    
                    print(f"總詞組數: {len(non_zero_words)} 個")
                    print(f"總詞頻: {sum(non_zero_words.values())} 次")
                    print(f"平均詞頻: {sum(non_zero_words.values()) / len(non_zero_words):.2f} 次")
                    print(f"最高詞頻: {max(non_zero_words.values())} 次")
                    
                    print("\n前5個高頻詞組:")
                    for j, (word, freq) in enumerate(sorted_words[:5]):
                        print(f"  {j+1:2d}. {word}: {freq:3d} 次")
                else:
                    print("  無詞組數據")
    
    # Analyze clustering results
    if '1gram_clusters' in data:
        print("\n\n🔍 地域語言群組實際分析")
        print("=" * 60)
        
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
                
                # Analyze common words in this cluster
                print(f"  群組特徵分析:")
                if cluster_id == 0:
                    print("    - 政治中心型: 關內道、河南道、其他地區、山南道、河東道")
                    print("    - 特徵: 政治色彩濃厚，用詞正式")
                elif cluster_id == 1:
                    print("    - 未知地域型: 未知地域")
                    print("    - 特徵: 地理信息不明，語言模式獨特")
                elif cluster_id == 2:
                    print("    - 江南文化型: 江南道、河北道")
                    print("    - 特徵: 文學性強，山水意象豐富")
                elif cluster_id == 3:
                    print("    - 邊疆型: 嶺南道、淮南道、劍南道、隴右道")
                    print("    - 特徵: 邊疆特色，語言風格獨特")
            else:
                print(f"  獨立地域: {regions[0]}")
    
    # Summary statistics
    print("\n\n📈 統計摘要")
    print("=" * 60)
    
    total_regions = len(data['1gram_similarity_matrix'][0]) if '1gram_similarity_matrix' in data else 0
    total_poets = 1461  # From previous analysis
    
    print(f"總分析地域: {total_regions} 個")
    print(f"匹配詩人: {total_poets} 人")
    print(f"分析層次: 1-gram, 2-gram, 4-gram")
    print(f"高頻詞彙: 每層次50個")
    
    # Calculate overall statistics
    if '1gram_regional_matrix' in data:
        total_words = 0
        total_freq = 0
        for region_data in data['1gram_regional_matrix']:
            non_zero_words = {word: freq for word, freq in region_data.items() if freq > 0}
            total_words += len(non_zero_words)
            total_freq += sum(non_zero_words.values())
        
        print(f"1-gram 總用字數: {total_words} 個")
        print(f"1-gram 總詞頻: {total_freq} 次")
        print(f"1-gram 平均詞頻: {total_freq / total_words if total_words > 0 else 0:.2f} 次")

def main():
    """Main function"""
    try:
        analyze_actual_word_statistics()
    except Exception as e:
        print(f"分析過程中出現錯誤: {e}")
        print("請確保 fixed_analysis_results.json 文件存在且格式正確")

if __name__ == "__main__":
    main()
