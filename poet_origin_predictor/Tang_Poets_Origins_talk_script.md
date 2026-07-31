# Tang Poets' Origins — 逐頁講稿
**Predicting Poets' Origins from Verse** · arXiv:2606.24093 · Chen & Liu

- 對應檔案：`Tang_Poets_Origins_slides (1).pdf`（23 實體頁，含 3 頁全幅地圖）
- 目標時長：約 18 分鐘（每頁 40–70 秒）＋ Q&A
- 頁碼格式：`實體頁 / 投影片頁碼`
- 每段英文講稿下方附中文翻譯（斜體），僅供對照與排練，上台唸英文即可。

---

## p.1 — Title（封面）

> Good morning, everyone. Today I'd like to ask a very old question with a very new instrument: can you tell where a poet came from — just by reading their poems? We take the Complete Tang Poems, all forty-nine thousand of them, and treat this as a prediction problem. I'm Chi-Sheng Chen, and this is joint work with Hung-Yun Liu.

*中譯：大家早安。今天我想用一個很新的工具，來問一個很古老的問題：只靠讀詩，你能不能看出一位詩人是哪裡人？我們拿整部《全唐詩》——四萬九千首——把這件事當成一個預測問題來做。我是陳其聖，這是與劉弘雲的合作研究。*

**備註**：開場不用急著解釋右側的詩句——第 2 頁會正式引出。停留 ~30 秒。

---

## p.2 — The Question (2/20)

> Thirteen centuries ago, the poet He Zhizhang went home after a lifetime at court, and wrote: "I left home young and return an old man; my native accent is unchanged, though my temple-hair has thinned." An accent survives a lifetime away from home. Our question is: does *home* also survive on the page?
>
> Literary historians have long debated regional schools in Tang poetry — but whether geographic origin shows up as *quantifiable* patterns in poetic language has resisted systematic study. We treat it as a measurement problem: read forty-nine thousand poems, and try to predict each poet's home circuit from text alone.
>
> And please keep He Zhizhang in mind — he will return near the end of this talk.

*中譯：一千三百年前，詩人賀知章在朝廷度過一生後返鄉，寫下「少小離家老大回，鄉音無改鬢毛衰」。口音可以撐過離家的一輩子——那麼我們的問題是：「家鄉」是否也留在了紙頁上？*

*文學史家長期爭論唐詩的地域流派，但「地理出身是否在詩歌語言中留下可量化的模式」一直缺乏系統性研究。我們把它當成一個測量問題：讀完四萬九千首詩，只靠文本預測每位詩人的家鄉道。*

*另外，請記住賀知章——他會在演講接近尾聲時回來。*

**備註**：這頁是整場的敘事鉤子，「keep him in mind」一定要講，第 16 頁回收。

---

## p.3 — Three Research Questions (3/20)

> We ask three questions. RQ1, Prediction: can a model recover a poet's circuit of origin from their collected work alone? RQ2, Signal: if it can, *which* features carry that signal — lexical choice, imagery, tonal patterns, themes? And RQ3, Persistence: does the regional fingerprint hold steady across the dynasty's poetic eras, or does it change with history?
>
> One design principle runs through everything: interpretability. Every modelling choice favours features a literary historian can read — and contest.

*中譯：我們問三個問題。RQ1「預測」：模型能否只靠一位詩人的全部作品，還原他的出身道？RQ2「訊號」：如果可以，是哪些特徵在承載訊號——用字、意象、平仄、主題？RQ3「持續性」：這個地域指紋在整個朝代的各個詩歌分期中是穩定的，還是隨歷史變動？*

*貫穿一切的設計原則是可解釋性：所有建模選擇都偏向文學史家讀得懂、也能反駁的特徵。*

**備註**：最後一句是全場的定位宣言，之後第 8、17、18 頁都會呼應。

---

## p.4 — The Corpus (4/20)

> Our data is the Complete Tang Poems — the Qing-era anthology: nine hundred volumes, which we aggregate end-to-end into roughly forty-nine thousand poems, from a full anthology of over two thousand two hundred poets. Texts come from the Chinese Text Project, the standard open digital edition.
>
> As a pipeline sanity check: for Bai Juyi, the best-attested poet, we recover about twenty-six hundred poems end-to-end — so the parser holds up at scale.

*中譯：我們的資料是《全唐詩》——清代編纂的總集：九百卷，端到端整併成約四萬九千首詩，全集收錄超過兩千兩百位詩人。文本來自中國哲學書電子化計劃（ctext.org），是標準的開放數位版本。*

