#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tang Poetry Poet Geographical Distribution Map - Complete Version
包含所有可识别地理信息的诗人（扩展识别规则）
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Polygon
from matplotlib.lines import Line2D
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

# 扩展的地理识别规则 - 通过县名/州名推断所属道
LOCATION_TO_DAO = {
    # 关内道
    '京兆': 'Guannei Dao', '长安': 'Guannei Dao', 'Chang\'an': 'Guannei Dao',
    '華州': 'Guannei Dao', '同州': 'Guannei Dao', '鳳翔': 'Guannei Dao',
    
    # 河南道
    '洛阳': 'Henan Dao', 'Luoyang': 'Henan Dao', '河南': 'Henan Dao',
    '開封': 'Henan Dao', 'Kaifeng': 'Henan Dao', '汴州': 'Henan Dao',
    '濟源': 'Henan Dao', '陝州': 'Henan Dao', '鄭州': 'Henan Dao',
    
    # 河北道
    '魏州': 'Hebei Dao', '幽州': 'Hebei Dao', '邯鄲': 'Hebei Dao',
    '定州': 'Hebei Dao', '趙州': 'Hebei Dao',
    
    # 江南道
    '蘇州': 'Jiangnan Dao', '杭州': 'Jiangnan Dao', '越州': 'Jiangnan Dao',
    '湖州': 'Jiangnan Dao', '潤州': 'Jiangnan Dao', '婺州': 'Jiangnan Dao',
    '常州': 'Jiangnan Dao', '紹興': 'Jiangnan Dao', '浙江': 'Jiangnan Dao',
    '江蘇': 'Jiangnan Dao', '餘杭': 'Jiangnan Dao', 'Yuhang': 'Jiangnan Dao',
    
    # 河东道
    '太原': 'Hedong Dao', 'Taiyuan': 'Hedong Dao', '並州': 'Hedong Dao',
    '河內': 'Hedong Dao', 'Henei': 'Hedong Dao', '懷州': 'Hedong Dao',
    '澤州': 'Hedong Dao', '晉州': 'Hedong Dao',
    
    # 淮南道
    '揚州': 'Huainan Dao', 'Yangzhou': 'Huainan Dao', '楚州': 'Huainan Dao',
    '壽州': 'Huainan Dao', '泗州': 'Huainan Dao',
    
    # 山南道
    '襄州': 'Shannan Dao', '漢中': 'Shannan Dao', '鄧州': 'Shannan Dao',
    
    # 陇右道
    '蘭州': 'Longyou Dao', 'Lanzhou': 'Longyou Dao', '涼州': 'Longyou Dao',
    '秦州': 'Longyou Dao',
    
    # 剑南道
    '成都': 'Jiannan Dao', 'Chengdu': 'Jiannan Dao', '益州': 'Jiannan Dao',
    '劍州': 'Jiannan Dao', '綿州': 'Jiannan Dao',
    
    # 岭南道
    '廣州': 'Lingnan Dao', 'Guangzhou': 'Lingnan Dao', '桂州': 'Lingnan Dao',
    '邕州': 'Lingnan Dao', '潮州': 'Lingnan Dao',
}

# China border (same as before)
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

YELLOW_RIVER = [(96, 35.5), (99, 36), (102, 36.5), (105, 36), (107, 35.5), 
    (109, 35), (111, 35.5), (113, 35.3), (114, 35), (115, 35), 
    (116.5, 35.5), (118, 36.5), (119, 37.5), (119.5, 38)]

YANGTZE_RIVER = [(91, 30.5), (94, 30), (97, 29.5), (99, 29), (101, 29.5),
    (103, 30), (105, 30), (107, 30.5), (109, 30.5), (111, 30.5),
    (113, 30.8), (115, 31), (117, 31.5), (119, 31.8), (121, 31.5), (122, 31)]

MAJOR_CITIES = {
    'Chang\'an': (108.95, 34.27, 'red', 14),
    'Luoyang': (112.45, 34.68, 'darkred', 12),
    'Kaifeng': (114.35, 34.80, 'black', 10),
    'Yangzhou': (119.42, 32.39, 'black', 10),
    'Chengdu': (104.07, 30.65, 'black', 10),
    'Guangzhou': (113.25, 23.13, 'black', 10),
    'Hangzhou': (120.15, 30.25, 'black', 10),
}

def load_poet_geo_data_extended():
    """Load poet data with extended geographical recognition"""
    print("Loading poet geographical data with extended recognition...")
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    def extract_region_extended(geography):
        """Extended region extraction with more location matching"""
        if pd.isna(geography):
            return "Unknown"
        
        geo_str = str(geography)
        
        # 首先检查十道标签
        for dao_cn, dao_en in DAO_NAME_MAP.items():
            if dao_cn in geo_str:
                return dao_en
        
        # 然后检查扩展的地名映射
        for location, dao in LOCATION_TO_DAO.items():
            if location in geo_str:
                return dao
        
        return "Other"
    
    df['region'] = df['Geography'].apply(extract_region_extended)
    
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

