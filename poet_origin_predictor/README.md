# 從詩作預測詩人出身 — 地域語言指紋的計算分析

根據 [`prompt.md`](prompt.md)（Chen & Liu，*從詩作預測詩人出身：《全唐詩》中地域語言指紋的計算分析*）所建立的機器學習模型。

任務：**僅憑詩人的全部詩作，預測其地理出身（唐代行政「道」）。**

## 資料來源

| 來源 | 用途 |
|------|------|
| `../quantangshi_crawler/quantangshi_volumes/*.txt`（全唐詩 900 卷） | 詩作文本 |
| `../quantangshi_crawler/poet_geo_label.csv`（CBDB 籍貫資料） | 詩人籍貫 → 唐代「道」級標籤 |

`build_dataset.py` 將每位詩人名下所有詩作彙整為詩人層級語料，
依 `作者:` 欄位比對籍貫（自動去除「著／撰／等」等後綴並清除逐句重複的標題前綴），
並濾除存詩過少（預設 < 5 首）或籍貫不明的詩人。

最終資料集（`dataset.csv`）：**357 位詩人、10 個道**，呈現論文所述的區域不平衡
（江南道 126 vs. 隴右道 6）。

## 流程

```
build_dataset.py   →  dataset.csv         # 1. 資料準備（解析 + 比對 + 過濾）
features.py        →  領域特徵向量          # 2. 特徵提取（意象/季節/典故）
train.py           →  交叉驗證評估 + 可解釋性  # 3. 分類與詮釋
```

### 特徵
- **字元 n-gram TF-IDF**（1–2 gram，捕捉詞彙與用語偏好）
- **領域特徵**（[`features.py`](features.py)，皆為每字相對頻率）：
  - 意象類別：山 / 川 / 草木 / 鳥獸 / 天體
  - 季節與時間標記
  - 用典密度（經典徵引 + 歷史人物）
  - 詞彙豐富度（type-token ratio）

### 模型與評估
邏輯迴歸、線性 SVM、隨機森林、**MLP（PyTorch 前饋神經網路，
[`nn_model.py`](nn_model.py)）**，以及**微調 Transformer（GuwenBERT，
[`transformer_model.py`](transformer_model.py)）**（皆 `class_weight="balanced"`），
以**分層 k 折交叉驗證**因應類別不平衡，報告 **accuracy 與 macro-F1**，
並對照 most-frequent 基線。最後重新擬合線性模型，輸出各區域**最具辨別力的字元**
與**領域特徵的區域平均值**以供詮釋。

## 執行

```bash
bash run.sh                              # 完整流程（三種任務）

# 或個別執行：
python3 build_dataset.py --min-poems 5
python3 train.py --task southnorth       # 南/北 二分類（訊號最清晰）
python3 train.py --task macro            # 東南/中原/邊陲 三分類
python3 train.py --task circuit --max-regions 6   # 道 多分類
```

主要參數：`--min-poems`（詩人最少存詩數）、`--folds`（CV 折數）、
`--max-regions`（circuit 任務保留最大的 N 個道）。

### Transformer（需 GPU）

```bash
# 用具備 CUDA torch 的 conda 環境（本機為 pytorch291，RTX 3090）
conda run -n pytorch291 python transformer_model.py \
    --task southnorth --epochs 6 --batch-size 32 --max-len 256 --lr 5e-5
```

依賴：`transformers`、`opencc-python-reimplemented`（繁→簡）。
GuwenBERT 權重需可由 HuggingFace 快取取得（離線可設 `HF_HUB_OFFLINE=1`）。

## 實驗參數設定（重現用）

以下為產生下方結果所用的完整設定。

### 資料與切分
| 項目 | 設定 |
|------|------|
| 區域標籤 | CBDB 籍貫的唐代「道」（circuit）；macro/南北為其分組 |
| 詩人最少存詩數 `--min-poems` | 傳統模型 10、資料集建置 5 |
| 南北分組 | 南＝江南/淮南/劍南/嶺南/山南；北＝河北/河南/河東/關內/隴右 |
| 字元清理 | 僅保留 CJK、去標題前綴、去作者「著/撰/等」後綴 |
| 交叉驗證 | 傳統/MLP：`StratifiedKFold(5, shuffle, seed=42)`；Transformer：`GroupKFold(5)` 依詩人分組 |
| 類別不平衡 | 所有模型 `class_weight="balanced"`（NN 為加權交叉熵） |

