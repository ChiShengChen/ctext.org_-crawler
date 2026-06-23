#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正CSV文件中重複性別標記的問題
"""

import pandas as pd
import re

def fix_duplicate_gender():
    """修正重複性別標記"""
    print("🔧 開始修正重複性別標記...")
    
    # 讀取CSV文件
    df = pd.read_csv('poet_geo_label.csv')
    print(f"✅ 載入CSV文件: {len(df)} 行")
    
    # 檢查重複標記
    print(f"\n📊 檢查重複標記:")
    duplicate_count = 0
    
    for idx, row in df.iterrows():
        if pd.notna(row['性別']) and pd.notna(row.iloc[2]):  # 檢查第3列（索引2）
            if str(row['性別']) == str(row.iloc[2]):
                print(f"  行 {idx+1}: {row['詩人']} - 重複標記: {row['性別']}")
                duplicate_count += 1
    
    print(f"  發現 {duplicate_count} 個重複標記")
    
    # 修正重複標記
    def clean_duplicate_gender(row):
        if pd.notna(row['性別']) and pd.notna(row.iloc[2]):
            if str(row['性別']) == str(row.iloc[2]):
                # 保留第一個標記，清空第二個
                row.iloc[2] = ''
        return row
    
    # 應用修正
    df = df.apply(clean_duplicate_gender, axis=1)
    
    # 檢查修正後的結果
    print(f"\n📊 修正後檢查:")
    remaining_duplicates = 0
    
    for idx, row in df.iterrows():
        if pd.notna(row['性別']) and pd.notna(row.iloc[2]):
            if str(row['性別']) == str(row.iloc[2]):
                print(f"  行 {idx+1}: {row['詩人']} - 仍有重複: {row['性別']}")
                remaining_duplicates += 1
    
    print(f"  剩餘重複標記: {remaining_duplicates} 個")
    
    # 保存修正後的文件
    df.to_csv('poet_geo_label_fixed.csv', index=False)
    print(f"\n✅ 修正後文件已保存為: poet_geo_label_fixed.csv")
    
    # 統計修正的內容
    print(f"\n📈 修正統計:")
    print(f"  - 總行數: {len(df)}")
    print(f"  - 修正的重複標記: {duplicate_count}")
    
    return df

def main():
    """主函數"""
    fix_duplicate_gender()

if __name__ == "__main__":
    main()
