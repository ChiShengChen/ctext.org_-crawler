# 量子神經網路唐代詩人關係預測

## 項目簡介

本項目開創性地將量子神經網路應用於唐代詩人關係預測，結合量子計算的優勢和古典文學的豐富內涵，探索新的詩人關係模式。

## 研究背景

### 數據基礎
- **網路規模**: 154個詩人節點，180條已知關係邊
- **特徵豐富**: 每個節點包含提及次數(weight)和重要性(size)特徵
- **歷史價值**: 涵蓋唐代主要詩人及其社交關係

### 量子優勢
1. **量子糾纏**: 捕捉詩人之間的非線性關係模式
2. **量子疊加**: 同時考慮多種關係可能性
3. **量子干涉**: 增強重要特徵，抑制噪聲

## 項目結構

```
quantum_tangshi_relation_predict/
├── quantum_relation_predictor.py    # 量子神經網路模型
├── experiment_runner.py             # 實驗運行器
├── research_proposal.md             # 研究提案
├── requirements.txt                 # 依賴包
├── README.md                       # 項目說明
└── person_network_filtered.json    # 人物網路數據
```

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 運行實驗

```bash
# 運行完整實驗
python experiment_runner.py

# 運行量子模型
python quantum_relation_predictor.py
```

### 3. 查看結果

實驗完成後會生成：
- `experiment_results.png`: 結果可視化圖表
- `experiment_report.md`: 詳細實驗報告

## 技術架構

### 量子神經網路設計

```
輸入層 → 經典編碼器 → 量子電路 → 經典預測器 → 輸出
```

#### 量子電路特點
- **量子比特數**: 4-8個量子比特
- **編碼方式**: 角度編碼(Angle Encoding)
- **糾纏結構**: 全連接糾纏 + 參數化旋轉門
- **測量策略**: Pauli-Z測量

#### 經典組件
- **節點編碼器**: 將詩人特徵映射到高維空間
- **特徵融合器**: 結合經典和量子特徵
- **關係預測器**: 二元分類器預測關係存在性

## 實驗設計

### 對比實驗

#### 基準模型
- **經典方法**: 隨機森林、SVM、邏輯回歸
- **深度學習**: GCN、GAT、GraphSAGE

#### 量子模型變體
- **純量子模型**: 完全基於量子電路的預測
- **混合量子模型**: 量子+經典混合架構
- **量子增強模型**: 量子特徵作為經典模型的增強

### 評估指標

#### 預測性能
- **AUC-ROC**: 關係預測的整體性能
- **Precision@K**: 前K個預測的準確率
- **Recall@K**: 前K個預測的召回率

#### 量子優勢指標
- **計算效率**: 訓練和推理時間
- **模型複雜度**: 參數數量
- **泛化能力**: 跨時間段預測性能

## 預期成果

### 技術創新
- **量子算法**: 開發專門的量子關係預測算法
- **混合架構**: 設計高效的量子-經典混合模型
- **優化策略**: 量子參數優化方法

### 應用價值
- **歷史研究**: 發現新的詩人關係模式
- **文學分析**: 理解唐代文學社交網路結構
- **文化傳承**: 數字化保護古代文學遺產

### 理論貢獻
- **量子機器學習**: 在社交網路分析中的應用理論
- **跨學科方法論**: 量子計算與人文學科的結合
- **可解釋性**: 量子模型的可解釋性研究

## 技術挑戰與解決方案

### 1. 量子硬體限制
**挑戰**: 當前量子硬體噪聲大、量子比特數有限
**解決方案**: 
- 使用量子模擬器進行開發
- 設計噪聲魯棒的量子電路
- 採用混合量子-經典方法

### 2. 數據稀疏性
**挑戰**: 歷史數據不完整，關係信息稀疏
**解決方案**:
- 使用圖神經網路的表示學習
- 引入外部知識庫增強數據
- 採用遷移學習方法

### 3. 可解釋性
**挑戰**: 量子模型的黑盒特性
**解決方案**:
- 設計可解釋的量子電路結構
- 使用注意力機制分析重要特徵
- 結合領域知識進行結果驗證

## 使用示例

### 基本使用

```python
from quantum_relation_predictor import QuantumRelationPredictor
from experiment_runner import QuantumExperimentRunner

# 初始化實驗運行器
runner = QuantumExperimentRunner("person_network_filtered.json")

# 提取特徵
features, labels = runner.extract_features()

# 創建量子模型
model = QuantumRelationPredictor(num_qubits=4, embedding_dim=16)

# 運行實驗
results = runner.run_classical_baselines(features, labels)
```

### 自定義量子電路

```python
import pennylane as qml

def custom_quantum_circuit(inputs, weights):
    """自定義量子電路"""
    # 編碼輸入
    for i in range(len(inputs)):
        qml.RY(inputs[i], wires=i)
    
    # 參數化層
    for layer in range(len(weights)):
        for i in range(len(inputs)):
            qml.CNOT(wires=[i, (i + 1) % len(inputs)])
        for i in range(len(inputs)):
            qml.Rot(*weights[layer][i], wires=i)
    
    return [qml.expval(qml.PauliZ(i)) for i in range(len(inputs))]
```

## 貢獻指南

歡迎貢獻代碼、報告問題或提出改進建議！

### 貢獻方式
1. Fork 本項目
2. 創建特性分支
3. 提交更改
4. 發起 Pull Request

### 代碼規範
- 使用 Python 3.8+
- 遵循 PEP 8 代碼風格
- 添加適當的註釋和文檔

## 參考文獻

1. PennyLane Documentation: https://pennylane.readthedocs.io/
2. NetworkX Documentation: https://networkx.org/
3. PyTorch Documentation: https://pytorch.org/
4. 量子機器學習相關論文

## 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 聯繫方式

如有問題或建議，請通過以下方式聯繫：
- 提交 Issue
- 發送郵件
- 參與討論

---

**注意**: 本項目是研究性質的實驗，量子計算部分需要使用量子模擬器運行。在實際量子硬體上運行可能需要額外的配置和優化。 