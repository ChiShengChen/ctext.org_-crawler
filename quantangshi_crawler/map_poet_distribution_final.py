#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tang Poetry Poet Geographical Distribution Map - Final Version
Beautiful visualization with detailed geographical features
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
from matplotlib.collections import LineCollection
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Tang Dynasty 10 Circuits coordinates
TANG_DAO_COORDINATES = {
    'Guannei Dao': (108.95, 34.27),
    'Henan Dao': (113.65, 34.76),
    'Hebei Dao': (114.48, 38.03),
    'Jiangnan Dao': (120.15, 30.28),
    'Hedong Dao': (112.55, 37.87),
    'Huainan Dao': (119.42, 32.39),
    'Shannan Dao': (106.71, 33.04),
    'Longyou Dao': (103.85, 36.06),
    'Jiannan Dao': (104.07, 30.65),
    'Lingnan Dao': (113.25, 23.13),
}

DAO_NAME_MAP = {
    '關內道': 'Guannei Dao',
    '河南道': 'Henan Dao',
    '河北道': 'Hebei Dao',
    '江南道': 'Jiangnan Dao',
    '河東道': 'Hedong Dao',
    '淮南道': 'Huainan Dao',
    '山南道': 'Shannan Dao',
    '隴右道': 'Longyou Dao',
    '劍南道': 'Jiannan Dao',
    '嶺南道': 'Lingnan Dao',
}

# Detailed China border (more points for smoother outline)
CHINA_BORDER = [
    (135.0, 48.5), (133.5, 50.0), (131.0, 51.5), (128.5, 52.0), (126.0, 52.5),
    (123.5, 53.0), (121.0, 53.3), (118.5, 53.5), (116.0, 53.3), (114.5, 52.5),
    (113.5, 51.0), (112.5, 49.5), (111.0, 48.0), (110.0, 46.5), (109.0, 45.0),
    (108.0, 43.5), (107.0, 42.5), (106.0, 42.0), (104.5, 42.0), (102.5, 42.5),
    (100.0, 42.5), (97.5, 42.5), (95.0, 42.5), (92.5, 42.3), (90.0, 42.0),
    (87.5, 41.0), (85.0, 40.0), (82.5, 38.5), (80.0, 37.0), (78.0, 36.0),
    (76.5, 35.5), (75.5, 35.0), (74.5, 34.0), (74.0, 33.0), (73.8, 32.0),
    (74.0, 31.0), (75.0, 30.5), (76.5, 30.0), (78.5, 29.5), (81.0, 29.0),
    (84.0, 28.5), (87.0, 28.2), (90.0, 28.0), (93.0, 27.5), (95.5, 27.0),
    (97.5, 26.0), (99.0, 25.0), (100.0, 23.5), (101.0, 22.0), (102.0, 21.0),
    (103.5, 20.5), (105.0, 20.0), (107.0, 20.0), (109.0, 20.3), (110.5, 20.8),
    (112.0, 21.3), (113.5, 21.8), (115.0, 22.0), (116.5, 22.5), (118.0, 23.0),
    (119.5, 23.8), (121.0, 24.5), (122.0, 25.3), (122.8, 26.5), (123.0, 27.5),
    (122.8, 28.8), (122.5, 30.0), (122.3, 31.5), (122.0, 33.0), (121.5, 34.5),
    (121.3, 36.0), (121.5, 37.5), (122.0, 39.0), (123.0, 40.5), (124.5, 42.0),
    (126.5, 43.5), (128.5, 45.0), (130.5, 46.5), (132.5, 47.8), (135.0, 48.5)
]

# Major rivers (Yangtze and Yellow River - simplified)
YELLOW_RIVER = [
    (96, 35.5), (99, 36), (102, 36.5), (105, 36), (107, 35.5), 
    (109, 35), (111, 35.5), (113, 35.3), (114, 35), (115, 35), 
    (116.5, 35.5), (118, 36.5), (119, 37.5), (119.5, 38)
]

YANGTZE_RIVER = [
    (91, 30.5), (94, 30), (97, 29.5), (99, 29), (101, 29.5),
    (103, 30), (105, 30), (107, 30.5), (109, 30.5), (111, 30.5),
    (113, 30.8), (115, 31), (117, 31.5), (119, 31.8), (121, 31.5), (122, 31)
]

# Major cities
MAJOR_CITIES = {
    'Chang\'an (Xi\'an)': (108.95, 34.27),
    'Luoyang': (112.45, 34.68),
    'Kaifeng': (114.35, 34.80),
    'Yangzhou': (119.42, 32.39),
    'Chengdu': (104.07, 30.65),
    'Guangzhou': (113.25, 23.13),
    'Hangzhou': (120.15, 30.25),
}