*管線的健全性檢查：以存詩最多的白居易為例，我們端到端還原約兩千六百首——解析器在這個規模下是撐得住的。*

**備註**：若被問「為何不是全部 5 萬多首」——回答：以能穩定切分、去重後的詩為準。

---

## p.5 — Grounding Poets in Circuits (5/20)

> To get labels, we do four things. Aggregate: group the poems into one corpus per poet. Locate: link each poet's birthplace through the China Biographical Database, CBDB. Filter: keep poets with at least five surviving poems and unambiguous attribution. Label: that leaves 357 poets across the ten early-Tang administrative circuits — the *dao* — of which 242 fall in the South/North subset.
>
> One thing to flag now, because it shapes everything downstream: the classes are heavily imbalanced. Jiangnan alone has 126 poets; Longyou has six.

*中譯：要取得標籤，我們做四件事。整併：把詩按詩人合成一人一個語料庫。定位：透過中國歷代人物傳記資料庫 CBDB 連結每位詩人的出生地。過濾：只留存詩至少五首、歸屬明確的詩人。標記：最後得到 357 位詩人，分布在唐初十個行政「道」上，其中 242 位落在南／北子集。*

*有一件事要現在先講，因為它影響後面所有環節：類別嚴重不平衡——光江南道就有 126 位詩人，隴右道只有 6 位。*

**備註**：主動講不平衡，第 9/20 的 balanced weights 與 macro-F1 才有伏筆。

---

## p.6 — 歷史地圖（全幅，無頁碼）

> Here is where those ten circuits actually sit. The yellow arrow is Chang'an, the capital, in Guannei circuit. Notice the geography: the two capital circuits cluster in the north-centre; Jiangnan stretches across the lower Yangtze in the south-east. Keep this map in your head — the results are, in a real sense, this map talking back.

*中譯：這就是十個道實際的位置。黃色箭頭是首都長安，在關內道。注意這個地理格局：兩個京畿道集中在中北部；江南道橫跨東南的長江下游。請把這張地圖記在腦中——後面的結果，某種意義上就是這張地圖在回話。*

**備註**：講 ~30 秒即可，重點只有「長安在哪、江南在哪」。

---

## p.7 — Bubble chart（全幅，無頁碼）※預定刪除

> *(此頁預定刪除。若仍在，快速帶過：)* This is the raw distribution of poets and poems by circuit from an earlier exploratory pass — the point is simply that both poets and poems concentrate heavily in Jiangnan and the capital circuits.

*中譯：這是早期探索階段各道詩人與詩作的原始分布——重點只有一個：詩人和詩作都高度集中在江南與京畿諸道。*

**備註**：此頁統計框的 1077 poets / 32,326 poems 與正文 357 / 49,000 口徑不同（前者是探索期、未過濾的另一套統計）。**強烈建議刪除**；若保留，被問到務必說明口徑差異，不要含糊。

---

## p.8 — 唐朝疆域圖（全幅，無頁碼）

> And zooming out: the Tang empire at its height. The circuits we can label with poets are the agricultural, densely settled core — the protectorates beyond were never going to give us poet-level data. So our map of "Tang poetry" is really a map of the empire's literate heartland.

*中譯：拉遠來看：這是全盛時期的唐帝國。我們能標上詩人的道，是農業發達、人口稠密的核心區——外圍的都護府本來就不會有詩人層級的資料。所以我們的「唐詩地圖」，其實是帝國識字核心區的地圖。*

**備註**：一句話帶過即可；也可視時間直接跳過此頁。

---

## p.9 — Three Tasks (6/20)

> We slice geography at three grains. Ten circuits: the full administrative map — hardest, many small classes. Three macro-regions: an intermediate grain. And South versus North: 242 poets — the headline task, because South-versus-North is the axis the literary-historical debate actually cares about.
>
> Given the imbalance I flagged, we use balanced class weights throughout, and report macro-F1 alongside accuracy.

*中譯：我們把地理切成三種粒度。十道：完整的行政地圖——最難，小類別很多。三大區：中間粒度。南對北：242 位詩人——這是主打任務，因為南北之分正是文學史論爭真正在意的軸線。*

*鑑於剛才提到的不平衡，我們全程使用平衡類別權重，並在 accuracy 之外同時報告 macro-F1。*

---

