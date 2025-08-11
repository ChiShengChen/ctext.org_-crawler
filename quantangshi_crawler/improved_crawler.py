#!/usr/bin/env python3
"""
全唐詩爬蟲 v3.1 - 調試改進版
專門用於爬取 ctext.org 上的全唐詩內容
增強反檢測機制，更好的錯誤處理和重試機制
"""

import requests
import time
import random
import json
import os
import re
import signal
import sys
from typing import Dict, List, Optional, Tuple
from urllib import request, parse
import html
from bs4 import BeautifulSoup
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://ctext.org/quantangshi"

class ImprovedQuantangshiCrawler:
    def __init__(self, config_file: str = "config.json", output_dir: str = None, delay: float = None):
        # 載入配置文件
        self.config = self.load_config(config_file)
        
        # 基本設置
        self.output_dir = output_dir or self.config.get('crawler_settings', {}).get('output_directory', 'quantangshi_volumes')
        self.delay = delay or self.config.get('crawler_settings', {}).get('delay_seconds', 2.0)
        self.max_retries = self.config.get('crawler_settings', {}).get('max_retries', 3)
        self.retry_delay = self.config.get('crawler_settings', {}).get('retry_delay', 5.0)
        
        # 創建輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化會話
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL驗證
        
        # 設置會話級別的請求頭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # 用戶代理池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # 重試計數器
        self.retry_count = 0
        
        # 成功和失敗統計
        self.success_count = 0
        self.failed_count = 0
        self.captcha_count = 0
        
        # 會話管理
        self.session_start_time = time.time()
        self.requests_in_session = 0
        self.max_requests_per_session = 10  # 減少到10個請求後重新建立會話
        
        # 調試模式
        self.debug_mode = self.config.get('output_format', {}).get('verbose_logging', False)
        
        # 中斷標誌
        self.interrupted = False
        
        # 設置信號處理器
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("🔄 初始化爬蟲完成")

    def signal_handler(self, signum, frame):
        """處理中斷信號"""
        print("\n⚠️  收到中斷信號，正在安全退出...")
        self.interrupted = True
        sys.exit(0)

    def load_config(self, config_file: str) -> Dict:
        """載入配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  配置文件 {config_file} 不存在，使用默認配置")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️  配置文件 {config_file} 格式錯誤，使用默認配置")
            return {}

    def reset_session(self):
        """重新建立會話以避免被檢測"""
        print("🔄 重新建立會話...")
        self.session.close()
        self.session = requests.Session()
        self.session.verify = False
        
        # 重新設置請求頭
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        self.requests_in_session = 0
        self.session_start_time = time.time()

    def smart_delay(self):
        """智能延遲，避免被檢測 - 減少延遲時間"""
        # 檢查是否需要重新建立會話
        if self.requests_in_session >= self.max_requests_per_session:
            self.reset_session()
        
        # 基礎延遲 - 減少到更合理的範圍
        base_delay = self.delay
        
        # 隨機變化 - 大幅減少延遲範圍
        random_delay = random.uniform(0.5, 2.0)
        
        # 根據重試次數增加延遲，但設置更小的上限
        retry_multiplier = min(1 + (self.retry_count * 0.3), 2.0)
        
        # 添加額外的隨機延遲 - 減少範圍
        extra_delay = random.uniform(0, 1.0)
        
        total_delay = (base_delay + random_delay + extra_delay) * retry_multiplier
        
        # 限制最大延遲時間
        total_delay = min(total_delay, 8.0)
        
        print(f"   等待 {total_delay:.1f} 秒...")
        time.sleep(total_delay)
        
        self.requests_in_session += 1

    def get_random_headers(self):
        """獲取隨機的請求頭"""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice([
                "zh-CN,zh;q=0.9,en;q=0.8",
                "zh-TW,zh;q=0.9,en;q=0.8", 
                "en-US,en;q=0.9,zh;q=0.8"
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": random.choice(["0", "1"]),
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": random.choice([
                "max-age=0",
                "no-cache"
            ]),
            "Referer": random.choice([
                "https://ctext.org/",
                "https://ctext.org/zh",
                "https://www.google.com/",
                "https://www.baidu.com/"
            ])
        }
        
        return headers

    def check_for_captcha(self, content: str) -> bool:
        """檢查頁面是否包含驗證碼"""
        captcha_indicators = [
            '驗證碼', 'captcha', 'verification', 'security check',
            '請輸入驗證碼', '請完成驗證', 'robot check', 'human verification',
            'cloudflare', 'security challenge', 'checking your browser'
        ]
        
        content_lower = content.lower()
        for indicator in captcha_indicators:
            if indicator.lower() in content_lower:
                return True
        return False

    def fetch_volume_with_retry(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """帶重試機制的卷獲取 - 改進版本"""
        for attempt in range(self.max_retries + 1):
            self.retry_count = attempt
            
            if attempt > 0:
                print(f"   第 {attempt} 次重試...")
                # 重試時使用較短的延遲
                time.sleep(random.uniform(2, 5))
            
            poems, status = self.fetch_volume(volume_num)
            
            # 如果成功，直接返回
            if status == "success":
                return poems, status
            
            # 如果遇到驗證碼，重新建立會話並短暫等待
            if status == "captcha":
                print(f"⚠️  遇到驗證碼，重新建立會話...")
                self.reset_session()
                time.sleep(random.uniform(3, 8))  # 減少等待時間
                # 如果是第一次遇到驗證碼，繼續重試
                if attempt < self.max_retries:
                    continue
                else:
                    self.captcha_count += 1
                    return None, "captcha"
            
            # 如果是403錯誤，重新建立會話
            if "http_error_403" in status:
                print(f"   遇到403錯誤，重新建立會話...")
                self.reset_session()
                time.sleep(random.uniform(2, 5))  # 減少等待時間
                continue
            
            # 最後一次嘗試
            if attempt == self.max_retries:
                print(f"   已重試 {self.max_retries} 次，放棄該卷")
                return None, f"max_retries_exceeded_{status}"
        
        return None, "unknown_error"

    def fetch_volume(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """獲取指定卷的內容"""
        url = f"{BASE_URL}/{volume_num}/zh"
        print(f"正在獲取第 {volume_num} 卷: {url}")
        
        try:
            # 智能延遲
            self.smart_delay()
            
            # 使用會話發送請求
            response = self.session.get(url, timeout=30, headers=self.get_random_headers())
            
            # 檢查響應狀態
            if response.status_code == 403:
                if self.debug_mode:
                    print(f"   DEBUG: 403錯誤，響應頭: {dict(response.headers)}")
                return None, "http_error_403"
            elif response.status_code != 200:
                if self.debug_mode:
                    print(f"   DEBUG: HTTP {response.status_code}錯誤")
                return None, f"http_error_{response.status_code}"
            
            # 獲取內容
            content = response.text
            
            # 先進行HTML解碼
            content = html.unescape(content)
            
            # 檢查是否需要驗證碼
            if self.check_for_captcha(content):
                print(f"⚠️  第 {volume_num} 卷需要驗證碼")
                return None, "captcha"
            
            # 檢查是否包含詩歌內容
            validation_config = self.config.get('content_validation', {})
            check_for_poetry = validation_config.get('check_for_poetry_content', True)
            
            if check_for_poetry:
                required_keywords = validation_config.get('required_keywords', [
                    '全唐詩', 'quantangshi',  
                    '<h2>《<a', '<td class="ctext">', '詩'
                ])
                
                has_poetry_content = any(keyword in content for keyword in required_keywords)
                
                if not has_poetry_content:
                    print(f"⚠️  第 {volume_num} 卷可能不是有效的詩歌頁面")
                    if self.debug_mode:
                        print(f"   DEBUG: 頁面內容長度: {len(content)}")
                        print(f"   DEBUG: 頁面前500字符: {content[:500]}")
                    return None, "invalid_page"
            
            # 提取詩歌
            poems = self.extract_poems_from_page(content)
            
            if poems:
                print(f"✅ 第 {volume_num} 卷成功提取 {len(poems)} 首詩")
                return poems, "success"
            else:
                print(f"⚠️  第 {volume_num} 卷未找到詩歌內容")
                if self.debug_mode:
                    print(f"   DEBUG: 頁面內容長度: {len(content)}")
                return None, "no_poems_found"
                
        except requests.exceptions.Timeout:
            print(f"   請求超時")
            return None, "timeout"
        except requests.exceptions.ConnectionError:
            print(f"   連接錯誤")
            return None, "connection_error"
        except requests.exceptions.RequestException as e:
            print(f"   請求異常: {e}")
            return None, f"request_error_{str(e)}"
        except Exception as e:
            print(f"   未知錯誤: {e}")
            return None, f"unknown_error_{str(e)}"

    def extract_poems_from_page(self, content: str) -> List[Dict]:
        """從網頁內容中提取詩歌"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            poems = []
            
            # 方法1: 從作者信息開始提取（適用於有作者的詩歌）
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
            
            # 方法2: 如果沒有找到有作者的詩歌，嘗試提取沒有作者的詩歌（如祭祀樂章）
            if not poems:
                # 尋找所有H2標題
                h2_elements = soup.find_all('h2')
                
                for h2_elem in h2_elements:
                    title_text = h2_elem.get_text().strip()
                    if not title_text.startswith('《') or not title_text.endswith('》'):
                        continue
                    
                    # 提取標題
                    title = title_text[1:-1]  # 移除《》
                    
                    # 尋找詩歌內容
                    content = ""
                    # 尋找下一個表格中的詩歌內容
                    table = h2_elem.find_parent('table')
                    if table:
                        next_table = table.find_next_sibling('table')
                        if next_table:
                            content_cells = next_table.find_all('td', class_='ctext')
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
                            'author': '佚名',  # 沒有作者信息時使用佚名
                            'content': content
                        })
            
            return poems
            
        except ImportError:
            print("⚠️  BeautifulSoup未安裝，無法解析HTML內容")
            return []
        except Exception as e:
            print(f"⚠️  解析詩歌內容時出錯: {e}")
            return []
    
    def save_volume_to_file(self, poems: List[Dict], volume_num: int):
        """保存單卷詩歌到文件"""
        filename = f"全唐詩_第{volume_num:03d}卷.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"全唐詩 第{volume_num}卷\n")
            f.write("=" * 50 + "\n\n")
            
            for i, poem in enumerate(poems, 1):
                f.write(f"{i}. {poem.get('title', '未知標題')}\n")
                f.write(f"   作者: {poem.get('author', '未知作者')}\n")
                f.write(f"   內容:\n{poem.get('content', '無內容')}\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"💾 已保存第 {volume_num} 卷到 {filepath}")
    
    def crawl_volumes(self, start_volume: int = 1, end_volume: int = 900):
        """爬取指定範圍的卷"""
        print(f"開始爬取全唐詩 (第 {start_volume} 卷到第 {end_volume} 卷)")
        print(f"輸出目錄: {self.output_dir}")
        print(f"請求延遲: {self.delay} 秒")
        print("=" * 60 + "\n")
        
        total_volumes = end_volume - start_volume + 1
        
        try:
            for i, volume_num in enumerate(range(start_volume, end_volume + 1), 1):
                # 檢查是否被中斷
                if self.interrupted:
                    print("\n⚠️  檢測到中斷信號，正在安全退出...")
                    break
                
                progress = (i / total_volumes) * 100
                print(f"進度: {i}/{total_volumes} ({progress:.1f}%)")
                
                poems, status = self.fetch_volume_with_retry(volume_num)
                
                if status == "success":
                    self.success_count += 1
                    self.save_volume_to_file(poems, volume_num)
                elif status == "captcha":
                    self.captcha_count += 1
                else:
                    self.failed_count += 1
                
                # 每10卷顯示一次統計
                if i % 10 == 0:
                    print(f"📊 當前統計: 成功 {self.success_count}, 失敗 {self.failed_count}, 驗證碼 {self.captcha_count}")
                    print()
                
                # 每50卷強制重新建立會話
                if i % 50 == 0:
                    print("🔄 定期重新建立會話...")
                    self.reset_session()
        
        except KeyboardInterrupt:
            print("\n⚠️  收到鍵盤中斷信號，正在安全退出...")
        except Exception as e:
            print(f"\n❌ 發生未預期的錯誤: {e}")
        
        # 最終統計
        print("=" * 60)
        if self.interrupted:
            print("⏹️  爬取被中斷！")
        else:
            print("🎉 爬取完成！")
        print(f"✅ 成功: {self.success_count} 卷")
        print(f"❌ 失敗: {self.failed_count} 卷")
        print(f"⚠️  驗證碼: {self.captcha_count} 卷")
        
        if self.failed_count > 0:
            print(f"\n失敗的卷: {self.failed_count} 卷")
        
        if self.captcha_count > 0:
            print(f"\n需要驗證碼的卷: {self.captcha_count} 卷")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="全唐詩爬蟲 v3.0")
    parser.add_argument("--start", type=int, default=1, help="開始卷號")
    parser.add_argument("--end", type=int, default=900, help="結束卷號")
    parser.add_argument("--output", type=str, default="quantangshi_volumes", help="輸出目錄")
    parser.add_argument("--delay", type=float, default=3.0, help="請求延遲（秒）")
    parser.add_argument("--config", type=str, default="config.json", help="配置文件")
    
    args = parser.parse_args()
    
    # 檢查範圍
    if args.end - args.start + 1 > 50:
        response = input(f"⚠️  警告: 本次運行將爬取 {args.end - args.start + 1} 卷，超過配置的最大限制 50\n是否繼續? (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    print("📋 配置信息:")
    print(f"   開始卷號: {args.start}")
    print(f"   結束卷號: {args.end}")
    print(f"   輸出目錄: {args.output}")
    print(f"   請求延遲: {args.delay} 秒")
    print(f"   配置文件: {args.config}")
    
    crawler = ImprovedQuantangshiCrawler(
        config_file=args.config,
        output_dir=args.output,
        delay=args.delay
    )
    
    crawler.crawl_volumes(args.start, args.end)

if __name__ == "__main__":
    main() 