### 特徵（傳統 / MLP）
| 項目 | 設定 |
|------|------|
| 字元 TF-IDF | `analyzer="char"`, `ngram_range=(1,2)`, `min_df=3`, `max_features=8000`, `sublinear_tf=True` |
| 領域特徵 | 意象(山/川/草木/鳥獸/天體)、季節、時間、用典(經典+人物)、TTR，皆每字頻率，`StandardScaler` |
| 合併 | TF-IDF 稀疏矩陣 ⊕ 標準化領域特徵 → 8013 維 |

### 模型超參數
| 模型 | 關鍵超參數 |
|------|-----------|
| LogisticRegression | `C=1.0`, `max_iter=2000`, balanced |
| LinearSVM | `C=0.5`, balanced |
| RandomForest | `n_estimators=400`, balanced, `seed=42` |
| MLP（[`nn_model.py`](nn_model.py)） | 隱藏層 256→64、`ReLU+BatchNorm+Dropout(0.4)`、`Adam lr=1e-3`, `weight_decay=1e-4`、`epochs=120`, `batch=32`、加權交叉熵、`seed=42` |
| Transformer（[`transformer_model.py`](transformer_model.py)） | `ethanyt/guwenbert-base`；繁→簡(opencc t2s)；片段 `chunk_chars=250`、`max_per_poet=20`、`max_len=256`；`AdamW lr=5e-5`, `weight_decay=0.01`、10% linear warmup、`grad_clip=1.0`、`epochs=6`, `batch=32`；poet-level＝片段機率平均 |

### 執行環境
| 項目 | 設定 |
|------|------|
| 傳統 / MLP | base conda（CPU 即可），sklearn 1.5、torch 2.7(CPU) |
| Transformer | conda `pytorch291`（torch 2.9.1+cu128、transformers 4.49）＋ RTX 3090 |
| 離線變數 | `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` |

## 結果摘要（5 折 CV）

傳統 / MLP 模型（5 折 CV，吃整篇拼接語料）：

| 任務 | 最佳模型 | Accuracy | macro-F1 | 基線 acc / F1 |
|------|---------|---------|---------|--------------|
| 南/北二分類 | MLP | 0.69 | 0.69 | 0.53 / 0.35 |
| 三分類（macro） | LinearSVM | 0.56 | **0.43** | 0.52 / 0.23 |
| 道（6 類） | LinearSVM | 0.34 | **0.18** | 0.39 / 0.09 |

Transformer（GuwenBERT 微調，南/北二分類，poet-level 聚合）：

| 評估協定 | Accuracy | macro-F1 |
|---------|---------|---------|
| 單次 grouped 留出（61 位未見詩人） | 0.71 | 0.71 |
| **grouped 5 折 CV（全 242 位詩人）** | **0.62 ± 0.06** | **0.59 ± 0.10** |

> ⚠️ 單次留出的 0.71 是較樂觀的一折；改用 **grouped 5 折交叉驗證**（每位詩人
> 恰好被留出一次、依詩人分組無洩漏）後,誠實估計為 **acc 0.62 / macro-F1 0.59**,
> 各折介於 0.55–0.69。
>
> **結論:在此資料規模(~242 詩人)下,微調 GuwenBERT 並未勝過簡單的
> TF-IDF + MLP(CV 0.69)。** 這是小資料常見現象——強古典基線難被大型預訓練
> 模型超越。Transformer 以 250 字片段微調、將片段機率平均回詩人層級;
> 傳統模型則吃整篇拼接語料(資訊更完整)。

#### 公平比較:階層式 / 凍結 BERT（[`transformer_hier.py`](transformer_hier.py)）

上面的微調版**資訊取用不對等**:它只看片段,傳統模型看整篇。階層式版本消除此偏差——
用**凍結 GuwenBERT** 編碼每個片段、masked-mean 池化,再**把詩人所有片段向量平均成
一個 768 維「整位詩人」向量**,於**相同的 StratifiedKFold 5 折**(每位詩人一樣本,
與古典模型完全一致)評估:

