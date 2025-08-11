#!/usr/bin/env python3
"""
提取全唐詩所有作者腳本 - 清理版
從 quantangshi_volumes 文件夾中的所有文件中提取作者信息
去掉作者名稱末尾的"著"字，重新計算去重後的作者數
"""

import os
import re
from collections import Counter

def clean_author_name(author_name):
    """清理作者名稱，去掉末尾的"著"字"""
    if author_name.endswith('著'):
        return author_name[:-1]  # 去掉最後一個字符"著"
    return author_name

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
                # 清理作者名稱
                clean_author = clean_author_name(author)
                authors.append(clean_author)
                
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
    
    print(f"\n📊 作者統計 (清理後):")
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

def save_authors_list(authors_list, output_file="authors_list_clean.txt"):
    """保存作者列表到文件"""
    unique_authors = sorted(list(set(authors_list)))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("全唐詩作者列表 (清理版)\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"總計: {len(unique_authors)} 位作者\n")
        f.write("注意: 已去掉作者名稱末尾的'著'字\n\n")
        
        for i, author in enumerate(unique_authors, 1):
            f.write(f"{i:4d}. {author}\n")
    
    print(f"\n💾 作者列表已保存到: {output_file}")
    return unique_authors

def compare_with_original():
    """比較清理前後的差異"""
    print("\n🔍 比較清理前後的差異:")
    
    # 讀取原始作者列表
    original_authors = []
    if os.path.exists("authors_python_list.py"):
        try:
            with open("authors_python_list.py", 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取作者列表
                import re
                pattern = r"'([^']+)'"
                original_authors = re.findall(pattern, content)
        except:
            print("無法讀取原始作者列表")
    
    if original_authors:
        original_unique = set(original_authors)
        print(f"   原始作者數: {len(original_unique)}")
        
        # 清理原始作者名稱
        cleaned_original = [clean_author_name(author) for author in original_authors]
        cleaned_unique = set(cleaned_original)
        print(f"   清理後作者數: {len(cleaned_unique)}")
        print(f"   減少了: {len(original_unique) - len(cleaned_unique)} 位重複作者")

def main():
    """主函數"""
    volumes_dir = "quantangshi_volumes"
    
    print("🔍 開始提取全唐詩作者 (清理版)...")
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
    print("authors_list_clean = [")
    for i, author in enumerate(unique_authors[:10]):
        print(f"    '{author}',")
    if len(unique_authors) > 10:
        print(f"    # ... 還有 {len(unique_authors) - 10} 位作者")
    print("]")
    
    # 保存完整的Python列表
    with open("authors_python_list_clean.py", 'w', encoding='utf-8') as f:
        f.write("# 全唐詩作者列表 - 清理版 (Python格式)\n")
        f.write("# 注意: 已去掉作者名稱末尾的'著'字\n")
        f.write("authors_list_clean = [\n")
        for author in unique_authors:
            f.write(f"    '{author}',\n")
        f.write("]\n\n")
        f.write(f"# 總計: {len(unique_authors)} 位作者\n")
        f.write("# 清理前可能有重複，如'厲玄'和'厲玄著'現在統一為'厲玄'\n")
    
    print(f"\n💾 Python列表已保存到: authors_python_list_clean.py")
    
    # 顯示一些有趣的統計
    print(f"\n🎯 有趣統計:")
    print(f"   最常見的作者: {author_counts.most_common(1)[0][0]} ({author_counts.most_common(1)[0][1]} 首)")
    print(f"   平均每位作者詩歌數: {len(all_authors) / len(author_counts):.1f} 首")
    
    # 比較清理前後的差異
    compare_with_original()
    
    # 顯示一些重複的例子
    print(f"\n📝 重複清理示例:")
    examples = [
        ("白居易著", "白居易"),
        ("杜甫著", "杜甫"),
        ("李白著", "李白"),
        ("厲玄著", "厲玄"),
        ("佚名", "佚名")
    ]
    for original, cleaned in examples:
        print(f"   '{original}' → '{cleaned}'")

if __name__ == "__main__":
    main() 