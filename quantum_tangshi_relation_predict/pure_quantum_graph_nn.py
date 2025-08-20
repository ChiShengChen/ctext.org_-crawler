#!/usr/bin/env python3
"""
純量子圖神經網路模型
基於圖的拓撲性質設計的量子神經網路
"""

import numpy as np
import networkx as nx
import json
import pennylane as qml
from pennylane import numpy as pnp
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import matplotlib.pyplot as plt
from tqdm import tqdm

class PureQuantumGraphNN:
    """
    純量子圖神經網路
    基於圖的拓撲性質設計，完全使用量子計算
    """
    
    def __init__(self, num_qubits=8, num_layers=3, graph_embedding_dim=4):
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.graph_embedding_dim = graph_embedding_dim
        
        # 量子設備
        self.dev = qml.device("default.qubit", wires=num_qubits)
        
        # 可訓練參數
        self.init_parameters()
        
    def init_parameters(self):
        """初始化可訓練參數"""
        # 圖嵌入參數
        self.graph_embedding_weights = pnp.random.randn(
            self.graph_embedding_dim, 2, requires_grad=True
        )
        
        # 量子電路參數
        self.quantum_weights = pnp.random.randn(
            self.num_layers, self.num_qubits, 3, requires_grad=True
        )
        
        # 讀出參數
        self.readout_weights = pnp.random.randn(
            self.num_qubits, requires_grad=True
        )
    
    def graph_to_quantum_features(self, node1_features, node2_features, graph_properties):
        """
        將圖特徵轉換為量子特徵
        """
        # 節點特徵編碼
        node1_encoded = pnp.dot(self.graph_embedding_weights, node1_features)
        node2_encoded = pnp.dot(self.graph_embedding_weights, node2_features)
        
        # 圖拓撲特徵編碼
        graph_encoded = pnp.array([
            graph_properties['degree_diff'],
            graph_properties['clustering_coeff'],
            graph_properties['path_length'],
            graph_properties['centrality_diff']
        ])
        
        # 組合所有特徵
        combined_features = pnp.concatenate([
            node1_encoded, node2_encoded, graph_encoded
        ])
        
        # 確保特徵數量匹配量子比特數
        if len(combined_features) > self.num_qubits:
            combined_features = combined_features[:self.num_qubits]
        elif len(combined_features) < self.num_qubits:
            # 用零填充
            padding = pnp.zeros(self.num_qubits - len(combined_features))
            combined_features = pnp.concatenate([combined_features, padding])
        
        return combined_features
    
    def quantum_circuit(self, inputs, weights):
        """
        量子電路設計
        基於圖的拓撲性質設計的量子電路
        """
        # 1. 特徵編碼層 - 將圖特徵編碼到量子態
        for i in range(self.num_qubits):
            qml.RY(inputs[i], wires=i)
            qml.RZ(inputs[i] * 0.5, wires=i)
        
        # 2. 圖結構感知的糾纏層
        for layer in range(len(weights)):
            # 全連接糾纏 - 模擬圖的全局連接
            for i in range(self.num_qubits):
                for j in range(i + 1, self.num_qubits):
                    qml.CNOT(wires=[i, j])
                    qml.CRZ(weights[layer][i][0], wires=[i, j])
            
            # 局部糾纏 - 模擬圖的局部結構
            for i in range(0, self.num_qubits - 1, 2):
                qml.CNOT(wires=[i, i + 1])
                qml.CRX(weights[layer][i][1], wires=[i, i + 1])
            
            # 參數化旋轉層
            for i in range(self.num_qubits):
                qml.Rot(*weights[layer][i], wires=i)
        
        # 3. 測量層 - 基於圖性質的測量策略
        measurements = []
        for i in range(self.num_qubits):
            # 使用Pauli-Z測量，適合二元分類
            measurements.append(qml.expval(qml.PauliZ(i)))
        
        return measurements
    
    def forward(self, node1_features, node2_features, graph_properties):
        """
        前向傳播
        """
        # 特徵轉換
        quantum_inputs = self.graph_to_quantum_features(
            node1_features, node2_features, graph_properties
        )
        
        # 量子電路執行
        qnode = qml.QNode(self.quantum_circuit, self.dev)
        quantum_outputs = qnode(quantum_inputs, self.quantum_weights)
        
        # 讀出層 - 將量子測量結果轉換為預測
        prediction = pnp.dot(quantum_outputs, self.readout_weights)
        
        # 使用sigmoid函數進行二元分類
        prediction = 1 / (1 + pnp.exp(-prediction))
        
        return prediction

