# Tang Poets' Origins — 10 分鐘版（v2）逐頁講稿
**Predicting Poets' Origins from Verse** · arXiv:2606.24093 · Chen & Liu

- 對應檔案：`Tang_Poets_Origins_slides_10min_v2.pptx`（12 頁）
- 目標時長：約 10 分鐘（每頁 40–55 秒）＋ Q&A
- 每段英文講稿下方附中文翻譯（斜體），僅供對照與排練，上台唸英文即可。
- 此版已移除賀知章敘事線；新增任務分類定義頁（p.4）。
- 各頁講稿與 pptx 內嵌的 speaker notes 一致（此檔為完整版）。

---

## p.1 — Title（封面，深色）

> Good morning, everyone. Today I'd like to ask a very old question with a very new instrument: can you tell where a poet came from — just by reading their poems? We take the Complete Tang Poems, all forty-nine thousand of them, and treat this as a prediction problem. I'm Chi-Sheng Chen, and this is joint work with Hung-Yun Liu.

*中譯：大家早安。今天我想用一個很新的工具，來問一個很古老的問題：只靠讀詩，你能不能看出一位詩人是哪裡人？我們拿整部《全唐詩》——四萬九千首——把這件事當成一個預測問題來做。我是陳其聖，這是與劉弘雲的合作研究。*

**備註**：~30 秒。右側直排「文如其地」是全場母題，結論頁會回收，開場不必解釋。

---

## p.2 — The Question + RQs

> Literary historians have long debated regional schools — 地域流派 — in Tang poetry. Yet whether geographic origin actually shows up as *quantifiable* patterns in poetic language has resisted systematic study. We treat it as a measurement problem: read forty-nine thousand poems, and predict each poet's home circuit from text alone.
>
> Three questions. RQ1, Prediction: can a model recover a poet's circuit of origin from their collected work alone? RQ2, Signal: if it can, which features carry it — lexical choice, imagery, tonal patterns, themes? RQ3, Persistence: does the fingerprint hold steady across the dynasty's poetic eras, or move with history?
>
> One design principle throughout: interpretability — features a literary historian can read, and contest.

*中譯：文學史家長期爭論唐詩的地域流派——但「地理出身是否在詩歌語言中留下可量化的模式」一直缺乏系統性研究。我們把它當成一個測量問題：讀完四萬九千首詩，只靠文本預測每位詩人的家鄉道。*

*三個問題。RQ1「預測」：模型能否只靠一位詩人的全部作品，還原他的出身道？RQ2「訊號」：如果可以，是哪些特徵在承載——用字、意象、平仄、主題？RQ3「持續性」：這個指紋在各詩歌分期中是穩定的，還是隨歷史變動？*

*貫穿全程的設計原則：可解釋性——文學史家讀得懂、也能反駁的特徵。*

**備註**：~55 秒。「measurement problem」與「interpretability」是全場定位，之後 p.5、p.11 都會呼應。

---

## p.3 — Data

> Our data is the Complete Tang Poems: nine hundred volumes, aggregated end-to-end into roughly forty-nine thousand poems at the poet level. Texts come from the Chinese Text Project; birthplaces are linked through the China Biographical Database, CBDB. Keeping poets with at least five surviving poems and unambiguous attribution leaves 357 poets across the ten early-Tang circuits, 242 of them in the South/North subset.
>
> One thing to flag now, because it shapes everything downstream: the classes are heavily imbalanced — Jiangnan alone has 126 poets, Longyou six. So: balanced class weights throughout, and macro-F1 reported alongside accuracy.

*中譯：資料是《全唐詩》：九百卷，端到端整併成約四萬九千首、以詩人為單位的語料。文本來自中國哲學書電子化計劃；出生地透過 CBDB 連結。留下存詩至少五首、歸屬明確的詩人後，得到 357 位、分布於唐初十道，其中 242 位屬南／北子集。*

*有件事要先講，因為它影響後面所有環節：類別嚴重不平衡——江南一道就有 126 位，隴右只有 6 位。所以全程使用平衡類別權重，並同時報告 macro-F1。*

**備註**：~50 秒。主動講不平衡，p.5 的 fair test 和 p.6 的 macro-F1 才有伏筆。

---

## p.4 — Three Tasks, Three Grains（新增頁）

