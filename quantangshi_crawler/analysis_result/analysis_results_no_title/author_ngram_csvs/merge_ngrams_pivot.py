import os
import pandas as pd
import glob

def merge_ngram_files_pivot():
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定義n-gram類型
    ngram_types = ['1gram', '2gram', '3gram', '4gram', '5gram', '6gram', '7gram']
    
    for ngram_type in ngram_types:
        print(f"處理 {ngram_type} 檔案...")
        
        # 找到所有對應的CSV檔案
        pattern = f"*_{ngram_type}_詞頻統計.csv"
        csv_files = glob.glob(os.path.join(current_dir, pattern))
        
        all_data = []
        
        for csv_file in csv_files:
            # 從檔案名提取作者名
            filename = os.path.basename(csv_file)
            author = filename.split('_')[0]
            
            try:
                # 讀取CSV檔案
                df = pd.read_csv(csv_file)
                
                # 確保有必要的欄位
                if '詞彙' in df.columns and '出現次數' in df.columns:
                    # 選擇需要的欄位
                    df_processed = df[['詞彙', '出現次數']].copy()
                    df_processed.columns = ['字詞', author]  # 將作者名作為欄位名
                    
                    all_data.append(df_processed)
                else:
                    print(f"警告: {filename} 缺少必要的欄位")
                    
            except Exception as e:
                print(f"錯誤處理檔案 {filename}: {e}")
        
        if all_data:
            # 合併所有資料，以字詞為基準
            merged_df = all_data[0]
            for df in all_data[1:]:
                merged_df = merged_df.merge(df, on='字詞', how='outer')
            
            # 填充NaN值為0
            merged_df = merged_df.fillna(0)
            
            # 計算總詞頻
            author_columns = [col for col in merged_df.columns if col != '字詞']
            merged_df['總詞頻'] = merged_df[author_columns].sum(axis=1)
            
            # 按總詞頻降序排序
            merged_df = merged_df.sort_values('總詞頻', ascending=False)
            
            # 重新排列欄位，將總詞頻放在第二位
            columns = ['字詞', '總詞頻'] + author_columns
            merged_df = merged_df[columns]
            
            # 儲存合併後的檔案
            output_filename = f"pivot_{ngram_type}_詞頻統計.csv"
            output_path = os.path.join(current_dir, output_filename)
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"已生成 {output_filename}")
            print(f"總共 {len(merged_df)} 個不同字詞")
            print(f"包含 {len(author_columns)} 位詩人")
            print(f"檔案大小: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
            print()
        else:
            print(f"沒有找到 {ngram_type} 的資料")

if __name__ == "__main__":
    merge_ngram_files_pivot()
