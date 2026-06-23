#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
唐诗诗人地理分布地图可视化 V2
使用 Basemap 或简单的地理投影创建美观的可视化
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch
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

# 中国边界大致轮廓（简化版）
CHINA_BORDER_POINTS = [
    # 东北部
    (135, 48), (130, 53), (125, 53), (120, 53), (115, 53),
    # 华北
    (115, 50), (112, 47), (110, 45), (108, 43), (106, 42),
    # 西北
    (105, 42), (100, 42), (95, 42), (90, 42), (85, 40),
    (80, 37), (75, 35),
    # 西南
    (75, 32), (78, 30), (85, 28), (90, 28), (95, 27),
    (98, 25), (100, 22), (102, 21),
    # 南部
    (105, 20), (108, 20), (110, 21), (112, 21), (115, 22),
    (118, 23), (120, 24), (122, 25),
    # 东部
    (123, 27), (122, 30), (122, 33), (121, 36), (122, 39),
    (124, 42), (127, 45), (130, 47), (135, 48)
]

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
    
    # 提取性别
    def extract_gender(text):
        if pd.isna(text):
            return "未知"
        text_str = str(text).lower()
        if 'male' in text_str and 'female' not in text_str:
            return "男"
        elif 'female' in text_str:
            return "女"
        return "未知"
    
    df['gender'] = df['性別'].apply(extract_gender)
    
    return df

