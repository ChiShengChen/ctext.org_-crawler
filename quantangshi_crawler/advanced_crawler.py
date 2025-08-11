#!/usr/bin/env python3
"""
全唐詩爬蟲 v4.0 - 高級反檢測版
專門用於爬取 ctext.org 上的全唐詩內容
使用高級反檢測技術繞過網站保護
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
import cloudscraper
from fake_useragent import UserAgent

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://ctext.org/quantangshi"

class AdvancedQuantangshiCrawler:
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
        
        # 初始化多種會話類型
        self.init_sessions()
        
        # 重試計數器
        self.retry_count = 0
        
        # 成功和失敗統計
        self.success_count = 0
        self.failed_count = 0
        self.captcha_count = 0
        
        # 會話管理
        self.session_start_time = time.time()
        self.requests_in_session = 0
        self.max_requests_per_session = 5  # 更頻繁地更換會話
        
        # 調試模式
        self.debug_mode = self.config.get('output_format', {}).get('verbose_logging', False)
        
        # 中斷標誌
        self.interrupted = False
        
        # 設置信號處理器
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("🔄 初始化高級爬蟲完成")

    def init_sessions(self):
        """初始化多種會話類型"""
        # 1. 標準會話
        self.session = requests.Session()
        self.session.verify = False
        
        # 2. Cloudscraper會話 (用於繞過Cloudflare保護)
        try:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            self.scraper.verify = False
            print("✅ Cloudscraper 會話初始化成功")
        except Exception as e:
            print(f"⚠️  Cloudscraper 初始化失敗: {e}")
            self.scraper = None
        
        # 3. 嘗試初始化UserAgent
        try:
            self.ua = UserAgent()
            print("✅ UserAgent 初始化成功")
        except Exception as e:
            print(f"⚠️  UserAgent 初始化失敗: {e}")
            self.ua = None
        
        # 設置會話級別的請求頭
        self.update_session_headers()

    def update_session_headers(self):
        """更新會話請求頭"""
        headers = self.get_advanced_headers()
        self.session.headers.update(headers)
        if self.scraper:
            self.scraper.headers.update(headers)

    def get_advanced_headers(self):
        """獲取高級請求頭"""
        # 使用真實的瀏覽器User-Agent
        if self.ua:
            user_agent = self.ua.chrome
        else:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Referer': 'https://ctext.org/',
            'Origin': 'https://ctext.org'
        }
        
        return headers

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
        
        # 關閉舊會話
        self.session.close()
        
        # 重新初始化會話
        self.session = requests.Session()
        self.session.verify = False
        
        # 更新請求頭
        self.update_session_headers()
        
        self.requests_in_session = 0
        self.session_start_time = time.time()

    def smart_delay(self):
        """智能延遲，避免被檢測"""
        # 檢查是否需要重新建立會話
        if self.requests_in_session >= self.max_requests_per_session:
            self.reset_session()
        
        # 基礎延遲
        base_delay = self.delay
        
        # 隨機變化
        random_delay = random.uniform(0.5, 2.0)
        
        # 根據重試次數增加延遲
        retry_multiplier = min(1 + (self.retry_count * 0.3), 2.0)
        
        # 添加額外的隨機延遲
        extra_delay = random.uniform(0, 1.0)
        
        total_delay = (base_delay + random_delay + extra_delay) * retry_multiplier
        
        # 限制最大延遲時間
        total_delay = min(total_delay, 8.0)
        
        print(f"   等待 {total_delay:.1f} 秒...")
        time.sleep(total_delay)
        
        self.requests_in_session += 1

    def check_for_blocking(self, content: str) -> bool:
        """檢查是否被阻擋"""
        blocking_indicators = [
            'Access unavailable',
            'Access to ctext.org is unavailable',
            'strictly prohibited',
            '無法提供服務',
            '嚴禁使用自動下載軟体',
            'cloudflare',
            'security challenge',
            'checking your browser'
        ]
        
        content_lower = content.lower()
        for indicator in blocking_indicators:
            if indicator.lower() in content_lower:
                return True
        return False

    def check_for_captcha(self, content: str) -> bool:
        """檢查頁面是否包含驗證碼"""
        captcha_indicators = [
            '驗證碼', 'captcha', 'verification', 'security check',
            '請輸入驗證碼', '請完成驗證', 'robot check', 'human verification'
        ]
        
        content_lower = content.lower()
        for indicator in captcha_indicators:
            if indicator.lower() in content_lower:
                return True
        return False

    def fetch_volume_with_retry(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """帶重試機制的卷獲取 - 使用多種方法"""
        for attempt in range(self.max_retries + 1):
            self.retry_count = attempt
            
            if attempt > 0:
                print(f"   第 {attempt} 次重試...")
                time.sleep(random.uniform(2, 5))
            
            # 嘗試不同的會話類型
            session_types = ['standard', 'cloudscraper']
            if self.scraper is None:
                session_types = ['standard']
            
            for session_type in session_types:
                print(f"   嘗試使用 {session_type} 會話...")
                poems, status = self.fetch_volume(volume_num, session_type)
                
                if status == "success":
                    return poems, status
                elif status == "blocked":
                    print(f"   {session_type} 會話被阻擋，嘗試下一個...")
                    continue
                elif status == "captcha":
                    print(f"⚠️  遇到驗證碼，重新建立會話...")
                    self.reset_session()
                    time.sleep(random.uniform(3, 8))
                    break
            
            # 最後一次嘗試
            if attempt == self.max_retries:
                print(f"   已重試 {self.max_retries} 次，放棄該卷")
                return None, f"max_retries_exceeded_{status}"
        
        return None, "unknown_error"

    def fetch_volume(self, volume_num: int, session_type: str = 'standard') -> Tuple[Optional[List[Dict]], str]:
        """獲取指定卷的內容"""
        url = f"{BASE_URL}/{volume_num}/zh"
        print(f"正在獲取第 {volume_num} 卷: {url}")
        
        try:
            # 智能延遲
            self.smart_delay()
            
            # 選擇會話類型
            if session_type == 'cloudscraper' and self.scraper:
                session = self.scraper
            else:
                session = self.session
            
            # 發送請求
            response = session.get(url, timeout=30)
            
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
            
            # 檢查是否被阻擋
            if self.check_for_blocking(content):
                print(f"⚠️  第 {volume_num} 卷被阻擋")
                if self.debug_mode:
                    print(f"   DEBUG: 阻擋頁面前500字符: {content[:500]}")
                return None, "blocked"
            
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
        """從頁面提取詩歌內容"""
        poems = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找詩歌表格
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 2:
                        # 提取標題和作者
                        title_cell = cells[0]
                        content_cell = cells[1] if len(cells) > 1 else None
                        
                        # 提取標題
                        title_link = title_cell.find('a')
                        if title_link:
                            title = title_link.get_text(strip=True)
                        else:
                            title = title_cell.get_text(strip=True)
                        
                        # 提取作者
                        author = "未知作者"
                        author_elements = title_cell.find_all('a')
                        if len(author_elements) > 1:
                            author = author_elements[1].get_text(strip=True)
                        
                        # 提取內容
                        content = ""
                        if content_cell:
                            content = content_cell.get_text(strip=True)
                        
                        if title and content:
                            poems.append({
                                'title': title,
                                'author': author,
                                'content': content
                            })
            
            # 如果沒有找到表格格式，嘗試其他方法
            if not poems:
                # 查找詩歌標題
                title_links = soup.find_all('a', href=re.compile(r'/quantangshi/'))
                
                for link in title_links:
                    title = link.get_text(strip=True)
                    if title and len(title) > 1:
                        # 查找對應的內容
                        parent = link.parent
                        if parent:
                            content = parent.get_text(strip=True)
                            if content and len(content) > len(title):
                                poems.append({
                                    'title': title,
                                    'author': "未知作者",
                                    'content': content
                                })
            
        except Exception as e:
            print(f"   提取詩歌時發生錯誤: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
        
        return poems

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
                elif status == "blocked":
                    self.failed_count += 1
                    print(f"⚠️  第 {volume_num} 卷被阻擋，可能需要更換IP或等待")
                else:
                    self.failed_count += 1
                
                # 每10卷顯示一次統計
                if i % 10 == 0:
                    print(f"📊 當前統計: 成功 {self.success_count}, 失敗 {self.failed_count}, 驗證碼 {self.captcha_count}")
                    print()
                
                # 每20卷強制重新建立會話
                if i % 20 == 0:
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

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="全唐詩爬蟲 v4.0 - 高級反檢測版")
    parser.add_argument("--start", type=int, default=1, help="開始卷號")
    parser.add_argument("--end", type=int, default=900, help="結束卷號")
    parser.add_argument("--output", type=str, default="quantangshi_volumes", help="輸出目錄")
    parser.add_argument("--delay", type=float, default=2.0, help="請求延遲（秒）")
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
    
    crawler = AdvancedQuantangshiCrawler(
        config_file=args.config,
        output_dir=args.output,
        delay=args.delay
    )
    
    crawler.crawl_volumes(args.start, args.end)

if __name__ == "__main__":
    main() 