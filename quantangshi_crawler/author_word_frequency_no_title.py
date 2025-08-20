#!/usr/bin/env python3
"""
全唐詩作者詞頻統計工具 (不包含標題)
統計每位詩人的詞頻，只計算詩歌內容，不包含標題
"""

import os
import re
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from datetime import datetime

class AuthorWordFrequencyAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_word_counts = defaultdict(Counter)
        self.author_char_counts = defaultdict(int)
        self.author_poem_counts = Counter()
        
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
    
    def analyze_author_word_frequency(self):
        """分析每位作者的詞頻統計 (不包含標題)"""
        print("🔍 正在分析作者詞頻統計 (不包含標題)...")
        
        for poem in self.poems_data:
            author = poem.get('author', '佚名')
            clean_author = self.clean_author_name(author)
            content = poem.get('content', '')
            
            # 只統計詩歌內容，不包含標題
            cleaned_content = self.clean_text(content)
            
            if cleaned_content:
                # 統計字符頻率
                for char in cleaned_content:
                    self.author_word_counts[clean_author][char] += 1
                
                # 統計字符總數
                self.author_char_counts[clean_author] += len(cleaned_content)
                self.author_poem_counts[clean_author] += 1
        
        print(f"✅ 分析完成！")
        print(f"   總字符數: {sum(self.author_char_counts.values()):,}")
        print(f"   總詩歌數: {sum(self.author_poem_counts.values()):,}")
        print(f"   總作者數: {len(self.author_word_counts):,}")
    
    def get_author_ranking_by_chars(self) -> List[Tuple[str, int]]:
        """按字符數獲取作者排名"""
        return sorted(self.author_char_counts.items(), key=lambda x: x[1], reverse=True)
    
    def save_author_char_ranking(self, output_file: str = "author_char_ranking_no_title.txt"):
        """保存作者字符數排名 (不包含標題)"""
        print("💾 正在保存作者字符數排名 (不包含標題)...")
        
        ranking = self.get_author_ranking_by_chars()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩作者字符數排名 (不包含標題)\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("注意: 只統計詩歌內容字符，不包含標題\n\n")
            
            f.write("📊 作者排名 (按字符數降序)\n")
            f.write("-" * 40 + "\n")
            
            for i, (author, char_count) in enumerate(ranking, 1):
                poem_count = self.author_poem_counts[author]
                avg_chars = char_count / poem_count if poem_count > 0 else 0
                f.write(f"{i:4d}. {author}: {char_count:,} 字符 ({poem_count:,} 首詩, 平均 {avg_chars:.1f} 字符/首)\n")
        
        print(f"✅ 作者字符數排名已保存到: {output_file}")
    
    def save_author_word_frequency(self, output_file: str = "author_word_frequency_no_title.json"):
        """保存作者詞頻統計為JSON格式"""
        print("💾 正在保存作者詞頻統計 (JSON格式)...")
        
        results = {
            'metadata': {
                'total_authors': len(self.author_word_counts),
                'total_chars': sum(self.author_char_counts.values()),
                'total_poems': sum(self.author_poem_counts.values()),
                'generated_at': datetime.now().isoformat(),
                'note': '只統計詩歌內容字符，不包含標題'
            },
            'author_statistics': {},
            'top_authors_by_chars': []
        }
        
        # 作者統計
        for author in self.author_word_counts:
            char_count = self.author_char_counts[author]
            poem_count = self.author_poem_counts[author]
            avg_chars = char_count / poem_count if poem_count > 0 else 0
            
            results['author_statistics'][author] = {
                'total_chars': char_count,
                'total_poems': poem_count,
                'avg_chars_per_poem': avg_chars,
                'top_words': [
                    {'word': word, 'count': count} 
                    for word, count in self.author_word_counts[author].most_common(50)
                ]
            }
        
        # 按字符數排名
        char_ranking = self.get_author_ranking_by_chars()
        results['top_authors_by_chars'] = [
            {
                'author': author, 
                'char_count': char_count,
                'poem_count': self.author_poem_counts[author],
                'avg_chars': char_count / self.author_poem_counts[author] if self.author_poem_counts[author] > 0 else 0
            }
            for author, char_count in char_ranking[:100]  # 前100名
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 作者詞頻統計已保存到: {output_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        char_ranking = self.get_author_ranking_by_chars()
        
        print("\n📋 作者詞頻統計摘要 (不包含標題):")
        print("=" * 50)
        print(f"總字符數: {sum(self.author_char_counts.values()):,}")
        print(f"總詩歌數: {sum(self.author_poem_counts.values()):,}")
        print(f"總作者數: {len(self.author_word_counts):,}")
        print(f"平均每首詩: {sum(self.author_char_counts.values()) / sum(self.author_poem_counts.values()):.1f} 字符")
        
        print(f"\n🏆 按字符數前10名作者:")
        for i, (author, char_count) in enumerate(char_ranking[:10], 1):
            poem_count = self.author_poem_counts[author]
            avg_chars = char_count / poem_count if poem_count > 0 else 0
            print(f"   {i:2d}. {author}: {char_count:,} 字符 ({poem_count:,} 首詩, 平均 {avg_chars:.1f} 字符/首)")

def main():
    """主函數"""
    print("🔍 全唐詩作者詞頻統計工具 (不包含標題)")
    print("=" * 50)
    
    analyzer = AuthorWordFrequencyAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析作者詞頻
    analyzer.analyze_author_word_frequency()
    
    # 保存結果
    analyzer.save_author_char_ranking()
    analyzer.save_author_word_frequency()
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n🎉 作者詞頻統計 (不包含標題) 完成！")
    print("📁 生成的文件:")
    print("   - author_char_ranking_no_title.txt (作者字符數排名)")
    print("   - author_word_frequency_no_title.json (詳細詞頻統計)")

if __name__ == "__main__":
    main() 