## p.10 — Features I: Character n-grams (7/20)

> Our workhorse representation is character n-gram TF-IDF. Take a five-character line — "empty mountain, after new rain" — and it becomes five unigrams and four bigrams. We count every character and every adjacent pair a poet uses, weight up what's distinctive to that poet, weight down what all Tang verse shares. One to two grams, at most eight thousand features, sublinear term frequency.
>
> Why does this suit classical Chinese? No word segmentation, no parsing, no modern linguistic assumptions imposed on eighth-century verse. Characters are the native unit.

*中譯：我們的主力表示法是字元 n-gram TF-IDF。拿一句五言詩「空山新雨後」來說，它會變成五個單字元和四個相鄰字對。我們統計詩人用的每個字、每個相鄰字對：對這位詩人獨特的加權放大，全體唐詩共有的加權壓低。一到二元、最多八千個特徵、次線性詞頻。*

*為什麼這適合古典漢語？不需要斷詞、不需要句法剖析、不把現代語言學假設強加在八世紀的詩上——「字」本來就是它的原生單位。*

---

## p.11 — Features II: Readable Features (8/20)

> On top of n-grams, we add features a literary historian can read directly: imagery classes — mountain, water, plant, fauna, celestial; seasonal markers; allusion density; lexical richness; and tonal patterns — approximated only, since a complete Middle-Chinese rime dictionary is lacking.
>
> Again — interpretability is the point. Each feature maps to a claim a Tang scholar could contest with close reading.

*中譯：在 n-gram 之上，我們加入文學史家可以直接閱讀的特徵：意象類別——山、水、草木、鳥獸、天體；季節標記；用典密度；詞彙豐富度；以及平仄——只能近似，因為完整的中古音韻書資料是缺乏的。*

*再強調一次——可解釋性就是重點。每個特徵都對應一個唐代文學學者能用細讀去反駁的主張。*

---

## p.12 — Models & Protocol (9/20)

> Five readers, one fair test. Logistic regression — fully inspectable. Linear SVM. Random forest. A small MLP. And GuwenBERT, a transformer pre-trained on classical Chinese.
>
> The fair test: stratified five-fold cross-validation, so every poet is a held-out test case exactly once. Balanced class weights, so small circuits aren't drowned out by Jiangnan. Accuracy plus macro-F1. And the baseline to beat is "always guess the biggest region" — 0.53 on South/North.

*中譯：五個「讀者」，一場公平測驗。邏輯迴歸——完全可檢視。線性 SVM。隨機森林。一個小型 MLP。以及 GuwenBERT——在古文上預訓練的 transformer。*

*公平測驗是：分層五折交叉驗證，每位詩人恰好當一次留出的測試案例；平衡類別權重，讓小的道不被江南淹沒；同時報告 accuracy 和 macro-F1；要打敗的基準線是「永遠猜最大的區」——在南北任務上是 0.53。*

---

## p.13 — Result RQ1 (10/20)

> So — can it be done? Yes. From the 0.53 most-frequent baseline, logistic regression reaches 0.60, linear SVM 0.64, random forest 0.67, and the MLP 0.69 accuracy on South versus North. More importantly, macro-F1 goes from 0.35 to 0.69 — so the gain is not an artefact of class imbalance.
>
> A poet's origin is readable, well above chance, from text alone.

*中譯：所以——做得到嗎？做得到。從 0.53 的最頻繁類基準線出發，邏輯迴歸達到 0.60、線性 SVM 0.64、隨機森林 0.67、MLP 在南北任務上達到 0.69。更重要的是 macro-F1 從 0.35 升到 0.69——所以這個增益不是類別不平衡造成的假象。*

*詩人的出身，光靠文本就能讀出來，而且遠高於隨機。*

**備註**：五根柱由左到右 = Baseline(most-frequent), LogReg, LinearSVM, RandomForest, MLP。

---

## p.14 — Every Grain (11/20)

> Does the signal survive when we make the map harder? Coarse maps are sharper — but even the hardest map is readable. South/North: 0.69 macro-F1. Three macro-regions: 0.43. The full ten-circuit task: 0.18. Each of those is roughly *twice* its own most-frequent baseline.
>
> Honestly, ten-way prediction where some classes have six poets is a brutal task — doubling baseline there is the surprise of this slide.

*中譯：把地圖切得更難，訊號還在嗎？粗的地圖更清晰——但連最難的地圖也讀得出來。南北：macro-F1 0.69。三大區：0.43。完整十道任務：0.18。每一個都大約是自己最頻繁類基準線的兩倍。*

