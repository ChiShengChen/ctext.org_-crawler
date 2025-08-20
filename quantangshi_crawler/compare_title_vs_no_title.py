#!/usr/bin/env python3
"""
全唐詩標題對比分析工具
比較包含標題和不包含標題的詞頻統計結果
"""

import os
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from datetime import datetime

class TitleComparisonAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_stats_with_title = defaultdict(lambda: {'chars': 0, 'poems': 0})
        self.author_stats_no_title = defaultdict(lambda: {'chars': 0, 'poems': 0})
        
    def load_data(self):
        """載入所有詩歌數據"""
        print("📚 正在載入詩歌數據...")
        
        for filename in os.listdir(self.volumes_dir):
            if filename.endswith('.txt') and filename.startswith('全唐詩_第'):
                file_path = os.path.join(self.volumes_dir, filename)
                volume_data = self.parse_volume_file(file_path)
                self.poems_data.extend(volume_data)
        
        print(f"✅ 載入完成！總共 {len(self.poems_data)} 首詩歌")
        
    def parse_volume_file(self, file_path: str) -> List[Dict]:
        """解析單個卷文件"""
        poems = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取卷號
            volume_match = re.search(r'全唐詩_第(\d+)卷', os.path.basename(file_path))
            volume_num = int(volume_match.group(1)) if volume_match else 0
            
            # 分割詩歌
            poem_sections = content.split('------------------------------')
            
            for section in poem_sections:
                if not section.strip():
                    continue
                    
                lines = section.strip().split('\n')
                if len(lines) < 3:
                    continue
                
                # 提取標題
                title_line = lines[0].strip()
                if title_line and not title_line.startswith('全唐詩'):
                    current_poem = {
                        'title': title_line,
                        'volume': volume_num,
                        'content': ''
                    }
                    
                    # 提取作者
                    for line in lines[1:]:
                        if '作者:' in line:
                            author = line.split('作者:')[1].strip()
                            current_poem['author'] = author
                            break
                    
                    # 提取內容
                    content_started = False
                    for line in lines[1:]:
                        if '內容:' in line:
                            content_started = True
                            continue
                        if content_started:
                            current_poem['content'] += line + '\n'
                    
                    if current_poem.get('title') and current_poem.get('author'):
                        poems.append(current_poem)
                        
        except Exception as e:
            print(f"⚠️  解析文件 {file_path} 時出錯: {e}")
            
        return poems
    
    def clean_author_name(self, author: str) -> str:
        """清理作者名稱，去掉"著"字"""
        if author.endswith('著'):
            return author[:-1]
        return author
    
    def clean_text(self, text: str) -> str:
        """清理文本，只保留中文字符"""
        # 移除標點符號、數字、英文等，只保留中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return ''.join(chinese_chars)
    
    def analyze_comparison(self):
        """分析包含標題和不包含標題的對比"""
        print("🔍 正在分析標題對比統計...")
        
        for poem in self.poems_data:
            author = poem.get('author', '佚名')
            clean_author = self.clean_author_name(author)
            title = poem.get('title', '')
            content = poem.get('content', '')
            
            # 清理文本
            cleaned_title = self.clean_text(title)
            cleaned_content = self.clean_text(content)
            
            # 統計包含標題的字符數
            chars_with_title = len(cleaned_title) + len(cleaned_content)
            self.author_stats_with_title[clean_author]['chars'] += chars_with_title
            self.author_stats_with_title[clean_author]['poems'] += 1
            
            # 統計不包含標題的字符數
            chars_no_title = len(cleaned_content)
            self.author_stats_no_title[clean_author]['chars'] += chars_no_title
            self.author_stats_no_title[clean_author]['poems'] += 1
        
        total_with_title = sum(stats['chars'] for stats in self.author_stats_with_title.values())
        total_no_title = sum(stats['chars'] for stats in self.author_stats_no_title.values())
        total_title_chars = total_with_title - total_no_title
        
        print(f"✅ 分析完成！")
        print(f"   包含標題總字符數: {total_with_title:,}")
        print(f"   不包含標題總字符數: {total_no_title:,}")
        print(f"   標題字符數: {total_title_chars:,}")
        print(f"   標題佔比: {total_title_chars/total_with_title*100:.2f}%")
    
    def save_comparison_report(self, output_file: str = "title_comparison_report.txt"):
        """保存對比報告"""
        print("💾 正在保存對比報告...")
        
        # 獲取排名
        with_title_ranking = sorted(
            self.author_stats_with_title.items(), 
            key=lambda x: x[1]['chars'], 
            reverse=True
        )
        
        no_title_ranking = sorted(
            self.author_stats_no_title.items(), 
            key=lambda x: x[1]['chars'], 
            reverse=True
        )
        
        # 創建排名字典
        with_title_dict = {author: (i+1, stats) for i, (author, stats) in enumerate(with_title_ranking)}
        no_title_dict = {author: (i+1, stats) for i, (author, stats) in enumerate(no_title_ranking)}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩標題對比分析報告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 總體統計
            total_with_title = sum(stats['chars'] for stats in self.author_stats_with_title.values())
            total_no_title = sum(stats['chars'] for stats in self.author_stats_no_title.values())
            total_title_chars = total_with_title - total_no_title
            
            f.write("📊 總體統計\n")
            f.write("-" * 20 + "\n")
            f.write(f"包含標題總字符數: {total_with_title:,}\n")
            f.write(f"不包含標題總字符數: {total_no_title:,}\n")
            f.write(f"標題字符數: {total_title_chars:,}\n")
            f.write(f"標題佔比: {total_title_chars/total_with_title*100:.2f}%\n\n")
            
            f.write("📈 前50名作者對比 (按不包含標題排名)\n")
            f.write("-" * 50 + "\n")
            f.write("排名 | 作者 | 包含標題 | 不包含標題 | 標題字符 | 排名變化\n")
            f.write("     |      | 排名/字符 | 排名/字符  |          |\n")
            f.write("-" * 80 + "\n")
            
            for i, (author, no_title_stats) in enumerate(no_title_ranking[:50], 1):
                with_title_rank, with_title_stats = with_title_dict.get(author, (999, {'chars': 0, 'poems': 0}))
                title_chars = with_title_stats['chars'] - no_title_stats['chars']
                rank_change = with_title_rank - i
                
                rank_change_str = f"+{rank_change}" if rank_change > 0 else str(rank_change)
                
                f.write(f"{i:4d} | {author:8s} | "
                       f"{with_title_rank:3d}/{with_title_stats['chars']:6d} | "
                       f"{i:3d}/{no_title_stats['chars']:6d} | "
                       f"{title_chars:8d} | {rank_change_str:>6s}\n")
        
        print(f"✅ 對比報告已保存到: {output_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 標題對比分析摘要:")
        print("=" * 40)
        
        total_with_title = sum(stats['chars'] for stats in self.author_stats_with_title.values())
        total_no_title = sum(stats['chars'] for stats in self.author_stats_no_title.values())
        total_title_chars = total_with_title - total_no_title
        
        print(f"包含標題總字符數: {total_with_title:,}")
        print(f"不包含標題總字符數: {total_no_title:,}")
        print(f"標題字符數: {total_title_chars:,}")
        print(f"標題佔比: {total_title_chars/total_with_title*100:.2f}%")
        
        # 前10名對比
        with_title_ranking = sorted(
            self.author_stats_with_title.items(), 
            key=lambda x: x[1]['chars'], 
            reverse=True
        )[:10]
        
        no_title_ranking = sorted(
            self.author_stats_no_title.items(), 
            key=lambda x: x[1]['chars'], 
            reverse=True
        )[:10]
        
        print(f"\n🏆 包含標題前10名:")
        for i, (author, stats) in enumerate(with_title_ranking, 1):
            print(f"   {i:2d}. {author}: {stats['chars']:,} 字符")
        
        print(f"\n🏆 不包含標題前10名:")
        for i, (author, stats) in enumerate(no_title_ranking, 1):
            print(f"   {i:2d}. {author}: {stats['chars']:,} 字符")

def main():
    """主函數"""
    print("🔍 全唐詩標題對比分析工具")
    print("=" * 40)
    
    analyzer = TitleComparisonAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析對比
    analyzer.analyze_comparison()
    
    # 保存結果
    analyzer.save_comparison_report()
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n🎉 標題對比分析完成！")
    print("📁 生成的文件:")
    print("   - title_comparison_report.txt (對比報告)")

if __name__ == "__main__":
    main() 