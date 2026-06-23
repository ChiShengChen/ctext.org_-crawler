#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
唐诗诗人地理分布地图可视化
将诗人分布标注在唐代历史地图上
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
import requests
from io import BytesIO
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 唐代十道的大致中心坐标（经纬度）
TANG_DAO_COORDINATES = {
    '關內道': (108.95, 34.27),  # 长安附近
    '河南道': (113.65, 34.76),  # 洛阳附近
    '河北道': (114.48, 38.03),  # 邯郸、定州附近
    '江南道': (120.15, 30.28),  # 杭州、苏州附近
    '河東道': (112.55, 37.87),  # 太原附近
    '淮南道': (119.42, 32.39),  # 扬州附近
    '山南道': (106.71, 33.04),  # 汉中附近
    '隴右道': (103.85, 36.06),  # 兰州附近
    '劍南道': (104.07, 30.65),  # 成都附近
    '嶺南道': (113.25, 23.13),  # 广州附近
}

# 地图边界（Web Mercator投影，EPSG:3857）
MAP_BOUNDS = {
    'xmin': 7373000,   # 约 66.3°E
    'ymin': 1914000,   # 约 17°N
    'xmax': 16367000,  # 约 147°E
    'ymax': 8456000    # 约 60.6°N
}

def load_poet_geo_data():
    """载入诗人地理数据"""
    print("正在读取诗人地理数据...")
    df = pd.read_csv('/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/poet_geo_label.csv')
    
    # 提取地域信息
    def extract_region(geography):
        if pd.isna(geography):
            return "未知"
        
        geo_str = str(geography)
        
        for dao in TANG_DAO_COORDINATES.keys():
            if dao in geo_str:
                return dao
        return "其他"
    
    df['region'] = df['Geography'].apply(extract_region)
    
    # 提取诗人名字和诗歌数量
    def extract_poet_info(text):
        if pd.isna(text):
            return "未知", 0
        text_str = str(text)
        
        # 提取名字
        if ':' in text_str:
            name = text_str.split(':')[0].strip()
            # 移除编号
            if '.' in name:
                name = name.split('.', 1)[1].strip()
        else:
            name = text_str
        
        # 提取诗歌数量
        import re
        count_match = re.search(r'(\d+)\s*首', text_str)
        count = int(count_match.group(1)) if count_match else 0
        
        return name, count
    
    df[['poet_name', 'poem_count']] = df['詩人'].apply(lambda x: pd.Series(extract_poet_info(x)))
    
    return df

def lonlat_to_web_mercator(lon, lat):
    """将经纬度转换为 Web Mercator 坐标"""
    from math import pi, log, tan
    x = lon * 20037508.34 / 180
    y = log(tan((90 + lat) * pi / 360)) / (pi / 180)
    y = y * 20037508.34 / 180
    return x, y

def web_mercator_to_pixel(x, y, img_width, img_height):
    """将 Web Mercator 坐标转换为图像像素坐标"""
    px = (x - MAP_BOUNDS['xmin']) / (MAP_BOUNDS['xmax'] - MAP_BOUNDS['xmin']) * img_width
    py = (MAP_BOUNDS['ymax'] - y) / (MAP_BOUNDS['ymax'] - MAP_BOUNDS['ymin']) * img_height
    return px, py

def deg_to_tile(lon, lat, zoom):
    """将经纬度转换为瓦片坐标"""
    from math import radians, tan, log, cos, pi
    lat_rad = radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - log(tan(lat_rad) + (1 / cos(lat_rad))) / pi) / 2.0 * n)
    return xtile, ytile

def fetch_wmts_tiles(zoom=4):
    """
    从中研院 WMTS 服务获取唐代地图瓦片并拼接
    """
    print(f"正在从中研院服务器获取唐代地图 (zoom={zoom})...")
    
    # WMTS 瓦片 URL 模板
    # 基于 .qlr 文件中的 URL: https://gis.sinica.edu.tw/ccts/wmts
    wmts_base = "https://gis.sinica.edu.tw/ccts/wmts"
    
    # 计算需要的瓦片范围（覆盖中国大陆区域）
    # 大致范围：东经 70-140度，北纬 15-55度
    min_lon, max_lon = 70, 140
    min_lat, max_lat = 15, 55
    
    min_x, max_y = deg_to_tile(min_lon, min_lat, zoom)
    max_x, min_y = deg_to_tile(max_lon, max_lat, zoom)
    
    print(f"  瓦片范围: X={min_x}-{max_x}, Y={min_y}-{max_y}")
    print(f"  总计: {(max_x-min_x+1)*(max_y-min_y+1)} 个瓦片")
    
    tile_size = 256
    tiles = []
    
    # 尝试不同的 WMTS URL 格式
    url_patterns = [
        f"{wmts_base}/GoogleMapsCompatible/ad0741/{{z}}/{{x}}/{{y}}.png",
        f"{wmts_base}?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ad0741&STYLE=default&TILEMATRIXSET=GoogleMapsCompatible&TILEMATRIX={{z}}&TILEROW={{y}}&TILECOL={{x}}&FORMAT=image/png",
    ]
    
    success = False
    
    for pattern_idx, url_pattern in enumerate(url_patterns):
        if success:
            break
            
        print(f"\n  尝试 URL 格式 {pattern_idx + 1}...")
        tiles = []
        
        # 只测试一个瓦片
        test_x, test_y = (min_x + max_x) // 2, (min_y + max_y) // 2
        test_url = url_pattern.replace('{z}', str(zoom)).replace('{x}', str(test_x)).replace('{y}', str(test_y))
        
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                print(f"  ✅ URL 格式有效！")
                success = True
                
                # 获取所有瓦片（限制数量以避免过多请求）
                max_tiles = 50
                tile_count = 0
                
                for x in range(min_x, max_x + 1):
                    row_tiles = []
                    for y in range(min_y, max_y + 1):
                        if tile_count >= max_tiles:
                            break
                        
                        url = url_pattern.replace('{z}', str(zoom)).replace('{x}', str(x)).replace('{y}', str(y))
                        try:
                            resp = requests.get(url, timeout=5)
                            if resp.status_code == 200:
                                tile_img = Image.open(BytesIO(resp.content))
                                row_tiles.append(tile_img)
                                tile_count += 1
                            else:
                                row_tiles.append(Image.new('RGB', (tile_size, tile_size), (240, 240, 230)))
                        except:
                            row_tiles.append(Image.new('RGB', (tile_size, tile_size), (240, 240, 230)))
                    
                    if row_tiles:
                        tiles.append(row_tiles)
                    if tile_count >= max_tiles:
                        break
                
                break
            else:
                print(f"  ❌ 无效响应 (状态码: {response.status_code})")
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
    
    if not success or not tiles:
        print("\n❌ 所有 URL 格式均失败")
        return None
    
    # 拼接瓦片
    print(f"\n  正在拼接 {len(tiles)} x {len(tiles[0]) if tiles else 0} 个瓦片...")
    
    rows = len(tiles)
    cols = len(tiles[0]) if tiles else 0
    
    result = Image.new('RGB', (cols * tile_size, rows * tile_size), (240, 240, 230))
    
    for i, row in enumerate(tiles):
        for j, tile in enumerate(row):
            result.paste(tile, (j * tile_size, i * tile_size))
    
    print(f"✅ 成功拼接地图，尺寸: {result.size}")
    return result