*老實說，有些類別只有六位詩人的十分類是很殘酷的任務——在那裡還能把基準線翻倍，才是這頁真正的驚喜。*

---

## p.15 — The Centre Blurs; Jiangnan Stands Apart (12/20)

> Now, *where* is the signal on the map? Two facts. First: near the court, one idiom. The circuits around Chang'an and Luoyang are heavily confused with one another — the shared court language erases local difference. Second: far from it, a voice of one's own — Jiangnan, the empire's literary south, is by far the most separable region, recall 0.71 on the ten-way task.
>
> And here I want to be careful — this is *not* a distance law. Across all six circuits the fit is non-significant, r equals 0.45, p 0.37; and if you drop Jiangnan, the slope actually reverses. So: two facts, not one gradient. The capitals share a single court idiom — and Jiangnan alone keeps a voice of its own.

*中譯：那麼，訊號在地圖上的「哪裡」？兩個事實。第一：靠近朝廷，只有一種語言。長安、洛陽周邊的道彼此嚴重混淆——共享的宮廷語言抹平了地方差異。第二：遠離朝廷，自成一格——江南，帝國的文學南方，是目前為止最可分辨的區域，十分類任務上 recall 0.71。*

*這裡我要特別小心地說——這**不是**一條距離定律。六個道整體的擬合不顯著，r 0.45、p 0.37；而且拿掉江南，斜率會反轉。所以是兩個事實，不是一條梯度：京畿共享同一套宮廷語言——而只有江南保有自己的聲音。*

**備註**：這頁是誠實度的展示點，「not a distance law」要放慢講。若被問「淮南也遠為何 recall 是 0？」——答案正是本頁論點：不是距離效應，淮南夾在南北之間、樣本又少（22 人），被鄰近大類吸走。

---

## p.16 — Imagery Carries the Region (13/20)

> RQ2 — which features carry the signal? The South writes landscape: mountain-and-water imagery used markedly more than in the north; Buddhist and recluse vocabulary — temples, retreat, withdrawal. The North writes the court: palace diction, the built world of the capitals, and *gongti* — courtly "boudoir" poetry, ironically inherited from the *southern* dynasties' courts.
>
> Tonal patterns, by contrast, carry comparatively weak geographic signal. The regional fingerprint lives in what poets *see*, not in how their verses *scan*.

*中譯：RQ2——哪些特徵承載訊號？南方寫山水：山水意象的使用明顯多於北方；還有佛教與隱逸詞彙——寺廟、退隱、出世。北方寫宮廷：宮殿語彙、京城的人造世界，還有宮體——宮廷「閨怨」詩，諷刺的是，它正是從南朝宮廷繼承來的。*

*相較之下，平仄承載的地理訊號很弱。地域指紋活在詩人「看見什麼」，而不在詩句「怎麼合律」。*

**備註**：最後一句是可引用的金句，值得停一拍。

---

## p.17 — Linguistic Distance Grows with the Map (14/20)

> A second geographic check: take each circuit's stylistic centroid, and compare linguistic distance with geographic distance, pair by pair. The correlation is r = 0.40; a Mantel permutation test — the correct test here, since pairwise distances aren't independent — gives p about 0.09.
>
> In plain terms: the farther apart two circuits lie on the map, the more distant their poetic language — dialect geography's classic pattern, surfacing in a literary corpus thirteen hundred years old. Suggestive rather than decisive at this sample size — and we say so.

*中譯：第二個地理檢驗：取每個道的風格質心，逐對比較語言距離和地理距離。相關係數 r = 0.40；Mantel 置換檢定——這裡正確的檢定方法，因為成對距離彼此不獨立——給出 p 約 0.09。*

*白話說：兩個道在地圖上離得越遠，詩歌語言就越不同——這是方言地理學的經典模式，浮現在一個一千三百年前的文學語料庫裡。在這個樣本量下，它是暗示性而非決定性的——我們也如實這麼說。*

**備註**：主動講 Mantel 而非 naive p=0.016，展現統計嚴謹；這與上一頁的 r=0.45/-0.89 是**不同的量**（風格距離矩陣 vs. 各道 recall），被問到要能區分。

---

## p.18 — Eras (15/20)