def load_poet_geo_data():
    """Load poet geographical data"""
    print("Loading poet geographical data...")
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    def extract_region(geography):
        if pd.isna(geography):
            return "Unknown"
        geo_str = str(geography)
        for dao_cn, dao_en in DAO_NAME_MAP.items():
            if dao_cn in geo_str:
                return dao_en
        return "Other"
    
    df['region'] = df['Geography'].apply(extract_region)
    
    def extract_poet_info(text):
        if pd.isna(text):
            return "Unknown", 0
        text_str = str(text)
        if ':' in text_str:
            name = text_str.split(':')[0].strip()
            if '.' in name:
                name = name.split('.', 1)[1].strip()
        else:
            name = text_str
        import re
        count_match = re.search(r'(\d+)\s*首', text_str)
        count = int(count_match.group(1)) if count_match else 0
        return name, count
    
    df[['poet_name', 'poem_count']] = df['詩人'].apply(lambda x: pd.Series(extract_poet_info(x)))
    
    def extract_gender(text):
        if pd.isna(text):
            return "Unknown"
        text_str = str(text).lower()
        if 'male' in text_str and 'female' not in text_str:
            return "Male"
        elif 'female' in text_str:
            return "Female"
        return "Unknown"
    
    df['gender'] = df['性別'].apply(extract_gender)
    
    return df

