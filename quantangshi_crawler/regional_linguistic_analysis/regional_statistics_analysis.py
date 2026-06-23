#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regional Statistics Analysis for Tang Poetry
地域統計分析：基於詩人地理標籤的詳細統計分析
"""

import pandas as pd
import numpy as np
import json
import os
from collections import defaultdict, Counter
import re

class RegionalStatisticsAnalyzer:
    def __init__(self, poet_geo_file, ngram_dir):
        """
        Initialize the analyzer with poet geographical data and n-gram data
        
        Args:
            poet_geo_file: Path to poet_geo_label.csv
            ngram_dir: Path to n-gram analysis directory
        """
        self.poet_geo_file = poet_geo_file
        self.ngram_dir = ngram_dir
        self.poet_data = None
        self.regional_stats = {}
        
    def load_poet_data(self):
        """Load poet geographical data"""
        print("Loading poet geographical data...")
        self.poet_data = pd.read_csv(self.poet_geo_file)
        
        # Clean and extract geographical information
        self.poet_data['region'] = self.poet_data['Geography'].apply(self._extract_region)
        self.poet_data['poet_name'] = self.poet_data['詩人'].apply(self._clean_poet_name)
        self.poet_data['poem_count'] = self.poet_data['詩人'].apply(self._extract_poem_count)
        self.poet_data['gender'] = self.poet_data['性別'].apply(self._clean_gender)
        self.poet_data['background'] = self.poet_data['背景'].apply(self._clean_background)
        self.poet_data['official_period'] = self.poet_data['當官年代'].apply(self._clean_official_period)
        
        print(f"Loaded {len(self.poet_data)} poets")
        return self.poet_data
    
    def _extract_region(self, geo_str):
        """Extract main region from geographical string"""
        if pd.isna(geo_str) or geo_str == '':
            return 'Unknown'
        
        # Extract the main administrative region
        if '關內道' in geo_str:
            return 'Guannei Dao'
        elif '江南道' in geo_str:
            return 'Jiangnan Dao'
        elif '河北道' in geo_str:
            return 'Hebei Dao'
        elif '河南道' in geo_str:
            return 'Henan Dao'
        elif '河東道' in geo_str:
            return 'Hedong Dao'
        elif '山南道' in geo_str:
            return 'Shannan Dao'
        elif '劍南道' in geo_str:
            return 'Jiannan Dao'
        elif '淮南道' in geo_str:
            return 'Huainan Dao'
        elif '隴右道' in geo_str:
            return 'Longyou Dao'
        elif '嶺南道' in geo_str:
            return 'Lingnan Dao'
        else:
            return 'Other'
    
    def _clean_poet_name(self, name_str):
        """Clean poet name from the original string"""
        if pd.isna(name_str):
            return 'Unknown'
        
        # Extract name from format like "1. 白居易: 2,600 首"
        match = re.search(r'(\d+\.\s*)?([^:：]+)', str(name_str))
        if match:
            return match.group(2).strip()
        return str(name_str).strip()
    
    def _extract_poem_count(self, name_str):
        """Extract poem count from the original string"""
        if pd.isna(name_str):
            return 0
        
        # Extract count from format like "1. 白居易: 2,600 首"
        match = re.search(r':\s*(\d{1,3}(?:,\d{3})*)\s*首', str(name_str))
        if match:
            return int(match.group(1).replace(',', ''))
        return 0
    
    def _clean_gender(self, gender_str):
        """Clean gender information"""
        if pd.isna(gender_str):
            return 'Unknown'
        return str(gender_str).strip()
    
    def _clean_background(self, bg_str):
        """Clean background information"""
        if pd.isna(bg_str):
            return 'Unknown'
        return str(bg_str).strip()
    
    def _clean_official_period(self, period_str):
        """Clean official period information"""
        if pd.isna(period_str):
            return 'Unknown'
        return str(period_str).strip()
    
    def analyze_regional_statistics(self):
        """Analyze regional statistics"""
        print("Analyzing regional statistics...")
        
        # Basic regional statistics
        regional_stats = {}
        
        for region in self.poet_data['region'].unique():
            if region == 'Unknown':
                continue
                
            region_data = self.poet_data[self.poet_data['region'] == region]
            
            stats = {
                'total_poets': len(region_data),
                'total_poems': region_data['poem_count'].sum(),
                'avg_poems_per_poet': region_data['poem_count'].mean(),
                'gender_distribution': region_data['gender'].value_counts().to_dict(),
                'top_poets': self._get_top_poets(region_data, 10),
                'background_distribution': self._analyze_backgrounds(region_data),
                'official_period_distribution': self._analyze_official_periods(region_data),
                'poem_count_distribution': self._analyze_poem_counts(region_data)
            }
            
            regional_stats[region] = stats
        
        self.regional_stats = regional_stats
        return regional_stats
    
    def _get_top_poets(self, region_data, top_n=10):
        """Get top poets in a region"""
        top_poets = region_data.nlargest(top_n, 'poem_count')[['poet_name', 'poem_count']].to_dict('records')
        return top_poets
    
    def _analyze_backgrounds(self, region_data):
        """Analyze background distribution"""
        backgrounds = region_data['background'].value_counts()
        return backgrounds.to_dict()
    
    def _analyze_official_periods(self, region_data):
        """Analyze official period distribution"""
        periods = region_data['official_period'].value_counts()
        return periods.to_dict()
    
    def _analyze_poem_counts(self, region_data):
        """Analyze poem count distribution"""
        poem_counts = region_data['poem_count']
        
        distribution = {
            'single_poem_poets': len(poem_counts[poem_counts == 1]),
            'multi_poem_poets': len(poem_counts[poem_counts > 1]),
            'highly_productive_poets': len(poem_counts[poem_counts >= 100]),
            'extremely_productive_poets': len(poem_counts[poem_counts >= 1000]),
            'max_poems': poem_counts.max(),
            'min_poems': poem_counts.min(),
            'median_poems': poem_counts.median(),
            'std_poems': poem_counts.std()
        }
        
        return distribution
    
    def analyze_cross_regional_patterns(self):
        """Analyze patterns across regions"""
        print("Analyzing cross-regional patterns...")
        
        cross_regional_stats = {
            'total_regions': len(self.poet_data['region'].unique()) - 1,  # Exclude Unknown
            'total_poets': len(self.poet_data),
            'total_poems': self.poet_data['poem_count'].sum(),
            'region_poet_distribution': self.poet_data['region'].value_counts().to_dict(),
            'region_poem_distribution': self.poet_data.groupby('region')['poem_count'].sum().to_dict(),
            'gender_distribution_by_region': self._analyze_gender_by_region(),
            'background_distribution_by_region': self._analyze_background_by_region(),
            'most_productive_regions': self._get_most_productive_regions(),
            'least_productive_regions': self._get_least_productive_regions()
        }
        
        return cross_regional_stats
    
    def _analyze_gender_by_region(self):
        """Analyze gender distribution by region"""
        gender_by_region = {}
        for region in self.poet_data['region'].unique():
            if region == 'Unknown':
                continue
            region_data = self.poet_data[self.poet_data['region'] == region]
            gender_by_region[region] = region_data['gender'].value_counts().to_dict()
        return gender_by_region
    
    def _analyze_background_by_region(self):
        """Analyze background distribution by region"""
        background_by_region = {}
        for region in self.poet_data['region'].unique():
            if region == 'Unknown':
                continue
            region_data = self.poet_data[self.poet_data['region'] == region]
            background_by_region[region] = region_data['background'].value_counts().to_dict()
        return background_by_region
    
    def _get_most_productive_regions(self):
        """Get most productive regions by poem count"""
        region_poems = self.poet_data.groupby('region')['poem_count'].sum().sort_values(ascending=False)
        return region_poems.to_dict()
    
    def _get_least_productive_regions(self):
        """Get least productive regions by poem count"""
        region_poems = self.poet_data.groupby('region')['poem_count'].sum().sort_values(ascending=True)
        return region_poems.to_dict()
    
    def analyze_linguistic_patterns(self):
        """Analyze linguistic patterns by region"""
        print("Analyzing linguistic patterns by region...")
        
        linguistic_patterns = {}
        
        # Analyze 1gram patterns
        if os.path.exists(os.path.join(self.ngram_dir, 'merged_1gram_詞頻統計.csv')):
            linguistic_patterns['1gram'] = self._analyze_ngram_patterns('1gram')
        
        # Analyze 2gram patterns
        if os.path.exists(os.path.join(self.ngram_dir, 'merged_2gram_詞頻統計.csv')):
            linguistic_patterns['2gram'] = self._analyze_ngram_patterns('2gram')
        
        # Analyze 4gram patterns
        if os.path.exists(os.path.join(self.ngram_dir, 'merged_4gram_詞頻統計.csv')):
            linguistic_patterns['4gram'] = self._analyze_ngram_patterns('4gram')
        
        return linguistic_patterns
    
    def _analyze_ngram_patterns(self, ngram_type):
        """Analyze n-gram patterns by region"""
        ngram_file = os.path.join(self.ngram_dir, f'merged_{ngram_type}_詞頻統計.csv')
        
        if not os.path.exists(ngram_file):
            return {}
        
        print(f"Analyzing {ngram_type} patterns...")
        
        # Load n-gram data
        ngram_data = pd.read_csv(ngram_file)
        
        # Get top n-grams
        if '字詞' in ngram_data.columns:
            ngram_column = '字詞'
        elif 'ngram' in ngram_data.columns:
            ngram_column = 'ngram'
        else:
            return {}
        
        # Get top 50 n-grams
        top_ngrams = ngram_data[ngram_column].value_counts().head(50).index.tolist()
        
        # Analyze by region
        regional_ngram_stats = {}
        
        for region in self.poet_data['region'].unique():
            if region == 'Unknown':
                continue
                
            region_poets = self.poet_data[self.poet_data['region'] == region]['poet_name'].tolist()
            
            region_ngram_freq = {}
            for ngram in top_ngrams:
                total_freq = 0
                for poet in region_poets:
                    if poet in ngram_data.columns:
                        poet_data = ngram_data[ngram_data[ngram_column] == ngram]
                        if not poet_data.empty and poet in poet_data.columns:
                            freq = poet_data[poet].iloc[0]
                            if pd.notna(freq) and freq > 0:
                                total_freq += freq
                
                if total_freq > 0:
                    region_ngram_freq[ngram] = total_freq
            
            # Sort by frequency
            region_ngram_freq = dict(sorted(region_ngram_freq.items(), key=lambda x: x[1], reverse=True))
            
            regional_ngram_stats[region] = {
                'top_ngrams': list(region_ngram_freq.keys())[:20],  # Top 20
                'ngram_frequencies': region_ngram_freq,
                'total_ngram_count': sum(region_ngram_freq.values()),
                'unique_ngrams': len(region_ngram_freq)
            }
        
        return regional_ngram_stats
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def save_detailed_statistics(self, output_dir):
        """Save detailed statistics to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to serializable format
        serializable_stats = self._convert_to_serializable(self.regional_stats)
        
        # Save regional statistics
        with open(os.path.join(output_dir, 'regional_statistics.json'), 'w', encoding='utf-8') as f:
            json.dump(serializable_stats, f, ensure_ascii=False, indent=2)
        
        # Save cross-regional patterns
        cross_regional_stats = self.analyze_cross_regional_patterns()
        serializable_cross = self._convert_to_serializable(cross_regional_stats)
        with open(os.path.join(output_dir, 'cross_regional_patterns.json'), 'w', encoding='utf-8') as f:
            json.dump(serializable_cross, f, ensure_ascii=False, indent=2)
        
        # Save linguistic patterns
        linguistic_patterns = self.analyze_linguistic_patterns()
        serializable_linguistic = self._convert_to_serializable(linguistic_patterns)
        with open(os.path.join(output_dir, 'linguistic_patterns.json'), 'w', encoding='utf-8') as f:
            json.dump(serializable_linguistic, f, ensure_ascii=False, indent=2)
        
        # Create detailed text report
        self._create_detailed_text_report(output_dir)
        
        print(f"Detailed statistics saved to {output_dir}")
    
    def _create_detailed_text_report(self, output_dir):
        """Create detailed text report"""
        report_path = os.path.join(output_dir, 'detailed_regional_statistics_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("唐代詩人地域統計詳細分析報告\n")
            f.write("=" * 50 + "\n\n")
            
            # Overall statistics
            f.write("一、總體統計\n")
            f.write("-" * 30 + "\n")
            f.write(f"總詩人數: {len(self.poet_data)}\n")
            f.write(f"總詩歌數: {self.poet_data['poem_count'].sum():,}\n")
            f.write(f"平均每位詩人詩歌數: {self.poet_data['poem_count'].mean():.1f}\n")
            f.write(f"地域數量: {len(self.poet_data['region'].unique()) - 1}\n\n")
            
            # Regional statistics
            f.write("二、各地域詳細統計\n")
            f.write("-" * 30 + "\n")
            
            for region, stats in self.regional_stats.items():
                f.write(f"\n{region}:\n")
                f.write(f"  詩人數量: {stats['total_poets']}\n")
                f.write(f"  詩歌總數: {stats['total_poems']:,}\n")
                f.write(f"  平均詩歌數: {stats['avg_poems_per_poet']:.1f}\n")
                
                f.write(f"  性別分布: {stats['gender_distribution']}\n")
                
                f.write(f"  前10名詩人:\n")
                for poet in stats['top_poets']:
                    f.write(f"    {poet['poet_name']}: {poet['poem_count']} 首\n")
                
                f.write(f"  社會背景分布:\n")
                for bg, count in list(stats['background_distribution'].items())[:5]:
                    f.write(f"    {bg}: {count} 人\n")
                
                f.write(f"  詩歌數量分布:\n")
                poem_dist = stats['poem_count_distribution']
                f.write(f"    僅一首詩: {poem_dist['single_poem_poets']} 人\n")
                f.write(f"    多首詩: {poem_dist['multi_poem_poets']} 人\n")
                f.write(f"    高產詩人(≥100首): {poem_dist['highly_productive_poets']} 人\n")
                f.write(f"    極高產詩人(≥1000首): {poem_dist['extremely_productive_poets']} 人\n")
                f.write(f"    最多詩歌數: {poem_dist['max_poems']}\n")
                f.write(f"    最少詩歌數: {poem_dist['min_poems']}\n")
                f.write(f"    中位數: {poem_dist['median_poems']:.1f}\n")
            
            # Cross-regional analysis
            f.write("\n\n三、跨地域比較分析\n")
            f.write("-" * 30 + "\n")
            
            cross_regional_stats = self.analyze_cross_regional_patterns()
            
            f.write("地域詩人數量排名:\n")
            for region, count in sorted(cross_regional_stats['region_poet_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
                f.write(f"  {region}: {count} 人\n")
            
            f.write("\n地域詩歌數量排名:\n")
            for region, count in sorted(cross_regional_stats['region_poem_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
                f.write(f"  {region}: {count:,} 首\n")
            
            # Linguistic patterns
            f.write("\n\n四、語言模式分析\n")
            f.write("-" * 30 + "\n")
            
            linguistic_patterns = self.analyze_linguistic_patterns()
            
            for ngram_type, patterns in linguistic_patterns.items():
                f.write(f"\n{ngram_type} 語言模式:\n")
                for region, region_patterns in patterns.items():
                    f.write(f"  {region}:\n")
                    f.write(f"    總詞頻: {region_patterns['total_ngram_count']:,}\n")
                    f.write(f"    獨特詞數: {region_patterns['unique_ngrams']}\n")
                    f.write(f"    前10個詞彙: {', '.join(region_patterns['top_ngrams'][:10])}\n")
        
        print(f"Detailed text report saved to {report_path}")

def main():
    """Main analysis function"""
    # Set up paths
    poet_geo_file = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv"
    ngram_dir = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs"
    output_dir = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis"
    
    # Initialize analyzer
    analyzer = RegionalStatisticsAnalyzer(poet_geo_file, ngram_dir)
    
    # Load data
    print("=== Regional Statistics Analysis ===")
    poet_data = analyzer.load_poet_data()
    
    # Analyze regional statistics
    regional_stats = analyzer.analyze_regional_statistics()
    
    # Save detailed statistics
    analyzer.save_detailed_statistics(output_dir)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Results saved to: {output_dir}")
    print("Generated files:")
    print("- regional_statistics.json")
    print("- cross_regional_patterns.json") 
    print("- linguistic_patterns.json")
    print("- detailed_regional_statistics_report.txt")

if __name__ == "__main__":
    main()
