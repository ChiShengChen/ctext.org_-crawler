#!/usr/bin/env python3
import json
import csv
import time
from urllib import request

def get_all_books():
    """獲取 ctext.org 網站上的所有書籍信息"""
    
    print("正在獲取書籍列表...")
    
    # 獲取所有書籍的基本信息
    url = "https://api.ctext.org/gettexttitles?if=zh&remap=gb"
    req = request.Request(url, headers={"User-Agent": "book-list-crawler"})
    
    with request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        books = data['books']
        print(f"找到 {len(books)} 本書")
        
        # 準備 CSV 數據
        csv_data = []
        
        for i, book in enumerate(books):
            print(f"處理第 {i+1}/{len(books)} 本書: {book['title']}")
            
            # 獲取每本書的詳細信息
            try:
                info_url = f"https://api.ctext.org/gettextinfo?urn={book['urn']}&if=zh&remap=gb"
                req = request.Request(info_url, headers={"User-Agent": "book-list-crawler"})
                
                with request.urlopen(req) as resp:
                    info_data = json.loads(resp.read().decode('utf-8'))
                    
                    # 提取朝代信息
                    dynasty_from = ""
                    dynasty_to = ""
                    if 'dynasty' in info_data:
                        if 'from' in info_data['dynasty']:
                            dynasty_from = info_data['dynasty']['from'].get('name', '')
                        if 'to' in info_data['dynasty']:
                            dynasty_to = info_data['dynasty']['to'].get('name', '')
                    
                    # 提取作者信息
                    author = info_data.get('author', '')
                    
                    # 提取創作日期
                    composition_date_from = ""
                    composition_date_to = ""
                    if 'compositiondate' in info_data:
                        composition_date_from = info_data['compositiondate'].get('from', '')
                        composition_date_to = info_data['compositiondate'].get('to', '')
                    
                    # 提取版本信息
                    edition_title = ""
                    if 'edition' in info_data and 'title' in info_data['edition']:
                        edition_title = info_data['edition']['title']
                    
                    # 提取標籤
                    tags = ", ".join(info_data.get('tags', []))
                    
                    # 添加到 CSV 數據
                    csv_data.append({
                        '序號': i + 1,
                        '書名': book['title'],
                        'URN': book['urn'],
                        '作者': author,
                        '朝代_開始': dynasty_from,
                        '朝代_結束': dynasty_to,
                        '創作日期_開始': composition_date_from,
                        '創作日期_結束': composition_date_to,
                        '版本': edition_title,
                        '標籤': tags,
                        '最後修改': info_data.get('lastmodified', ''),
                        '頂層標題': info_data.get('toptitle', ''),
                        '頂層URN': info_data.get('topurn', ''),
                        '作品URN': info_data.get('workurn', '')
                    })
                    
            except Exception as e:
                print(f"獲取 {book['title']} 詳細信息時出錯: {e}")
                # 如果獲取詳細信息失敗，至少保存基本信息
                csv_data.append({
                    '序號': i + 1,
                    '書名': book['title'],
                    'URN': book['urn'],
                    '作者': '',
                    '朝代_開始': '',
                    '朝代_結束': '',
                    '創作日期_開始': '',
                    '創作日期_結束': '',
                    '版本': '',
                    '標籤': '',
                    '最後修改': '',
                    '頂層標題': '',
                    '頂層URN': '',
                    '作品URN': ''
                })
            
            # 添加延遲以避免過於頻繁的請求
            if i % 10 == 0:  # 每10本書暫停一下
                time.sleep(1)
        
        return csv_data

def save_to_csv(data, filename='ctext_books.csv'):
    """將數據保存為 CSV 文件"""
    
    if not data:
        print("沒有數據可保存")
        return
    
    # 獲取所有字段名
    fieldnames = data[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"已保存 {len(data)} 本書的信息到 {filename}")

def main():
    """主函數"""
    print("開始獲取 ctext.org 書籍列表...")
    
    try:
        # 獲取所有書籍信息
        books_data = get_all_books()
        
        # 保存為 CSV
        save_to_csv(books_data)
        
        print("完成！")
        
        # 顯示統計信息
        print(f"\n統計信息:")
        print(f"總書籍數量: {len(books_data)}")
        
        # 統計朝代分布
        dynasties = {}
        for book in books_data:
            dynasty = book['朝代_開始']
            if dynasty:
                dynasties[dynasty] = dynasties.get(dynasty, 0) + 1
        
        print(f"朝代分布:")
        for dynasty, count in sorted(dynasties.items(), key=lambda x: x[1], reverse=True):
            print(f"  {dynasty}: {count} 本")
        
    except Exception as e:
        print(f"出錯: {e}")

if __name__ == "__main__":
    main() 