class GraphPropertyExtractor:
    """
    圖性質提取器
    提取用於量子計算的圖拓撲特徵
    """
    
    def __init__(self, graph):
        self.graph = graph
        self.compute_global_properties()
    
    def compute_global_properties(self):
        """計算全局圖性質"""
        self.degree_centrality = nx.degree_centrality(self.graph)
        self.betweenness_centrality = nx.betweenness_centrality(self.graph)
        self.clustering_coefficient = nx.clustering(self.graph)
        self.shortest_paths = dict(nx.all_pairs_shortest_path_length(self.graph))
    
    def extract_edge_properties(self, node1, node2):
        """
        提取邊的圖性質特徵
        """
        # 度數差異
        degree1 = self.graph.degree(node1)
        degree2 = self.graph.degree(node2)
        degree_diff = abs(degree1 - degree2) / max(degree1 + degree2, 1)
        
        # 聚類係數
        clustering1 = self.clustering_coefficient.get(node1, 0)
        clustering2 = self.clustering_coefficient.get(node2, 0)
        clustering_coeff = (clustering1 + clustering2) / 2
        
        # 最短路徑長度
        try:
            path_length = self.shortest_paths[node1][node2]
        except KeyError:
            path_length = float('inf')
        
        # 中心性差異
        centrality1 = self.degree_centrality.get(node1, 0)
        centrality2 = self.degree_centrality.get(node2, 0)
        centrality_diff = abs(centrality1 - centrality2)
        
        return {
            'degree_diff': degree_diff,
            'clustering_coeff': clustering_coeff,
            'path_length': min(path_length, 10) / 10,  # 正規化
            'centrality_diff': centrality_diff
        }

class QuantumGraphDataset:
    """
    量子圖數據集
    專門為量子圖神經網路準備數據
    """
    
    def __init__(self, network_file):
        with open(network_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 創建NetworkX圖
        self.graph = nx.Graph()
        for node in self.data['nodes']:
            self.graph.add_node(node['id'], weight=node['weight'], size=node['size'])
        for edge in self.data['edges']:
            self.graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
        # 初始化圖性質提取器
        self.property_extractor = GraphPropertyExtractor(self.graph)
    
    def prepare_quantum_data(self, negative_ratio=1.0):
        """
        準備量子計算數據
        """
        positive_edges = list(self.graph.edges())
        nodes = list(self.graph.nodes())
        
        # 生成負樣本
        negative_edges = []
        while len(negative_edges) < len(positive_edges) * negative_ratio:
            n1, n2 = np.random.choice(nodes, 2, replace=False)
            if not self.graph.has_edge(n1, n2) and (n1, n2) not in negative_edges:
                negative_edges.append((n1, n2))
        
        # 準備數據
        quantum_data = []
        labels = []
        
        # 正樣本
        for edge in positive_edges:
            node1, node2 = edge
            data_point = self.create_quantum_data_point(node1, node2, 1)
            quantum_data.append(data_point)
            labels.append(1)
        
        # 負樣本
        for edge in negative_edges:
            node1, node2 = edge
            data_point = self.create_quantum_data_point(node1, node2, 0)
            quantum_data.append(data_point)
            labels.append(0)
        
        return quantum_data, np.array(labels)
    
    def create_quantum_data_point(self, node1, node2, label):
        """
        創建單個量子數據點
        """
        # 節點特徵
        node1_features = pnp.array([
            self.graph.nodes[node1]['weight'],
            self.graph.nodes[node1]['size']
        ])
        node2_features = pnp.array([
            self.graph.nodes[node2]['weight'],
            self.graph.nodes[node2]['size']
        ])
        
        # 圖性質特徵
        graph_properties = self.property_extractor.extract_edge_properties(node1, node2)
        
        return {
            'node1_features': node1_features,
            'node2_features': node2_features,
            'graph_properties': graph_properties,
            'label': label
        }

def train_quantum_graph_nn(model, dataset, epochs=50, learning_rate=0.01):
    """
    訓練純量子圖神經網路
    """
    print("開始訓練純量子圖神經網路...")
    
    # 準備數據
    quantum_data, labels = dataset.prepare_quantum_data()
    
    # 分割數據
    train_data, test_data, train_labels, test_labels = train_test_split(
        quantum_data, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # 優化器
    opt = qml.AdamOptimizer(learning_rate)
    
    # 訓練歷史
    train_losses = []
    test_aucs = []
    
    for epoch in tqdm(range(epochs), desc="訓練進度"):
        # 計算梯度
        def cost_fn(embedding_weights, quantum_weights, readout_weights):
            total_loss = 0
            for data_point in train_data:
                # 臨時替換模型參數
                old_embedding = model.graph_embedding_weights
                old_quantum = model.quantum_weights
                old_readout = model.readout_weights
                
                model.graph_embedding_weights = embedding_weights
                model.quantum_weights = quantum_weights
                model.readout_weights = readout_weights
                
                prediction = model.forward(
                    data_point['node1_features'],
                    data_point['node2_features'],
                    data_point['graph_properties']
                )
                
                # 恢復原參數
                model.graph_embedding_weights = old_embedding
                model.quantum_weights = old_quantum
                model.readout_weights = old_readout
                
                # 二元交叉熵損失
                loss = -data_point['label'] * pnp.log(prediction + 1e-8) - \
                       (1 - data_point['label']) * pnp.log(1 - prediction + 1e-8)
                total_loss += loss
            return total_loss / len(train_data)
        
        # 更新參數
        params = [model.graph_embedding_weights, model.quantum_weights, model.readout_weights]
        params = opt.step(cost_fn, params)
        model.graph_embedding_weights, model.quantum_weights, model.readout_weights = params
        
        # 計算訓練損失
        train_loss = cost_fn(model.graph_embedding_weights, model.quantum_weights, model.readout_weights)
        train_losses.append(train_loss)
        
        # 計算測試AUC
        if epoch % 10 == 0:
            test_predictions = []
            for data_point in test_data:
                pred = model.forward(
                    data_point['node1_features'],
                    data_point['node2_features'],
                    data_point['graph_properties']
                )
                test_predictions.append(pred)
            
            test_auc = roc_auc_score(test_labels, test_predictions)
            test_aucs.append(test_auc)
            
            print(f"Epoch {epoch}: Loss={train_loss:.4f}, Test AUC={test_auc:.4f}")
    
    return train_losses, test_aucs

def analyze_quantum_advantages():
    """
    分析量子圖神經網路的優勢
    """
    print("\n=== 純量子圖神經網路優勢分析 ===")
    
    advantages = [
        "1. **圖拓撲感知**: 量子電路直接編碼圖的拓撲結構",
        "2. **全局糾纏**: 通過量子糾纏捕捉圖的全局關係",
        "3. **局部結構**: 局部糾纏模擬圖的鄰域結構",
        "4. **量子疊加**: 同時考慮多種圖結構可能性",
        "5. **量子干涉**: 增強重要的圖特徵模式",
        "6. **參數效率**: 量子參數空間更豐富",
        "7. **非線性建模**: 量子門天然的非線性特性"
    ]
    
    for advantage in advantages:
        print(advantage)
    
    print("\n=== 與經典圖神經網路的比較 ===")
    comparisons = [
        "• 經典GCN: 基於鄰接矩陣的線性組合",
        "• 量子GNN: 基於量子糾纏的非線性組合",
        "• 經典GAT: 注意力機制計算",
        "• 量子GNN: 量子干涉增強注意力",
        "• 經典GraphSAGE: 鄰域採樣聚合",
        "• 量子GNN: 量子疊加考慮所有鄰域"
    ]
    
    for comparison in comparisons:
        print(comparison)

def visualize_quantum_circuit():
    """
    可視化量子電路結構
    """
    print("\n=== 量子電路結構可視化 ===")
    
    # 創建一個簡單的量子電路進行可視化
    dev = qml.device("default.qubit", wires=4)
    
    @qml.qnode(dev)
    def circuit_demo():
        # 特徵編碼
        qml.RY(0.5, wires=0)
        qml.RY(0.3, wires=1)
        qml.RY(0.7, wires=2)
        qml.RY(0.2, wires=3)
        
        # 圖結構糾纏
        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 2])
        qml.CNOT(wires=[2, 3])
        qml.CNOT(wires=[3, 0])
        
        # 參數化旋轉
        qml.Rot(0.1, 0.2, 0.3, wires=0)
        qml.Rot(0.4, 0.5, 0.6, wires=1)
        qml.Rot(0.7, 0.8, 0.9, wires=2)
        qml.Rot(1.0, 1.1, 1.2, wires=3)
        
        return [qml.expval(qml.PauliZ(i)) for i in range(4)]
    
    # 繪製電路圖
    fig, ax = qml.draw_mpl(circuit_demo)()
    plt.savefig('quantum_circuit_structure.png', dpi=300, bbox_inches='tight')
    print("量子電路結構圖已保存到 quantum_circuit_structure.png")