| 特徵 | 模型 | accuracy | macro-F1 |
|------|------|---------|---------|
| TF-IDF | MLP | 0.674 | 0.672 |
| **BERT(凍結,階層池化)** | **LogReg** | **0.674** | 0.672 |
| BERT + TF-IDF 混合 | LogReg | 0.653 | 0.651 |

> **給它整篇語料後,transformer 追平最佳古典模型**(handicapped 微調 0.62 → 公平 0.67)。
> **混合並未加分** → TF-IDF 與 GuwenBERT 抓到的地域訊號高度重疊,預訓練編碼器
> 在此任務上沒有提供 TF-IDF 以外的額外資訊。這是公平、誠實、可寫進論文的對照。
> (同一 pytorch291 環境一次跑出,故與上方 base 環境的 0.69 有 ~0.02 版本差異。)

執行:`conda run -n pytorch291 python transformer_hier.py --task southnorth`

### ⚠️ 關鍵踩雷：繁簡轉換
GuwenBERT 字表為**簡體**,而《全唐詩》為**繁體**——若不轉換,約半數字元會被
切成 `[UNK]`,模型完全學不起來(train accuracy 卡在 0.5)。
[`transformer_model.py`](transformer_model.py) 預設以 opencc 做繁→簡轉換後才微調,
train accuracy 隨即升到 0.75、留出表現達 0.71。可用 `--no-simplify` 關閉,
或改用 `--model bert-base-chinese`(其字表直接支援繁體)。

### 與論文一致的發現
1. **預測顯著優於隨機**：所有任務的 macro-F1 皆遠高於基線。
2. **江南遠比中心易辨識**：江南道 recall 達 0.71、F1 0.62；
   而鄰近長安／洛陽政治中心的關內道、河南道彼此混淆嚴重。
   ⚠️ 這是**江南 vs. 中心的個案對比,並非「離首都越遠越易辨識」的距離梯度**——
   見上節穩健性檢驗(去江南符號反轉、嶺南最遠卻 recall=0)。
3. **意象為最強地域標記**：南方詩人的山、川意象使用頻率高於北方
   （見 train.py 輸出的領域特徵平均值表）。

> 註：論文提及的聲調（平仄）特徵因需完整中古音韻典而未納入，
> 以詞彙豐富度作為近體／古體風格的近似；可作為後續延伸。

## 進階分析（論文延伸）

兩支獨立腳本,把「能分類」升級為更有論文價值的命題。

### 分析 #3：地理距離衰減（[`analysis_distance_decay.py`](analysis_distance_decay.py)）

檢驗**詩歌語言相似度是否隨地理距離衰減**(方言地理學核心命題)。
對每對「道」計算:語言距離(區域平均字-TF-IDF 的 1−cosine)、分類器混淆率、
地理距離(道中心 haversine),以 **Mantel 置換檢定**測相關。

| 配對範圍 | geo × 語言距離 (Pearson) | Mantel p |
|---------|------------------------|---------|
| 6 大道（每道 ≥8 詩人） | −0.02 | 0.93（無）|
| **9 道（每道 ≥5 詩人，36 配對）** | **+0.40** | **0.093**|

→ 納入更多道後出現**距離衰減趨勢**(越遠語言越不同),Mantel p≈0.09 達顯著邊緣。
注意圖上 `analysis_distance_decay.py`/`make_figures.py` 也會印 naive Pearson p=0.016;
**正確的是 Mantel p≈0.09**——naive p 把 36 個 pairwise 當獨立樣本,低估了不確定性。

### 穩健性檢驗（[`analysis_distance_decay_robustness.py`](analysis_distance_decay_robustness.py)）

審稿最會戳「小樣本相關是不是被單一離群點(江南道)帶起來」。逐一剔除每個道重跑:

| 檢驗 | 結果 |
|------|------|
| 距離衰減 leave-one-out（9 道） | r 全程為正 **+0.24 ~ +0.60**,無任何道翻轉符號 |
| **去掉江南道** | r **+0.40 → +0.60**、Mantel p **0.09 → 0.02**(**變強**,非離群假象)|
| periphery「離長安越遠越易辨識」 | 全樣本 r≈0.19–0.46 **不顯著**(p>0.3)|
| **periphery 去掉江南道** | r **翻負** −0.40(Spearman −0.51);最遠的嶺南道 recall=0 |