> We slice geography at three grains, and I want to be precise about what the classes are. First, South versus North — the headline task, 242 poets: the southern five circuits — Jiangnan, Huainan, Jiannan, Lingnan, Shannan — against the northern five — Hebei, Henan, Hedong, Guannei, Longyou. This is the axis the literary-historical debate cares about.
>
> Second, three macro-regions — a different axis, core versus periphery: the Southeast, Jiangnan plus Huainan; the Central Plains, the four northern heartland circuits; and the Frontier — Jiannan, Lingnan, Shannan, Longyou.
>
> Third, the full ten-circuit map — hardest, with classes as small as six poets.
>
> Note these are two different geographic hypotheses, not one nested hierarchy: Shannan, Jiannan and Lingnan are "south" on the South/North axis, but "frontier" on the core–periphery axis.

*中譯：我們把地理切成三種粒度，這裡把類別講清楚。第一，南對北——主打任務、242 位詩人：南方五道（江南、淮南、劍南、嶺南、山南）對北方五道（河北、河南、河東、關內、隴右）。這是文學史論爭真正在意的軸線。*

*第二，三大區——另一條軸線：核心對邊陲。東南＝江南＋淮南；中原＝北方四個核心道；邊陲＝劍南、嶺南、山南、隴右。*

*第三，完整十道地圖——最難，最小的類別只有六位詩人。*

*注意：這是兩種不同的地理假設，不是一個巢狀層級——山南、劍南、嶺南在南北軸上是「南」，在核心–邊陲軸上是「邊陲」。*

**備註**：~55 秒。最後一句是本頁重點，也是 Q&A 高頻題（「三大區為什麼不是南北再細分？」）的預防針。

---

## p.5 — Method

> Our workhorse representation is character n-gram TF-IDF. A five-character line — "empty mountain, after new rain" — becomes five unigrams and four bigrams; one to two grams, at most eight thousand features. No word segmentation, no parsing, no modern linguistic assumptions imposed on eighth-century verse — characters are the native unit. On top, features a historian can read directly: imagery classes, seasonal markers, allusion density, lexical richness, and tonal patterns — approximated only.
>
> The fair test: five models — logistic regression, linear SVM, random forest, a small MLP, and GuwenBERT, a transformer pre-trained on classical Chinese. Stratified five-fold cross-validation, so every poet is held out exactly once; balanced class weights; and the baseline to beat is "always guess the biggest region" — 0.53 on South/North.

*中譯：主力表示法是字元 n-gram TF-IDF。一句五言「空山新雨後」變成五個單字元、四個相鄰字對；一到二元、最多八千個特徵。不斷詞、不剖析、不把現代語言學假設強加在八世紀的詩上——「字」就是原生單位。之上再加史家能直接閱讀的特徵：意象類別、季節標記、用典密度、詞彙豐富度、平仄（僅能近似）。*

*公平測驗：五個模型——邏輯迴歸、線性 SVM、隨機森林、小型 MLP、以及在古文上預訓練的 GuwenBERT。分層五折交叉驗證，每位詩人恰好留出一次；平衡類別權重；要打敗的基準線是「永遠猜最大區」——南北任務上 0.53。*

**備註**：~50 秒。

---

## p.6 — RQ1: Geography Is Legible

> So — can it be done? Yes. From the 0.53 most-frequent baseline: logistic regression 0.60, linear SVM 0.64, random forest 0.67, and the MLP 0.69 accuracy on South versus North. More importantly, macro-F1 rises from 0.35 to 0.69 — so the gain is not an artefact of class imbalance.
>
> A poet's origin is readable, well above chance, from text alone.

*中譯：所以——做得到嗎？做得到。從 0.53 的最頻繁類基準線出發：邏輯迴歸 0.60、線性 SVM 0.64、隨機森林 0.67、MLP 在南北任務達 0.69。更重要的是 macro-F1 從 0.35 升到 0.69——增益不是類別不平衡的假象。*

*詩人的出身，光靠文本就能讀出來，遠高於隨機。*

**備註**：~45 秒。五根柱由左到右＝Baseline、LogReg、SVM、RF、MLP。

---

## p.7 — The Signal Survives at Every Grain

> Does the signal survive when the map gets harder? Coarse maps are sharper — but even the hardest map is readable. South/North: macro-F1 0.69. Three macro-regions: 0.43. The full ten-circuit task: 0.18. Each of those is roughly twice its own most-frequent baseline.
>
> Ten-way prediction with six-poet classes is a brutal task — doubling baseline there is the real surprise of this slide.

*中譯：把地圖切得更難，訊號還在嗎？粗的地圖更清晰——但連最難的地圖也讀得出來。南北 0.69、三大區 0.43、完整十道 0.18——每一個都約是自身基準線的兩倍。*

*有六人小類的十分類是很殘酷的任務——在那裡還能翻倍基準線，才是本頁真正的驚喜。*

