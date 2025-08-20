import pandas as pd
import json
import networkx as nx
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import torch
import torch.nn as nn
import torch.optim as optim
import pennylane as qml
from pennylane import numpy as pnp

class QuantumRelationPredictor:
    """量子神經網路用於唐代詩人關係預測"""
    
    def __init__(self, num_qubits=4, embedding_dim=16):
        self.num_qubits = num_qubits
        self.embedding_dim = embedding_dim
        
        # 量子設備
        self.dev = qml.device("default.qubit", wires=num_qubits)
        self.qnode = qml.QNode(self.quantum_circuit, self.dev)
        
        # 經典神經網路
        self.node_encoder = nn.Linear(2, embedding_dim)
        self.edge_predictor = nn.Sequential(
            nn.Linear(embedding_dim * 2 + num_qubits, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def quantum_circuit(self, inputs, weights):
        """量子電路"""
        # 編碼輸入
        for i in range(self.num_qubits):
            qml.RY(inputs[i], wires=i)
        
        # 參數化層
        for layer in range(len(weights)):
            for i in range(self.num_qubits):
                qml.CNOT(wires=[i, (i + 1) % self.num_qubits])
            for i in range(self.num_qubits):
                qml.Rot(*weights[layer][i], wires=i)
        
        return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]
    
    def forward(self, node1_features, node2_features):
        """前向傳播"""
        # 節點編碼
        node1_embedding = self.node_encoder(node1_features)
        node2_embedding = self.node_encoder(node2_features)
        
        # 量子特徵
        inputs = torch.cat([node1_features, node2_features])[:self.num_qubits]
        weights = torch.randn(2, self.num_qubits, 3) * 0.1
        quantum_features = torch.tensor(self.qnode(inputs.numpy(), weights.numpy()))
        
        # 特徵融合
        combined = torch.cat([node1_embedding, node2_embedding, quantum_features])
        return self.edge_predictor(combined)

class TangPoetDataset:
    """唐代詩人數據集"""
    
    def __init__(self, network_file):
        with open(network_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.G = nx.Graph()
        for node in self.data['nodes']:
            self.G.add_node(node['id'], weight=node['weight'], size=node['size'])
        for edge in self.data['edges']:
            self.G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    def prepare_data(self):
        """準備訓練數據"""
        positive_edges = list(self.G.edges())
        nodes = list(self.G.nodes())
        
        # 生成負樣本
        negative_edges = []
        while len(negative_edges) < len(positive_edges):
            n1, n2 = np.random.choice(nodes, 2, replace=False)
            if not self.G.has_edge(n1, n2):
                negative_edges.append((n1, n2))
        
        # 特徵提取
        features = []
        labels = []
        
        for edge in positive_edges + negative_edges:
            n1, n2 = edge
            features.append([
                self.G.nodes[n1]['weight'], self.G.nodes[n1]['size'],
                self.G.nodes[n2]['weight'], self.G.nodes[n2]['size']
            ])
            labels.append(1 if self.G.has_edge(n1, n2) else 0)
        
        return np.array(features), np.array(labels)

def train_model(model, features, labels, epochs=50):
    """訓練模型"""
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.BCELoss()
    
    X_train, X_val, y_train, y_val = train_test_split(features, labels, test_size=0.2)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for i in range(0, len(X_train), 16):
            batch_features = X_train[i:i+16]
            batch_labels = y_train[i:i+16]
            
            batch_loss = 0
            for features, label in zip(batch_features, batch_labels):
                node1 = torch.tensor([features[0], features[1]], dtype=torch.float32)
                node2 = torch.tensor([features[2], features[3]], dtype=torch.float32)
                
                pred = model.forward(node1, node2)
                loss = criterion(pred, torch.tensor([label], dtype=torch.float32))
                batch_loss += loss
            
            optimizer.zero_grad()
            batch_loss.backward()
            optimizer.step()
            total_loss += batch_loss.item()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Loss = {total_loss/len(X_train):.4f}")
    
    return model

if __name__ == "__main__":
    # 載入數據
    dataset = TangPoetDataset("person_network_filtered.json")
    features, labels = dataset.prepare_data()
    
    # 創建模型
    model = QuantumRelationPredictor()
    
    # 訓練
    print("開始訓練量子神經網路...")
    trained_model = train_model(model, features, labels)
    
    print("訓練完成！") 
import numpy as np
 