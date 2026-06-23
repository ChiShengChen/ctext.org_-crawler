#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tang Poetry Poet Geographical Distribution Map Visualization (English Version)
Map poets' distribution on Tang Dynasty historical map with English labels
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
from matplotlib.patches import Circle
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Tang Dynasty 10 Circuits (Dao) coordinates (longitude, latitude)
TANG_DAO_COORDINATES = {
    'Guannei Dao': (108.95, 34.27),      # Near Chang'an (Xi'an)
    'Henan Dao': (113.65, 34.76),        # Near Luoyang
    'Hebei Dao': (114.48, 38.03),        # Near Handan, Dingzhou
    'Jiangnan Dao': (120.15, 30.28),     # Near Hangzhou, Suzhou
    'Hedong Dao': (112.55, 37.87),       # Near Taiyuan
    'Huainan Dao': (119.42, 32.39),      # Near Yangzhou
    'Shannan Dao': (106.71, 33.04),      # Near Hanzhong
    'Longyou Dao': (103.85, 36.06),      # Near Lanzhou
    'Jiannan Dao': (104.07, 30.65),      # Near Chengdu
    'Lingnan Dao': (113.25, 23.13),      # Near Guangzhou
}

# Chinese to English mapping
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

# China border outline (simplified)
CHINA_BORDER_POINTS = [
    (135, 48), (130, 53), (125, 53), (120, 53), (115, 53),
    (115, 50), (112, 47), (110, 45), (108, 43), (106, 42),
    (105, 42), (100, 42), (95, 42), (90, 42), (85, 40),
    (80, 37), (75, 35),
    (75, 32), (78, 30), (85, 28), (90, 28), (95, 27),
    (98, 25), (100, 22), (102, 21),
    (105, 20), (108, 20), (110, 21), (112, 21), (115, 22),
    (118, 23), (120, 24), (122, 25),
    (123, 27), (122, 30), (122, 33), (121, 36), (122, 39),
    (124, 42), (127, 45), (130, 47), (135, 48)
]

def load_poet_geo_data():
    """Load poet geographical data"""
    print("Loading poet geographical data...")
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    # Extract region information
    def extract_region(geography):
        if pd.isna(geography):
            return "Unknown"
        
        geo_str = str(geography)
        
        for dao_cn, dao_en in DAO_NAME_MAP.items():
            if dao_cn in geo_str:
                return dao_en
        return "Other"
    
    df['region'] = df['Geography'].apply(extract_region)
    
    # Extract poet name and poem count
    def extract_poet_info(text):
        if pd.isna(text):
            return "Unknown", 0
        text_str = str(text)
        
        # Extract name
        if ':' in text_str:
            name = text_str.split(':')[0].strip()
            if '.' in name:
                name = name.split('.', 1)[1].strip()
        else:
            name = text_str
        
        # Extract poem count
        import re
        count_match = re.search(r'(\d+)\s*首', text_str)
        count = int(count_match.group(1)) if count_match else 0
        
        return name, count
    
    df[['poet_name', 'poem_count']] = df['詩人'].apply(lambda x: pd.Series(extract_poet_info(x)))
    
    # Extract gender
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

def fetch_historical_map():
    """
    Fetch Tang Dynasty historical map from Academia Sinica or alternative sources
    """
    print("Attempting to fetch Tang Dynasty historical map...")
    
    # Try multiple approaches
    approaches = [
        {
            'name': 'Academia Sinica WMTS (REST)',
            'url': 'https://gis.sinica.edu.tw/ccts/wmts/GoogleMapsCompatible/ad0741/4/12/6.png',
            'method': 'single'
        },
        {
            'name': 'OpenStreetMap as fallback',
            'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            'method': 'tiles'
        }
    ]
    
    # Try Academia Sinica first
    print("\n  Trying Academia Sinica WMTS service...")
    base_url = "https://gis.sinica.edu.tw/ccts/wmts/GoogleMapsCompatible/ad0741"
    
    # Try to fetch multiple tiles at zoom level 4 (covers China region)
    zoom = 4
    tiles_to_fetch = [
        (12, 6), (13, 6), (12, 7), (13, 7),  # Central China tiles
        (11, 6), (11, 7), (14, 6), (14, 7),  # Surrounding tiles
    ]
    
    tile_size = 256
    tiles_fetched = []
    
    for x, y in tiles_to_fetch:
        url = f"{base_url}/{zoom}/{x}/{y}.png"
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                # Try to open as image
                try:
                    img = Image.open(BytesIO(response.content))
                    # Check if it's a valid image (not an error page)
                    if img.size[0] > 100 and img.size[1] > 100:
                        tiles_fetched.append((x, y, img))
                        print(f"    ✓ Fetched tile ({x}, {y}) - size: {img.size}")
                    else:
                        print(f"    ✗ Invalid tile ({x}, {y}): too small {img.size}")
                except Exception as img_error:
                    print(f"    ✗ Not an image ({x}, {y}): {img_error}")
            else:
                print(f"    ✗ Failed tile ({x}, {y}): status {response.status_code}")
        except Exception as e:
            print(f"    ✗ Error fetching tile ({x}, {y}): {e}")
    
    if tiles_fetched:
        print(f"\n  ✅ Successfully fetched {len(tiles_fetched)} tiles")
        
        # Calculate canvas size
        min_x = min(t[0] for t in tiles_fetched)
        max_x = max(t[0] for t in tiles_fetched)
        min_y = min(t[1] for t in tiles_fetched)
        max_y = max(t[1] for t in tiles_fetched)
        
        canvas_width = (max_x - min_x + 1) * tile_size
        canvas_height = (max_y - min_y + 1) * tile_size
        
        # Create canvas and paste tiles
        canvas = Image.new('RGB', (canvas_width, canvas_height), (240, 235, 220))
        
        for x, y, img in tiles_fetched:
            paste_x = (x - min_x) * tile_size
            paste_y = (y - min_y) * tile_size
            canvas.paste(img, (paste_x, paste_y))
        
        print(f"  ✅ Stitched map size: {canvas.size}")
        return canvas, zoom, (min_x, min_y, max_x, max_y)
    
    print("\n  ⚠️  Could not fetch historical map, using simple background")
    return None, None, None