def main():
    """
    主函數
    """
    print("=== 純量子圖神經網路實驗 ===")
    
    # 載入數據
    dataset = QuantumGraphDataset("person_network_filtered.json")
    print(f"載入圖: {dataset.graph.number_of_nodes()} 個節點, {dataset.graph.number_of_edges()} 條邊")
    
    # 創建純量子圖神經網路
    model = PureQuantumGraphNN(num_qubits=8, num_layers=3, graph_embedding_dim=4)
    print(f"創建量子模型: {model.num_qubits} 量子比特, {model.num_layers} 層")
    
    # 訓練模型
    train_losses, test_aucs = train_quantum_graph_nn(model, dataset, epochs=50)
    
    # 分析量子優勢
    analyze_quantum_advantages()
    
    # 可視化量子電路
    visualize_quantum_circuit()
    
    # 繪製訓練曲線
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title('訓練損失')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(range(0, len(train_losses), 10), test_aucs)
    plt.title('測試AUC')
    plt.xlabel('Epoch')
    plt.ylabel('AUC')
    
    plt.tight_layout()
    plt.savefig('quantum_training_curves.png', dpi=300, bbox_inches='tight')
    print("訓練曲線已保存到 quantum_training_curves.png")
    
    print(f"\n最終測試AUC: {test_aucs[-1]:.4f}")
    print("純量子圖神經網路實驗完成！")

if __name__ == "__main__":
    main() 