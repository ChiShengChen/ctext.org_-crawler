#!/usr/bin/env python3
"""
全唐詩作者 N-gram 分析工具 (不包含標題)
對每個詩人進行1-gram, 2-gram, 4-gram統計，只統計詩歌內容，不包含標題
"""

import os
import re
import json
import csv
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from datetime import datetime

class AuthorNgramAnalyzerNoTitle:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_poems = defaultdict(list)
        self.author_ngram_stats = defaultdict(lambda: {
            '1gram': Counter(),
            '2gram': Counter(),
            '4gram': Counter()
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
    
    def analyze_author_ngrams(self):
        """分析每位作者的n-gram"""
        print("🔍 正在分析作者n-gram統計 (不包含標題)...")
        
        total_authors = len(self.author_poems)
        processed_authors = 0
        
        for author, poems in self.author_poems.items():
            processed_authors += 1
            if processed_authors % 100 == 0:
                print(f"   進度: {processed_authors}/{total_authors}")
            
            # 合併該作者所有詩歌的內容（不包含標題）
            all_content = ""
            for poem in poems:
                content = poem.get('content', '')
                cleaned_content = self.clean_text(content)
                all_content += cleaned_content
            
            if all_content:
                # 提取1-gram, 2-gram, 4-gram
                for n in [1, 2, 4]:
                    ngram_type = f'{n}gram'
                    ngrams = self.extract_ngrams(all_content, n)
                    self.author_ngram_stats[author][ngram_type].update(ngrams)
        
        print(f"✅ 分析完成！")
    
    def save_author_ngram_csvs(self, output_dir: str = "analysis_result/analysis_results_no_title"):
        """保存每位作者的n-gram CSV文件"""
        print("💾 正在保存作者n-gram CSV文件...")
        
        # 創建輸出目錄
        csv_dir = os.path.join(output_dir, "author_ngram_csvs")
        os.makedirs(csv_dir, exist_ok=True)
        
        total_authors = len(self.author_ngram_stats)
        processed_authors = 0
        
        for author, ngram_data in self.author_ngram_stats.items():
            processed_authors += 1
            if processed_authors % 100 == 0:
                print(f"   進度: {processed_authors}/{total_authors}")
            
            # 為每個n-gram類型創建CSV文件
            for n in [1, 2, 4]:
                ngram_type = f'{n}gram'
                counter = ngram_data[ngram_type]
                
                if counter:
                    # 創建CSV文件名
                    filename = f"{author}_{n}gram_詞頻統計.csv"
                    filepath = os.path.join(csv_dir, filename)
                    
                    # 寫入CSV文件
                    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['排名', '詞彙', '出現次數'])
                        
                        # 按出現次數排序
                        sorted_items = counter.most_common()
                        for rank, (ngram, count) in enumerate(sorted_items, 1):
                            writer.writerow([rank, ngram, count])
        
        print(f"✅ CSV文件已保存到: {csv_dir}")
    
    def save_detailed_analysis(self, output_dir: str = "analysis_result/analysis_results_no_title"):
        """保存詳細分析結果"""
        print("💾 正在保存詳細分析結果...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存詳細的JSON分析結果
        detailed_results = {
            'metadata': {
                'total_authors': len(self.author_ngram_stats),
                'total_poems': len(self.poems_data),
                'generated_at': datetime.now().isoformat(),
                'note': '不包含標題的n-gram分析'
            },
            'author_statistics': {}
        }
        
        for author, ngram_data in self.author_ngram_stats.items():
            author_stats = {
                'poem_count': len(self.author_poems[author]),
                'ngram_counts': {}
            }
            
            for n in [1, 2, 4]:
                ngram_type = f'{n}gram'
                counter = ngram_data[ngram_type]
                author_stats['ngram_counts'][ngram_type] = {
                    'unique_count': len(counter),
                    'total_count': sum(counter.values()),
                    'top_ngrams': [
                        {'ngram': ngram, 'count': count} 
                        for ngram, count in counter.most_common(50)
                    ]
                }
            
            detailed_results['author_statistics'][author] = author_stats
        
        json_file = os.path.join(output_dir, "detailed_ngram_analysis_no_title.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 詳細分析結果已保存到: {json_file}")
    
    def save_author_summary(self, output_dir: str = "analysis_result/analysis_results_no_title"):
        """保存作者摘要統計"""
        print("💾 正在保存作者摘要統計...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        summary_data = []
        for author, ngram_data in self.author_ngram_stats.items():
            poem_count = len(self.author_poems[author])
            
            # 計算總字符數（不包含標題）
            total_chars = 0
            for poem in self.author_poems[author]:
                content = poem.get('content', '')
                cleaned_content = self.clean_text(content)
                total_chars += len(cleaned_content)
            
            summary_data.append({
                'author': author,
                'poem_count': poem_count,
                'total_chars': total_chars,
                'avg_chars_per_poem': total_chars / poem_count if poem_count > 0 else 0,
                'unique_1gram': len(ngram_data['1gram']),
                'unique_2gram': len(ngram_data['2gram']),
                'unique_4gram': len(ngram_data['4gram']),
                'total_1gram': sum(ngram_data['1gram'].values()),
                'total_2gram': sum(ngram_data['2gram'].values()),
                'total_4gram': sum(ngram_data['4gram'].values())
            })
        
        # 按字符數排序
        summary_data.sort(key=lambda x: x['total_chars'], reverse=True)
        
        # 保存為CSV
        csv_file = os.path.join(output_dir, "author_summary_no_title.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['author', 'poem_count', 'total_chars', 'avg_chars_per_poem', 
                         'unique_1gram', 'unique_2gram', 'unique_4gram',
                         'total_1gram', 'total_2gram', 'total_4gram']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)
        
        print(f"✅ 作者摘要統計已保存到: {csv_file}")
    
    def create_analysis_report(self, output_dir: str = "analysis_result/analysis_results_no_title"):
        """創建分析報告"""
        print("📊 正在創建分析報告...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        total_authors = len(self.author_ngram_stats)
        total_poems = len(self.poems_data)
        
        # 計算總字符數（不包含標題）
        total_chars = 0
        for author_poems in self.author_poems.values():
            for poem in author_poems:
                content = poem.get('content', '')
                cleaned_content = self.clean_text(content)
                total_chars += len(cleaned_content)
        
        # 統計n-gram總數
        total_1gram = sum(len(stats['1gram']) for stats in self.author_ngram_stats.values())
        total_2gram = sum(len(stats['2gram']) for stats in self.author_ngram_stats.values())
        total_4gram = sum(len(stats['4gram']) for stats in self.author_ngram_stats.values())
        
        report_file = os.path.join(output_dir, "analysis_report_no_title.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 全唐詩作者 N-gram 分析報告 (不包含標題)\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 總體統計\n\n")
            f.write(f"- 總作者數: {total_authors:,}\n")
            f.write(f"- 總詩歌數: {total_poems:,}\n")
            f.write(f"- 總字符數: {total_chars:,} (不包含標題)\n")
            f.write(f"- 平均每首詩: {total_chars/total_poems:.1f} 字符\n\n")
            
            f.write("## N-gram 統計\n\n")
            f.write(f"- 1-gram 總數: {total_1gram:,}\n")
            f.write(f"- 2-gram 總數: {total_2gram:,}\n")
            f.write(f"- 4-gram 總數: {total_4gram:,}\n\n")
            
            f.write("## 文件說明\n\n")
            f.write("- `author_ngram_csvs/`: 每位作者的n-gram CSV文件\n")
            f.write("- `detailed_ngram_analysis_no_title.json`: 詳細的JSON分析結果\n")
            f.write("- `author_summary_no_title.csv`: 作者摘要統計\n")
            f.write("- `analysis_report_no_title.md`: 本報告\n\n")
            
            f.write("## 注意事項\n\n")
            f.write("- 本分析只統計詩歌內容，不包含標題\n")
            f.write("- 已清理作者名稱，去掉末尾的'著'字\n")
            f.write("- 只保留中文字符，移除標點符號和數字\n")
        
        print(f"✅ 分析報告已保存到: {report_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 N-gram分析摘要 (不包含標題):")
        print("=" * 50)
        
        total_authors = len(self.author_ngram_stats)
        total_poems = len(self.poems_data)
        
        # 計算總字符數（不包含標題）
        total_chars = 0
        for author_poems in self.author_poems.values():
            for poem in author_poems:
                content = poem.get('content', '')
                cleaned_content = self.clean_text(content)
                total_chars += len(cleaned_content)
        
        print(f"總作者數: {total_authors:,}")
        print(f"總詩歌數: {total_poems:,}")
        print(f"總字符數: {total_chars:,} (不包含標題)")
        print(f"平均每首詩: {total_chars/total_poems:.1f} 字符")
        
        # 統計n-gram總數
        total_1gram = sum(len(stats['1gram']) for stats in self.author_ngram_stats.values())
        total_2gram = sum(len(stats['2gram']) for stats in self.author_ngram_stats.values())
        total_4gram = sum(len(stats['4gram']) for stats in self.author_ngram_stats.values())
        
        print(f"\nN-gram統計:")
        print(f"  1-gram 總數: {total_1gram:,}")
        print(f"  2-gram 總數: {total_2gram:,}")
        print(f"  4-gram 總數: {total_4gram:,}")

def main():
    """主函數"""
    print("🔍 全唐詩作者 N-gram 分析工具 (不包含標題)")
    print("=" * 50)
    
    analyzer = AuthorNgramAnalyzerNoTitle()
    
    # 載入數據
    analyzer.load_data()
    
    # 按作者組織詩歌
    analyzer.organize_poems_by_author()
    
    # 分析n-gram
    analyzer.analyze_author_ngrams()
    
    # 保存結果
    output_dir = "analysis_result/analysis_results_no_title"
    analyzer.save_author_ngram_csvs(output_dir)
    analyzer.save_detailed_analysis(output_dir)
    analyzer.save_author_summary(output_dir)
    analyzer.create_analysis_report(output_dir)
    
    # 打印摘要
    analyzer.print_summary()
    
    print(f"\n🎉 N-gram分析 (不包含標題) 完成！")
    print(f"📁 結果保存在: {output_dir}")

if __name__ == "__main__":
    main() 