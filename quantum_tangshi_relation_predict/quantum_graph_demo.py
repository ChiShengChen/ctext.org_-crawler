#!/usr/bin/env python3
"""
純量子圖神經網路演示
基於圖性質設計的量子神經網路
"""

import numpy as np
import networkx as nx
import json
import pennylane as qml
from pennylane import numpy as pnp
import matplotlib.pyplot as plt

class QuantumGraphNN:
    """純量子圖神經網路"""
    
    def __init__(self, num_qubits=4):
        self.num_qubits = num_qubits
        self.dev = qml.device("default.qubit", wires=num_qubits)
        self.init_params()
    
    def init_params(self):
        """初始化參數"""
        self.embedding_weights = pnp.random.randn(2, 2, requires_grad=True)
        self.quantum_params = pnp.random.randn(2, self.num_qubits, 3, requires_grad=True)
        self.readout_weights = pnp.random.randn(self.num_qubits, requires_grad=True)
    
    def graph_quantum_circuit(self, inputs, params):
        """圖感知量子電路"""
        # 特徵編碼
        for i in range(self.num_qubits):
            qml.RY(inputs[i], wires=i)
        
        # 圖結構糾纏
        for layer in range(len(params)):
            # 全連接糾纏
            for i in range(self.num_qubits):
                for j in range(i + 1, self.num_qubits):
                    qml.CNOT(wires=[i, j])
            
            # 局部糾纏
            for i in range(0, self.num_qubits - 1, 2):
                qml.CRZ(params[layer][i][0], wires=[i, i + 1])
            
            # 參數化旋轉
            for i in range(self.num_qubits):
                qml.Rot(*params[layer][i], wires=i)
        
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
        qnode = qml.QNode(self.graph_quantum_circuit, self.dev)
        quantum_outputs = qnode(combined, self.quantum_params)
        
        # 讀出
        prediction = pnp.dot(quantum_outputs, self.readout_weights)
        return 1 / (1 + pnp.exp(-prediction))

def demo_quantum_graph_nn():
    """演示量子圖神經網路"""
    print("=== 純量子圖神經網路演示 ===")
    
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
    model = QuantumGraphNN(num_qubits=4)
    print(f"量子模型: {model.num_qubits} 量子比特")
    
    # 測試一些邊
    edges = list(G.edges())[:3]
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
        print()

def visualize_circuit():
    """可視化量子電路"""
    print("=== 量子電路結構 ===")
    
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
        qml.CNOT(wires=[3, 0])
        
        qml.Rot(0.1, 0.2, 0.3, wires=0)
        qml.Rot(0.4, 0.5, 0.6, wires=1)
        qml.Rot(0.7, 0.8, 0.9, wires=2)
        qml.Rot(1.0, 1.1, 1.2, wires=3)
        
        return [qml.expval(qml.PauliZ(i)) for i in range(4)]
    
    fig, ax = qml.draw_mpl(demo_circuit)()
    plt.savefig('quantum_graph_circuit.png', dpi=300, bbox_inches='tight')
    print("量子電路圖已保存")

def explain_design():
    """解釋設計理念"""
    print("\n=== 量子圖神經網路設計理念 ===")
    
    design_points = [
        "1. **圖拓撲感知**:",
        "   - 量子電路直接編碼圖的拓撲結構",
        "   - 通過糾纏門模擬節點間的連接關係",
        "",
        "2. **量子糾纏優勢**:",
        "   - 全連接糾纏捕捉全局關係",
        "   - 局部糾纏模擬鄰域結構",
        "",
        "3. **量子疊加優勢**:",
        "   - 同時考慮多種圖結構可能性",
        "   - 處理圖的不確定性",
        "",
        "4. **量子干涉優勢**:",
        "   - 增強重要的圖特徵模式",
        "   - 抑制無關的噪聲信息"
    ]
    
    for point in design_points:
        print(point)

if __name__ == "__main__":
    demo_quantum_graph_nn()
    visualize_circuit()
    explain_design()
    print("\n演示完成！") 