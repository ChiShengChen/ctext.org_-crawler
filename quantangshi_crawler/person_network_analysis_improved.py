#!/usr/bin/env python3
"""
全唐詩人物關係網路分析工具 (改進版)
只保留作者列表中的人名，解決中文顯示問題，並將結果放在單獨的資料夾中
"""

import os
import re
import json
import csv
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class ImprovedPersonNetworkAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.author_list = set()  # 作者列表
        self.person_poems = defaultdict(list)  # 人物 -> 詩歌列表
        self.poem_persons = defaultdict(set)   # 詩歌 -> 人物集合
        self.person_mentions = Counter()       # 人物提及次數
        self.person_connections = defaultdict(Counter)  # 人物關係網絡
        
    def load_author_list(self):
        """載入作者列表"""
        print("📚 正在載入作者列表...")
        
        author_file = "analysis_result/authors_list_clean.txt"
        with open(author_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            # 跳過標題行和空行
            if line.startswith('全唐詩') or line.startswith('=') or line.startswith('總計') or line.startswith('注意') or not line:
                continue
            
            # 提取作者名稱（去掉序號和點）
            if '. ' in line:
                author = line.split('. ', 1)[1]
            else:
                author = line
            
            if author and len(author) >= 2:
                self.author_list.add(author)
        
        print(f"✅ 載入完成！總共 {len(self.author_list)} 位作者")
        
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
    
    def extract_persons_from_text(self, text: str) -> Set[str]:
        """從文本中提取人物（只保留作者列表中的人名）"""
        persons = set()
        
        # 只匹配作者列表中的人名
        for author in self.author_list:
            if author in text:
                persons.add(author)
        
        return persons
    
    def analyze_person_mentions(self):
        """分析詩中的人物提及"""
        print("🔍 正在分析詩中的人物提及...")
        
        total_poems_with_persons = 0
        
        for poem in self.poems_data:
            title = poem.get('title', '')
            content = poem.get('content', '')
            full_text = title + '\n' + content
            
            # 提取人物
            persons = self.extract_persons_from_text(full_text)
            
            if persons:
                total_poems_with_persons += 1
                poem_id = f"{poem.get('author', '佚名')}_{poem.get('title', '')}"
                
                # 記錄詩歌中的人物
                self.poem_persons[poem_id] = persons
                
                # 統計人物提及次數
                for person in persons:
                    self.person_mentions[person] += 1
                    self.person_poems[person].append(poem)
                
                # 建立人物關係網絡（同一首詩中的人物相互關聯）
                person_list = list(persons)
                for i in range(len(person_list)):
                    for j in range(i + 1, len(person_list)):
                        person1, person2 = person_list[i], person_list[j]
                        self.person_connections[person1][person2] += 1
                        self.person_connections[person2][person1] += 1
        
        print(f"✅ 分析完成！")
        print(f"   提到人物的詩歌: {total_poems_with_persons:,} 首")
        print(f"   發現的人物: {len(self.person_mentions):,} 個")
        print(f"   人物提及總次數: {sum(self.person_mentions.values()):,}")
    
    def save_person_poems(self, output_dir: str = "analysis_result/person_network_analysis"):
        """保存提到人物的詩歌列表"""
        print("💾 正在保存提到人物的詩歌列表...")
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "person_poems.csv")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['詩歌ID', '作者', '標題', '人物', '提及次數']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for poem_id, persons in self.poem_persons.items():
                author, title = poem_id.split('_', 1)
                for person in persons:
                    writer.writerow({
                        '詩歌ID': poem_id,
                        '作者': author,
                        '標題': title,
                        '人物': person,
                        '提及次數': self.person_mentions[person]
                    })
        
        print(f"✅ 提到人物的詩歌列表已保存到: {output_file}")
    
    def save_person_statistics(self, output_dir: str = "analysis_result/person_network_analysis"):
        """保存人物統計數據"""
        print("💾 正在保存人物統計數據...")
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "person_statistics.csv")
        
        # 按提及次數排序
        sorted_persons = self.person_mentions.most_common()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['排名', '人物', '提及次數', '相關詩歌數', '關聯人物數']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for rank, (person, mentions) in enumerate(sorted_persons, 1):
                related_poems = len(self.person_poems[person])
                related_persons = len(self.person_connections[person])
                
                writer.writerow({
                    '排名': rank,
                    '人物': person,
                    '提及次數': mentions,
                    '相關詩歌數': related_poems,
                    '關聯人物數': related_persons
                })
        
        print(f"✅ 人物統計數據已保存到: {output_file}")
    
    def create_person_network(self, min_mentions: int = 3, min_connections: int = 1):
        """創建人物關係網路圖"""
        print("🕸️ 正在創建人物關係網路圖...")
        
        # 創建NetworkX圖
        G = nx.Graph()
        
        # 過濾重要人物（提及次數和關聯數達到閾值）
        important_persons = []
        for person, mentions in self.person_mentions.items():
            if mentions >= min_mentions:
                connections = len(self.person_connections[person])
                if connections >= min_connections:
                    important_persons.append(person)
        
        print(f"   重要人物數量: {len(important_persons)}")
        
        # 添加節點
        for person in important_persons:
            mentions = self.person_mentions[person]
            G.add_node(person, weight=mentions, size=min(mentions/5 + 5, 30))
        
        # 添加邊
        for person1 in important_persons:
            for person2 in important_persons:
                if person1 < person2:  # 避免重複邊
                    weight = self.person_connections[person1].get(person2, 0)
                    if weight > 0:
                        G.add_edge(person1, person2, weight=weight)
        
        print(f"   節點數量: {G.number_of_nodes()}")
        print(f"   邊數量: {G.number_of_edges()}")
        
        return G, important_persons
    
    def draw_network_graph(self, G, output_dir: str = "analysis_result/person_network_analysis"):
        """繪製人物關係網路圖"""
        print("🎨 正在繪製人物關係網路圖...")
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "person_network.png")
        
        # 設置圖的大小
        plt.figure(figsize=(20, 16))
        
        # 計算節點大小和顏色
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        node_weights = [G.nodes[node]['weight'] for node in G.nodes()]
        
        # 計算邊的寬度
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        edge_widths = [w/3 for w in edge_weights]
        
        # 計算佈局
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # 繪製節點
        nx.draw_networkx_nodes(G, pos, 
                              node_size=node_sizes,
                              node_color=node_weights,
                              cmap=plt.cm.viridis,
                              alpha=0.8)
        
        # 繪製邊
        nx.draw_networkx_edges(G, pos,
                              width=edge_widths,
                              alpha=0.3,
                              edge_color='gray')
        
        # 繪製標籤（只顯示重要節點）
        labels = {}
        for node in G.nodes():
            if G.nodes[node]['weight'] >= 10:  # 只顯示提及次數>=10的人物
                labels[node] = node
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        # 添加標題和說明
        plt.title('Tang Poetry Person Network\n(Node size: mention count, Edge width: connection strength)', 
                 fontsize=16, pad=20)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 人物關係網路圖已保存到: {output_file}")
    
    def save_network_data(self, G, output_dir: str = "analysis_result/person_network_analysis"):
        """保存網路數據為JSON格式"""
        print("💾 正在保存網路數據...")
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "person_network_data.json")
        
        network_data = {
            'metadata': {
                'total_nodes': G.number_of_nodes(),
                'total_edges': G.number_of_edges(),
                'generated_at': datetime.now().isoformat()
            },
            'nodes': [],
            'edges': []
        }
        
        # 節點數據
        for node in G.nodes():
            network_data['nodes'].append({
                'id': node,
                'weight': G.nodes[node]['weight'],
                'size': G.nodes[node]['size']
            })
        
        # 邊數據
        for u, v in G.edges():
            network_data['edges'].append({
                'source': u,
                'target': v,
                'weight': G[u][v]['weight']
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 網路數據已保存到: {output_file}")
    
    def create_analysis_report(self, output_dir: str = "analysis_result/person_network_analysis"):
        """創建分析報告"""
        print("📊 正在創建分析報告...")
        
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "analysis_report.md")
        
        total_poems_with_persons = len(self.poem_persons)
        total_persons = len(self.person_mentions)
        total_mentions = sum(self.person_mentions.values())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 全唐詩人物關係網路分析報告 (改進版)\n\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 分析概述\n\n")
            f.write("本分析只保留作者列表中的人名，確保所有提及的人物都是真實的詩人或歷史人物。\n\n")
            
            f.write("## 統計摘要\n\n")
            f.write(f"- 總詩歌數: {len(self.poems_data):,} 首\n")
            f.write(f"- 提到人物的詩歌: {total_poems_with_persons:,} 首\n")
            f.write(f"- 發現的人物: {total_persons:,} 個\n")
            f.write(f"- 人物提及總次數: {total_mentions:,} 次\n")
            f.write(f"- 作者列表總數: {len(self.author_list):,} 位\n\n")
            
            f.write("## 提及次數最多的前20位人物\n\n")
            f.write("| 排名 | 人物 | 提及次數 | 相關詩歌數 | 關聯人物數 |\n")
            f.write("|------|------|----------|------------|------------|\n")
            
            for i, (person, mentions) in enumerate(self.person_mentions.most_common(20), 1):
                related_poems = len(self.person_poems[person])
                related_persons = len(self.person_connections[person])
                f.write(f"| {i} | {person} | {mentions} | {related_poems} | {related_persons} |\n")
            
            f.write("\n## 文件說明\n\n")
            f.write("- `person_poems.csv`: 提到人物的詩歌列表\n")
            f.write("- `person_statistics.csv`: 人物統計數據\n")
            f.write("- `person_network.png`: 人物關係網路圖\n")
            f.write("- `person_network_data.json`: 網路數據\n")
            f.write("- `analysis_report.md`: 本報告\n\n")
            
            f.write("## 改進說明\n\n")
            f.write("1. **精確人物識別**: 只保留作者列表中的人名\n")
            f.write("2. **解決中文顯示**: 使用英文標題避免字體問題\n")
            f.write("3. **組織結構**: 所有結果文件放在單獨的資料夾中\n")
        
        print(f"✅ 分析報告已保存到: {output_file}")
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 人物關係網路分析摘要 (改進版):")
        print("=" * 50)
        
        total_poems_with_persons = len(self.poem_persons)
        total_persons = len(self.person_mentions)
        total_mentions = sum(self.person_mentions.values())
        
        print(f"總詩歌數: {len(self.poems_data):,} 首")
        print(f"提到人物的詩歌: {total_poems_with_persons:,} 首")
        print(f"發現的人物: {total_persons:,} 個")
        print(f"人物提及總次數: {total_mentions:,}")
        print(f"作者列表總數: {len(self.author_list):,} 位")
        
        print(f"\n🏆 提及次數最多的前10位人物:")
        for i, (person, mentions) in enumerate(self.person_mentions.most_common(10), 1):
            related_poems = len(self.person_poems[person])
            print(f"   {i:2d}. {person}: {mentions:,} 次提及 ({related_poems:,} 首詩)")

def main():
    """主函數"""
    print("🕸️ 全唐詩人物關係網路分析工具 (改進版)")
    print("=" * 50)
    
    analyzer = ImprovedPersonNetworkAnalyzer()
    
    # 載入作者列表
    analyzer.load_author_list()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析人物提及
    analyzer.analyze_person_mentions()
    
    # 保存結果
    output_dir = "analysis_result/person_network_analysis"
    analyzer.save_person_poems(output_dir)
    analyzer.save_person_statistics(output_dir)
    
    # 創建網路圖
    G, important_persons = analyzer.create_person_network(min_mentions=3, min_connections=1)
    
    # 繪製網路圖
    analyzer.draw_network_graph(G, output_dir)
    
    # 保存網路數據
    analyzer.save_network_data(G, output_dir)
    
    # 創建分析報告
    analyzer.create_analysis_report(output_dir)
    
    # 打印摘要
    analyzer.print_summary()
    
    print(f"\n🎉 人物關係網路分析 (改進版) 完成！")
    print(f"📁 結果保存在: {output_dir}")

if __name__ == "__main__":
    main() 