**備註**：~40 秒。柱狀圖順序（細→粗）與右欄列表（粗→細）相反，口頭帶一句「from hardest to easiest」即可。

---

## p.8 — The Centre Blurs; Jiangnan Stands Apart

> Where is the signal on the map? Two facts. First: near the court, one idiom. The circuits around Chang'an and Luoyang are heavily confused with one another — the shared court language erases local difference. Second: far from it, a voice of one's own. Jiangnan, the empire's literary south, is by far the most separable region — recall 0.71 on the ten-way task.
>
> And here I want to be careful: this is *not* a distance law. Across all six circuits the fit is non-significant — r 0.45, p 0.37 — and if you drop Jiangnan, the slope actually reverses. Two facts, not one gradient: the capitals share a single court idiom, and Jiangnan alone keeps a voice of its own.

*中譯：訊號在地圖上的哪裡？兩個事實。第一：靠近朝廷，只有一種語言——長安、洛陽周邊的道彼此嚴重混淆，共享的宮廷語言抹平了地方差異。第二：遠離朝廷，自成一格——江南是目前最可分辨的區域，十分類 recall 0.71。*

*這裡要小心地說：這不是一條距離定律。六道整體擬合不顯著（r 0.45、p 0.37），拿掉江南斜率還會反轉。兩個事實，不是一條梯度：京畿共享同一套宮廷語言，只有江南保有自己的聲音。*

**備註**：~55 秒。「not a distance law」放慢講。被問「淮南也遠為何 recall 0？」——答案就是本頁論點：不是距離效應，淮南 22 人、夾在南北過渡帶，被鄰近大類吸走。

---

## p.9 — RQ2: Imagery Carries the Region

> RQ2 — which features carry the signal? The South writes landscape: mountain-and-water imagery markedly more than the north, plus Buddhist and recluse vocabulary — temples, retreat, withdrawal. The North writes the court: palace diction, the built world of the capitals, and gongti motifs — courtly "boudoir" poetry.
>
> Tonal patterns, by contrast, carry comparatively weak geographic signal. The regional fingerprint lives in what poets *see*, not in how their verses *scan*.

*中譯：RQ2——哪些特徵承載訊號？南方寫山水：山水意象明顯多於北方，加上佛教與隱逸詞彙——寺廟、退隱、出世。北方寫宮廷：宮殿語彙、京城的人造世界、宮體題材。*

*相較之下，平仄的地理訊號很弱。地域指紋活在詩人「看見什麼」，不在詩句「怎麼合律」。*

**備註**：~45 秒。最後一句是金句，停一拍。

---

## p.10 — RQ3: The Fingerprint Waxes and Wanes

> RQ3 — persistence. The fingerprint moves with the dynasty. Early Tang: 0.41 on twenty-nine poets — the within-era split is unreadable, because southern poets wrote the northern court idiom; with the full-corpus model, all seven early-Tang errors read a southerner as northern. High Tang, the empire's height: 0.50 — exactly at chance; maximum political integration, maximum stylistic integration. Mid Tang, after the An Lushan rebellion: 0.53 — regional voices begin to return. Late Tang, as central authority weakens: 0.68 — the strongest separation in the whole dynasty.
>
> Regional distinctiveness is not constant. It waxes and wanes with the political integration of the dynasty — now with numbers attached.

*中譯：RQ3——持續性。指紋隨王朝盛衰而動。初唐：29 人上只有 0.41——期內南北無法分辨，因為南方詩人寫的是北方宮廷語；用全語料模型看，初唐七個誤判全部把南方人讀成北方人。盛唐，帝國頂峰：0.50——恰好等於隨機；政治整合最大化，風格整合也最大化。中唐，安史之亂後：0.53——地方聲音開始回來。晚唐，中央權威衰落：0.68——全朝代最強的分離度。*

*地域獨特性不是恆定的。它隨王朝政治整合而消長——現在有數字佐證。*

**備註**：~55 秒。0.41→0.50→0.53→0.68 單調遞增是賣點。注意兩個口徑：0.41 是期內 CV；「7/7 S→N」來自全語料模型誤判按期分組——被追問要分得清。各期 n 僅 25–43，可主動承認樣本小。

---

## p.11 — Transformers + Caveats

> A natural challenge: wouldn't a transformer see more than character counts? Three stress tests. Naive fine-tuning of GuwenBERT, per fragment: 0.62 — below the n-gram models. A hierarchical frozen encoder, pooling fragments over a poet's whole corpus: 0.674 — ties the best classical models. A hybrid of BERT embeddings plus TF-IDF: adds nothing. Character n-grams already capture the available regional signal — interpretability costs nothing.
>
> And the caveats, in one breath: small samples — 357 poets, 242 for South/North, era subsets of 25 to 43; labels inherit the uncertainties of the anthology and CBDB; tone is approximated; and the distance-decay geography is suggestive, not decisive — r 0.40, Mantel p about 0.09. All four point the same way: more data would sharpen the picture, not overturn it.

