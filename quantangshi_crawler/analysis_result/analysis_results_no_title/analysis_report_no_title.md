# 全唐詩作者 N-gram 分析報告 (不包含標題)

生成時間: 2025-08-20 22:40:22

## 總體統計

- 總作者數: 2,460
- 總詩歌數: 41,380
- 總字符數: 2,819,637 (不包含標題)
- 平均每首詩: 68.1 字符

## N-gram 統計

- 1-gram 總數: 572,946
- 2-gram 總數: 2,215,737
- 4-gram 總數: 2,716,966

## 文件說明

- `author_ngram_csvs/`: 每位作者的n-gram CSV文件
- `detailed_ngram_analysis_no_title.json`: 詳細的JSON分析結果
- `author_summary_no_title.csv`: 作者摘要統計
- `analysis_report_no_title.md`: 本報告

## 注意事項

- 本分析只統計詩歌內容，不包含標題
- 已清理作者名稱，去掉末尾的'著'字
- 只保留中文字符，移除標點符號和數字
