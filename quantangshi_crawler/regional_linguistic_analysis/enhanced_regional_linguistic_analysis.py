#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Regional Linguistic Analysis for Tang Poetry
增強版地域語言分析：確保所有數字都正確顯示
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json
import numpy as np
import matplotlib.font_manager as fm

# Set Chinese font for matplotlib
try:
    font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
except:
    print("Chinese font not found, using default. Chinese characters might not display correctly.")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class EnhancedRegionalLinguisticAnalyzer:
    def __init__(self, poet_geo_path, ngram_dir):
        self.poet_geo_path = poet_geo_path
        self.ngram_dir = ngram_dir
        self.poet_data = self.load_poet_data()
        self.ngram_data = {}
        self.matched_poets = set()

    def load_poet_data(self):
        """Load poet geographical data and clean it."""
        df = pd.read_csv(self.poet_geo_path)
        df.columns = [col.strip() for col in df.columns]

        # Filter out summary rows
        df = df[~df['詩人'].str.contains('統計摘要|產量分布|頂級作者統計', na=False)].copy()

        # Extract poet name and poem count
        def extract_poet_info(row):
            name_str = str(row['詩人'])
            # Extract name from format like "1. 白居易: 2,600 首"
            name_match = re.search(r'(\d+\.\s*)?([^:：]+)', name_str)
            if name_match:
                name = name_match.group(2).strip()
                # Extract count
                count_match = re.search(r':\s*(\d{1,3}(?:,\d{3})*)\s*首', name_str)
                if count_match:
                    count = int(count_match.group(1).replace(',', ''))
                else:
                    count = 0
                return name, count
            return name_str, 0

        df[['poet_name', 'poem_count']] = df.apply(extract_poet_info, axis=1, result_type='expand')
        
        # Extract primary region
        def extract_primary_region(geo_str):
            if pd.isna(geo_str):
                return 'Unknown'
            geo_str = str(geo_str)
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

        df['region'] = df['Geography'].apply(extract_primary_region)
        
        print(f"Loaded {len(df)} poets")
        return df[['poet_name', 'region', 'poem_count']].dropna(subset=['region'])

    def load_ngram_data(self):
        """Load 1-gram, 2-gram, and 4-gram data."""
        ngram_files = {
            '1gram': 'merged_1gram_詞頻統計.csv',
            '2gram': 'merged_2gram_詞頻統計.csv',
            '4gram': 'merged_4gram_詞頻統計.csv'
        }
        
        for ngram_type, filename in ngram_files.items():
            file_path = os.path.join(self.ngram_dir, filename)
            if os.path.exists(file_path):
                print(f"Loading {ngram_type} data from {filename}")
                self.ngram_data[ngram_type] = pd.read_csv(file_path)
            else:
                print(f"Warning: {filename} not found")
        
        return self.ngram_data
    
    def find_matched_poets(self):
        """Find poets that exist in both datasets."""
        if '1gram' not in self.ngram_data:
            print("No n-gram data loaded")
            return set()
        
        # Get all poets from n-gram data
        ngram_poets = set(self.ngram_data['1gram']['詩人'].unique())
        
        # Get all poets from geographical data
        geo_poets = set(self.poet_data['poet_name'].unique())
        
        # Find intersection
        matched_poets = ngram_poets.intersection(geo_poets)
        
        print(f"Found {len(matched_poets)} matched poets")
        print(f"Sample matched poets: {list(matched_poets)[:10]}")
        
        self.matched_poets = matched_poets
        return matched_poets

    def create_regional_ngram_matrix(self, ngram_type='1gram', top_n=100):
        """Create regional n-gram frequency matrix"""
        if ngram_type not in self.ngram_data:
            print(f"Error: {ngram_type} data not loaded")
            return None
        
        print(f"Creating regional {ngram_type} matrix...")
        
        # Get the n-gram data
        ngram_df = self.ngram_data[ngram_type]
        
        # Get top n-grams by total frequency
        ngram_freq = ngram_df.groupby('字詞')['詞頻'].sum().sort_values(ascending=False)
        top_ngrams = ngram_freq.head(top_n).index.tolist()
        
        # Create regional matrix
        regions = self.poet_data['region'].unique()
        regional_matrix = pd.DataFrame(index=regions, columns=top_ngrams)
        regional_matrix = regional_matrix.fillna(0)
        
        # Calculate frequencies for each region
        for region in regions:
            region_poets = self.poet_data[self.poet_data['region'] == region]['poet_name'].tolist()
            
            for poet in region_poets:
                if poet in self.matched_poets:
                    # Get poet's n-gram data
                    poet_data = ngram_df[ngram_df['詩人'] == poet]
                    
                    for ngram in top_ngrams:
                        ngram_data = poet_data[poet_data['字詞'] == ngram]
                        if not ngram_data.empty:
                            freq = ngram_data['詞頻'].iloc[0]
                            if pd.notna(freq) and freq > 0:
                                regional_matrix.loc[region, ngram] += freq
        
        # Remove rows with all zeros
        regional_matrix = regional_matrix.loc[(regional_matrix != 0).any(axis=1)]
        
        print(f"Regional matrix shape: {regional_matrix.shape}")
        print(f"Non-zero entries: {(regional_matrix > 0).sum().sum()}")
        
        return regional_matrix

    def calculate_regional_similarity(self, regional_matrix):
        """Calculate cosine similarity between regions"""
        # Normalize the matrix
        normalized_matrix = regional_matrix.div(regional_matrix.sum(axis=1), axis=0)
        
        # Fill NaN values with 0 after normalization
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
        scaled_matrix = scaler.fit_transform(regional_matrix)
        
        # Fill NaN values with 0 after scaling
        scaled_matrix = np.nan_to_num(scaled_matrix, nan=0.0)

        # Perform PCA for dimensionality reduction for visualization
        pca = PCA(n_components=min(regional_matrix.shape[0], regional_matrix.shape[1], 2))
        pca_components = pca.fit_transform(scaled_matrix)
        
        # Perform K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_matrix)
        
        cluster_results = pd.DataFrame({
            'region': regional_matrix.index,
            'cluster': clusters,
            'pca1': pca_components[:, 0],
            'pca2': pca_components[:, 1]
        })
        
        return cluster_results, pca

    def plot_heatmap_with_all_numbers(self, data, title, filename, output_dir):
        """Plot a heatmap with ALL numbers visible."""
        plt.figure(figsize=(20, 16))
        
        # Create heatmap with all numbers visible
        ax = sns.heatmap(data, annot=True, cmap='viridis', fmt=".4f", 
                        linewidths=0.5, cbar_kws={'shrink': 0.8},
                        annot_kws={'size': 10, 'weight': 'bold', 'color': 'white'})
        
        # Customize the plot
        plt.title(title, fontsize=20, pad=30, weight='bold')
        plt.xticks(rotation=45, ha='right', fontsize=14)
        plt.yticks(rotation=0, fontsize=14)
        
        # Ensure all annotations are visible and properly formatted
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=12)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=12)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save with high DPI
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close()

    def plot_clusters_with_all_numbers(self, cluster_results, title, filename, output_dir):
        """Plot clustering results with all numbers visible."""
        plt.figure(figsize=(14, 12))
        
        # Create scatter plot
        sns.scatterplot(data=cluster_results, x='pca1', y='pca2', hue='cluster', 
                        palette='deep', s=200, alpha=0.8)
        
        # Add region labels with numbers
        for i, row in cluster_results.iterrows():
            plt.text(row['pca1'] + 0.02, row['pca2'] + 0.02, 
                    f"{row['region']}\nCluster: {row['cluster']}", 
                    horizontalalignment='left', size=12, color='black', weight='bold')
        
        plt.title(title, fontsize=18, weight='bold')
        plt.xlabel('PCA Component 1', fontsize=14)
        plt.ylabel('PCA Component 2', fontsize=14)
        plt.legend(title='Cluster', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save with high DPI
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close()

    def save_results(self, results, output_dir):
        """Save analysis results to a JSON file."""
        # Convert any non-JSON serializable types
        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                results[key] = value.to_dict(orient='records')
            elif isinstance(value, np.ndarray):
                results[key] = value.tolist()
            elif isinstance(value, (np.int64, np.int32)):
                results[key] = int(value)
            elif isinstance(value, (np.float64, np.float32)):
                results[key] = float(value)

        with open(os.path.join(output_dir, 'enhanced_analysis_results.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    poet_geo_path = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv'
    ngram_dir = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/analysis_result/analysis_results_no_title/author_ngram_csvs'
    output_dir = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/regional_linguistic_analysis'

    os.makedirs(output_dir, exist_ok=True)

    analyzer = EnhancedRegionalLinguisticAnalyzer(poet_geo_path, ngram_dir)
    print("=== Enhanced Regional Linguistic Analysis ===")
    
    print("Loading poet geographical data...")
    # Poet data is loaded in __init__
    
    print("Loading n-gram data...")
    analyzer.load_ngram_data()
    
    print("Finding matched poets...")
    matched_poets = analyzer.find_matched_poets()
    
    if len(matched_poets) == 0:
        print("No matched poets found. Analysis cannot proceed.")
        return
    
    all_results = {}

    for ngram_type in ['1gram', '2gram', '4gram']:
        print(f"\n=== Analyzing {ngram_type} patterns ===")
        regional_matrix = analyzer.create_regional_ngram_matrix(ngram_type, top_n=50)
        
        if regional_matrix is not None and not regional_matrix.empty:
            # Plot heatmap of regional n-gram frequencies with ALL numbers
            analyzer.plot_heatmap_with_all_numbers(regional_matrix, 
                                f'Top 50 {ngram_type.capitalize()} Frequencies by Region (All Numbers Visible)',
                                f'enhanced_regional_{ngram_type}_heatmap.png', output_dir)
            
            # Calculate and plot similarity matrix with ALL numbers
            similarity_matrix = analyzer.calculate_regional_similarity(regional_matrix)
            analyzer.plot_heatmap_with_all_numbers(similarity_matrix, 
                                f'Regional {ngram_type.capitalize()} Cosine Similarity (All Numbers Visible)',
                                f'enhanced_regional_{ngram_type}_similarity.png', output_dir)
            
            # Perform and plot clustering with ALL numbers
            n_clusters = min(4, len(regional_matrix.index))
            if n_clusters > 1:
                cluster_results, pca_model = analyzer.perform_regional_clustering(regional_matrix, n_clusters=n_clusters)
                analyzer.plot_clusters_with_all_numbers(cluster_results, 
                                    f'Regional {ngram_type.capitalize()} Clustering (PCA) All Numbers Visible',
                                    f'enhanced_regional_{ngram_type}_clusters.png', output_dir)
                all_results[f'{ngram_type}_clusters'] = cluster_results
                all_results[f'{ngram_type}_pca_explained_variance'] = pca_model.explained_variance_ratio_.sum()
            else:
                print(f"Not enough regions to perform clustering for {ngram_type}.")

            all_results[f'{ngram_type}_regional_matrix'] = regional_matrix
            all_results[f'{ngram_type}_similarity_matrix'] = similarity_matrix
            print(f"Analysis completed for {ngram_type}")
        else:
            print(f"No data to analyze for {ngram_type}")

    analyzer.save_results(all_results, output_dir)
    print(f"\nEnhanced regional linguistic analysis completed!")
    print(f"Found {len(matched_poets)} matched poets between datasets")
    print("All charts now include ALL numbers visible!")

if __name__ == '__main__':
    main()
