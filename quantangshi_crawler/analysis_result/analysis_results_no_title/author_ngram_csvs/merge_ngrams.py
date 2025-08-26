import os
import pandas as pd
import glob

def merge_ngram_files():
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定義n-gram類型
    ngram_types = ['1gram', '2gram', '4gram']
    
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
                    # 為每一行添加作者資訊
                    df['作者'] = author
                    
                    # 選擇需要的欄位並重新排序
                    df_processed = df[['詞彙', '作者', '出現次數']].copy()
                    df_processed.columns = ['字詞', '詩人', '詞頻']
                    
                    all_data.append(df_processed)
                else:
                    print(f"警告: {filename} 缺少必要的欄位")
                    
            except Exception as e:
                print(f"錯誤處理檔案 {filename}: {e}")
        
        if all_data:
            # 合併所有資料
            merged_df = pd.concat(all_data, ignore_index=True)
            
            # 按詞頻降序排序
            merged_df = merged_df.sort_values('詞頻', ascending=False)
            
            # 儲存合併後的檔案
            output_filename = f"merged_{ngram_type}_詞頻統計.csv"
            output_path = os.path.join(current_dir, output_filename)
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"已生成 {output_filename}")
            print(f"總共 {len(merged_df)} 筆資料")
            print(f"包含 {merged_df['詩人'].nunique()} 位詩人")
            print()
        else:
            print(f"沒有找到 {ngram_type} 的資料")

if __name__ == "__main__":
    merge_ngram_files()