def create_map_visualization(df, base_map=None):
    """创建地图可视化"""
    print("正在创建地图可视化...")
    
    # 统计各地域诗人数量
    region_stats = df[df['region'] != '未知'].groupby('region').agg({
        'poet_name': 'count',
        'poem_count': 'sum'
    }).reset_index()
    region_stats.columns = ['region', 'poet_count', 'total_poems']
    
    print("\n各地域诗人统计:")
    for _, row in region_stats.iterrows():
        print(f"  {row['region']}: {row['poet_count']}位诗人, {row['total_poems']}首诗")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'WenQuanYi Micro Hei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(20, 16), dpi=150)
    
    # 如果有底图，显示底图
    if base_map:
        ax.imshow(base_map, extent=[
            MAP_BOUNDS['xmin'], MAP_BOUNDS['xmax'],
            MAP_BOUNDS['ymin'], MAP_BOUNDS['ymax']
        ], aspect='auto', zorder=0)
    else:
        # 没有底图时使用简单背景
        ax.set_facecolor('#f5f5dc')  # 米色背景
        ax.set_xlim(MAP_BOUNDS['xmin'], MAP_BOUNDS['xmax'])
        ax.set_ylim(MAP_BOUNDS['ymin'], MAP_BOUNDS['ymax'])
    
    # 为每个地域绘制标记
    max_poets = region_stats['poet_count'].max()
    
    for _, row in region_stats.iterrows():
        region = row['region']
        if region not in TANG_DAO_COORDINATES:
            continue
        
        lon, lat = TANG_DAO_COORDINATES[region]
        x, y = lonlat_to_web_mercator(lon, lat)
        
        # 气泡大小与诗人数量成正比
        size = 500 + (row['poet_count'] / max_poets) * 3000
        
        # 绘制气泡
        ax.scatter(x, y, s=size, alpha=0.6, c='red', edgecolors='darkred', 
                  linewidth=2, zorder=5)
        
        # 添加文本标签
        label = f"{region}\n{row['poet_count']}位诗人\n{row['total_poems']}首诗"
        ax.text(x, y, label, fontsize=11, ha='center', va='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor='darkred', alpha=0.8),
               fontweight='bold', zorder=6)
    
    # 设置标题和标签
    ax.set_title('全唐诗诗人地理分布图（按唐代十道）', fontsize=24, fontweight='bold', pad=20)
    ax.set_xlabel('经度（Web Mercator投影）', fontsize=14)
    ax.set_ylabel('纬度（Web Mercator投影）', fontsize=14)
    
    # 添加图例
    total_poets = region_stats['poet_count'].sum()
    total_poems = region_stats['total_poems'].sum()
    legend_text = f'总计: {total_poets}位诗人, {total_poems}首诗\n气泡大小表示诗人数量'
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
           fontsize=12, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 移除坐标轴刻度（更清晰）
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    
    return fig

def main():
    """主函数"""
    print("=" * 60)
    print("全唐诗诗人地理分布地图可视化")
    print("=" * 60)
    
    # 1. 加载诗人数据
    df = load_poet_geo_data()
    print(f"\n✅ 共载入 {len(df)} 位诗人数据")
    
    # 2. 获取唐代地图底图
    base_map = fetch_wmts_tiles()
    
    if base_map is None:
        print("\n⚠️  无法获取底图，将使用简化地图")
        print("可能原因：网络连接问题或服务器限制")
        print("继续使用简化版本...\n")
    
    # 3. 创建可视化
    fig = create_map_visualization(df, base_map)
    
    # 4. 保存图片
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_distribution_map.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ 地图已保存到: {output_file}")
    
    plt.close()
    
    print("\n" + "=" * 60)
    print("可视化完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