> RQ3 — persistence. It turns out the fingerprint waxes and wanes with the dynasty. Early Tang: within-era South/North is unreadable — 0.41 on twenty-nine poets — because southern poets wrote the northern court idiom; every single misclassification reads a southerner as northern. High Tang, the empire's height: 0.50 — exactly at chance. Maximum political integration, maximum stylistic integration. Mid Tang, after the An Lushan rebellion: 0.53 — regional voices begin to return. Late Tang, as central authority weakens: 0.68 — the strongest separation in the whole dynasty.
>
> Regional distinctiveness is not constant. It waxes and wanes with the political integration of the dynasty — and now we have numbers attached.

*中譯：RQ3——持續性。結果顯示，這個指紋隨著朝代盛衰而消長。初唐：期內南北無法分辨——二十九位詩人上只有 0.41——因為南方詩人寫的是北方宮廷語；每一個誤判都是把南方人讀成北方人。盛唐，帝國的頂峰：0.50——恰好等於隨機。政治整合最大化，風格整合也最大化。中唐，安史之亂後：0.53——地方的聲音開始回來。晚唐，中央權威衰落：0.68——整個朝代最強的分離度。*

*地域獨特性不是恆定的。它隨王朝的政治整合而消長——而現在，我們有數字可以佐證了。*

**備註**：0.41→0.50→0.53→0.68 單調遞增是本頁賣點。注意：0.41 是「期內 CV」，而「all 7 errors S→N」來自**全語料模型**的誤判按期分組——兩個分析不同，Q&A 被追問時要分清楚。各期 n 很小（25–43），可主動承認這是 caveats 之一。

---

## p.19 — Reading the Errors (16/20)

> And this is where He Zhizhang returns. In the early Tang, the model's misclassifications run seven out of seven in one direction: southern poets read as northern — none err the other way. Yu Shinan, Chu Liang, He Zhizhang: all southern-born, all court-trained, all writing the dominant northern court idiom.
>
> He Zhizhang swore the accent of home never left him. On the page, the classifier reads him as northern. The "error" is the court's gravity, measured. Misclassification here is not noise — it encodes the prestige of the early-Tang court style.

*中譯：這裡，賀知章回來了。初唐時期，模型的誤判七個裡有七個都朝同一個方向：把南方詩人讀成北方人——沒有一個反向。虞世南、褚亮、賀知章：都生於南方、都受宮廷訓練、都寫著主導性的北方宮廷語言。*

*賀知章發誓鄉音從未離開他。但在紙頁上，分類器把他讀成北方人。這個「錯誤」，是朝廷引力的測量值。這裡的誤判不是雜訊——它編碼了初唐宮廷文風的威望。*

**備註**：全場情感高點，語速放慢。「the court's gravity, measured」後停一拍再翻頁。

---

## p.20 — Do Transformers Read Anything More? (17/20)

> A natural challenge: wouldn't a transformer see more than character counts? We stress-tested this three ways. Naive fine-tuning of GuwenBERT, per fragment: 0.62 — *below* the character n-gram models. A hierarchical frozen encoder, pooling fragments over a poet's whole corpus: 0.674 — now it ties the best classical models. And a hybrid, BERT embeddings plus TF-IDF: adds nothing at all.
>
> Our reading: character n-grams already capture the available regional signal in this corpus. Interpretability costs nothing — the readable model and the deep model see the same geography.

*中譯：一個很自然的質疑：transformer 難道不會比數字元看得更多嗎？我們用三種方式壓力測試。GuwenBERT 逐片段的樸素微調：0.62——比字元 n-gram 模型還低。階層式凍結編碼器，把片段在詩人整個語料庫上池化：0.674——這下追平了最好的古典模型。混合方案，BERT 嵌入加 TF-IDF：完全沒有增益。*

*我們的解讀是：字元 n-gram 已經抓住了這個語料庫裡可得的地域訊號。可解釋性不用付出任何代價——可讀的模型和深度模型，看見的是同一幅地理。*

---

## p.21 — What This Offers Literary History (18/20)

> Three things. First, a dynamic answer to the regional-schools debate: regional distinctiveness is real but not constant — it moves with political integration, now with numbers attached. Second, hypotheses a scholar can contest: because our features are imagery, allusion and diction — not opaque embeddings — every finding is a claim open to close reading. Third, errors as evidence: the model's failures mark exactly where court prestige overrode origin.
>
> This is not a replacement for close reading. It's an instrument that tells close readers where to look.

