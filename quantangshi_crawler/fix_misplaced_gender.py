#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正錯位的性別標記
將錯位到唐詩紀事卷欄位的性別標記移回正確位置
"""

import pandas as pd
import re

def fix_misplaced_gender():
    """修正錯位的性別標記"""
    print("🔧 開始修正錯位的性別標記...")
    
    # 讀取CSV文件
    df = pd.read_csv('poet_geo_label.csv')
    print(f"✅ 載入CSV文件: {len(df)} 行")
    
    # 檢查錯位的性別標記
    print(f"\n📊 檢查錯位的性別標記:")
    misplaced_count = 0
    
    for idx, row in df.iterrows():
        # 檢查第3列（唐詩紀事卷）是否有性別標記
        if pd.notna(row.iloc[2]) and str(row.iloc[2]).strip() in ['male', 'female']:
            print(f"  行 {idx+1}: {row['詩人']} - 第3列有性別標記: {row.iloc[2]}")
            misplaced_count += 1
    
    print(f"  發現 {misplaced_count} 個錯位的性別標記")
    
    # 修正錯位的性別標記
    def fix_misplaced_row(row):
        # 檢查第3列是否有性別標記
        if pd.notna(row.iloc[2]) and str(row.iloc[2]).strip() in ['male', 'female']:
            gender = str(row.iloc[2]).strip()
            
            # 如果第2列（性別欄位）是空的，將性別標記移到第2列
            if pd.isna(row['性別']) or str(row['性別']).strip() == '':
                row['性別'] = gender
                row.iloc[2] = ''  # 清空第3列
                print(f"    修正: {row['詩人']} - 將 {gender} 從第3列移到第2列")
            else:
                # 如果第2列已經有性別標記，檢查是否一致
                existing_gender = str(row['性別']).strip()
                if existing_gender != gender:
                    print(f"    衝突: {row['詩人']} - 第2列: {existing_gender}, 第3列: {gender}")
                # 清空第3列
                row.iloc[2] = ''
        
        return row
    
    # 應用修正
    df = df.apply(fix_misplaced_row, axis=1)
    
    # 檢查修正後的結果
    print(f"\n📊 修正後檢查:")
    remaining_misplaced = 0
    
    for idx, row in df.iterrows():
        if pd.notna(row.iloc[2]) and str(row.iloc[2]).strip() in ['male', 'female']:
            print(f"  行 {idx+1}: {row['詩人']} - 仍有錯位: {row.iloc[2]}")
            remaining_misplaced += 1
    
    print(f"  剩餘錯位標記: {remaining_misplaced} 個")
    
    # 保存修正後的文件
    df.to_csv('poet_geo_label_fixed.csv', index=False)
    print(f"\n✅ 修正後文件已保存為: poet_geo_label_fixed.csv")
    
    # 統計修正的內容
    print(f"\n📈 修正統計:")
    print(f"  - 總行數: {len(df)}")
    print(f"  - 修正的錯位標記: {misplaced_count}")
    
    # 檢查最終的性別分布
    print(f"\n📊 最終性別分布:")
    gender_counts = df['性別'].value_counts()
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count} 人")
    
    return df

def main():
    """主函數"""
    fix_misplaced_gender()

if __name__ == "__main__":
    main()
