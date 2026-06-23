#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正CSV文件中性別欄位的問題
統一性別標記格式
"""

import pandas as pd
import re

def fix_gender_column():
    """修正性別欄位"""
    print("🔧 開始修正性別欄位...")
    
    # 讀取CSV文件
    df = pd.read_csv('poet_geo_label.csv')
    print(f"✅ 載入CSV文件: {len(df)} 行")
    
    # 檢查當前的性別分布
    print(f"\n📊 修正前性別分布:")
    gender_counts = df['性別'].value_counts()
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count} 人")
    
    # 修正性別欄位
    def clean_gender(gender_str):
        if pd.isna(gender_str):
            return ''
        
        gender_str = str(gender_str).strip()
        
        # 處理帶空格的male
        if gender_str == 'male ':
            return 'male'
        
        # 處理帶空格的female
        if gender_str == 'female ':
            return 'female'
        
        # 處理其他格式
        if gender_str.lower() in ['male', 'female']:
            return gender_str.lower()
        
        # 保持原有的特殊標記
        if gender_str in ['female?', 'female/male?', '?']:
            return gender_str
        
        # 空字符串保持為空
        if gender_str == '':
            return ''
        
        # 其他情況保持原樣
        return gender_str
    
    # 應用修正
    df['性別'] = df['性別'].apply(clean_gender)
    
    # 檢查修正後的性別分布
    print(f"\n📊 修正後性別分布:")
    gender_counts = df['性別'].value_counts()
    for gender, count in gender_counts.items():
        print(f"  {gender}: {count} 人")
    
    # 保存修正後的文件
    df.to_csv('poet_geo_label_fixed.csv', index=False)
    print(f"\n✅ 修正後文件已保存為: poet_geo_label_fixed.csv")
    
    # 統計修正的內容
    print(f"\n📈 修正統計:")
    print(f"  - 總行數: {len(df)}")
    print(f"  - 男性詩人: {len(df[df['性別'] == 'male'])}")
    print(f"  - 女性詩人: {len(df[df['性別'].str.contains('female', case=False, na=False)])}")
    print(f"  - 未知性別: {len(df[df['性別'] == ''])}")
    
    return df

def main():
    """主函數"""
    fix_gender_column()

if __name__ == "__main__":
    main()