def create_beautiful_map(df):
    """创建美观的地图可视化"""
    print("正在创建地图可视化...")
    
    # 统计各地域诗人数量
    region_stats = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region').agg({
        'poet_name': 'count',
        'poem_count': 'sum',
        'gender': lambda x: (x == '男').sum()
    }).reset_index()
    region_stats.columns = ['region', 'poet_count', 'total_poems', 'male_count']
    region_stats['female_count'] = df[df['region'].isin(TANG_DAO_COORDINATES.keys())].groupby('region')['gender'].apply(lambda x: (x == '女').sum()).values
    
    print("\n各地域诗人统计:")
    for _, row in region_stats.iterrows():
        print(f"  {row['region']}: {row['poet_count']}位诗人 (男{row['male_count']}, 女{row['female_count']}), {row['total_poems']}首诗")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'WenQuanYi Micro Hei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(20, 16), dpi=150)
    
    # 设置地图范围
    min_lon, max_lon = 70, 135
    min_lat, max_lat = 15, 55
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    
    # 绘制背景渐变
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    ax.imshow(gradient, extent=[min_lon, max_lon, min_lat, max_lat],
             aspect='auto', cmap='terrain', alpha=0.3, zorder=0)
    
    # 绘制中国边界（简化版）
    border_x = [p[0] for p in CHINA_BORDER_POINTS]
    border_y = [p[1] for p in CHINA_BORDER_POINTS]
    ax.plot(border_x, border_y, 'k-', linewidth=2, alpha=0.5, zorder=1)
    ax.fill(border_x, border_y, color='wheat', alpha=0.2, zorder=1)
    
    # 绘制经纬网格
    for lon in range(75, 135, 10):
        ax.axvline(lon, color='gray', linestyle=':', linewidth=0.5, alpha=0.3)
    for lat in range(20, 55, 10):
        ax.axhline(lat, color='gray', linestyle=':', linewidth=0.5, alpha=0.3)
    
    # 为每个地域绘制标记
    max_poets = region_stats['poet_count'].max()
    max_poems = region_stats['total_poems'].max()
    
    # 颜色映射
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(region_stats)))
    
    for idx, row in region_stats.iterrows():
        region = row['region']
        if region not in TANG_DAO_COORDINATES:
            continue
        
        lon, lat = TANG_DAO_COORDINATES[region]
        
        # 气泡大小与诗人数量成正比
        size = 300 + (row['poet_count'] / max_poets) * 2500
        
        # 绘制主气泡（诗人总数）
        circle = Circle((lon, lat), size/5000, 
                       color=colors[idx], alpha=0.6, 
                       edgecolor='darkred', linewidth=2.5, zorder=5)
        ax.add_patch(circle)
        
        # 绘制性别比例环（如果有数据）
        if row['male_count'] > 0 or row['female_count'] > 0:
            # 男性（蓝色环）
            male_ratio = row['male_count'] / row['poet_count'] if row['poet_count'] > 0 else 0
            if male_ratio > 0:
                male_circle = Circle((lon, lat), size/5000 * 1.15, 
                                   fill=False, edgecolor='blue', 
                                   linewidth=male_ratio * 4, alpha=0.6, zorder=6)
                ax.add_patch(male_circle)
            
            # 女性（粉色环）
            female_ratio = row['female_count'] / row['poet_count'] if row['poet_count'] > 0 else 0
            if female_ratio > 0:
                female_circle = Circle((lon, lat), size/5000 * 1.25, 
                                      fill=False, edgecolor='hotpink', 
                                      linewidth=female_ratio * 8, alpha=0.8, zorder=7)
                ax.add_patch(female_circle)
        
        # 添加文本标签
        label = f"{region}\n{row['poet_count']}位诗人\n{row['total_poems']}首诗"
        
        # 标签背景框
        bbox_props = dict(boxstyle='round,pad=0.6', 
                         facecolor='white', 
                         edgecolor=colors[idx], 
                         linewidth=2,
                         alpha=0.9)
        
        ax.text(lon, lat, label, fontsize=10, ha='center', va='center',
               bbox=bbox_props, fontweight='bold', zorder=8)
    
    # 设置标题
    ax.set_title('全唐诗诗人地理分布图（按唐代十道）\n诗人籍贯与作品统计', 
                fontsize=26, fontweight='bold', pad=25)
    
    # 设置坐标轴标签
    ax.set_xlabel('东经（度）', fontsize=16, fontweight='bold')
    ax.set_ylabel('北纬（度）', fontsize=16, fontweight='bold')
    
    # 添加图例
    total_poets = region_stats['poet_count'].sum()
    total_poems = region_stats['total_poems'].sum()
    total_male = region_stats['male_count'].sum()
    total_female = region_stats['female_count'].sum()
    
    legend_elements = [
        mpatches.Patch(facecolor='red', edgecolor='darkred', alpha=0.6, 
                      label=f'气泡大小 = 诗人数量'),
        mpatches.Patch(facecolor='blue', alpha=0.6, 
                      label=f'蓝色环 = 男性诗人比例'),
        mpatches.Patch(facecolor='hotpink', alpha=0.8, 
                      label=f'粉色环 = 女性诗人比例'),
    ]
    
    legend1 = ax.legend(handles=legend_elements, loc='upper left', 
                       fontsize=12, framealpha=0.9)
    ax.add_artist(legend1)
    
    # 添加统计信息文本框
    stats_text = (f'总计统计\n'
                 f'━━━━━━━━━━━━━━\n'
                 f'诗人总数: {total_poets}位\n'
                 f'  男性: {total_male}位\n'
                 f'  女性: {total_female}位\n'
                 f'诗歌总数: {total_poems}首\n'
                 f'━━━━━━━━━━━━━━\n'
                 f'平均每人: {total_poems/total_poets:.1f}首')
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
           fontsize=13, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', 
                    edgecolor='orange', linewidth=2, alpha=0.95),
           fontweight='bold', family='monospace')
    
    # 添加排名（前5名）
    top5 = region_stats.nlargest(5, 'poet_count')
    ranking_text = '诗人数量排名 Top 5\n' + '━' * 20 + '\n'
    for i, row in enumerate(top5.itertuples(), 1):
        ranking_text += f'{i}. {row.region}: {row.poet_count}位\n'
    
    ax.text(0.02, 0.98, ranking_text, transform=ax.transAxes,
           fontsize=12, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='lightblue', 
                    edgecolor='navy', linewidth=2, alpha=0.9),
           fontweight='bold')
    
    # 设置背景色
    ax.set_facecolor('#f0f8ff')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    return fig

def main():
    """主函数"""
    print("=" * 70)
    print("全唐诗诗人地理分布地图可视化 V2")
    print("=" * 70)
    
    # 1. 加载诗人数据
    df = load_poet_geo_data()
    print(f"\n✅ 共载入 {len(df)} 位诗人数据")
    
    # 2. 创建可视化
    fig = create_beautiful_map(df)
    
    # 3. 保存图片
    output_file = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_distribution_map_v2.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ 地图已保存到: {output_file}")
    
    # 4. 同时保存一个高清版本
    output_file_hd = '/media/meow/One Touch/ctext.org_-crawler/quantangshi_crawler/tang_poet_distribution_map_v2_HD.png'
    fig.savefig(output_file_hd, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"✅ 高清版已保存到: {output_file_hd}")
    
    plt.close()
    
    print("\n" + "=" * 70)
    print("可视化完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()

