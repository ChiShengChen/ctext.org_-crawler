#!/usr/bin/env python3
"""
量子神經網路唐代詩人關係預測實驗運行器
"""

import numpy as np
import pandas as pd
import json
import networkx as nx
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import torch
import torch.nn as nn
import torch.optim as optim
import pennylane as qml
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class ClassicalBaseline:
    """經典機器學習基準模型"""
    
    def __init__(self):
        self.models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'SVM': SVC(probability=True, random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42)
        }
        self.results = {}
    
    def train_and_evaluate(self, X_train, X_test, y_train, y_test):
        """訓練和評估所有基準模型"""
        for name, model in self.models.items():
            print(f"訓練 {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # 計算指標
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
            
            self.results[name] = {
                'accuracy': accuracy,
                'auc': auc,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
            print(f"{name}: AUC={auc:.4f}, Accuracy={accuracy:.4f}")

class QuantumExperimentRunner:
    """量子實驗運行器"""
    
    def __init__(self, network_file):
        self.network_file = network_file
        self.load_data()
        
    def load_data(self):
        """載入網路數據"""
        with open(self.network_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 創建NetworkX圖
        self.G = nx.Graph()
        for node in self.data['nodes']:
            self.G.add_node(node['id'], weight=node['weight'], size=node['size'])
        for edge in self.data['edges']:
            self.G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
        print(f"載入網路: {self.G.number_of_nodes()} 個節點, {self.G.number_of_edges()} 條邊")
    
    def extract_features(self):
        """提取特徵"""
        features = []
        labels = []
        
        # 正樣本（存在的邊）
        positive_edges = list(self.G.edges())
        for edge in positive_edges:
            node1, node2 = edge
            features.append([
                self.G.nodes[node1]['weight'], self.G.nodes[node1]['size'],
                self.G.nodes[node2]['weight'], self.G.nodes[node2]['size']
            ])
            labels.append(1)
        
        # 負樣本（不存在的邊）
        nodes = list(self.G.nodes())
        negative_count = len(positive_edges)
        negative_edges = []
        
        while len(negative_edges) < negative_count:
            n1, n2 = np.random.choice(nodes, 2, replace=False)
            if not self.G.has_edge(n1, n2) and (n1, n2) not in negative_edges:
                negative_edges.append((n1, n2))
                features.append([
                    self.G.nodes[n1]['weight'], self.G.nodes[n1]['size'],
                    self.G.nodes[n2]['weight'], self.G.nodes[n2]['size']
                ])
                labels.append(0)
        
        return np.array(features), np.array(labels)
    
    def run_classical_baselines(self, features, labels):
        """運行經典基準模型"""
        print("\n=== 運行經典基準模型 ===")
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        baseline = ClassicalBaseline()
        baseline.train_and_evaluate(X_train, X_test, y_train, y_test)
        
        return baseline.results
    
    def run_quantum_experiment(self, features, labels):
        """運行量子實驗"""
        print("\n=== 運行量子神經網路實驗 ===")
        
        # 這裡可以調用你的量子模型
        # 由於量子計算的複雜性，這裡提供一個框架
        print("量子模型實驗框架已準備就緒")
        print("請運行 quantum_relation_predictor.py 進行具體的量子實驗")
        
        return {"quantum_model": "實驗框架已準備"}
    
    def analyze_network_properties(self):
        """分析網路屬性"""
        print("\n=== 網路屬性分析 ===")
        
        # 基本統計
        print(f"節點數: {self.G.number_of_nodes()}")
        print(f"邊數: {self.G.number_of_edges()}")
        print(f"平均度: {np.mean([d for n, d in self.G.degree()]):.2f}")
        print(f"網路密度: {nx.density(self.G):.4f}")
        
        # 中心性分析
        degree_centrality = nx.degree_centrality(self.G)
        betweenness_centrality = nx.betweenness_centrality(self.G)
        
        # 找出最重要的節點
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        print("\n最重要的10個節點 (按度中心性):")
        for node, centrality in top_nodes:
            weight = self.G.nodes[node]['weight']
            size = self.G.nodes[node]['size']
            print(f"  {node}: 中心性={centrality:.3f}, 提及次數={weight}, 大小={size}")
        
        return {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality
        }
    
    def visualize_results(self, classical_results):
        """可視化結果"""
        print("\n=== 生成結果可視化 ===")
        
        # 模型性能比較
        models = list(classical_results.keys())
        metrics = ['auc', 'accuracy', 'precision', 'recall', 'f1']
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, metric in enumerate(metrics):
            values = [classical_results[model][metric] for model in models]
            axes[i].bar(models, values)
            axes[i].set_title(f'{metric.upper()} Score')
            axes[i].set_ylabel(metric.upper())
            axes[i].tick_params(axis='x', rotation=45)
        
        # 網路可視化
        axes[5].text(0.5, 0.5, '網路可視化\n(需要額外的圖形庫)', 
                    ha='center', va='center', transform=axes[5].transAxes)
        axes[5].set_title('Network Visualization')
        
        plt.tight_layout()
        plt.savefig('experiment_results.png', dpi=300, bbox_inches='tight')
        print("結果已保存到 experiment_results.png")
    
    def generate_report(self, classical_results, network_properties):
        """生成實驗報告"""
        print("\n=== 生成實驗報告 ===")
        
        report = f"""
# 唐代詩人關係預測實驗報告

## 數據概況
- 節點數: {self.G.number_of_nodes()}
- 邊數: {self.G.number_of_edges()}
- 平均度: {np.mean([d for n, d in self.G.degree()]):.2f}
- 網路密度: {nx.density(self.G):.4f}

## 經典模型性能

"""
        
        for model_name, results in classical_results.items():
            report += f"""
### {model_name}
- AUC: {results['auc']:.4f}
- Accuracy: {results['accuracy']:.4f}
- Precision: {results['precision']:.4f}
- Recall: {results['recall']:.4f}
- F1-Score: {results['f1']:.4f}

"""
        
        report += """
## 量子模型預期優勢

1. **量子糾纏**: 捕捉詩人之間的非線性關係模式
2. **量子疊加**: 同時考慮多種關係可能性
3. **量子干涉**: 增強重要特徵，抑制噪聲

## 下一步計劃

1. 實現完整的量子神經網路模型
2. 進行量子-經典模型對比實驗
3. 分析量子優勢的具體表現
4. 探索可解釋性方法
"""
        
        with open('experiment_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("實驗報告已保存到 experiment_report.md")

def main():
    """主函數"""
    print("=== 唐代詩人關係預測實驗 ===")
    
    # 初始化實驗運行器
    runner = QuantumExperimentRunner("person_network_filtered.json")
    
    # 分析網路屬性
    network_properties = runner.analyze_network_properties()
    
    # 提取特徵
    print("\n=== 特徵提取 ===")
    features, labels = runner.extract_features()
    print(f"特徵矩陣形狀: {features.shape}")
    print(f"正樣本: {np.sum(labels)}")
    print(f"負樣本: {len(labels) - np.sum(labels)}")
    
    # 運行經典基準模型
    classical_results = runner.run_classical_baselines(features, labels)
    
    # 運行量子實驗框架
    quantum_results = runner.run_quantum_experiment(features, labels)
    
    # 可視化結果
    runner.visualize_results(classical_results)
    
    # 生成報告
    runner.generate_report(classical_results, network_properties)
    
    print("\n=== 實驗完成 ===")
    print("請查看生成的報告和圖表文件")

if __name__ == "__main__":
    main() 