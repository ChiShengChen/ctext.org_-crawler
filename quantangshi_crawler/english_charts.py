#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Charts and Visualizations for Tang Poetry Analysis
《全唐詩》詩人分布與文學集中化現象 - 英文圖表生成
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams
import matplotlib.font_manager as fm

# Set up matplotlib for better Chinese font support
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Set style
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

def create_top_poets_chart():
    """Create chart for top 10 poets by poem count"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Data for top 10 poets
    poets = ['Bai Juyi', 'Du Fu', 'Li Bai', 'Qi Ji', 
             'Liu Yuxi', 'Yuan Zhen', 'Li Shangyin', 
             'Wei Yingwu', 'Guan Xiu', 'Lu Guimeng']
    
    poem_counts = [2600, 1137, 853, 770, 688, 563, 552, 540, 537, 503]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
              '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    
    bars = ax.barh(poets, poem_counts, color=colors)
    
    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, poem_counts)):
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
                f'{count:,}', ha='left', va='center', fontweight='bold')
    
    ax.set_xlabel('Number of Poems', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Poets by Poem Count in Complete Tang Poetry', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add percentage annotations
    total_poems = sum(poem_counts)
    for i, count in enumerate(poem_counts):
        percentage = (count / total_poems) * 100
        ax.text(bar.get_width() + 200, i, f'({percentage:.1f}%)', 
                ha='left', va='center', fontsize=10, style='italic')
    
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/top_poets_chart.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_concentration_chart():
    """Create chart showing literary concentration phenomenon"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Chart 1: Cumulative distribution
    categories = ['Top 10\nPoets', 'Top 50\nPoets', 'Top 100\nPoets', 'All Others\n(1,360 poets)']
    percentages = [21.1, 53.6, 71.5, 28.5]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#DDA0DD']
    
    bars1 = ax1.bar(categories, percentages, color=colors, alpha=0.8)
    ax1.set_ylabel('Percentage of Total Poems (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Literary Concentration in Tang Poetry', 
                  fontsize=14, fontweight='bold')
    
    # Add value labels
    for bar, pct in zip(bars1, percentages):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{pct}%', ha='center', va='bottom', fontweight='bold')
    
    ax1.grid(axis='y', alpha=0.3)
    
    # Chart 2: Marginal poets distribution
    marginal_categories = ['1 Poem Only\n(1,313 poets)', 'Multiple Poems\n(1,147 poets)']
    marginal_counts = [1313, 1147]
    marginal_colors = ['#FFB6C1', '#87CEEB']
    
    wedges, texts, autotexts = ax2.pie(marginal_counts, labels=marginal_categories, 
                                      colors=marginal_colors, autopct='%1.1f%%', 
                                      startangle=90, textprops={'fontsize': 10})
    
    ax2.set_title('Distribution of Marginal vs. Productive Poets', 
                  fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/concentration_chart.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_geographical_distribution():
    """Create geographical distribution chart"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Geographic regions and poet counts
    regions = ['Guannei Dao\n(Chang\'an Region)', 
               'Jiangnan Dao\n(Jiangnan Region)',
               'Hebei Dao\n(Hebei Region)', 
               'Hedong Dao\n(Hedong Region)',
               'Other Regions']
    
    poet_counts = [45, 38, 32, 28, 15]  # Approximate counts based on data analysis
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']
    
    bars = ax.bar(regions, poet_counts, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, count in zip(bars, poet_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Number of Top Poets', fontsize=12, fontweight='bold')
    ax.set_title('Geographical Distribution of Top Tang Poets', 
                 fontsize=14, fontweight='bold')
    
    # Add annotations
    ax.annotate('Political Centers', xy=(0, 45), xytext=(1, 50),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, ha='center')
    
    ax.annotate('Economic & Cultural Centers', xy=(1, 38), xytext=(2, 43),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                fontsize=10, ha='center')
    
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/geographical_distribution.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_social_status_analysis():
    """Create social status analysis chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Chart 1: Social status distribution
    status_categories = ['Civil Officials', 'Monks', 'Imperial Family', 
                        'Recluses', 'Others']
    status_counts = [65, 15, 8, 7, 5]
    status_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']
    
    bars1 = ax1.bar(status_categories, status_counts, color=status_colors, alpha=0.8)
    ax1.set_ylabel('Number of Top Poets', fontsize=12, fontweight='bold')
    ax1.set_title('Social Status Distribution of Top Poets', 
                  fontsize=14, fontweight='bold')
    
    for bar, count in zip(bars1, status_counts):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    ax1.grid(axis='y', alpha=0.3)
    plt.setp(ax1.get_xticklabels(), rotation=15)
    
    # Chart 2: Gender distribution
    gender_categories = ['Male Poets', 'Female Poets']
    gender_counts = [2312, 148]
    gender_colors = ['#4ECDC4', '#FFB6C1']
    
    wedges, texts, autotexts = ax2.pie(gender_counts, labels=gender_categories, 
                                      colors=gender_colors, autopct='%1.1f%%', 
                                      startangle=90, textprops={'fontsize': 12})
    
    ax2.set_title('Gender Distribution in Tang Poetry', 
                  fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/social_status_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_bai_juyi_analysis():
    """Create Bai Juyi success factors analysis"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Bai Juyi's success factors
    factors = ['Political Status', 'Geographic Advantage', 
               'Multiple Identities', 'Social Network',
               'Writing Philosophy', 'Language Style']
    
    importance_scores = [9, 8, 9, 8, 9, 8]  # Importance scores out of 10
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    bars = ax.barh(factors, importance_scores, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, score in zip(bars, importance_scores):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{score}/10', ha='left', va='center', fontweight='bold')
    
    ax.set_xlabel('Importance Score (1-10)', fontsize=12, fontweight='bold')
    ax.set_title('Bai Juyi\'s Success Factors Analysis', 
                 fontsize=14, fontweight='bold')
    
    # Add annotations
    ax.annotate('Highest Impact', xy=(9, 0), xytext=(7, -0.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, ha='center')
    
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/bai_juyi_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_marginal_poets_analysis():
    """Create marginal poets analysis chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Marginal poets characteristics
    characteristics = ['Imperial Family', 'Imperial Consorts', 
                      'Rulers', 'Low Officials', 
                      'Unknown Status']
    
    counts = [25, 15, 12, 35, 1226]  # Approximate counts
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']
    
    bars = ax.bar(characteristics, counts, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, 
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Number of Marginal Poets', fontsize=12, fontweight='bold')
    ax.set_title('Characteristics of Marginal Poets (1 Poem Only)', 
                 fontsize=14, fontweight='bold')
    
    # Add percentage annotations
    total_marginal = sum(counts)
    for i, count in enumerate(counts):
        percentage = (count / total_marginal) * 100
        ax.text(i, count + 20, f'({percentage:.1f}%)', ha='center', va='bottom', 
                fontsize=10, style='italic')
    
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/marginal_poets_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def create_temporal_analysis():
    """Create temporal analysis chart"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Time periods and poet counts
    periods = ['Early Tang\n(618-712)', 'High Tang\n(713-765)', 
               'Mid Tang\n(766-835)', 'Late Tang\n(836-907)']
    
    poet_counts = [45, 120, 85, 60]  # Approximate counts
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars = ax.bar(periods, poet_counts, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, count in zip(bars, poet_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Number of Top Poets', fontsize=12, fontweight='bold')
    ax.set_title('Temporal Distribution of Tang Poets', 
                 fontsize=14, fontweight='bold')
    
    # Add annotations
    ax.annotate('Peak Period', xy=(1, 120), xytext=(1, 140),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, ha='center')
    
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/temporal_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Generate all charts"""
    print("Generating English charts for Tang Poetry Analysis...")
    
    print("1. Creating top poets chart...")
    create_top_poets_chart()
    
    print("2. Creating concentration analysis chart...")
    create_concentration_chart()
    
    print("3. Creating geographical distribution chart...")
    create_geographical_distribution()
    
    print("4. Creating social status analysis chart...")
    create_social_status_analysis()
    
    print("5. Creating Bai Juyi analysis chart...")
    create_bai_juyi_analysis()
    
    print("6. Creating marginal poets analysis chart...")
    create_marginal_poets_analysis()
    
    print("7. Creating temporal analysis chart...")
    create_temporal_analysis()
    
    print("All charts generated successfully!")
    print("Charts saved in the project directory with high resolution (300 DPI)")

if __name__ == "__main__":
    main()
