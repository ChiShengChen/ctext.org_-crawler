# Tang_Poets_Origins_slides_10min_v2.pptx — Speaker Notes（原樣抽取）

自 pptx 內嵌 speaker notes 逐頁抽出，未經改寫。

---

## Slide 1 — Title

Good morning. Today I'd like to ask a very old question with a very new instrument: can you tell where a poet came from, just by reading their poems? We take the Complete Tang Poems — 49,000 of them — and treat this as a prediction problem. (~30s)

## Slide 2 — Can a poem betray where its poet came from?

The regional-schools debate is old; what's been missing is quantification. We treat it as a measurement problem: predict each poet's home circuit from text alone. Three RQs: prediction, signal, persistence. Design principle: interpretability — features a literary historian can read and contest. (~55s)

## Slide 3 — 49,000 poems, 357 poets, ten circuits 道

Complete Tang Poems, 900 volumes, ~49k poems into poet-level corpora. Birthplaces via CBDB; filter to >=5 poems, unambiguous attribution: 357 poets across ten circuits, 242 South/North. Flag now: heavy imbalance — Jiangnan 126, Longyou 6 — hence balanced weights + macro-F1. (~50s)

## Slide 4 — Three tasks, three grains of geography

Three grains. South/North — the headline: five southern vs five northern circuits, 242 poets. Three macro-regions — a different axis: Southeast (Jiangnan+Huainan), Central Plains, Frontier. Ten circuits — the full map, hardest. Note: S/N and macro are two different hypotheses, not a nested hierarchy — Shannan, Jiannan, Lingnan are 'south' on one axis, 'frontier' on the other. (~55s)

## Slide 5 — Readable features, one fair test

Workhorse: character n-gram TF-IDF — no segmentation, no modern linguistic assumptions. On top, readable features: imagery, seasons, allusion, lexical richness, approximate tone. Five models incl. GuwenBERT, stratified 5-fold CV, balanced weights; baseline 0.53. (~50s)

## Slide 6 — Geography is legible from verse alone

Can it be done? Yes. Baseline 0.53 -> LogReg 0.60, SVM 0.64, RF 0.67, MLP 0.69. Macro-F1 0.35 -> 0.69, so not an imbalance artefact. Origin is readable from text alone. (~45s)

## Slide 7 — The signal survives at every grain

Harder maps: South/North 0.69, three macro-regions 0.43, full ten-circuit task 0.18 — each roughly TWICE its own baseline. Ten-way with six-poet classes is brutal; doubling baseline there is the surprise. (~40s)

## Slide 8 — The centre blurs; Jiangnan stands apart

Where is the signal on the map? Two facts: capitals blur into one court idiom; Jiangnan stands apart at recall 0.71. Careful: NOT a distance law — full fit non-significant, slope reverses without Jiangnan. Two facts, not one gradient. (~55s)

## Slide 9 — Imagery carries the region

RQ2: the South writes landscape — mountain/water imagery, Buddhist and recluse vocabulary. The North writes the court — palace diction, gongti motifs. Tone is weak. The fingerprint lives in what poets SEE, not how verses scan. (~45s)

## Slide 10 — The fingerprint waxes and wanes with the dynasty

RQ3: 0.41 early Tang — southerners wrote the northern court idiom, and all 7 full-model errors in that era run S->N. 0.50 at chance at the empire's height, 0.53 after An Lushan, 0.68 late Tang. Distinctiveness moves with political integration — now with numbers. (~55s)

## Slide 11 — Do transformers read anything more?

Wouldn't a transformer see more? Naive fine-tuning 0.62 — below n-grams. Hierarchical frozen encoder 0.674 — ties classical. Hybrid adds nothing. N-grams already capture the signal; interpretability costs nothing. Caveats in one breath: small samples, inherited label noise, approximate tone, suggestive geography — all point the same way. (~55s)

## Slide 12 — Conclusion

Conclusion: origin leaves a detectable trace — carried by imagery and lexical choice, not a simple distance law, modulated by history. Next: stylistic similarity networks. 文如其地 — the text is like its land. Thank you. (~40s)
