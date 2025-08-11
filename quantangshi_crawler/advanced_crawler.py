#!/usr/bin/env python3
"""
高級全唐詩爬蟲 v4.0
包含更先進的反檢測機制
"""

import requests
import time
import random
import json
import os
import re
from typing import Dict, List, Optional, Tuple
import html
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime, timedelta
import threading

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://ctext.org/quantangshi"

class AdvancedQuantangshiCrawler:
    def __init__(self, config_file: str = "advanced_config.json", output_dir: str = None, delay: float = None):
        # 載入配置文件
        self.config = self.load_config(config_file)
        
        # 基本設置
        self.output_dir = output_dir or self.config.get('crawler_settings', {}).get('output_directory', 'quantangshi_volumes')
        self.delay = delay or self.config.get('crawler_settings', {}).get('delay_seconds', 3.0)
        self.max_retries = self.config.get('crawler_settings', {}).get('max_retries', 5)
        self.retry_delay = self.config.get('crawler_settings', {}).get('retry_delay', 8.0)
        
        # 創建輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 用戶代理池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # 會話管理
        self.session_pool = []
        self.current_session_index = 0
        self.session_lock = threading.Lock()
        
        # 初始化會話池
        self.init_session_pool()
        
        # 統計信息
        self.success_count = 0
        self.failed_count = 0
        self.captcha_count = 0
        self.retry_count = 0
        
        # 請求歷史
        self.request_history = []
        self.max_history_size = 100
        
        # 冷卻時間管理
        self.last_request_time = 0
        self.min_request_interval = 2.0
        
        print("🚀 高級爬蟲初始化完成")

    def load_config(self, config_file: str) -> Dict:
        """載入配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  配置文件 {config_file} 不存在，使用默認配置")
            return self.get_default_config()
        except json.JSONDecodeError:
            print(f"⚠️  配置文件 {config_file} 格式錯誤，使用默認配置")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """獲取默認配置"""
        return {
            "crawler_settings": {
                "start_volume": 1,
                "end_volume": 900,
                "output_directory": "quantangshi_volumes",
                "delay_seconds": 3.0,
                "max_retries": 5,
                "retry_delay": 8.0,
                "max_requests_per_session": 10,
                "session_pool_size": 3
            },
            "session_management": {
                "session_timeout": 300,
                "rotate_user_agents": True,
                "use_proxy": False,
                "proxy_list": []
            },
            "content_validation": {
                "check_for_poetry_content": True,
                "required_keywords": [
                    "全唐詩", "quantangshi", "<h2>《<a", "<td class=\"ctext\">", "詩"
                ]
            }
        }

    def init_session_pool(self):
        """初始化會話池"""
        pool_size = self.config.get('crawler_settings', {}).get('session_pool_size', 3)
        
        for i in range(pool_size):
            session = requests.Session()
            session.verify = False
            
            # 設置會話級別的請求頭
            session.headers.update({
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
            
            self.session_pool.append({
                'session': session,
                'created_at': datetime.now(),
                'request_count': 0,
                'last_used': datetime.now()
            })
        
        print(f"🔄 已初始化 {pool_size} 個會話")

    def get_session(self):
        """獲取會話"""
        with self.session_lock:
            # 選擇使用最少的會話
            session_info = min(self.session_pool, key=lambda x: x['request_count'])
            session_info['request_count'] += 1
            session_info['last_used'] = datetime.now()
            
            # 如果會話使用過多，重新創建
            if session_info['request_count'] >= self.config.get('crawler_settings', {}).get('max_requests_per_session', 10):
                self.recreate_session(session_info)
            
            return session_info['session']

    def recreate_session(self, session_info):
        """重新創建會話"""
        print("🔄 重新創建會話...")
        
        # 關閉舊會話
        session_info['session'].close()
        
        # 創建新會話
        new_session = requests.Session()
        new_session.verify = False
        
        # 設置新的請求頭
        new_session.headers.update({
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
        
        # 更新會話信息
        session_info['session'] = new_session
        session_info['created_at'] = datetime.now()
        session_info['request_count'] = 0
        session_info['last_used'] = datetime.now()

    def smart_delay(self):
        """智能延遲"""
        # 確保最小請求間隔
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        # 基礎延遲
        base_delay = self.delay
        
        # 隨機變化
        random_delay = random.uniform(1.5, 5.0)
        
        # 根據重試次數增加延遲
        retry_multiplier = min(1 + (self.retry_count * 0.3), 2.5)
        
        # 添加額外的隨機延遲
        extra_delay = random.uniform(0, 3.0)
        
        total_delay = (base_delay + random_delay + extra_delay) * retry_multiplier
        
        print(f"   等待 {total_delay:.1f} 秒...")
        time.sleep(total_delay)
        
        self.last_request_time = time.time()

    def get_advanced_headers(self):
        """獲取高級請求頭"""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": random.choice([
                "zh-CN,zh;q=0.9,en;q=0.8",
                "zh-TW,zh;q=0.9,en;q=0.8", 
                "en-US,en;q=0.9,zh;q=0.8",
                "zh-HK,zh;q=0.9,en;q=0.8"
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
                "no-cache",
                "no-store"
            ]),
            "Pragma": random.choice(["no-cache", ""]),
            "Referer": random.choice([
                "https://ctext.org/",
                "https://ctext.org/zh",
                "https://www.google.com/",
                "https://www.baidu.com/",
                "https://ctext.org/quantangshi/",
                ""
            ]),
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"', '"Linux"'])
        }
        
        return headers

    def check_for_captcha(self, content: str) -> bool:
        """檢查頁面是否包含驗證碼"""
        captcha_indicators = [
            '驗證碼', 'captcha', 'verification', 'security check',
            '請輸入驗證碼', '請完成驗證', 'robot check', 'human verification',
            'cloudflare', 'security challenge', 'checking your browser',
            'please complete the security check', 'ddos protection'
        ]
        
        content_lower = content.lower()
        for indicator in captcha_indicators:
            if indicator.lower() in content_lower:
                return True
        return False

    def fetch_volume_with_retry(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """帶重試機制的卷獲取"""
        for attempt in range(self.max_retries + 1):
            self.retry_count = attempt
            
            if attempt > 0:
                print(f"   第 {attempt} 次重試...")
                self.smart_delay()
            
            poems, status = self.fetch_volume(volume_num)
            
            # 如果成功，直接返回
            if status == "success":
                return poems, status
            
            # 如果遇到驗證碼，更換會話並等待
            if status == "captcha":
                print(f"⚠️  遇到驗證碼，更換會話...")
                self.rotate_sessions()
                time.sleep(random.uniform(8, 20))  # 更長的等待時間
                if attempt < self.max_retries:
                    continue
                else:
                    self.captcha_count += 1
                    return None, "captcha"
            
            # 如果是403錯誤，更換會話
            if "http_error_403" in status:
                print(f"   遇到403錯誤，更換會話...")
                self.rotate_sessions()
                time.sleep(random.uniform(5, 15))
            
            # 最後一次嘗試
            if attempt == self.max_retries:
                print(f"   已重試 {self.max_retries} 次，放棄該卷")
                return None, f"max_retries_exceeded_{status}"
        
        return None, "unknown_error"

    def rotate_sessions(self):
        """輪換會話"""
        with self.session_lock:
            for session_info in self.session_pool:
                self.recreate_session(session_info)

    def fetch_volume(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """獲取指定卷的內容"""
        url = f"{BASE_URL}/{volume_num}/zh"
        print(f"正在獲取第 {volume_num} 卷: {url}")
        
        try:
            # 智能延遲
            self.smart_delay()
            
            # 獲取會話
            session = self.get_session()
            
            # 使用會話發送請求
            response = session.get(url, timeout=30, headers=self.get_advanced_headers())
            
            # 檢查響應狀態
            if response.status_code == 403:
                return None, "http_error_403"
            elif response.status_code != 200:
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
                    print(f"   頁面內容長度: {len(content)}")
                    return None, "invalid_page"
            
            # 提取詩歌
            poems = self.extract_poems_from_page(content)
            
            if poems:
                print(f"✅ 第 {volume_num} 卷成功提取 {len(poems)} 首詩")
                return poems, "success"
            else:
                print(f"⚠️  第 {volume_num} 卷未找到詩歌內容")
                return None, "no_poems_found"
                
        except requests.exceptions.Timeout:
            print(f"   請求超時")
            return None, "timeout"
        except requests.exceptions.ConnectionError:
            print(f"   連接錯誤")
            return None, "connection_error"
        except Exception as e:
            print(f"   未知錯誤: {str(e)}")
            return None, f"unknown_error_{str(e)}"

    def extract_poems_from_page(self, content: str) -> List[Dict]:
        """從網頁內容中提取詩歌"""
        poems = []
        
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # 找到所有的詩歌表格
            poem_tables = soup.find_all('table', {'width': '100%'})
            
            for table in poem_tables:
                # 查找標題
                title_element = table.find('h2')
                if title_element:
                    title_link = title_element.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                    else:
                        title = title_element.get_text(strip=True)
                else:
                    continue
                
                # 查找作者
                author_element = table.find('span', {'class': 'author'})
                if author_element:
                    author = author_element.get_text(strip=True)
                else:
                    # 嘗試其他方式查找作者
                    author_span = table.find('span')
                    if author_span:
                        author = author_span.get_text(strip=True)
                    else:
                        author = '佚名'
                
                # 查找詩歌內容
                content_element = table.find('td', {'class': 'ctext'})
                if content_element:
                    content = content_element.get_text(strip=True)
                else:
                    # 嘗試其他方式查找內容
                    content_div = table.find('div', {'id': re.compile(r'comm.*')})
                    if content_div:
                        content = content_div.get_text(strip=True)
                    else:
                        content = ''
                
                # 清理內容
                if content:
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    if title and content:
                        poems.append({
                            'title': title,
                            'author': author,
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
        
        for i, volume_num in enumerate(range(start_volume, end_volume + 1), 1):
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
        
        # 最終統計
        print("=" * 60)
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
    
    parser = argparse.ArgumentParser(description="高級全唐詩爬蟲 v4.0")
    parser.add_argument("--start", type=int, default=1, help="開始卷號")
    parser.add_argument("--end", type=int, default=900, help="結束卷號")
    parser.add_argument("--output", type=str, default="quantangshi_volumes", help="輸出目錄")
    parser.add_argument("--delay", type=float, default=3.0, help="請求延遲（秒）")
    parser.add_argument("--config", type=str, default="advanced_config.json", help="配置文件")
    
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
    
    # 創建爬蟲實例
    crawler = AdvancedQuantangshiCrawler(
        config_file=args.config,
        output_dir=args.output,
        delay=args.delay
    )
    
    # 開始爬取
    crawler.crawl_volumes(args.start, args.end)

if __name__ == "__main__":
    main() 