def create_detailed_map(df):
    """Create detailed map with geographical features"""
    print("\nCreating detailed map visualization...")
    
    # Statistics
    region_stats = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region').agg({
        'poet_name': 'count',
        'poem_count': 'sum',
        'gender': lambda x: (x == 'Male').sum()
    }).reset_index()
    region_stats.columns = ['region', 'poet_count', 'total_poems', 'male_count']
    region_stats['female_count'] = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region')['gender'].apply(lambda x: (x == 'Female').sum()).values
    
    print("\nPoet statistics by region:")
    for _, row in region_stats.iterrows():
        print(f"  {row['region']}: {row['poet_count']} poets (M:{row['male_count']}, F:{row['female_count']}), {row['total_poems']} poems")
    
    # Setup
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, ax = plt.subplots(figsize=(24, 20), dpi=150)
    
    # Map bounds
    min_lon, max_lon = 72, 135
    min_lat, max_lat = 17, 54
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    
    # Background with gradient
    for i in range(5):
        alpha_val = 0.15 - i * 0.03
        color_val = ['#e8f4f8', '#d4e9f0', '#c0dee8', '#acd3e0', '#98c8d8'][i]
        gradient_y = min_lat + (max_lat - min_lat) * i / 5
        gradient_h = (max_lat - min_lat) / 5
        ax.add_patch(plt.Rectangle((min_lon, gradient_y), max_lon - min_lon, gradient_h,
                                   facecolor=color_val, alpha=alpha_val, zorder=0))
    
    # China border
    border_x = [p[0] for p in CHINA_BORDER]
    border_y = [p[1] for p in CHINA_BORDER]
    china_polygon = Polygon(list(zip(border_x, border_y)), 
                           facecolor='#f5f1e8', edgecolor='#8B4513', 
                           linewidth=3, alpha=0.4, zorder=1)
    ax.add_patch(china_polygon)
    
    # Rivers
    yellow_x = [p[0] for p in YELLOW_RIVER]
    yellow_y = [p[1] for p in YELLOW_RIVER]
    ax.plot(yellow_x, yellow_y, color='#DAA520', linewidth=3, 
           alpha=0.6, linestyle='-', label='Yellow River', zorder=2)
    
    yangtze_x = [p[0] for p in YANGTZE_RIVER]
    yangtze_y = [p[1] for p in YANGTZE_RIVER]
    ax.plot(yangtze_x, yangtze_y, color='#4682B4', linewidth=3,
           alpha=0.6, linestyle='-', label='Yangtze River', zorder=2)
    
    # Grid
    for lon in np.arange(75, 135, 5):
        ax.axvline(lon, color='gray', linestyle=':', linewidth=0.5, alpha=0.25, zorder=2)
        ax.text(lon, min_lat + 1, f'{int(lon)}°E', ha='center', fontsize=8, 
               color='gray', alpha=0.7)
    for lat in np.arange(20, 55, 5):
        ax.axhline(lat, color='gray', linestyle=':', linewidth=0.5, alpha=0.25, zorder=2)
        ax.text(min_lon + 1, lat, f'{int(lat)}°N', va='center', fontsize=8,
               color='gray', alpha=0.7)
    
    # Major cities
    for city, (lon, lat) in MAJOR_CITIES.items():
        ax.plot(lon, lat, 'k^', markersize=8, alpha=0.5, zorder=4)
        ax.text(lon, lat - 1.2, city, fontsize=9, ha='center',
               style='italic', alpha=0.6, zorder=4)
    
    # Poet distribution bubbles
    max_poets = region_stats['poet_count'].max()
    colors = plt.cm.Spectral_r(np.linspace(0.1, 0.9, len(region_stats)))
    
    for idx, row in region_stats.iterrows():
        region = row['region']
        if region not in TANG_DAO_COORDINATES:
            continue
        
        lon, lat = TANG_DAO_COORDINATES[region]
        size = 400 + (row['poet_count'] / max_poets) * 3000
        radius = size / 5000
        
        # Main bubble
        circle = Circle((lon, lat), radius, 
                       color=colors[idx], alpha=0.75, 
                       edgecolor='darkred', linewidth=3.5, zorder=5)
        ax.add_patch(circle)
        
        # Gender rings
        if row['male_count'] > 0:
            male_ratio = row['male_count'] / row['poet_count']
            male_circle = Circle((lon, lat), radius * 1.18, 
                               fill=False, edgecolor='#1E90FF', 
                               linewidth=male_ratio * 6, alpha=0.8, zorder=6)
            ax.add_patch(male_circle)
        
        if row['female_count'] > 0:
            female_ratio = row['female_count'] / row['poet_count']
            female_circle = Circle((lon, lat), radius * 1.32, 
                                  fill=False, edgecolor='#FF1493', 
                                  linewidth=female_ratio * 12, alpha=0.9, zorder=7)
            ax.add_patch(female_circle)
        
        # Labels
        label = f"{region}\n{row['poet_count']} poets\n{row['total_poems']:,} poems"
        bbox_props = dict(boxstyle='round,pad=0.8', 
                         facecolor='white', 
                         edgecolor=colors[idx], 
                         linewidth=3,
                         alpha=0.95)
        ax.text(lon, lat, label, fontsize=12, ha='center', va='center',
               bbox=bbox_props, fontweight='bold', zorder=8)
    
    # Title
    title = 'Geographical Distribution of Tang Dynasty Poets\nClassified by the Ten Circuits (Dao) System'
    ax.set_title(title, fontsize=32, fontweight='bold', pad=30)
    
    ax.set_xlabel('Longitude (°E)', fontsize=20, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=20, fontweight='bold')
    
    # Legend
    total_poets = region_stats['poet_count'].sum()
    total_poems = region_stats['total_poems'].sum()
    total_male = region_stats['male_count'].sum()
    total_female = region_stats['female_count'].sum()
    
    legend_elements = [
        mpatches.Patch(facecolor='red', edgecolor='darkred', alpha=0.75, 
                      label='Bubble size ∝ Number of poets'),
        mpatches.Patch(facecolor='#1E90FF', alpha=0.8, 
                      label='Blue ring ∝ Male ratio'),
        mpatches.Patch(facecolor='#FF1493', alpha=0.9, 
                      label='Pink ring ∝ Female ratio'),
        mpatches.Patch(facecolor='none', edgecolor='none', label=''),
        plt.Line2D([0], [0], color='#DAA520', linewidth=3, alpha=0.6, label='Yellow River'),
        plt.Line2D([0], [0], color='#4682B4', linewidth=3, alpha=0.6, label='Yangtze River'),
    ]
    
    legend1 = ax.legend(handles=legend_elements, loc='upper left', 
                       fontsize=14, framealpha=0.95, edgecolor='black', 
                       fancybox=True, shadow=True)
    
    # Statistics box
    stats_text = (f'TOTAL STATISTICS\n'
                 f'{"═" * 30}\n'
                 f'Total Poets:  {total_poets:>6}\n'
                 f'  ├─ Male:    {total_male:>6}\n'
                 f'  └─ Female:  {total_female:>6}\n'
                 f'\n'
                 f'Total Poems:  {total_poems:>6,}\n'
                 f'{"═" * 30}\n'
                 f'Average/Poet: {total_poems/total_poets:>6.1f}')
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
           fontsize=15, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=1.2', facecolor='#fffacd', 
                    edgecolor='#ff8c00', linewidth=3, alpha=0.95),
           fontweight='bold', family='monospace')
    
    # Top 5 ranking
    top5 = region_stats.nlargest(5, 'poet_count')
    ranking_text = 'TOP 5 REGIONS\n' + '─' * 28 + '\n'
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    for i, row in enumerate(top5.itertuples()):
        ranking_text += f'{i+1}. {row.region}\n   {row.poet_count} poets | {row.total_poems:,} poems\n'
    
    ax.text(0.02, 0.98, ranking_text, transform=ax.transAxes,
           fontsize=14, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=1', facecolor='#e6f3ff', 
                    edgecolor='#000080', linewidth=3, alpha=0.95),
           fontweight='bold')
    
    ax.set_facecolor('#f8f8f5')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    return fig

def main():
    """Main function"""
    print("=" * 90)
    print("Tang Dynasty Poet Geographical Distribution Map - Final English Version")
    print("=" * 90)
    
    df = load_poet_geo_data()
    print(f"\n✅ Loaded {len(df)} poets")
    
    fig = create_detailed_map(df)
    
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_map_english_final.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Map saved: {output_file}")
    
    output_hd = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_map_english_final_HD.png'
    fig.savefig(output_hd, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"✅ HD version saved: {output_hd}")
    
    plt.close()
    print("\n" + "=" * 90)
    print("✨ Visualization complete!")
    print("=" * 90)

if __name__ == '__main__':
    main()

