#!/usr/bin/env python3
"""
全唐詩人物關係網路分析工具
提取詩中提到的人物，並生成人物關係網路圖
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
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PersonNetworkAnalyzer:
    def __init__(self, volumes_dir: str = "quantangshi_volumes"):
        self.volumes_dir = volumes_dir
        self.poems_data = []
        self.person_poems = defaultdict(list)  # 人物 -> 詩歌列表
        self.poem_persons = defaultdict(set)   # 詩歌 -> 人物集合
        self.person_mentions = Counter()       # 人物提及次數
        self.person_connections = defaultdict(Counter)  # 人物關係網絡
        
        # 常見的人物稱謂和名字模式
        self.person_patterns = [
            # 常見姓氏
            r'[李王張劉陳楊黃趙吳周徐孫馬朱胡郭何高林羅鄭梁謝宋唐許韓馮鄧曹彭曾蕭田董袁潘於蔣蔡余杜葉程蘇魏呂丁任沈姚盧姜崔鍾譚陸汪范金石廖賈夏韋付方白鄒孟熊秦邱江尹薛閆段雷侯龍史陶黎賀顧毛郝龔邵萬錢嚴覃武戴莫孔向湯]',
            # 常見名字
            r'[白李杜王孟韓柳劉韋元張賈姚許渾羅隱皮日休陸龜蒙司空圖鄭穀崔塗吳融韓偓杜荀鶴韋莊黃滔徐夤翁承贊王貞白張蠙褚載鄭遨尚顏齊己貫休皎然靈一靈澈清江法振法照廣宣無可棲白棲一護國文益可止歸仁玄寶子蘭鸞棲鳳]',
            # 官職稱謂
            r'[丞相|尚書|侍郎|御史|將軍|太守|刺史|縣令|主簿|司馬|參軍|校尉|都尉|中郎|郎中|員外|博士|學士|翰林|侍講|侍讀|太師|太傅|太保|少師|少傅|少保]',
            # 親屬稱謂
            r'[父|母|兄|弟|姊|妹|子|女|夫|妻|翁|姑|舅|姨|叔|伯|侄|甥|孫|曾孫|玄孫]',
            # 朋友稱謂
            r'[友|朋|故|舊|同|僚|師|徒|生|門|客|賓|主]',
            # 其他稱謂
            r'[君|卿|公|侯|伯|子|男|士|民|人|客|主|賓|友|朋|故|舊|同|僚|師|徒|生|門]'
        ]
        
        # 常見人物名字（從全唐詩中提取的知名人物）
        self.known_persons = {
            # 詩人
            '李白', '杜甫', '白居易', '王維', '孟浩然', '韓愈', '柳宗元', '劉禹錫', 
            '韋應物', '元稹', '張籍', '賈島', '姚合', '許渾', '羅隱', '皮日休', 
            '陸龜蒙', '司空圖', '鄭穀', '崔塗', '吳融', '韓偓', '杜荀鶴', '韋莊',
            '黃滔', '徐夤', '翁承贊', '王貞白', '張蠙', '褚載', '鄭遨', '尚顏',
            '齊己', '貫休', '皎然', '靈一', '靈澈', '清江', '法振', '法照', '廣宣',
            '無可', '棲白', '棲一', '護國', '文益', '可止', '歸仁', '玄寶', '子蘭',
            '鸞棲鳳',
            
            # 歷史人物
            '唐玄宗', '唐肅宗', '唐代宗', '唐德宗', '唐順宗', '唐憲宗', '唐穆宗',
            '唐敬宗', '唐文宗', '唐武宗', '唐宣宗', '唐懿宗', '唐僖宗', '唐昭宗',
            '武則天', '楊貴妃', '安祿山', '史思明', '郭子儀', '李光弼', '李泌',
            '房玄齡', '杜如晦', '魏徵', '長孫無忌', '褚遂良', '狄仁傑', '張柬之',
            '姚崇', '宋璟', '張說', '張九齡', '李林甫', '楊國忠', '高力士',
            
            # 其他知名人物
            '孔子', '孟子', '莊子', '老子', '屈原', '司馬遷', '班固', '蔡邕',
            '曹操', '曹丕', '曹植', '阮籍', '嵇康', '陶淵明', '謝靈運', '謝朓',
            '庾信', '王勃', '楊炯', '盧照鄰', '駱賓王', '陳子昂', '賀知章',
            '張旭', '懷素', '吳道子', '閻立本', '韓幹', '張萱', '周昉'
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
    
    def clean_author_name(self, author: str) -> str:
        """清理作者名稱，去掉"著"字"""
        if author.endswith('著'):
            return author[:-1]
        return author
    
    def extract_persons_from_text(self, text: str) -> Set[str]:
        """從文本中提取人物"""
        persons = set()
        
        # 1. 直接匹配已知人物名字
        for person in self.known_persons:
            if person in text:
                persons.add(person)
        
        # 2. 使用正則表達式匹配人物模式
        for pattern in self.person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:  # 至少2個字符
                    persons.add(match)
        
        # 3. 匹配常見的人物稱謂模式
        # 姓氏 + 名字
        surname_pattern = r'([李王張劉陳楊黃趙吳周徐孫馬朱胡郭何高林羅鄭梁謝宋唐許韓馮鄧曹彭曾蕭田董袁潘於蔣蔡余杜葉程蘇魏呂丁任沈姚盧姜崔鍾譚陸汪范金石廖賈夏韋付方白鄒孟熊秦邱江尹薛閆段雷侯龍史陶黎賀顧毛郝龔邵萬錢嚴覃武戴莫孔向湯])([白李杜王孟韓柳劉韋元張賈姚許渾羅隱皮日休陸龜蒙司空圖鄭穀崔塗吳融韓偓杜荀鶴韋莊黃滔徐夤翁承贊王貞白張蠙褚載鄭遨尚顏齊己貫休皎然靈一靈澈清江法振法照廣宣無可棲白棲一護國文益可止歸仁玄寶子蘭鸞棲鳳])'
        matches = re.findall(surname_pattern, text)
        for surname, name in matches:
            full_name = surname + name
            if len(full_name) >= 2:
                persons.add(full_name)
        
        # 4. 匹配官職 + 姓氏的模式
        title_pattern = r'(丞相|尚書|侍郎|御史|將軍|太守|刺史|縣令|主簿|司馬|參軍|校尉|都尉|中郎|郎中|員外|博士|學士|翰林|侍講|侍讀|太師|太傅|太保|少師|少傅|少保)([李王張劉陳楊黃趙吳周徐孫馬朱胡郭何高林羅鄭梁謝宋唐許韓馮鄧曹彭曾蕭田董袁潘於蔣蔡余杜葉程蘇魏呂丁任沈姚盧姜崔鍾譚陸汪范金石廖賈夏韋付方白鄒孟熊秦邱江尹薛閆段雷侯龍史陶黎賀顧毛郝龔邵萬錢嚴覃武戴莫孔向湯])'
        matches = re.findall(title_pattern, text)
        for title, surname in matches:
            persons.add(title + surname)
        
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
    
    def save_person_poems(self, output_file: str = "analysis_result/person_poems.csv"):
        """保存提到人物的詩歌列表"""
        print("💾 正在保存提到人物的詩歌列表...")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
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
    
    def save_person_statistics(self, output_file: str = "analysis_result/person_statistics.csv"):
        """保存人物統計數據"""
        print("💾 正在保存人物統計數據...")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
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
    
    def create_person_network(self, min_mentions: int = 5, min_connections: int = 2):
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
            G.add_node(person, weight=mentions, size=min(mentions/10 + 5, 30))
        
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
    
    def draw_network_graph(self, G, output_file: str = "analysis_result/person_network.png"):
        """繪製人物關係網路圖"""
        print("🎨 正在繪製人物關係網路圖...")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 設置圖的大小
        plt.figure(figsize=(20, 16))
        
        # 計算節點大小和顏色
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        node_weights = [G.nodes[node]['weight'] for node in G.nodes()]
        
        # 計算邊的寬度
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        edge_widths = [w/2 for w in edge_weights]
        
        # 計算佈局
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
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
            if G.nodes[node]['weight'] >= 20:  # 只顯示提及次數>=20的人物
                labels[node] = node
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_family='SimHei')
        
        # 添加標題和說明
        plt.title('全唐詩人物關係網路圖\n(節點大小表示提及次數，邊寬度表示關聯強度)', 
                 fontsize=16, fontfamily='SimHei', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 人物關係網路圖已保存到: {output_file}")
    
    def save_network_data(self, G, output_file: str = "analysis_result/person_network_data.json"):
        """保存網路數據為JSON格式"""
        print("💾 正在保存網路數據...")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
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
    
    def print_summary(self):
        """打印摘要信息"""
        print("\n📋 人物關係網路分析摘要:")
        print("=" * 50)
        
        total_poems_with_persons = len(self.poem_persons)
        total_persons = len(self.person_mentions)
        total_mentions = sum(self.person_mentions.values())
        
        print(f"提到人物的詩歌: {total_poems_with_persons:,} 首")
        print(f"發現的人物: {total_persons:,} 個")
        print(f"人物提及總次數: {total_mentions:,}")
        
        print(f"\n🏆 提及次數最多的前10位人物:")
        for i, (person, mentions) in enumerate(self.person_mentions.most_common(10), 1):
            related_poems = len(self.person_poems[person])
            print(f"   {i:2d}. {person}: {mentions:,} 次提及 ({related_poems:,} 首詩)")

def main():
    """主函數"""
    print("🕸️ 全唐詩人物關係網路分析工具")
    print("=" * 50)
    
    analyzer = PersonNetworkAnalyzer()
    
    # 載入數據
    analyzer.load_data()
    
    # 分析人物提及
    analyzer.analyze_person_mentions()
    
    # 保存結果
    analyzer.save_person_poems()
    analyzer.save_person_statistics()
    
    # 創建網路圖
    G, important_persons = analyzer.create_person_network(min_mentions=5, min_connections=2)
    
    # 繪製網路圖
    analyzer.draw_network_graph(G)
    
    # 保存網路數據
    analyzer.save_network_data(G)
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n🎉 人物關係網路分析完成！")
    print("📁 生成的文件:")
    print("   - person_poems.csv (提到人物的詩歌列表)")
    print("   - person_statistics.csv (人物統計數據)")
    print("   - person_network.png (人物關係網路圖)")
    print("   - person_network_data.json (網路數據)")

if __name__ == "__main__":
    main() 