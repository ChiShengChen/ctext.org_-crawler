#!/usr/bin/env python3
"""
全唐詩 N-gram 分析工具
統計1-gram, 2-gram, 3-gram, 4-gram高頻詞
"""

import os
import re
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class NgramAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.ngram_stats = {
            '1gram': Counter(),
            '2gram': Counter(),
            '3gram': Counter(),
            '4gram': Counter()
        }
        
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
    
    def analyze_ngrams(self):
        """分析所有n-gram"""
        print("🔍 正在分析n-gram...")
        
        total_chars = 0
        
        for poem in self.poems_data:
            content = poem.get('content', '')
            cleaned_text = self.clean_text(content)
            total_chars += len(cleaned_text)
            
            # 提取1-4gram
            for n in range(1, 5):
                ngrams = self.extract_ngrams(cleaned_text, n)
                self.ngram_stats[f'{n}gram'].update(ngrams)
        
        print(f"✅ 分析完成！總共處理 {total_chars:,} 個中文字符")
        
        # 打印統計信息
        for n in range(1, 5):
            ngram_type = f'{n}gram'
            unique_count = len(self.ngram_stats[ngram_type])
            total_count = sum(self.ngram_stats[ngram_type].values())
            print(f"   {n}-gram: {unique_count:,} 個唯一詞，{total_count:,} 個總出現次數")
    
    def get_top_ngrams(self, n: int, top_k: int = 50) -> List[Tuple[str, int]]:
        """獲取前k個n-gram"""
        ngram_type = f'{n}gram'
        return self.ngram_stats[ngram_type].most_common(top_k)
    
    def save_ngram_results(self, output_file: str = "ngram_analysis_results.txt"):
        """保存n-gram分析結果"""
        print("💾 正在保存分析結果...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩 N-gram 分析結果\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for n in range(1, 5):
                ngram_type = f'{n}gram'
                top_ngrams = self.get_top_ngrams(n, 100)
                
                f.write(f"📊 {n}-gram 高頻詞 (前100名)\n")
                f.write("-" * 40 + "\n")
                
                for i, (ngram, count) in enumerate(top_ngrams, 1):
                    f.write(f"{i:3d}. '{ngram}': {count:,} 次\n")
                
                f.write(f"\n總計: {len(self.ngram_stats[ngram_type]):,} 個唯一{n}-gram\n")
                f.write(f"總出現次數: {sum(self.ngram_stats[ngram_type].values()):,}\n\n")
        
        print(f"✅ 分析結果已保存到: {output_file}")
    
    def save_json_results(self, output_file: str = "ngram_analysis.json"):
        """保存JSON格式的結果"""
        results = {
            'metadata': {
                'total_poems': len(self.poems_data),
                'generated_at': datetime.now().isoformat()
            },
            'statistics': {},
            'top_ngrams': {}
        }
        
        for n in range(1, 5):
            ngram_type = f'{n}gram'
            top_ngrams = self.get_top_ngrams(n, 100)
            
            results['statistics'][ngram_type] = {
                'unique_count': len(self.ngram_stats[ngram_type]),
                'total_count': sum(self.ngram_stats[ngram_type].values())
            }
            
            results['top_ngrams'][ngram_type] = [
                {'ngram': ngram, 'count': count} 
                for ngram, count in top_ngrams
            ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON結果已保存到: {output_file}")
    
    def create_visualizations(self):
        """創建可視化圖表"""
        print("📊 正在創建可視化圖表...")
        
        # 設置圖表樣式
        plt.style.use('seaborn-v0_8')
        
        # 創建2x2的子圖
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        
        for n in range(1, 5):
            row = (n - 1) // 2
            col = (n - 1) % 2
            
            top_ngrams = self.get_top_ngrams(n, 20)
            ngrams, counts = zip(*top_ngrams)
            
            # 創建水平條形圖
            axes[row, col].barh(range(len(ngrams)), counts)
            axes[row, col].set_yticks(range(len(ngrams)))
            axes[row, col].set_yticklabels(ngrams)
            axes[row, col].set_title(f'{n}-gram 高頻詞 (前20名)')
            axes[row, col].set_xlabel('出現次數')
            
            # 在條形圖上添加數值標籤
            for i, count in enumerate(counts):
                axes[row, col].text(count, i, f'{count:,}', 
                                  va='center', ha='left', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('ngram_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ 可視化圖表已保存為: ngram_analysis.png")
    
    def analyze_ngram_patterns(self):
        """分析n-gram模式"""
        print("🔍 正在分析n-gram模式...")
        
        patterns = {}
        
        for n in range(1, 5):
            ngram_type = f'{n}gram'
            top_ngrams = self.get_top_ngrams(n, 50)
            
            # 分析字符分布
            char_freq = Counter()
            for ngram, count in top_ngrams:
                for char in ngram:
                    char_freq[char] += count
            
            patterns[ngram_type] = {
                'top_chars': char_freq.most_common(20),
                'avg_length': n,
                'total_unique': len(self.ngram_stats[ngram_type])
            }
        
        # 保存模式分析結果
        with open("ngram_patterns.txt", 'w', encoding='utf-8') as f:
            f.write("N-gram 模式分析\n")
            f.write("=" * 30 + "\n\n")
            
            for n in range(1, 5):
                ngram_type = f'{n}gram'
                pattern = patterns[ngram_type]
                
                f.write(f"📊 {n}-gram 模式分析\n")
                f.write("-" * 25 + "\n")
                f.write(f"總唯一{n}-gram數: {pattern['total_unique']:,}\n")
                f.write(f"平均長度: {pattern['avg_length']}\n")
                f.write("高頻字符 (前20名):\n")
                
                for i, (char, count) in enumerate(pattern['top_chars'], 1):
                    f.write(f"  {i:2d}. '{char}': {count:,} 次\n")
                
                f.write("\n")
        
        print("✅ 模式分析結果已保存到: ngram_patterns.txt")
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 N-gram 分析摘要:")
        print("=" * 40)
        
        for n in range(1, 5):
            ngram_type = f'{n}gram'
            top_ngrams = self.get_top_ngrams(n, 10)
            
            print(f"\n🔤 {n}-gram 前10名:")
            for i, (ngram, count) in enumerate(top_ngrams, 1):
                print(f"   {i:2d}. '{ngram}': {count:,} 次")
            
            total_unique = len(self.ngram_stats[ngram_type])
            total_count = sum(self.ngram_stats[ngram_type].values())
            print(f"   總計: {total_unique:,} 個唯一{n}-gram，{total_count:,} 次出現")

def main():
    """主函數"""
    print("🔍 全唐詩 N-gram 分析工具")
    print("=" * 40)
    
    analyzer = NgramAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析n-gram
    analyzer.analyze_ngrams()
    
    # 保存結果
    analyzer.save_ngram_results()
    analyzer.save_json_results()
    
    # 創建可視化
    try:
        analyzer.create_visualizations()
    except Exception as e:
        print(f"⚠️  可視化創建失敗: {e}")
        print("請確保已安裝 matplotlib 和 seaborn")
    
    # 分析模式
    analyzer.analyze_ngram_patterns()
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n🎉 N-gram 分析完成！")
    print("📁 生成的文件:")
    print("   - ngram_analysis_results.txt (詳細分析結果)")
    print("   - ngram_analysis.json (JSON格式結果)")
    print("   - ngram_analysis.png (可視化圖表)")
    print("   - ngram_patterns.txt (模式分析)")

if __name__ == "__main__":
    main() 