*中譯：三件事。第一，給地域流派論爭一個動態的答案：地域獨特性是真的，但不是恆定的——它隨政治整合而變動，而且現在有數字佐證。第二，學者可以反駁的假說：因為我們的特徵是意象、用典和語彙——不是不透明的嵌入向量——每個發現都是一個開放給細讀檢驗的主張。第三，誤判即證據：模型失敗的地方，恰好標出宮廷威望壓過出身的位置。*

*這不是要取代細讀。它是一件儀器，告訴細讀者該往哪裡看。*

---

## p.22 — Caveats (19/20)

> Read with care. Small samples: 357 poets overall, 242 for South/North, era subsets smaller still. Inherited noise: attribution and geographic labels carry the uncertainties of the Complete Tang Poems and CBDB. Approximate phonology: tonal features lack a complete Middle-Chinese rime dictionary. And the distance-decay geography is suggestive, not decisive — r 0.40, p about 0.09.
>
> But note: all four caveats point the same way. Finer geocoding, richer phonology, more poets would sharpen — not overturn — the picture. The claims are sized to the evidence.

*中譯：請謹慎解讀。樣本小：總共 357 位詩人，南北任務 242 位，分期子集更小。繼承的雜訊：作品歸屬和地理標籤帶著《全唐詩》和 CBDB 本身的不確定性。近似的音韻：平仄特徵缺乏完整的中古音韻書。距離衰減的地理模式是暗示性而非決定性的——r 0.40、p 約 0.09。*

*但請注意：四個 caveat 指向同一個方向。更精細的地理編碼、更豐富的歷史音韻、更多的詩人，只會讓圖像更清晰——不會推翻它。我們的主張，是按證據的尺寸裁剪的。*

---

## p.23 — Conclusion (20/20)

> To conclude: a Tang poet's origin leaves a computationally detectable trace in their verse. It is carried chiefly by imagery and lexical choice — mountains and waters in the south, palace and gongti diction in the north. It grows with geographic distance. And it is modulated by history — at chance amid High-Tang integration, strongest as Late-Tang authority wanes.
>
> Next, we want to extend the temporal analysis and build stylistic similarity networks — does textual proximity track geography, or transcend it through literary influence?
>
> 鄉音無改 — the accent never left the page either. Thank you.

*中譯：總結：唐代詩人的出身，在詩中留下了計算上可偵測的痕跡。它主要由意象和用字承載——南方的山與水，北方的宮殿與宮體語彙。它隨地理距離增長。而且它被歷史調節——盛唐大一統時降到隨機水準，晚唐中央權威衰落時最強。*

*接下來，我們想延伸時間維度的分析，並建立風格相似度網絡——文本上的親近，是跟著地理走，還是透過文學影響超越了地理？*

*鄉音無改——鄉音也從未離開紙頁。謝謝大家。*

**備註**：結尾用「鄉音無改」收束呼應開場。

---

# Q&A 準備（常見追問）

1. **淮南 recall = 0，但它離長安很遠？**
   正因如此我們說「not a distance law」（12/20）。淮南只有 22 位詩人，地理上夾在南北過渡帶，樣本被江南與河南兩個大類吸走。

2. **12/20 的 r=0.45 / −0.89 和 14/20、結論頁的 r=0.40 是什麼關係？**
   不同的量：前者是「各道 recall vs. 離長安距離」（6 個點）；後者是「道與道的風格距離 vs. 地理距離」的成對矩陣（36 對，Mantel test）。前者不顯著且由江南主導；後者是弱而一致的 distance decay。

3. **初唐 0.41 低於 chance，為什麼？和 7/7 S→N 矛盾嗎？**
   0.41 是期內 5-fold CV（n=29、南方僅 7 人，balanced weights 下模型過度補償）；7/7 S→N 來自全語料模型的誤判按期分組。兩個分析口徑不同、結論一致：初唐南方人寫北方宮廷語。

4. **為什麼不用斷詞/現代 NLP pipeline？**
   古典漢語無公認斷詞標準；字元 n-gram 不引入現代語言學假設，且 transformer 對照組（17/20）顯示可得訊號已被 n-gram 捕捉。

5. **生卒年缺失怎麼辦？**
   分期分析僅用有生卒年的 125/242 位詩人；這是 caveats「small samples」的一部分。

6. **地理標籤可靠嗎？**
   出生地來自 CBDB；錯誤標籤只會稀釋訊號（使結果偏保守），不會偽造訊號。
