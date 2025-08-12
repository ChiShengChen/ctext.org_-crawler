#!/usr/bin/env python3
"""
全唐詩數據分析工具
用於分析已爬取的全唐詩數據，生成統計報告和可視化
"""

import os
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class QuantangshiAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.authors_data = {}
        self.volumes_data = {}
        
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
        current_poem = {}
        
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
    
    def analyze_authors(self) -> Dict:
        """分析作者統計"""
        print("👥 正在分析作者統計...")
        
        author_counts = Counter()
        author_poems = defaultdict(list)
        
        for poem in self.poems_data:
            author = poem.get('author', '佚名')
            author_counts[author] += 1
            author_poems[author].append(poem)
        
        # 計算統計數據
        total_authors = len(author_counts)
        total_poems = len(self.poems_data)
        avg_poems_per_author = total_poems / total_authors if total_authors > 0 else 0
        
        # 只出現一次的作者
        single_poem_authors = sum(1 for count in author_counts.values() if count == 1)
        
        self.authors_data = {
            'total_authors': total_authors,
            'total_poems': total_poems,
            'avg_poems_per_author': avg_poems_per_author,
            'single_poem_authors': single_poem_authors,
            'top_authors': author_counts.most_common(20),
            'author_poems': dict(author_poems)
        }
        
        return self.authors_data
    
    def analyze_volumes(self) -> Dict:
        """分析卷統計"""
        print("📖 正在分析卷統計...")
        
        volume_counts = Counter()
        volume_poems = defaultdict(list)
        
        for poem in self.poems_data:
            volume = poem.get('volume', 0)
            volume_counts[volume] += 1
            volume_poems[volume].append(poem)
        
        self.volumes_data = {
            'total_volumes': len(volume_counts),
            'volume_poem_counts': dict(volume_counts),
            'volume_poems': dict(volume_poems),
            'avg_poems_per_volume': len(self.poems_data) / len(volume_counts) if volume_counts else 0
        }
        
        return self.volumes_data
    
    def analyze_content(self) -> Dict:
        """分析內容統計"""
        print("📝 正在分析內容統計...")
        
        content_stats = {
            'total_characters': 0,
            'avg_poem_length': 0,
            'longest_poem': None,
            'shortest_poem': None,
            'common_words': Counter()
        }
        
        poem_lengths = []
        
        for poem in self.poems_data:
            content = poem.get('content', '')
            char_count = len(content)
            poem_lengths.append(char_count)
            content_stats['total_characters'] += char_count
            
            # 簡單的詞頻統計（按字符）
            for char in content:
                if char.strip():
                    content_stats['common_words'][char] += 1
        
        if poem_lengths:
            content_stats['avg_poem_length'] = sum(poem_lengths) / len(poem_lengths)
            
            # 最長和最短的詩
            max_length = max(poem_lengths)
            min_length = min(poem_lengths)
            
            for poem in self.poems_data:
                if len(poem.get('content', '')) == max_length:
                    content_stats['longest_poem'] = poem
                if len(poem.get('content', '')) == min_length:
                    content_stats['shortest_poem'] = poem
        
        return content_stats
    
    def generate_report(self, output_file: str = "analysis_report.txt"):
        """生成分析報告"""
        print("📊 正在生成分析報告...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩數據分析報告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 基本統計
            f.write("📈 基本統計\n")
            f.write("-" * 20 + "\n")
            f.write(f"總詩歌數: {self.authors_data['total_poems']}\n")
            f.write(f"總作者數: {self.authors_data['total_authors']}\n")
            f.write(f"總卷數: {self.volumes_data['total_volumes']}\n")
            f.write(f"平均每卷詩歌數: {self.volumes_data['avg_poems_per_volume']:.1f}\n")
            f.write(f"平均每位作者詩歌數: {self.authors_data['avg_poems_per_author']:.1f}\n")
            f.write(f"只出現一次的作者: {self.authors_data['single_poem_authors']}\n\n")
            
            # 最活躍作者
            f.write("🏆 最活躍的作者 (前20名)\n")
            f.write("-" * 30 + "\n")
            for i, (author, count) in enumerate(self.authors_data['top_authors'], 1):
                f.write(f"{i:2d}. {author}: {count} 首\n")
            f.write("\n")
            
            # 內容統計
            content_stats = self.analyze_content()
            f.write("📝 內容統計\n")
            f.write("-" * 15 + "\n")
            f.write(f"總字符數: {content_stats['total_characters']:,}\n")
            f.write(f"平均詩歌長度: {content_stats['avg_poem_length']:.1f} 字符\n")
            
            if content_stats['longest_poem']:
                f.write(f"最長詩歌: {content_stats['longest_poem']['title']} (作者: {content_stats['longest_poem']['author']})\n")
            if content_stats['shortest_poem']:
                f.write(f"最短詩歌: {content_stats['shortest_poem']['title']} (作者: {content_stats['shortest_poem']['author']})\n")
            
            f.write("\n")
            
            # 最常見字符
            f.write("🔤 最常見字符 (前20個)\n")
            f.write("-" * 25 + "\n")
            for char, count in content_stats['common_words'].most_common(20):
                f.write(f"'{char}': {count:,} 次\n")
        
        print(f"✅ 分析報告已保存到: {output_file}")
    
    def create_visualizations(self):
        """創建可視化圖表"""
        print("📊 正在創建可視化圖表...")
        
        # 設置圖表樣式
        plt.style.use('seaborn-v0_8')
        
        # 1. 作者詩歌數量分布
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 前20名作者的詩歌數量
        top_authors = self.authors_data['top_authors'][:20]
        authors, counts = zip(*top_authors)
        
        axes[0, 0].barh(range(len(authors)), counts)
        axes[0, 0].set_yticks(range(len(authors)))
        axes[0, 0].set_yticklabels(authors)
        axes[0, 0].set_title('前20名作者的詩歌數量')
        axes[0, 0].set_xlabel('詩歌數量')
        
        # 詩歌長度分布
        poem_lengths = [len(poem.get('content', '')) for poem in self.poems_data]
        axes[0, 1].hist(poem_lengths, bins=50, alpha=0.7)
        axes[0, 1].set_title('詩歌長度分布')
        axes[0, 1].set_xlabel('字符數')
        axes[0, 1].set_ylabel('詩歌數量')
        
        # 卷號與詩歌數量
        volume_data = sorted(self.volumes_data['volume_poem_counts'].items())
        volumes, poem_counts = zip(*volume_data)
        
        axes[1, 0].plot(volumes, poem_counts, alpha=0.7)
        axes[1, 0].set_title('各卷詩歌數量')
        axes[1, 0].set_xlabel('卷號')
        axes[1, 0].set_ylabel('詩歌數量')
        
        # 作者活躍度分布
        author_counts = [count for _, count in self.authors_data['top_authors']]
        axes[1, 1].hist(author_counts, bins=30, alpha=0.7)
        axes[1, 1].set_title('作者活躍度分布')
        axes[1, 1].set_xlabel('詩歌數量')
        axes[1, 1].set_ylabel('作者數量')
        
        plt.tight_layout()
        plt.savefig('quantangshi_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ 可視化圖表已保存為: quantangshi_analysis.png")
    
    def export_json_data(self, output_file: str = "quantangshi_data.json"):
        """導出數據為JSON格式"""
        print("💾 正在導出JSON數據...")
        
        export_data = {
            'metadata': {
                'total_poems': len(self.poems_data),
                'total_authors': self.authors_data['total_authors'],
                'total_volumes': self.volumes_data['total_volumes'],
                'generated_at': datetime.now().isoformat()
            },
            'poems': self.poems_data,
            'authors': {
                'statistics': {
                    'total_authors': self.authors_data['total_authors'],
                    'avg_poems_per_author': self.authors_data['avg_poems_per_author'],
                    'single_poem_authors': self.authors_data['single_poem_authors']
                },
                'top_authors': dict(self.authors_data['top_authors'])
            },
            'volumes': {
                'statistics': {
                    'total_volumes': self.volumes_data['total_volumes'],
                    'avg_poems_per_volume': self.volumes_data['avg_poems_per_volume']
                },
                'volume_poem_counts': self.volumes_data['volume_poem_counts']
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON數據已導出到: {output_file}")

def main():
    """主函數"""
    print("🔍 全唐詩數據分析工具")
    print("=" * 40)
    
    analyzer = QuantangshiAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析數據
    analyzer.analyze_authors()
    analyzer.analyze_volumes()
    
    # 生成報告
    analyzer.generate_report()
    
    # 創建可視化
    try:
        analyzer.create_visualizations()
    except Exception as e:
        print(f"⚠️  可視化創建失敗: {e}")
        print("請確保已安裝 matplotlib 和 seaborn")
    
    # 導出JSON數據
    analyzer.export_json_data()
    
    print("\n🎉 分析完成！")
    print("📁 生成的文件:")
    print("   - analysis_report.txt (分析報告)")
    print("   - quantangshi_analysis.png (可視化圖表)")
    print("   - quantangshi_data.json (JSON數據)")

if __name__ == "__main__":
    main() 