*中譯：很自然的質疑：transformer 不會看得比數字元更多嗎？三個壓力測試。GuwenBERT 逐片段樸素微調：0.62——比 n-gram 還低。階層式凍結編碼器、在詩人整個語料庫上池化：0.674——追平最佳古典模型。BERT 嵌入＋TF-IDF 混合：毫無增益。字元 n-gram 已經抓住可得的地域訊號——可解釋性不用付出代價。*

*Caveats 一口氣講：樣本小——357 位、南北 242 位、各期僅 25–43；標籤繼承總集與 CBDB 的不確定性；平仄僅是近似；距離衰減是暗示性而非決定性（r 0.40、Mantel p≈0.09）。四者指向同一方向：更多資料只會讓圖像更清晰，不會推翻它。*

**備註**：~55 秒。0.674 出自同協定的一致 GPU 實驗；被問 Mantel 時說明「成對距離不獨立，故不用 naive p」。

---

## p.12 — Conclusion（深色）

> To conclude: a Tang poet's origin leaves a computationally detectable trace in their verse. It is carried chiefly by imagery and lexical choice — mountains and waters in the south, palace and gongti diction in the north. It is not a simple distance law — the capitals blur into one court idiom, and Jiangnan alone keeps a voice of its own. And it is modulated by history — at chance amid High-Tang integration, strongest as Late-Tang authority wanes.
>
> Next, we want to build stylistic similarity networks — does textual proximity track geography, or transcend it through literary influence?
>
> 文如其地 — the text is like its land. Thank you.

*中譯：總結：唐代詩人的出身在詩中留下計算上可偵測的痕跡。它主要由意象和用字承載——南方的山與水，北方的宮殿與宮體語彙。它不是簡單的距離定律——京畿融成同一套宮廷語言，只有江南自成一格。而且它被歷史調節——盛唐整合時降到隨機，晚唐權威衰落時最強。*

*接下來，我們想建立風格相似度網絡——文本上的親近是跟著地理走，還是透過文學影響超越地理？*

*文如其地。謝謝大家。*

**備註**：~40 秒。「文如其地」呼應封面直排字，是本版的收束母題。

---

# Q&A 準備（常見追問）

1. **淮南 recall = 0，但它離長安很遠？**
   正因如此我們說「not a distance law」（p.8）。淮南只有 22 位詩人，地理上夾在南北過渡帶，樣本被江南與河南兩個大類吸走。

2. **三大區為什麼不是南北任務的細分？**
   它們是兩種不同的地理假設（p.4）：南北測的是南北軸；三大區測的是核心–邊陲軸。山南、劍南、嶺南在前者是「南」、在後者是「邊陲」。0.69 和 0.43 不是同一棵分類樹的兩層。

3. **p.8 的 r=0.45 / −0.89 和 p.11 的 r=0.40 是什麼關係？**
   不同的量：前者是「各道 recall vs. 離長安距離」（6 個點）；後者是「道與道的風格距離 vs. 地理距離」成對矩陣（36 對，Mantel 檢定）。前者不顯著且由江南主導；後者是弱而一致的 distance decay。

4. **初唐 0.41 低於 chance，為什麼？和 7/7 S→N 矛盾嗎？**
   0.41 是期內 5-fold CV（n=29、南方僅 7 人，balanced weights 下模型過度補償）；7/7 S→N 來自全語料模型的誤判按期分組。口徑不同、結論一致：初唐南方詩人寫北方宮廷語。

5. **為什麼不用斷詞／現代 NLP pipeline？**
   古典漢語無公認斷詞標準；字元 n-gram 不引入現代語言學假設，且 transformer 對照（p.11）顯示可得訊號已被 n-gram 捕捉。

6. **「circuit／道」與「家鄉」的關係？**
   Circuit 是漢學標準譯法（Hucker《中國官名辭典》；CBDB 同用）。我們以「出生地所在道」作為家鄉的操作型定義——粗粒度、含籍貫／出生地混雜的噪音，但這類標籤噪音只會稀釋訊號、使估計偏保守，不會偽造訊號。

7. **生卒年缺失怎麼辦？**
   分期分析僅用有生卒年的 125/242 位詩人；屬於「small samples」caveat 的一部分。
