#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理CSV文件，移除統計摘要和格式問題
"""

import pandas as pd
import re

def clean_csv_file():
    """清理CSV文件"""
    print("🔧 開始清理CSV文件...")
    
    # 讀取原始文件
    with open('poet_geo_label.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ 原始文件行數: {len(lines)}")
    
    # 清理行
    cleaned_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 跳過空行
        if not line:
            continue
        
        # 跳過統計摘要行
        if any(keyword in line for keyword in [
            '📈 統計摘要', '📋 產量分布', '🏆 頂級作者統計',
            '最多產作者', '最少產作者', '平均每位作者',
            '只寫一首詩的作者', '寫多首詩的作者',
            '前10名作者總詩歌數', '前50名作者總詩歌數', '前100名作者總詩歌數'
        ]):
            print(f"  移除統計行 {i+1}: {line[:50]}...")
            continue
        
        # 跳過只有逗號的行
        if line.count(',') >= 8 and all(c in ', ' for c in line):
            print(f"  移除空行 {i+1}: {line}")
            continue
        
        # 保留有效行
        cleaned_lines.append(line)
    
    print(f"✅ 清理後行數: {len(cleaned_lines)}")
    print(f"  移除了 {len(lines) - len(cleaned_lines)} 行")
    
    # 保存清理後的文件
    with open('poet_geo_label_cleaned.csv', 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            f.write(line + '\n')
    
    print(f"✅ 清理後文件已保存為: poet_geo_label_cleaned.csv")
    
    # 驗證清理結果
    print(f"\n📊 驗證清理結果:")
    
    # 檢查性別分布
    df = pd.read_csv('poet_geo_label_cleaned.csv')
    print(f"  - 總行數: {len(df)}")
    print(f"  - 男性詩人: {len(df[df['性別'] == 'male'])}")
    print(f"  - 女性詩人: {len(df[df['性別'].str.contains('female', case=False, na=False)])}")
    print(f"  - 未知性別: {len(df[df['性別'] == ''])}")
    
    return df

def main():
    """主函數"""
    clean_csv_file()

if __name__ == "__main__":
    main()
