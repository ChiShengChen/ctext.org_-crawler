#!/usr/bin/env python3
"""
提取全唐詩所有作者腳本
從 quantangshi_volumes 文件夾中的所有文件中提取作者信息
"""

import os
import re
from collections import Counter

def extract_authors_from_file(file_path):
    """從單個文件中提取作者"""
    authors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 使用正則表達式匹配 "作者: " 後面的內容
        author_pattern = r'作者:\s*(.+?)(?:\n|$)'
        matches = re.findall(author_pattern, content)
        
        for match in matches:
            author = match.strip()
            if author and author != "未知作者":
                authors.append(author)
                
    except Exception as e:
        print(f"讀取文件 {file_path} 時出錯: {e}")
    
    return authors

def extract_all_authors(volumes_dir):
    """從所有文件中提取作者"""
    all_authors = []
    file_count = 0
    
    if not os.path.exists(volumes_dir):
        print(f"目錄不存在: {volumes_dir}")
        return []
    
    # 遍歷目錄中的所有文件
    for filename in os.listdir(volumes_dir):
        if filename.endswith('.txt') and filename.startswith('全唐詩_第'):
            file_path = os.path.join(volumes_dir, filename)
            file_count += 1
            
            print(f"正在處理: {filename}")
            authors = extract_authors_from_file(file_path)
            all_authors.extend(authors)
    
    print(f"\n總共處理了 {file_count} 個文件")
    return all_authors

def analyze_authors(authors_list):
    """分析作者統計信息"""
    if not authors_list:
        print("沒有找到任何作者")
        return
    
    # 統計每個作者出現的次數
    author_counts = Counter(authors_list)
    
    print(f"\n📊 作者統計:")
    print(f"   總作者數: {len(author_counts)}")
    print(f"   總詩歌數: {len(authors_list)}")
    
    # 顯示出現次數最多的作者
    print(f"\n🏆 出現次數最多的作者 (前20名):")
    for author, count in author_counts.most_common(20):
        print(f"   {author}: {count} 首")
    
    # 顯示只出現一次的作者數量
    single_occurrence = sum(1 for count in author_counts.values() if count == 1)
    print(f"\n📝 只出現一次的作者: {single_occurrence} 人")
    
    return author_counts

def save_authors_list(authors_list, output_file="authors_list.txt"):
    """保存作者列表到文件"""
    unique_authors = sorted(list(set(authors_list)))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("全唐詩作者列表\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"總計: {len(unique_authors)} 位作者\n\n")
        
        for i, author in enumerate(unique_authors, 1):
            f.write(f"{i:4d}. {author}\n")
    
    print(f"\n💾 作者列表已保存到: {output_file}")
    return unique_authors

def main():
    """主函數"""
    volumes_dir = "quantangshi_volumes"
    
    print("🔍 開始提取全唐詩作者...")
    print("=" * 50)
    
    # 提取所有作者
    all_authors = extract_all_authors(volumes_dir)
    
    if not all_authors:
        print("❌ 沒有找到任何作者信息")
        return
    
    # 分析作者統計
    author_counts = analyze_authors(all_authors)
    
    # 保存作者列表
    unique_authors = save_authors_list(all_authors)
    
    # 輸出Python列表格式
    print(f"\n📋 Python列表格式 (前10位作者):")
    print("authors_list = [")
    for i, author in enumerate(unique_authors[:10]):
        print(f"    '{author}',")
    if len(unique_authors) > 10:
        print(f"    # ... 還有 {len(unique_authors) - 10} 位作者")
    print("]")
    
    # 保存完整的Python列表
    with open("authors_python_list.py", 'w', encoding='utf-8') as f:
        f.write("# 全唐詩作者列表 - Python格式\n")
        f.write("authors_list = [\n")
        for author in unique_authors:
            f.write(f"    '{author}',\n")
        f.write("]\n\n")
        f.write(f"# 總計: {len(unique_authors)} 位作者\n")
    
    print(f"\n💾 Python列表已保存到: authors_python_list.py")
    
    # 顯示一些有趣的統計
    print(f"\n🎯 有趣統計:")
    print(f"   最常見的作者: {author_counts.most_common(1)[0][0]} ({author_counts.most_common(1)[0][1]} 首)")
    print(f"   平均每位作者詩歌數: {len(all_authors) / len(author_counts):.1f} 首")

if __name__ == "__main__":
    main() 