def create_complete_bubble_map(df):
    """Create complete bubble map with all identifiable poets"""
    print("\nCreating complete bubble map...")
    
    # Statistics
    region_stats = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region').agg({
        'poet_name': 'count',
        'poem_count': 'sum',
        'gender': lambda x: (x == 'Male').sum()
    }).reset_index()
    region_stats.columns = ['region', 'poet_count', 'total_poems', 'male_count']
    region_stats['female_count'] = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region')['gender'].apply(lambda x: (x == 'Female').sum()).values
    
    print("\nPoet statistics by region (extended recognition):")
    total_identified = 0
    for _, row in region_stats.iterrows():
        print(f"  {row['region']}: {row['poet_count']} poets, {row['total_poems']:,} poems")
        total_identified += row['poet_count']
    
    print(f"\n✅ Total poets with geographical data: {total_identified}")
    print(f"⚠️  Poets without clear location: {len(df[df['region'] == 'Unknown'])}")
    print(f"⚠️  Poets with unmatched locations: {len(df[df['region'] == 'Other'])}")
    
    # Setup
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig = plt.figure(figsize=(26, 20), dpi=150)
    ax = fig.add_axes([0.05, 0.05, 0.72, 0.90])
    
    min_lon, max_lon = 72, 135
    min_lat, max_lat = 17, 54
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    
    # Background
    for i in range(6):
        alpha_val = 0.12 - i * 0.02
        color_val = ['#e3f2fd', '#cfe8fc', '#bbdefb', '#a7d4fa', '#93caf9', '#7fc0f8'][i]
        gradient_y = min_lat + (max_lat - min_lat) * i / 6
        gradient_h = (max_lat - min_lat) / 6
        ax.add_patch(plt.Rectangle((min_lon, gradient_y), max_lon - min_lon, gradient_h,
                                   facecolor=color_val, alpha=alpha_val, zorder=0))
    
    # China border
    border_x = [p[0] for p in CHINA_BORDER]
    border_y = [p[1] for p in CHINA_BORDER]
    china_polygon = Polygon(list(zip(border_x, border_y)), 
                           facecolor='#fef5e7', edgecolor='#8B4513', 
                           linewidth=3.5, alpha=0.5, zorder=1)
    ax.add_patch(china_polygon)
    
    # Rivers
    yellow_x = [p[0] for p in YELLOW_RIVER]
    yellow_y = [p[1] for p in YELLOW_RIVER]
    ax.plot(yellow_x, yellow_y, color='#DAA520', linewidth=4, 
           alpha=0.7, linestyle='-', zorder=2)
    
    yangtze_x = [p[0] for p in YANGTZE_RIVER]
    yangtze_y = [p[1] for p in YANGTZE_RIVER]
    ax.plot(yangtze_x, yangtze_y, color='#4682B4', linewidth=4,
           alpha=0.7, linestyle='-', zorder=2)
    
    # Grid
    for lon in np.arange(75, 135, 10):
        ax.axvline(lon, color='gray', linestyle=':', linewidth=0.6, alpha=0.3, zorder=2)
        ax.text(lon, min_lat + 0.8, f'{int(lon)}°E', ha='center', fontsize=9, 
               color='gray', alpha=0.8)
    for lat in np.arange(20, 55, 10):
        ax.axhline(lat, color='gray', linestyle=':', linewidth=0.6, alpha=0.3, zorder=2)
        ax.text(min_lon + 0.8, lat, f'{int(lat)}°N', va='center', fontsize=9,
               color='gray', alpha=0.8)
    
    # Cities
    for city, (lon, lat, color, size) in MAJOR_CITIES.items():
        ax.plot(lon, lat, '^', markersize=size, color=color, 
               markeredgecolor='black', markeredgewidth=1.5, alpha=0.8, zorder=4)
        ax.text(lon, lat - 1.2, city, fontsize=size-2, ha='center',
               style='italic', alpha=0.7, zorder=4, fontweight='bold')
    
    # Bubbles
    max_poets = region_stats['poet_count'].max()
    colors = plt.cm.Set3(np.linspace(0, 1, len(region_stats)))
    
    for idx, row in region_stats.iterrows():
        region = row['region']
        if region not in TANG_DAO_COORDINATES:
            continue
        
        lon, lat = TANG_DAO_COORDINATES[region]
        poet_ratio = np.sqrt(row['poet_count'] / max_poets)
        base_radius = 3.5
        radius = base_radius * poet_ratio
        
        circle = Circle((lon, lat), radius, 
                       color=colors[idx], alpha=0.75, 
                       edgecolor='darkred', linewidth=4, zorder=5)
        ax.add_patch(circle)
        
        if row['male_count'] > 0:
            male_ratio = row['male_count'] / row['poet_count']
            male_circle = Circle((lon, lat), radius * 1.12, 
                               fill=False, edgecolor='#1E90FF', 
                               linewidth=male_ratio * 4, alpha=0.7, zorder=6)
            ax.add_patch(male_circle)
        
        if row['female_count'] > 0:
            female_ratio = row['female_count'] / row['poet_count']
            female_circle = Circle((lon, lat), radius * 1.22, 
                                  fill=False, edgecolor='#FF1493', 
                                  linewidth=female_ratio * 8, alpha=0.85, zorder=7)
            ax.add_patch(female_circle)
        
        label = f"{region}\n{row['poet_count']} poets\n{row['total_poems']:,} poems"
        bbox_props = dict(boxstyle='round,pad=0.5', facecolor='white', 
                         edgecolor=colors[idx], linewidth=2.5, alpha=0.95)
        label_fontsize = 9 + poet_ratio * 4
        ax.text(lon, lat, label, fontsize=label_fontsize, ha='center', va='center',
               bbox=bbox_props, fontweight='bold', zorder=8)
    
    # Title
    total_poets = region_stats['poet_count'].sum()
    total_in_db = len(df)
    title = f'Geographical Distribution of Tang Dynasty Poets\n{total_poets} poets with identified locations (out of {total_in_db} total)'
    ax.set_title(title, fontsize=28, fontweight='bold', pad=20)
    
    ax.set_xlabel('Longitude (°E)', fontsize=18, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=18, fontweight='bold')
    
    # Legends (same as optimized version)
    legend_ax1 = fig.add_axes([0.80, 0.65, 0.18, 0.30])
    legend_ax1.set_xlim(0, 10)
    legend_ax1.set_ylim(0, 10)
    legend_ax1.axis('off')
    legend_ax1.text(5, 9.5, 'BUBBLE SIZE SCALE', ha='center', fontsize=14, 
                   fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    reference_counts = [50, 150, 310]
    y_positions = [7, 4.5, 1.5]
    for ref_count, y_pos in zip(reference_counts, y_positions):
        ref_ratio = np.sqrt(ref_count / max_poets)
        ref_radius = base_radius * ref_ratio * 0.5
        circle = Circle((3, y_pos), ref_radius, color='coral', alpha=0.6,
                       edgecolor='darkred', linewidth=2)
        legend_ax1.add_patch(circle)
        legend_ax1.text(7, y_pos, f'{ref_count} poets', va='center', fontsize=11, fontweight='bold')
    
    # Statistics
    total_poems = region_stats['total_poems'].sum()
    total_male = region_stats['male_count'].sum()
    total_female = region_stats['female_count'].sum()
    unknown_count = len(df[df['region'] == 'Unknown'])
    other_count = len(df[df['region'] == 'Other'])
    
    stats_ax = fig.add_axes([0.80, 0.05, 0.18, 0.55])
    stats_ax.set_xlim(0, 10)
    stats_ax.set_ylim(0, 10)
    stats_ax.axis('off')
    
    stats_text = (f'STATISTICS\n'
                 f'{"═" * 22}\n'
                 f'Database Total:\n'
                 f'  {total_in_db:>6} poets\n'
                 f'\n'
                 f'Mapped (10 Dao):\n'
                 f'  {total_poets:>6} poets\n'
                 f'  ├─Male:  {total_male:>5}\n'
                 f'  └─Female:{total_female:>5}\n'
                 f'\n'
                 f'Not Mapped:\n'
                 f'  {unknown_count:>6} no location\n'
                 f'  {other_count:>6} other location\n'
                 f'\n'
                 f'Total Poems: {total_poems:>6,}\n'
                 f'{"─" * 22}\n'
                 f'Avg/Poet: {total_poems/total_poets:>7.1f}\n'
                 f'\n'
                 f'TOP 3 REGIONS:\n')
    
    top3 = region_stats.nlargest(3, 'poet_count')
    for i, row in enumerate(top3.itertuples(), 1):
        stats_text += f'{i}. {row.region[:13]}\n   {row.poet_count} poets\n'
    
    stats_ax.text(5, 5, stats_text, ha='center', va='center', fontsize=10.5,
                 family='monospace', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=1', facecolor='#fffacd',
                          edgecolor='#ff8c00', linewidth=3, alpha=0.95))
    
    ax.set_facecolor('#f8f8f5')
    fig.patch.set_facecolor('white')
    
    return fig

def main():
    """Main function"""
    print("=" * 90)
    print("Tang Dynasty Poet Distribution - Complete Version (Extended Recognition)")
    print("=" * 90)
    
    df = load_poet_geo_data_extended()
    print(f"\n✅ Loaded {len(df)} poets from database")
    
    fig = create_complete_bubble_map(df)
    
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_map_complete.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Complete map saved: {output_file}")
    
    output_hd = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_map_complete_HD.png'
    fig.savefig(output_hd, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"✅ HD version saved: {output_hd}")
    
    plt.close()
    print("\n" + "=" * 90)
    print("✨ Complete map with extended recognition finished!")
    print("=" * 90)

if __name__ == '__main__':
    main()

