#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全唐詩詩題 N-gram 分析工具
只統計詩歌標題的詞頻，不包含詩歌內容
"""

import os
import re
import csv
from collections import Counter, defaultdict
from typing import Dict, List
from datetime import datetime

class TitleNgramAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_poems = defaultdict(list)
        self.author_ngram_stats = defaultdict(lambda: {
            '1gram': Counter(),
            '2gram': Counter(),
            '3gram': Counter(),
            '4gram': Counter(),
            '5gram': Counter(),
            '6gram': Counter(),
            '7gram': Counter()
        })
        
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
                if len(lines) < 2:
                    continue
                
                # 提取標題（第一行，可能有編號）
                title_line = lines[0].strip()
                
                # 移除編號（如 "1. "）
                title_match = re.match(r'^\s*\d+\.\s*(.+)$', title_line)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = title_line
                
                if not title or title.startswith('全唐詩'):
                    continue
                
                current_poem = {
                    'title': title,
                    'volume': volume_num,
                    'author': None
                }
                
                # 提取作者
                for line in lines[1:]:
                    if '作者:' in line:
                        author = line.split('作者:')[1].strip()
                        current_poem['author'] = author
                        break
                
                if current_poem['title'] and current_poem['author']:
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
    
    def extract_ngrams(self, text: str, n: int) -> List[str]:
        """提取n-gram"""
        if len(text) < n:
            return []
        
        ngrams = []
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            ngrams.append(ngram)
        
        return ngrams
    
    def organize_poems_by_author(self):
        """按作者組織詩歌"""
        print("👥 正在按作者組織詩歌...")
        
        for poem in self.poems_data:
            author = poem.get('author', '佚名')
            clean_author = self.clean_author_name(author)
            self.author_poems[clean_author].append(poem)
        
        print(f"✅ 組織完成！總共 {len(self.author_poems)} 位作者")
    
    def analyze_author_title_ngrams(self):
        """分析每位作者的詩題n-gram"""
        print("🔍 正在分析作者詩題n-gram統計...")
        
        total_authors = len(self.author_poems)
        processed_authors = 0
        
        for author, poems in self.author_poems.items():
            processed_authors += 1
            if processed_authors % 100 == 0:
                print(f"   進度: {processed_authors}/{total_authors}")
            
            # 合併該作者所有詩歌的標題
            all_titles = ""
            for poem in poems:
                title = poem.get('title', '')
                cleaned_title = self.clean_text(title)
                all_titles += cleaned_title
            
            if all_titles:
                # 提取1-7 gram
                for n in [1, 2, 3, 4, 5, 6, 7]:
                    ngram_type = f'{n}gram'
                    ngrams = self.extract_ngrams(all_titles, n)
                    self.author_ngram_stats[author][ngram_type].update(ngrams)
        
        print(f"✅ 分析完成！")
    
    def save_author_title_ngram_csvs(self, output_dir: str = "analysis_result/title_analysis"):
        """保存每位作者的詩題n-gram CSV文件"""
        print("💾 正在保存作者詩題n-gram CSV文件...")
        
        # 創建輸出目錄
        csv_dir = os.path.join(output_dir, "author_title_ngram_csvs")
        os.makedirs(csv_dir, exist_ok=True)
        
        total_authors = len(self.author_ngram_stats)
        processed_authors = 0
        created_files = 0
        
        for author, ngram_data in self.author_ngram_stats.items():
            processed_authors += 1
            if processed_authors % 100 == 0:
                print(f"   進度: {processed_authors}/{total_authors}")
            
            # 為每個n-gram類型創建CSV文件
            for n in [1, 2, 3, 4, 5, 6, 7]:
                ngram_type = f'{n}gram'
                counter = ngram_data[ngram_type]
                
                if counter:
                    # 創建CSV文件名
                    filename = f"{author}_title_{n}gram_詞頻統計.csv"
                    filepath = os.path.join(csv_dir, filename)
                    
                    # 寫入CSV文件
                    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['排名', '詞彙', '出現次數'])
                        
                        # 按出現次數排序
                        sorted_items = counter.most_common()
                        for rank, (ngram, count) in enumerate(sorted_items, 1):
                            writer.writerow([rank, ngram, count])
                    
                    created_files += 1
        
        # 生成合併的CSV文件
        print("📊 正在生成合併的詩題n-gram CSV文件...")
        for n in [1, 2, 3, 4, 5, 6, 7]:
            merged_path = os.path.join(csv_dir, f"merged_title_{n}gram_詞頻統計.csv")
            rows = []
            
            for author, ngram_data in self.author_ngram_stats.items():
                counter = ngram_data[f'{n}gram']
                for ngram, count in counter.items():
                    rows.append({'字詞': ngram, '詩人': author, '詞頻': count})
            
            if rows:
                with open(merged_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['字詞', '詩人', '詞頻']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
        
        print(f"✅ CSV文件處理完成！")
        print(f"   📁 目錄: {csv_dir}")
        print(f"   ✨ 建立檔案: {created_files:,} 個")
    
    def save_author_summary(self, output_dir: str = "analysis_result/title_analysis"):
        """保存作者詩題摘要統計"""
        print("💾 正在保存作者詩題摘要統計...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        summary_data = []
        for author, ngram_data in self.author_ngram_stats.items():
            poem_count = len(self.author_poems[author])
            
            # 計算總字符數（只計算標題）
            total_chars = 0
            for poem in self.author_poems[author]:
                title = poem.get('title', '')
                cleaned_title = self.clean_text(title)
                total_chars += len(cleaned_title)
            
            summary_data.append({
                'author': author,
                'poem_count': poem_count,
                'total_title_chars': total_chars,
                'avg_title_chars': total_chars / poem_count if poem_count > 0 else 0,
                'unique_1gram': len(ngram_data['1gram']),
                'unique_2gram': len(ngram_data['2gram']),
                'unique_4gram': len(ngram_data['4gram']),
                'total_1gram': sum(ngram_data['1gram'].values()),
                'total_2gram': sum(ngram_data['2gram'].values()),
                'total_4gram': sum(ngram_data['4gram'].values())
            })
        
        # 按字符數排序
        summary_data.sort(key=lambda x: x['total_title_chars'], reverse=True)
        
        # 保存為CSV
        csv_file = os.path.join(output_dir, "author_title_summary.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['author', 'poem_count', 'total_title_chars', 'avg_title_chars', 
                         'unique_1gram', 'unique_2gram', 'unique_4gram',
                         'total_1gram', 'total_2gram', 'total_4gram']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
        
        print(f"✅ 作者詩題摘要統計已保存到: {csv_file}")
    
    def create_analysis_report(self, output_dir: str = "analysis_result/title_analysis"):
        """創建分析報告"""
        print("📊 正在創建詩題分析報告...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        total_authors = len(self.author_ngram_stats)
        total_poems = len(self.poems_data)
        
        # 計算總字符數（只計算標題）
        total_chars = 0
        for author_poems in self.author_poems.values():
            for poem in author_poems:
                title = poem.get('title', '')
                cleaned_title = self.clean_text(title)
                total_chars += len(cleaned_title)
        
        # 統計n-gram總數
        total_1gram = sum(len(stats['1gram']) for stats in self.author_ngram_stats.values())
        total_2gram = sum(len(stats['2gram']) for stats in self.author_ngram_stats.values())
        total_4gram = sum(len(stats['4gram']) for stats in self.author_ngram_stats.values())
        
        report_file = os.path.join(output_dir, "title_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 全唐詩詩題 N-gram 分析報告\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 總體統計\n\n")
            f.write(f"- 總作者數: {total_authors:,}\n")
            f.write(f"- 總詩歌數: {total_poems:,}\n")
            f.write(f"- 詩題總字符數: {total_chars:,}\n")
            f.write(f"- 平均每首詩題: {total_chars/total_poems:.1f} 字符\n\n")
            
            f.write("## N-gram 統計\n\n")
            f.write(f"- 1-gram 總數: {total_1gram:,}\n")
            f.write(f"- 2-gram 總數: {total_2gram:,}\n")
            f.write(f"- 4-gram 總數: {total_4gram:,}\n\n")
            
            f.write("## 文件說明\n\n")
            f.write("- `author_title_ngram_csvs/`: 每位作者的詩題n-gram CSV文件\n")
            f.write("- `author_title_summary.csv`: 作者詩題摘要統計\n")
            f.write("- `title_analysis_report.md`: 本報告\n\n")
            
            f.write("## 注意事項\n\n")
            f.write("- 本分析只統計詩歌標題，不包含詩歌內容\n")
            f.write("- 已清理作者名稱，去掉末尾的'著'字\n")
            f.write("- 只保留中文字符，移除標點符號和數字\n")
        
        print(f"✅ 詩題分析報告已保存到: {report_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 詩題N-gram分析摘要:")
        print("=" * 50)
        
        total_authors = len(self.author_ngram_stats)
        total_poems = len(self.poems_data)
        
        # 計算總字符數（只計算標題）
        total_chars = 0
        for author_poems in self.author_poems.values():
            for poem in author_poems:
                title = poem.get('title', '')
                cleaned_title = self.clean_text(title)
                total_chars += len(cleaned_title)
        
        print(f"總作者數: {total_authors:,}")
        print(f"總詩歌數: {total_poems:,}")
        print(f"詩題總字符數: {total_chars:,}")
        print(f"平均每首詩題: {total_chars/total_poems:.1f} 字符")
        
        # 統計n-gram總數
        total_1gram = sum(len(stats['1gram']) for stats in self.author_ngram_stats.values())
        total_2gram = sum(len(stats['2gram']) for stats in self.author_ngram_stats.values())
        total_3gram = sum(len(stats['3gram']) for stats in self.author_ngram_stats.values())
        total_4gram = sum(len(stats['4gram']) for stats in self.author_ngram_stats.values())
        total_5gram = sum(len(stats['5gram']) for stats in self.author_ngram_stats.values())
        total_6gram = sum(len(stats['6gram']) for stats in self.author_ngram_stats.values())
        total_7gram = sum(len(stats['7gram']) for stats in self.author_ngram_stats.values())
        
        print(f"\nN-gram統計:")
        print(f"  1-gram 總數: {total_1gram:,}")
        print(f"  2-gram 總數: {total_2gram:,}")
        print(f"  3-gram 總數: {total_3gram:,}")
        print(f"  4-gram 總數: {total_4gram:,}")
        print(f"  5-gram 總數: {total_5gram:,}")
        print(f"  6-gram 總數: {total_6gram:,}")
        print(f"  7-gram 總數: {total_7gram:,}")

def main():
    """主函數"""
    print("🔍 全唐詩詩題 N-gram 分析工具")
    print("=" * 50)
    
    analyzer = TitleNgramAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 按作者組織詩歌
    analyzer.organize_poems_by_author()
    
    # 分析詩題n-gram
    analyzer.analyze_author_title_ngrams()
    
    # 保存結果
    output_dir = "analysis_result/title_analysis"
    analyzer.save_author_title_ngram_csvs(output_dir)
    analyzer.save_author_summary(output_dir)
    analyzer.create_analysis_report(output_dir)
    
    # 打印摘要
    analyzer.print_summary()
    
    print(f"\n🎉 詩題N-gram分析完成！")
    print(f"📁 結果保存在: {output_dir}")

if __name__ == "__main__":
    main()