→ **距離衰減(r=0.40)是穩健的**:去掉江南反而更顯著,通過 leave-one-out。
但**periphery「越遠越易辨識」並不成立**——整條趨勢由江南單點撐起、本就不顯著、
去江南即反轉。故論文已將其改寫為**「江南 vs. 中心」的混淆結構**,不作距離梯度解讀。

### 分析 #1：混淆變項控制（[`analysis_confound.py`](analysis_confound.py)）

檢驗南/北訊號是否只是其他變項的假象。(刻意不用 `背景`/性別當控制:
CBDB 背景標籤雜訊大——白居易被標 monk;性別 239:3 過度傾斜。)

**(A) 語料長度——非假象。** 南/北中位字數幾乎相同(2419 / 2350);把每位詩人
截到共同 993 字後,acc 0.603→**0.591**,幾乎不變 → 模型不是在讀「誰寫得多」。

**(B) 時代——部分混淆,但更有洞見。** 區域×時代顯著關聯(χ²=11.9, **p=0.008**;
初唐偏北 22:7、晚唐偏南 8:17,反映文學重心南移)。逐期分類:

| 時代 | n | acc | macro-F1 |
|------|---|-----|---------|
| 初唐 | 29 | 0.41（小樣本、雜訊） | 0.34 |
| 盛唐 | 28 | **0.50（等於亂猜）** | 0.49 |
| 中唐 | 43 | 0.54 | 0.51 |
| 晚唐 | 25 | **0.68** | 0.63 |

→ **盛唐南北幾乎不可分、晚唐明顯可分**:正是論文「帝國鼎盛期菁英文化同質化、
晚唐地方化」命題的量化證據,並打開時間維度(注:逐期樣本小,趨勢可信、絕對值待擴充)。

### 分析 #6：把「誤分類」讀成文學史（[`analysis_misclassification.py`](analysis_misclassification.py)）

模型自信地分錯的詩人不只是錯誤——往往反映其**實際生活/任官/被貶之地**或
**時代主流文風**,而非籍貫。取南/北 OOF 預測機率,排序高信心誤判,並對照生平。

**直接的「第二居地」假說只解釋少數(96 誤判中僅 4 人有多地紀錄)**,因多數詩人
只記一地。但**誤判方向依時代呈現強烈規律**:

| 時代 | 南→北(被讀成北) | 北→南 |
|------|:---:|:---:|
| **初唐** | **7** | **0** |
| 盛唐 | 5 | 10 |
| 中唐 | 5 | 9 |
| 晚唐 | 5 | 3 |

→ **初唐誤判全是「南方詩人被讀成北方」(7:0)**:初唐文壇中心在北、宮廷文風主導,
南方詩人(虞世南 558-638、褚亮、賀知章、馬懷素)以宮廷雅言寫作,故詩風「北化」。
模型的錯誤正好**編碼了宮廷對地方文風的同質化拉力**,與分析 #1(盛唐同質化)互相印證。
這就是論文「人機協作——模型生成假設、供細讀與文學史檢驗」的具體示範。
完整誤判表輸出至 `misclassified_poets.csv`。

執行:
```bash
python3 analysis_distance_decay.py --min-poets 5   # 距離衰減 + 圖 distance_decay.png
python3 analysis_distance_decay_robustness.py      # leave-one-out / naive vs Mantel 穩健性
python3 analysis_confound.py                        # 長度 / 時代 控制
python3 analysis_misclassification.py --top 20      # 誤分類傳記學 + CSV
```

## 圖表（figures/）

`make_figures.py` 一次重跑並輸出全部 11 張圖。支援中英雙語標籤
（自動使用系統 CJK 字型 WenQuanYi Zen Hei）：

```bash
python3 make_figures.py            # 中文標籤 -> figures/
python3 make_figures.py --lang en  # 英文標籤 -> figures_en/（投稿英文場合）
```

英文版:標題/座標/圖例皆英文,道名以拼音(Jiangnan、Hebei…)、時代為
Early/High/Mid/Late Tang;fig08 的字元因屬資料本身仍保留漢字。

