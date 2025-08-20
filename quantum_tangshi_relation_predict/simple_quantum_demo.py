#!/usr/bin/env python3
"""
簡化的量子圖神經網路演示
避免複雜的參數傳遞問題
"""

import numpy as np
import networkx as nx
import json
import pennylane as qml
from pennylane import numpy as pnp
import matplotlib.pyplot as plt

class SimpleQuantumGraphNN:
    """簡化的量子圖神經網路"""
    
    def __init__(self, num_qubits=4):
        self.num_qubits = num_qubits
        self.dev = qml.device("default.qubit", wires=num_qubits)
        self.init_params()
    
    def init_params(self):
        """初始化參數"""
        self.embedding_weights = pnp.random.randn(2, 2, requires_grad=True)
        self.quantum_params = pnp.random.randn(2, self.num_qubits, 3, requires_grad=True)
        self.readout_weights = pnp.random.randn(self.num_qubits, requires_grad=True)
    
    def quantum_circuit(self, inputs, params):
        """簡化的量子電路"""
        # 特徵編碼
        for i in range(self.num_qubits):
            qml.RY(inputs[i], wires=i)
        
        # 參數化層
        for layer in range(len(params)):
            for i in range(self.num_qubits):
                qml.Rot(*params[layer][i], wires=i)
            
            # 簡單糾纏
            for i in range(self.num_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
        
        return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]
    
    def forward(self, node1_features, node2_features):
        """前向傳播"""
        # 特徵編碼
        node1_encoded = pnp.dot(self.embedding_weights, node1_features)
        node2_encoded = pnp.dot(self.embedding_weights, node2_features)
        combined = pnp.concatenate([node1_encoded, node2_encoded])
        
        # 長度調整
        if len(combined) > self.num_qubits:
            combined = combined[:self.num_qubits]
        elif len(combined) < self.num_qubits:
            padding = pnp.zeros(self.num_qubits - len(combined))
            combined = pnp.concatenate([combined, padding])
        
        # 量子電路
        qnode = qml.QNode(self.quantum_circuit, self.dev)
        quantum_outputs = qnode(combined, self.quantum_params)
        
        # 讀出
        prediction = pnp.dot(quantum_outputs, self.readout_weights)
        return 1 / (1 + pnp.exp(-prediction))

def demo_quantum_graph_nn():
    """演示量子圖神經網路"""
    print("=== 簡化量子圖神經網路演示 ===")
    
    # 載入數據
    with open("person_network_filtered.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 創建圖
    G = nx.Graph()
    for node in data['nodes']:
        G.add_node(node['id'], weight=node['weight'], size=node['size'])
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    print(f"圖規模: {G.number_of_nodes()} 節點, {G.number_of_edges()} 邊")
    
    # 創建量子模型
    model = SimpleQuantumGraphNN(num_qubits=4)
    print(f"量子模型: {model.num_qubits} 量子比特")
    
    # 測試一些邊
    edges = list(G.edges())[:5]
    print("\n=== 量子預測演示 ===")
    
    for i, (node1, node2) in enumerate(edges):
        node1_features = pnp.array([
            G.nodes[node1]['weight'],
            G.nodes[node1]['size']
        ])
        node2_features = pnp.array([
            G.nodes[node2]['weight'],
            G.nodes[node2]['size']
        ])
        
        prediction = model.forward(node1_features, node2_features)
        
        print(f"邊 {i+1}: {node1} - {node2}")
        print(f"  預測概率: {prediction:.4f}")
        print(f"  實際關係: 存在")
        print(f"  節點1特徵: weight={G.nodes[node1]['weight']}, size={G.nodes[node1]['size']:.1f}")
        print(f"  節點2特徵: weight={G.nodes[node2]['weight']}, size={G.nodes[node2]['size']:.1f}")
        print()

def analyze_graph_properties():
    """分析圖性質"""
    print("=== 圖性質分析 ===")
    
    with open("person_network_filtered.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    G = nx.Graph()
    for node in data['nodes']:
        G.add_node(node['id'], weight=node['weight'], size=node['size'])
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    # 基本統計
    print(f"節點數: {G.number_of_nodes()}")
    print(f"邊數: {G.number_of_edges()}")
    print(f"平均度: {np.mean([d for n, d in G.degree()]):.2f}")
    print(f"網路密度: {nx.density(G):.4f}")
    
    # 中心性分析
    degree_centrality = nx.degree_centrality(G)
    top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("\n最重要的5個節點:")
    for node, centrality in top_nodes:
        weight = G.nodes[node]['weight']
        size = G.nodes[node]['size']
        print(f"  {node}: 中心性={centrality:.3f}, 提及次數={weight}, 大小={size}")

def visualize_quantum_circuit():
    """可視化量子電路"""
    print("\n=== 量子電路結構 ===")
    
    dev = qml.device("default.qubit", wires=4)
    
    @qml.qnode(dev)
    def demo_circuit():
        qml.RY(0.5, wires=0)
        qml.RY(0.3, wires=1)
        qml.RY(0.7, wires=2)
        qml.RY(0.2, wires=3)
        
        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 2])
        qml.CNOT(wires=[2, 3])
        
        qml.Rot(0.1, 0.2, 0.3, wires=0)
        qml.Rot(0.4, 0.5, 0.6, wires=1)
        qml.Rot(0.7, 0.8, 0.9, wires=2)
        qml.Rot(1.0, 1.1, 1.2, wires=3)
        
        return [qml.expval(qml.PauliZ(i)) for i in range(4)]
    
    fig, ax = qml.draw_mpl(demo_circuit)()
    plt.savefig('simple_quantum_circuit.png', dpi=300, bbox_inches='tight')
    print("量子電路圖已保存到 simple_quantum_circuit.png")

def explain_quantum_advantages():
    """解釋量子優勢"""
    print("\n=== 量子圖神經網路優勢 ===")
    
    advantages = [
        "1. **量子糾纏**: 直接模擬圖的連接關係",
        "2. **量子疊加**: 同時考慮多種可能性",
        "3. **量子干涉**: 增強重要特徵",
        "4. **非線性**: 天然的非線性變換",
        "5. **參數效率**: 更少的參數實現複雜功能"
    ]
    
    for advantage in advantages:
        print(advantage)

if __name__ == "__main__":
    analyze_graph_properties()
    demo_quantum_graph_nn()
    visualize_quantum_circuit()
    explain_quantum_advantages()
    print("\n演示完成！") 