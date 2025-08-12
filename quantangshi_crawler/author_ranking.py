#!/usr/bin/env python3
"""
全唐詩作者作品數量完整排序
生成所有作者的詩歌數量排序列表
"""

import os
import re
from collections import Counter
from typing import List, Tuple, Dict
import json
from datetime import datetime

class AuthorRankingAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_counts = Counter()
        
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
    
    def analyze_authors(self):
        """分析作者統計"""
        print("👥 正在分析作者統計...")
        
        # 統計每個作者的詩歌數量
        for poem in self.poems_data:
            author = poem.get('author', '佚名')
            self.author_counts[author] += 1
        
        print(f"✅ 分析完成！總共 {len(self.author_counts)} 位作者")
    
    def get_author_ranking(self) -> List[Tuple[str, int]]:
        """獲取作者排名"""
        return self.author_counts.most_common()
    
    def save_ranking_txt(self, output_file: str = "author_ranking.txt"):
        """保存排名為文本格式"""
        print("💾 正在保存作者排名...")
        
        ranking = self.get_author_ranking()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩作者作品數量完整排序\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"總詩歌數: {len(self.poems_data):,} 首\n")
            f.write(f"總作者數: {len(self.author_counts):,} 位\n\n")
            
            f.write("📊 作者排名 (按作品數量降序)\n")
            f.write("-" * 40 + "\n")
            
            for i, (author, count) in enumerate(ranking, 1):
                f.write(f"{i:4d}. {author}: {count:,} 首\n")
            
            f.write(f"\n📈 統計摘要:\n")
            f.write(f"   最多產作者: {ranking[0][0]} ({ranking[0][1]:,} 首)\n")
            f.write(f"   最少產作者: {ranking[-1][0]} ({ranking[-1][1]:,} 首)\n")
            f.write(f"   平均每位作者: {len(self.poems_data) / len(self.author_counts):.1f} 首\n")
            
            # 統計不同產量級別的作者數量
            single_poem_authors = sum(1 for _, count in ranking if count == 1)
            multi_poem_authors = len(ranking) - single_poem_authors
            
            f.write(f"\n📋 產量分布:\n")
            f.write(f"   只寫一首詩的作者: {single_poem_authors:,} 位\n")
            f.write(f"   寫多首詩的作者: {multi_poem_authors:,} 位\n")
            
            # 統計前10名、前50名、前100名的作者
            top_10_total = sum(count for _, count in ranking[:10])
            top_50_total = sum(count for _, count in ranking[:50])
            top_100_total = sum(count for _, count in ranking[:100])
            
            f.write(f"\n🏆 頂級作者統計:\n")
            f.write(f"   前10名作者總詩歌數: {top_10_total:,} 首 ({top_10_total/len(self.poems_data)*100:.1f}%)\n")
            f.write(f"   前50名作者總詩歌數: {top_50_total:,} 首 ({top_50_total/len(self.poems_data)*100:.1f}%)\n")
            f.write(f"   前100名作者總詩歌數: {top_100_total:,} 首 ({top_100_total/len(self.poems_data)*100:.1f}%)\n")
        
        print(f"✅ 排名已保存到: {output_file}")
    
    def save_ranking_json(self, output_file: str = "author_ranking.json"):
        """保存排名為JSON格式"""
        print("💾 正在保存JSON格式排名...")
        
        ranking = self.get_author_ranking()
        
        data = {
            'metadata': {
                'total_poems': len(self.poems_data),
                'total_authors': len(self.author_counts),
                'generated_at': datetime.now().isoformat()
            },
            'ranking': [
                {
                    'rank': i,
                    'author': author,
                    'poem_count': count
                }
                for i, (author, count) in enumerate(ranking, 1)
            ],
            'statistics': {
                'top_author': ranking[0][0],
                'top_author_count': ranking[0][1],
                'avg_poems_per_author': len(self.poems_data) / len(self.author_counts),
                'single_poem_authors': sum(1 for _, count in ranking if count == 1)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON排名已保存到: {output_file}")
    
    def save_top_authors(self, output_file: str = "top_authors.txt", top_n: int = 100):
        """保存前N名作者"""
        print(f"💾 正在保存前{top_n}名作者...")
        
        ranking = self.get_author_ranking()[:top_n]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"全唐詩前{top_n}名作者排名\n")
            f.write("=" * 40 + "\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, (author, count) in enumerate(ranking, 1):
                f.write(f"{i:3d}. {author}: {count:,} 首\n")
        
        print(f"✅ 前{top_n}名作者已保存到: {output_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        ranking = self.get_author_ranking()
        
        print("\n📋 作者排名摘要:")
        print("=" * 40)
        print(f"總詩歌數: {len(self.poems_data):,} 首")
        print(f"總作者數: {len(self.author_counts):,} 位")
        print(f"平均每位作者: {len(self.poems_data) / len(self.author_counts):.1f} 首")
        
        print(f"\n🏆 前20名作者:")
        for i, (author, count) in enumerate(ranking[:20], 1):
            print(f"   {i:2d}. {author}: {count:,} 首")
        
        # 統計信息
        single_poem_authors = sum(1 for _, count in ranking if count == 1)
        print(f"\n📊 統計信息:")
        print(f"   只寫一首詩的作者: {single_poem_authors:,} 位")
        print(f"   寫多首詩的作者: {len(ranking) - single_poem_authors:,} 位")
        
        # 前10名作者總詩歌數
        top_10_total = sum(count for _, count in ranking[:10])
        print(f"   前10名作者總詩歌數: {top_10_total:,} 首 ({top_10_total/len(self.poems_data)*100:.1f}%)")

def main():
    """主函數"""
    print("👥 全唐詩作者作品數量排序工具")
    print("=" * 40)
    
    analyzer = AuthorRankingAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析作者
    analyzer.analyze_authors()
    
    # 保存結果
    analyzer.save_ranking_txt()
    analyzer.save_ranking_json()
    analyzer.save_top_authors("top_100_authors.txt", 100)
    analyzer.save_top_authors("top_50_authors.txt", 50)
    analyzer.save_top_authors("top_20_authors.txt", 20)
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n🎉 作者排名完成！")
    print("📁 生成的文件:")
    print("   - author_ranking.txt (完整排名)")
    print("   - author_ranking.json (JSON格式)")
    print("   - top_100_authors.txt (前100名)")
    print("   - top_50_authors.txt (前50名)")
    print("   - top_20_authors.txt (前20名)")

if __name__ == "__main__":
    main() 