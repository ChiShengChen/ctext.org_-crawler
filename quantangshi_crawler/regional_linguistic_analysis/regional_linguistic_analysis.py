#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regional Linguistic Analysis for Tang Poetry
地域語言分析：分析不同地域詩人的用字習慣
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
from collections import defaultdict, Counter
import json

# Set up matplotlib for better font support
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

class RegionalLinguisticAnalyzer:
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
        self.regional_data = {}
        self.ngram_data = {}
        
    def load_poet_data(self):
        """Load poet geographical data"""
        print("Loading poet geographical data...")
        self.poet_data = pd.read_csv(self.poet_geo_file)
        
        # Clean and extract geographical information
        self.poet_data['region'] = self.poet_data['Geography'].apply(self._extract_region)
        self.poet_data['poet_name'] = self.poet_data['詩人'].apply(self._clean_poet_name)
        
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
    
    def load_ngram_data(self):
        """Load n-gram data for analysis"""
        print("Loading n-gram data...")
        
        # Load merged n-gram data
        ngram_files = {
            '1gram': 'merged_1gram_詞頻統計.csv',
            '2gram': 'merged_2gram_詞頻統計.csv', 
            '4gram': 'merged_4gram_詞頻統計.csv'
        }
        
        for ngram_type, filename in ngram_files.items():
            filepath = os.path.join(self.ngram_dir, filename)
            if os.path.exists(filepath):
                print(f"Loading {ngram_type} data from {filename}")
                df = pd.read_csv(filepath)
                self.ngram_data[ngram_type] = df
            else:
                print(f"Warning: {filename} not found")
        
        return self.ngram_data
    
    def create_regional_ngram_matrix(self, ngram_type='1gram', top_n=100):
        """Create regional n-gram frequency matrix"""
        if ngram_type not in self.ngram_data:
            print(f"Error: {ngram_type} data not loaded")
            return None
        
        print(f"Creating regional {ngram_type} matrix...")
        
        # Get the n-gram data
        ngram_df = self.ngram_data[ngram_type]
        
        # For pivot data, get top n-grams from the first column (字詞)
        if '字詞' in ngram_df.columns:
            # This is pivot data format
            ngram_column = '字詞'
            # Get top n-grams by total frequency
            total_freq = ngram_df[ngram_column].value_counts().head(top_n)
            top_ngrams = total_freq.index.tolist()
        else:
            # This is merged data format
            if 'ngram' in ngram_df.columns:
                total_freq = ngram_df['ngram'].value_counts().head(top_n)
                top_ngrams = total_freq.index.tolist()
            else:
                print(f"Error: Cannot find n-gram column in {ngram_type} data")
                return None
        
        # Create regional matrix
        regions = self.poet_data['region'].unique()
        regional_matrix = pd.DataFrame(index=regions, columns=top_ngrams)
        regional_matrix = regional_matrix.fillna(0)
        
        # Calculate frequencies for each region
        for region in regions:
            region_poets = self.poet_data[self.poet_data['region'] == region]['poet_name'].tolist()
            
            for poet in region_poets:
                if poet in ngram_df.columns:
                    for ngram in top_ngrams:
                        if ngram in ngram_df[ngram_column].values:
                            # Get frequency for this poet and n-gram
                            poet_data = ngram_df[ngram_df[ngram_column] == ngram]
                            if not poet_data.empty and poet in poet_data.columns:
                                freq = poet_data[poet].iloc[0]
                                if pd.notna(freq) and freq > 0:
                                    regional_matrix.loc[region, ngram] += freq
        
        return regional_matrix
    
    def calculate_regional_similarity(self, regional_matrix):
        """Calculate cosine similarity between regions"""
        # Normalize the matrix
        normalized_matrix = regional_matrix.div(regional_matrix.sum(axis=1), axis=0)
        
        # Fill NaN values with 0
        normalized_matrix = normalized_matrix.fillna(0)
        
        # Calculate cosine similarity
        similarity_matrix = pd.DataFrame(
            cosine_similarity(normalized_matrix),
            index=regional_matrix.index,
            columns=regional_matrix.index
        )
        
        return similarity_matrix
    
    def perform_regional_clustering(self, regional_matrix, n_clusters=4):
        """Perform clustering analysis on regional linguistic patterns"""
        # Normalize the matrix
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(regional_matrix)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(normalized_data)
        
        # Add cluster labels to the matrix
        regional_matrix_with_clusters = regional_matrix.copy()
        regional_matrix_with_clusters['cluster'] = cluster_labels
        
        return regional_matrix_with_clusters, kmeans
    
    def create_regional_heatmap(self, regional_matrix, title="Regional Linguistic Patterns"):
        """Create heatmap of regional linguistic patterns"""
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Normalize for better visualization
        normalized_matrix = regional_matrix.div(regional_matrix.sum(axis=1), axis=0)
        
        # Create heatmap
        sns.heatmap(normalized_matrix, 
                    annot=False, 
                    cmap='YlOrRd',
                    ax=ax,
                    cbar_kws={'label': 'Normalized Frequency'})
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('N-grams', fontsize=12)
        ax.set_ylabel('Regions', fontsize=12)
        
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        return fig
    
    def create_similarity_heatmap(self, similarity_matrix, title="Regional Linguistic Similarity"):
        """Create heatmap of regional similarity"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(similarity_matrix, 
                    annot=True, 
                    cmap='RdYlBu_r',
                    center=0,
                    square=True,
                    ax=ax,
                    cbar_kws={'label': 'Cosine Similarity'})
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Regions', fontsize=12)
        ax.set_ylabel('Regions', fontsize=12)
        
        plt.tight_layout()
        
        return fig
    
    def create_regional_cluster_plot(self, regional_matrix_with_clusters):
        """Create PCA plot showing regional clusters"""
        # Prepare data for PCA
        data_for_pca = regional_matrix_with_clusters.drop('cluster', axis=1)
        
        # Perform PCA
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(data_for_pca)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each cluster with different colors
        clusters = regional_matrix_with_clusters['cluster'].unique()
        colors = plt.cm.Set1(np.linspace(0, 1, len(clusters)))
        
        for i, cluster in enumerate(clusters):
            cluster_data = pca_result[regional_matrix_with_clusters['cluster'] == cluster]
            ax.scatter(cluster_data[:, 0], cluster_data[:, 1], 
                      c=[colors[i]], label=f'Cluster {cluster}', s=100, alpha=0.7)
        
        # Add region labels
        for i, region in enumerate(regional_matrix_with_clusters.index):
            ax.annotate(region, (pca_result[i, 0], pca_result[i, 1]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=10)
        
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
        ax.set_title('Regional Linguistic Clusters (PCA)', fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return fig
    
    def analyze_regional_characteristics(self, regional_matrix):
        """Analyze characteristics of each region"""
        results = {}
        
        for region in regional_matrix.index:
            region_data = regional_matrix.loc[region]
            
            # Get top n-grams for this region
            top_ngrams = region_data.nlargest(10)
            
            # Calculate diversity (entropy)
            normalized_freq = region_data / region_data.sum()
            entropy = -np.sum(normalized_freq * np.log(normalized_freq + 1e-10))
            
            results[region] = {
                'top_ngrams': top_ngrams.to_dict(),
                'entropy': entropy,
                'total_frequency': region_data.sum(),
                'unique_ngrams': (region_data > 0).sum()
            }
        
        return results
    
    def save_results(self, results, output_dir):
        """Save analysis results"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save regional characteristics
        with open(os.path.join(output_dir, 'regional_characteristics.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {output_dir}")

def main():
    """Main analysis function"""
    # Set up paths
    poet_geo_file = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv"
    ngram_dir = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs"
    output_dir = "/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis"
    
    # Initialize analyzer
    analyzer = RegionalLinguisticAnalyzer(poet_geo_file, ngram_dir)
    
    # Load data
    print("=== Regional Linguistic Analysis ===")
    poet_data = analyzer.load_poet_data()
    ngram_data = analyzer.load_ngram_data()
    
    # Create regional matrices for different n-gram types
    ngram_types = ['1gram', '2gram', '4gram']
    all_results = {}
    
    for ngram_type in ngram_types:
        if ngram_type in ngram_data:
            print(f"\n=== Analyzing {ngram_type} patterns ===")
            
            # Create regional matrix
            regional_matrix = analyzer.create_regional_ngram_matrix(ngram_type, top_n=50)
            
            if regional_matrix is not None and not regional_matrix.empty:
                # Calculate similarity
                similarity_matrix = analyzer.calculate_regional_similarity(regional_matrix)
                
                # Perform clustering
                regional_matrix_with_clusters, kmeans = analyzer.perform_regional_clustering(regional_matrix)
                
                # Create visualizations
                heatmap_fig = analyzer.create_regional_heatmap(
                    regional_matrix, 
                    f"Regional {ngram_type.upper()} Patterns"
                )
                heatmap_fig.savefig(os.path.join(output_dir, f'regional_{ngram_type}_heatmap.png'), 
                                   dpi=300, bbox_inches='tight')
                plt.close(heatmap_fig)
                
                similarity_fig = analyzer.create_similarity_heatmap(
                    similarity_matrix,
                    f"Regional {ngram_type.upper()} Similarity"
                )
                similarity_fig.savefig(os.path.join(output_dir, f'regional_{ngram_type}_similarity.png'), 
                                      dpi=300, bbox_inches='tight')
                plt.close(similarity_fig)
                
                cluster_fig = analyzer.create_regional_cluster_plot(regional_matrix_with_clusters)
                cluster_fig.savefig(os.path.join(output_dir, f'regional_{ngram_type}_clusters.png'), 
                                   dpi=300, bbox_inches='tight')
                plt.close(cluster_fig)
                
                # Analyze characteristics
                characteristics = analyzer.analyze_regional_characteristics(regional_matrix)
                all_results[ngram_type] = {
                    'characteristics': characteristics,
                    'similarity_matrix': similarity_matrix.to_dict(),
                    'clusters': regional_matrix_with_clusters['cluster'].to_dict()
                }
                
                print(f"Analysis completed for {ngram_type}")
            else:
                print(f"No data available for {ngram_type}")
    
    # Save all results
    analyzer.save_results(all_results, output_dir)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Results saved to: {output_dir}")
    print("Generated visualizations:")
    print("- Regional linguistic heatmaps")
    print("- Regional similarity matrices") 
    print("- Regional clustering plots")

if __name__ == "__main__":
    main()
