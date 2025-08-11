#!/usr/bin/env python3
"""
簡潔版全唐詩爬蟲
使用 requests 和 BeautifulSoup 爬取 ctext.org 上的全唐詩
每卷輸出一個單獨的 txt 文件
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import os
from pathlib import Path
import re

class SimpleQuantangshiCrawler:
    def __init__(self, output_dir="quantangshi_volumes", delay=2.0):
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.session = requests.Session()
        
        # 設置請求頭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 創建輸出目錄
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 統計信息
        self.success_count = 0
        self.failed_volumes = []
        self.captcha_volumes = []
        
    def check_for_captcha(self, soup):
        """檢查頁面是否包含驗證碼"""
        text = soup.get_text().lower()
        captcha_keywords = ['驗證碼', 'captcha', 'verification', 'security check', 'robot check']
        return any(keyword in text for keyword in captcha_keywords)
    
    def extract_poems(self, soup):
        """從BeautifulSoup對象中提取詩歌"""
        poems = []
        
        # 從作者信息開始提取，這樣更可靠
        author_spans = soup.find_all('span', class_='etext opt')
        
        for author_span in author_spans:
            author_text = author_span.get_text().strip()
            if not author_text or author_text == "電子圖書館":
                continue
                
            # 找到包含作者信息的table
            parent_table = author_span.find_parent('table')
            if not parent_table:
                continue
                
            # 在table中尋找H2標題
            h2_elem = parent_table.find('h2')
            if not h2_elem:
                continue
                
            title_text = h2_elem.get_text().strip()
            if not title_text.startswith('《') or not title_text.endswith('》'):
                continue
                
            # 提取標題
            title = title_text[1:-1]  # 移除《》
            
            # 尋找詩歌內容
            content = ""
            # 尋找下一個表格中的詩歌內容
            table = parent_table.find_next_sibling('table')
            if table:
                content_cells = table.find_all('td', class_='ctext')
                if content_cells:
                    content_parts = []
                    for cell in content_cells:
                        cell_text = cell.get_text().strip()
                        if cell_text and not cell_text.startswith('打開字典'):
                            content_parts.append(cell_text)
                    content = '\n'.join(content_parts)
            
            if title and content:
                poems.append({
                    'title': title,
                    'author': author_text,
                    'content': content
                })
        
        return poems
    
    def fetch_volume(self, volume_num):
        """獲取指定卷的內容"""
        url = f"https://ctext.org/quantangshi/{volume_num}/zh"
        print(f"正在獲取第 {volume_num} 卷: {url}")
        
        try:
            # 添加隨機延遲
            time.sleep(self.delay + random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 檢查是否需要驗證碼
            if self.check_for_captcha(soup):
                print(f"⚠️  第 {volume_num} 卷需要驗證碼")
                return None, "captcha"
            
            # 檢查是否包含詩歌內容
            if '全唐詩' not in soup.get_text():
                print(f"⚠️  第 {volume_num} 卷可能不是有效的詩歌頁面")
                return None, "invalid_page"
            
            # 提取詩歌
            poems = self.extract_poems(soup)
            
            if poems:
                print(f"✅ 第 {volume_num} 卷成功提取 {len(poems)} 首詩")
                return poems, "success"
            else:
                print(f"⚠️  第 {volume_num} 卷未找到詩歌內容")
                return [], "no_poems"
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 第 {volume_num} 卷請求錯誤: {e}")
            return None, "request_error"
        except Exception as e:
            print(f"❌ 第 {volume_num} 卷獲取失敗: {e}")
            return None, "unknown_error"
    
    def save_volume(self, poems, volume_num):
        """保存單卷詩歌到文件"""
        filename = f"全唐詩_第{volume_num:03d}卷.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"全唐詩 第{volume_num}卷\n")
            f.write("=" * 50 + "\n\n")
            
            if poems:
                for i, poem in enumerate(poems, 1):
                    f.write(f"{i}. {poem['title']}\n")
                    f.write(f"   作者: {poem['author']}\n")
                    f.write(f"   內容:\n{poem['content']}\n")
                    f.write("-" * 30 + "\n\n")
            else:
                f.write("本卷暫無詩歌內容\n")
        
        print(f"💾 已保存第 {volume_num} 卷到 {filepath}")
    
    def save_summary(self):
        """保存爬取摘要"""
        summary_file = self.output_dir / "爬取摘要.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("全唐詩爬取摘要\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"成功爬取卷數: {self.success_count}\n")
            f.write(f"失敗卷數: {len(self.failed_volumes)}\n")
            f.write(f"需要驗證碼卷數: {len(self.captcha_volumes)}\n\n")
            
            if self.failed_volumes:
                f.write("失敗的卷:\n")
                for vol in self.failed_volumes:
                    f.write(f"  第{vol}卷\n")
                f.write("\n")
            
            if self.captcha_volumes:
                f.write("需要驗證碼的卷:\n")
                for vol in self.captcha_volumes:
                    f.write(f"  第{vol}卷\n")
                f.write("\n")
        
        print(f"📊 爬取摘要已保存到 {summary_file}")
    
    def crawl(self, start_volume=1, end_volume=900):
        """爬取指定範圍的卷"""
        print(f"開始爬取全唐詩 (第 {start_volume} 卷到第 {end_volume} 卷)")
        print(f"輸出目錄: {self.output_dir}")
        print(f"請求延遲: {self.delay} 秒")
        print("=" * 60)
        
        for volume_num in range(start_volume, end_volume + 1):
            print(f"\n進度: {volume_num}/{end_volume} ({volume_num/end_volume*100:.1f}%)")
            
            poems, status = self.fetch_volume(volume_num)
            
            if status == "success" and poems:
                self.save_volume(poems, volume_num)
                self.success_count += 1
            elif status == "captcha":
                self.captcha_volumes.append(volume_num)
                # 即使有驗證碼也保存空文件
                self.save_volume([], volume_num)
            elif status == "no_poems":
                self.save_volume([], volume_num)
                self.success_count += 1
            else:
                self.failed_volumes.append(volume_num)
            
            # 顯示統計信息
            print(f"📊 當前統計: 成功 {self.success_count}, 失敗 {len(self.failed_volumes)}, 驗證碼 {len(self.captcha_volumes)}")
        
        # 保存摘要
        self.save_summary()
        
        print("\n" + "=" * 60)
        print("爬取完成！")
        print(f"✅ 總共成功爬取 {self.success_count} 卷")
        print(f"✅ 輸出目錄: {self.output_dir}")
        
        if self.failed_volumes:
            print(f"⚠️  失敗的卷: {self.failed_volumes}")
        
        if self.captcha_volumes:
            print(f"⚠️  需要驗證碼的卷: {self.captcha_volumes}")
            print("請手動處理這些卷或重新運行")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="簡潔版全唐詩爬蟲")
    parser.add_argument("--start", type=int, default=1, help="開始卷號 (默認: 1)")
    parser.add_argument("--end", type=int, default=900, help="結束卷號 (默認: 900)")
    parser.add_argument("--output", "-o", default="quantangshi_volumes", help="輸出目錄 (默認: quantangshi_volumes)")
    parser.add_argument("--delay", type=float, default=2.0, help="請求延遲秒數 (默認: 2.0)")
    parser.add_argument("--test", action="store_true", help="測試模式 (只爬取前5卷)")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 測試模式: 只爬取前5卷")
        args.end = min(5, args.end)
    
    crawler = SimpleQuantangshiCrawler(args.output, args.delay)
    crawler.crawl(args.start, args.end)

if __name__ == "__main__":
    main() 