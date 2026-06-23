import os
import pandas as pd
import glob
from collections import defaultdict

def merge_ngram_files_pivot_optimized():
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定義n-gram類型
    ngram_types = ['2gram', '3gram', '4gram', '5gram', '6gram', '7gram']
    
    for ngram_type in ngram_types:
        print(f"處理 {ngram_type} 檔案...")
        
        # 找到所有對應的CSV檔案
        pattern = f"*_{ngram_type}_詞頻統計.csv"
        csv_files = glob.glob(os.path.join(current_dir, pattern))
        
        # 使用字典來存儲所有字詞的資料
        word_data = defaultdict(dict)
        all_authors = set()
        
        for csv_file in csv_files:
            # 從檔案名提取作者名
            filename = os.path.basename(csv_file)
            author = filename.split('_')[0]
            all_authors.add(author)
            
            try:
                print(f"  處理檔案: {filename}")
                # 讀取CSV檔案
                df = pd.read_csv(csv_file)
                
                # 確保有必要的欄位
                if '詞彙' in df.columns and '出現次數' in df.columns:
                    # 將資料加入字典
                    for _, row in df.iterrows():
                        word = row['詞彙']
                        count = row['出現次數']
                        word_data[word][author] = count
                else:
                    print(f"警告: {filename} 缺少必要的欄位")
                    
            except Exception as e:
                print(f"錯誤處理檔案 {filename}: {e}")
        
        if word_data:
            # 轉換為DataFrame
            print(f"  轉換資料為DataFrame...")
            
            # 創建結果列表
            result_data = []
            all_authors_list = sorted(list(all_authors))
            
            for word, author_counts in word_data.items():
                row = {'字詞': word}
                total_count = 0
                
                # 為每個作者添加詞頻
                for author in all_authors_list:
                    count = author_counts.get(author, 0)
                    row[author] = count
                    total_count += count
                
                row['總詞頻'] = total_count
                result_data.append(row)
            
            # 創建DataFrame
            merged_df = pd.DataFrame(result_data)
            
            # 按總詞頻降序排序
            merged_df = merged_df.sort_values('總詞頻', ascending=False)
            
            # 重新排列欄位，將總詞頻放在第二位
            columns = ['字詞', '總詞頻'] + all_authors_list
            merged_df = merged_df[columns]
            
            # 儲存合併後的檔案
            output_filename = f"pivot_{ngram_type}_詞頻統計.csv"
            output_path = os.path.join(current_dir, output_filename)
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"已生成 {output_filename}")
            print(f"總共 {len(merged_df)} 個不同字詞")
            print(f"包含 {len(all_authors_list)} 位詩人")
            print(f"檔案大小: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
            print()
        else:
            print(f"沒有找到 {ngram_type} 的資料")

if __name__ == "__main__":
    merge_ngram_files_pivot_optimized()