| 檔案 | 內容 |
|------|------|
| `fig01_model_comparison.png` | 南/北各模型 acc 與 macro-F1（5 折 CV）|
| `fig02_confusion.png` | 道級混淆矩陣 + 各道辨識率 |
| `fig03_distance_decay.png` | 地理距離 × 語言距離（距離衰減）|
| `fig04_era_evolution.png` | 逐期南/北可分性（盛唐同質化→晚唐地方化）|
| `fig05_misclass_by_era.png` | 誤分類方向 × 時代（初唐全為 南→北）|
| `fig06_region_distribution.png` | 各道詩人數（紅南/藍北）|
| `fig07_domain_radar.png` | 意象特徵南北雷達圖 |
| `fig08_discriminative_chars.png` | 南/北最具辨別力字元 |
| `fig09_transformer.png` | Transformer 協定 / 訓練曲線 / 各折 |
| `fig10_length_control.png` | 語料長度控制 |
| `fig11_periphery.png` | 離長安距離 × 辨識率 |
| `fig12_hier_comparison.png` | 公平比較:階層式 BERT vs TF-IDF（同一 5 折）|

> 註:`fig09` 的訓練曲線讀取 `tf_curve.log`(由 transformer 單次訓練產生);
> 各折與協定數字取自已記錄的 grouped 5 折結果。時代分期全專案統一為
> 初唐≤712 / 盛唐 713–765 / 中唐 766–835 / 晚唐 836–907（五代 >907 不計）。

## 實踐結論

**1. 地域訊號確實存在，但屬中等強度。**
南/北二分類最佳約 acc 0.69（MLP，5 折 CV），顯著高於基線 0.53；
道級 10 類較難（macro-F1 0.18，仍為基線兩倍）。任務難度：**南北 > macro 三類 > 道十類**。

**2. 簡單模型在此資料規模最划算;公平的 transformer 只能追平、無法超越。**
TF-IDF(字 1–2 gram) + MLP/線性模型，吃**整篇拼接語料**，是 CP 值最高的組合。
**微調**版片段化、grouped CV 僅 0.62(資訊取用不對等);改成**階層式凍結 BERT**
(整篇詩人向量、同一 5 折)後**追平最佳古典模型 0.67，但混合 TF-IDF 不再加分**
——代表預訓練編碼器沒提供 TF-IDF 以外的地域訊號。
**建議:主力用 TF-IDF + 線性/MLP;transformer 用「階層式」版本作公平對照，
不要只用片段微調版下結論。**

**3. 評估協定決定數字可信度。**
- 必須**依詩人分組切分**（同一詩人不可橫跨 train/test），否則洩漏。
- **單次留出會高估**（Transformer 單折 0.71 vs. 5 折 0.62±0.06）；務必用 k 折報 mean±std。
- 類別嚴重不平衡，**以 macro-F1 為主指標**、對照 most-frequent 基線，勿只看 accuracy。

**4. 繁簡不一致是最大隱形地雷。**
GuwenBERT 字表為簡體、《全唐詩》為繁體，不轉換則半數字元變 `[UNK]`，
train accuracy 永遠卡 0.5。**用古典中文預訓練模型前，務必先檢查 tokenizer 的
UNK 率**（本案以 opencc t2s 修正後 train acc 0.5→0.75）。

**5. 資料比對細節影響可用樣本數。**
作者名「著/撰/等」後綴、逐句重複的標題前綴若不清理，
可用詩人數會從 357 暴跌到 64。**先驗證 join 命中率與大詩人詩數**（如白居易應 ≈2600 首）。

**6. 與論文一致的核心發現成立**：江南遠比政治中心（關內/河南）易辨識（屬江南個案、
非距離梯度,見穩健性檢驗），意象為最強地域標記——詳見上節。

**7. 訊號通過穩健性檢驗,且時代是關鍵變項。**
南/北訊號**非語料長度假象**(截等長後幾乎不變);與時代**部分混淆**但更有意義——
**盛唐近乎不可分(同質化)、晚唐明顯可分(地方化)**。距離衰減在納入 9 道後浮現
(r=0.40, p≈0.09)。**寫論文時務必加時代控制,並把時代當成發現而非雜訊。**

### 後續可嘗試
- Transformer 餵更長片段（`--max-len 512 --chunk-chars 480`）或階層式整篇建模。
- 納入聲調（平仄）特徵（需中古音韻典）。
- 道級任務改用時代分層（初/盛/晚唐）檢視地域獨特性的時間演變。