def tile_to_lonlat(x, y, zoom):
    """Convert tile coordinates to longitude/latitude"""
    from math import pi, atan, sinh
    n = 2.0 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = atan(sinh(pi * (1 - 2 * y / n)))
    lat = lat_rad * 180.0 / pi
    return lon, lat

def create_beautiful_map_with_basemap(df, base_map=None, zoom=None, tile_bounds=None):
    """Create beautiful map visualization with historical basemap"""
    print("\nCreating map visualization...")
    
    # Calculate statistics by region
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
    
    # Set up fonts
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Create figure
    fig, ax = plt.subplots(figsize=(22, 18), dpi=150)
    
    # Set map bounds
    min_lon, max_lon = 70, 135
    min_lat, max_lat = 15, 55
    
    if base_map and zoom and tile_bounds:
        # Calculate geographical bounds for the tiles
        min_x, min_y, max_x, max_y = tile_bounds
        lon_min, lat_max = tile_to_lonlat(min_x, min_y, zoom)
        lon_max, lat_min = tile_to_lonlat(max_x + 1, max_y + 1, zoom)
        
        print(f"  Base map bounds: lon({lon_min:.2f}, {lon_max:.2f}), lat({lat_min:.2f}, {lat_max:.2f})")
        
        # Display base map
        ax.imshow(base_map, extent=[lon_min, lon_max, lat_min, lat_max],
                 aspect='auto', zorder=0, alpha=0.7)
        
        # Adjust view to include both map and all points
        min_lon = min(min_lon, lon_min)
        max_lon = max(max_lon, lon_max)
        min_lat = min(min_lat, lat_min)
        max_lat = max(max_lat, lat_max)
    else:
        # Simple background without historical map
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        ax.imshow(gradient, extent=[min_lon, max_lon, min_lat, max_lat],
                 aspect='auto', cmap='terrain', alpha=0.3, zorder=0)
        
        # Draw China border
        border_x = [p[0] for p in CHINA_BORDER_POINTS]
        border_y = [p[1] for p in CHINA_BORDER_POINTS]
        ax.plot(border_x, border_y, 'k-', linewidth=2.5, alpha=0.6, zorder=1)
        ax.fill(border_x, border_y, color='wheat', alpha=0.2, zorder=1)
    
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    
    # Draw grid
    for lon in range(75, 135, 10):
        ax.axvline(lon, color='gray', linestyle=':', linewidth=0.5, alpha=0.3, zorder=2)
    for lat in range(20, 55, 10):
        ax.axhline(lat, color='gray', linestyle=':', linewidth=0.5, alpha=0.3, zorder=2)
    
    # Plot markers for each region
    max_poets = region_stats['poet_count'].max()
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(region_stats)))
    
    for idx, row in region_stats.iterrows():
        region = row['region']
        if region not in TANG_DAO_COORDINATES:
            continue
        
        lon, lat = TANG_DAO_COORDINATES[region]
        
        # Bubble size proportional to number of poets
        size = 300 + (row['poet_count'] / max_poets) * 2500
        radius = size / 5000
        
        # Draw main bubble
        circle = Circle((lon, lat), radius, 
                       color=colors[idx], alpha=0.7, 
                       edgecolor='darkred', linewidth=3, zorder=5)
        ax.add_patch(circle)
        
        # Draw gender ratio rings
        if row['male_count'] > 0 or row['female_count'] > 0:
            male_ratio = row['male_count'] / row['poet_count'] if row['poet_count'] > 0 else 0
            if male_ratio > 0:
                male_circle = Circle((lon, lat), radius * 1.15, 
                                   fill=False, edgecolor='blue', 
                                   linewidth=male_ratio * 5, alpha=0.7, zorder=6)
                ax.add_patch(male_circle)
            
            female_ratio = row['female_count'] / row['poet_count'] if row['poet_count'] > 0 else 0
            if female_ratio > 0:
                female_circle = Circle((lon, lat), radius * 1.28, 
                                      fill=False, edgecolor='hotpink', 
                                      linewidth=female_ratio * 10, alpha=0.8, zorder=7)
                ax.add_patch(female_circle)
        
        # Add text labels
        label = f"{region}\n{row['poet_count']} poets\n{row['total_poems']} poems"
        
        bbox_props = dict(boxstyle='round,pad=0.7', 
                         facecolor='white', 
                         edgecolor=colors[idx], 
                         linewidth=2.5,
                         alpha=0.95)
        
        ax.text(lon, lat, label, fontsize=11, ha='center', va='center',
               bbox=bbox_props, fontweight='bold', zorder=8)
    
    # Set title
    title_text = 'Geographical Distribution of Tang Poetry Poets\nBy Tang Dynasty Ten Circuits (Dao)'
    ax.set_title(title_text, fontsize=28, fontweight='bold', pad=25)
    
    # Axis labels
    ax.set_xlabel('Longitude (°E)', fontsize=18, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=18, fontweight='bold')
    
    # Legend
    total_poets = region_stats['poet_count'].sum()
    total_poems = region_stats['total_poems'].sum()
    total_male = region_stats['male_count'].sum()
    total_female = region_stats['female_count'].sum()
    
    legend_elements = [
        mpatches.Patch(facecolor='red', edgecolor='darkred', alpha=0.7, 
                      label='Bubble size = Number of poets'),
        mpatches.Patch(facecolor='blue', alpha=0.7, 
                      label='Blue ring = Male poet ratio'),
        mpatches.Patch(facecolor='hotpink', alpha=0.8, 
                      label='Pink ring = Female poet ratio'),
    ]
    
    legend1 = ax.legend(handles=legend_elements, loc='upper left', 
                       fontsize=13, framealpha=0.95, edgecolor='black', fancybox=True)
    ax.add_artist(legend1)
    
    # Statistics box
    stats_text = (f'Total Statistics\n'
                 f'{"─" * 22}\n'
                 f'Total Poets: {total_poets}\n'
                 f'  Male: {total_male}\n'
                 f'  Female: {total_female}\n'
                 f'Total Poems: {total_poems:,}\n'
                 f'{"─" * 22}\n'
                 f'Avg per Poet: {total_poems/total_poets:.1f}')
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
           fontsize=14, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', 
                    edgecolor='orange', linewidth=2.5, alpha=0.95),
           fontweight='bold', family='monospace')
    
    # Top 5 ranking
    top5 = region_stats.nlargest(5, 'poet_count')
    ranking_text = 'Top 5 Regions by Poets\n' + '─' * 24 + '\n'
    for i, row in enumerate(top5.itertuples(), 1):
        ranking_text += f'{i}. {row.region}: {row.poet_count}\n'
    
    ax.text(0.02, 0.98, ranking_text, transform=ax.transAxes,
           fontsize=13, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.9', facecolor='lightblue', 
                    edgecolor='navy', linewidth=2.5, alpha=0.95),
           fontweight='bold')
    
    # Background
    ax.set_facecolor('#f5f5f0')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    return fig

def main():
    """Main function"""
    print("=" * 80)
    print("Tang Poetry Poet Geographical Distribution Map (English Version)")
    print("=" * 80)
    
    # 1. Load poet data
    df = load_poet_geo_data()
    print(f"\n✅ Loaded {len(df)} poets")
    
    # 2. Fetch historical map
    base_map, zoom, tile_bounds = fetch_historical_map()
    
    # 3. Create visualization
    fig = create_beautiful_map_with_basemap(df, base_map, zoom, tile_bounds)
    
    # 4. Save outputs
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_distribution_english.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Map saved to: {output_file}")
    
    output_file_hd = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_distribution_english_HD.png'
    fig.savefig(output_file_hd, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"✅ HD version saved to: {output_file_hd}")
    
    plt.close()
    
    print("\n" + "=" * 80)
    print("Visualization complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()

