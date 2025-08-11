#!/usr/bin/env python3
"""
全唐詩爬蟲 v2.0
專門用於爬取 ctext.org 上的全唐詩內容
支持驗證碼處理，每卷輸出單獨的txt文件
支持配置文件控制
"""

import re
import time
import json
import html
import os
import sys
from pathlib import Path
from urllib import request, error
from typing import List, Dict, Optional, Tuple
import random

BASE_URL = "https://ctext.org/quantangshi"

class QuantangshiCrawler:
    def __init__(self, config_file: str = "config.json", output_dir: str = None, delay: float = None):
        # 載入配置文件
        self.config = self.load_config(config_file)
        
        # 使用配置文件中的設置，如果沒有提供參數的話
        self.output_dir = Path(output_dir or self.config.get('crawler_settings', {}).get('output_directory', 'quantangshi_volumes'))
        self.delay = delay or self.config.get('crawler_settings', {}).get('delay_seconds', 2.0)
        
        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # 創建輸出目錄
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 統計信息
        self.success_count = 0
        self.failed_volumes = []
        self.captcha_volumes = []
    
    def load_config(self, config_file: str) -> Dict:
        """載入配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  配置文件 {config_file} 不存在，使用默認設置")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式錯誤: {e}")
            return {}
        
    def extract_poems_from_page(self, content: str) -> List[Dict]:
        """從網頁內容中提取詩歌"""
        poems = []
        
        # 移除 script 和 style 標籤
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # 使用更精確的方法提取詩歌
        # 首先找到所有的詩歌標題和作者
        title_author_blocks = re.findall(r'<table width=\'100%\'>.*?<h2>《<a[^>]*>([^<]+)</a>》</h2>.*?<span[^>]*><b>\s*([^<]+)</b></span>.*?</table>', content, re.DOTALL)
        
        verbose_logging = self.config.get('output_format', {}).get('verbose_logging', False)
        
        if verbose_logging:
            print(f"   找到 {len(title_author_blocks)} 個詩歌標題")
            
            # 然後找到所有的詩歌內容
            content_blocks = re.findall(r'<table border="0">.*?</table>', content, re.DOTALL)
            
            print(f"   找到 {len(content_blocks)} 個內容區塊")
        else:
            # 然後找到所有的詩歌內容
            content_blocks = re.findall(r'<table border="0">.*?</table>', content, re.DOTALL)
        
        # 組合標題和內容
        for i, (title, author) in enumerate(title_author_blocks):
            if verbose_logging and i < 5:  # 只顯示前5個詩歌的處理信息
                print(f"   處理第 {i+1} 個詩歌: {title}")
            
            # 清理作者名稱
            clean_author = author.strip().replace('著', '').strip()
            
            # 尋找對應的內容區塊
            if i < len(content_blocks):
                content_block = content_blocks[i]
                
                # 提取詩歌內容
                content_matches = re.findall(r'<div id="comm[^"]*"></div>([^<]+)<p class="ctext"></p>', content_block, re.DOTALL)
                
                if verbose_logging and i < 5:  # 只顯示前5個詩歌的詳細信息
                    print(f"     詩歌 {i+1} 找到 {len(content_matches)} 個內容片段")
                
                if content_matches:
                    # 將所有內容片段組合成完整的詩歌
                    full_content = '\n'.join([text.strip() for text in content_matches if text.strip()])
                    
                    if full_content:
                        if verbose_logging and i < 5:  # 只顯示前5個詩歌的詳細信息
                            print(f"     詩歌 {i+1} 成功提取內容，長度: {len(full_content)}")
                        poems.append({
                            'title': title.strip(),
                            'author': clean_author,
                            'content': full_content
                        })
                    else:
                        if verbose_logging and i < 5:  # 只顯示前5個詩歌的詳細信息
                            print(f"     詩歌 {i+1} 內容為空")
                else:
                    if verbose_logging and i < 5:  # 只顯示前5個詩歌的詳細信息
                        print(f"     詩歌 {i+1} 未找到內容")
            else:
                if verbose_logging and i < 5:  # 只顯示前5個詩歌的詳細信息
                    print(f"     詩歌 {i+1} 沒有對應的內容區塊")
        
        return poems
    
    def check_for_captcha(self, content: str) -> bool:
        """檢查頁面是否包含驗證碼"""
        captcha_indicators = [
            '驗證碼', 'captcha', 'verification', 'security check',
            '請輸入驗證碼', '請完成驗證', 'robot check'
        ]
        
        content_lower = content.lower()
        for indicator in captcha_indicators:
            if indicator.lower() in content_lower:
                return True
        return False
    
    def fetch_volume(self, volume_num: int) -> Tuple[Optional[List[Dict]], str]:
        """獲取指定卷的內容"""
        url = f"{BASE_URL}/{volume_num}/zh"
        print(f"正在獲取第 {volume_num} 卷: {url}")
        
        try:
            # 添加隨機延遲避免被檢測
            time.sleep(self.delay + random.uniform(0.5, 1.5))
            
            req = request.Request(url, headers=self.session_headers)
            
            with request.urlopen(req) as resp:
                # 檢查是否為壓縮內容
                content_encoding = resp.headers.get('Content-Encoding', '').lower()
                
                if content_encoding == 'gzip':
                    import gzip
                    content = gzip.decompress(resp.read()).decode('utf-8', errors='ignore')
                elif content_encoding == 'deflate':
                    import zlib
                    content = zlib.decompress(resp.read()).decode('utf-8', errors='ignore')
                else:
                    content = resp.read().decode('utf-8', errors='ignore')
                
                # 先進行HTML解碼
                content = html.unescape(content)
                
                # 調試：檢查HTML解碼是否成功
                print(f"   HTML解碼後包含'全唐詩': {'全唐詩' in content}")
                print(f"   HTML解碼後包含'帝京篇': {'帝京篇' in content}")
                print(f"   HTML解碼後包含'李世民': {'李世民' in content}")
                
                # 調試：保存原始內容到文件（根據配置文件設置）
                output_config = self.config.get('output_format', {})
                save_debug = output_config.get('save_debug_content', False)
                debug_limit = output_config.get('debug_content_limit', 3)
                
                if save_debug and volume_num <= debug_limit:
                    with open(f"debug_content_{volume_num}.txt", "w", encoding="utf-8") as f:
                        f.write(content)  # 保存全部內容
                    print(f"   調試內容已保存到 debug_content_{volume_num}.txt")
                
                # 檢查是否需要驗證碼
                if self.check_for_captcha(content):
                    print(f"⚠️  第 {volume_num} 卷需要驗證碼")
                    return None, "captcha"
                
                # 檢查是否包含詩歌內容 - 使用配置文件中的設置
                validation_config = self.config.get('content_validation', {})
                check_for_poetry = validation_config.get('check_for_poetry_content', True)
                
                if check_for_poetry:
                    required_keywords = validation_config.get('required_keywords', [
                        '全唐詩', 'quantangshi', '帝京篇', '李世民', 
                        '<h2>《<a', '<td class="ctext">'
                    ])
                    
                    has_poetry_content = any(keyword in content for keyword in required_keywords)
                    
                    # 調試信息
                    verbose_logging = self.config.get('output_format', {}).get('verbose_logging', False)
                    if verbose_logging:
                        print(f"   調試信息:")
                        for keyword in required_keywords:
                            print(f"   包含'{keyword}': {keyword in content}")
                    
                    if not has_poetry_content:
                        print(f"⚠️  第 {volume_num} 卷可能不是有效的詩歌頁面")
                        print(f"   頁面內容長度: {len(content)}")
                        print(f"   包含詩歌相關內容: {has_poetry_content}")
                        return None, "invalid_page"
                
                # 提取詩歌
                poems = self.extract_poems_from_page(content)
                
                if poems:
                    print(f"✅ 第 {volume_num} 卷成功提取 {len(poems)} 首詩")
                    return poems, "success"
                else:
                    print(f"⚠️  第 {volume_num} 卷未找到詩歌內容")
                    return [], "no_poems"
                    
        except error.HTTPError as e:
            print(f"❌ 第 {volume_num} 卷 HTTP 錯誤: {e.code}")
            return None, f"http_error_{e.code}"
        except error.URLError as e:
            print(f"❌ 第 {volume_num} 卷 URL 錯誤: {e.reason}")
            return None, "url_error"
        except Exception as e:
            print(f"❌ 第 {volume_num} 卷獲取失敗: {e}")
            return None, "unknown_error"
    
    def save_volume_to_file(self, poems: List[Dict], volume_num: int):
        """保存單卷詩歌到文件"""
        filename = f"全唐詩_第{volume_num:03d}卷.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"全唐詩 第{volume_num}卷\n")
            f.write("=" * 50 + "\n\n")
            
            for i, poem in enumerate(poems, 1):
                f.write(f"{i}. {poem['title']}\n")
                f.write(f"   作者: {poem['author']}\n")
                f.write(f"   內容:\n{poem['content']}\n")
                f.write("-" * 30 + "\n\n")
        
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
    
    def crawl_volumes(self, start_volume: int = 1, end_volume: int = 900):
        """爬取指定範圍的卷"""
        print(f"開始爬取全唐詩 (第 {start_volume} 卷到第 {end_volume} 卷)")
        print(f"輸出目錄: {self.output_dir}")
        print(f"請求延遲: {self.delay} 秒")
        print("=" * 60)
        
        for volume_num in range(start_volume, end_volume + 1):
            print(f"\n進度: {volume_num}/{end_volume} ({volume_num/end_volume*100:.1f}%)")
            
            poems, status = self.fetch_volume(volume_num)
            
            if status == "success" and poems:
                self.save_volume_to_file(poems, volume_num)
                self.success_count += 1
            elif status == "captcha":
                self.captcha_volumes.append(volume_num)
            elif status == "no_poems":
                # 即使沒有詩歌也保存空文件
                self.save_volume_to_file([], volume_num)
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
    
    parser = argparse.ArgumentParser(description="全唐詩爬蟲 v2.0")
    parser.add_argument("--config", "-c", default="config.json", help="配置文件路徑 (默認: config.json)")
    parser.add_argument("--start", type=int, help="開始卷號 (覆蓋配置文件設置)")
    parser.add_argument("--end", type=int, help="結束卷號 (覆蓋配置文件設置)")
    parser.add_argument("--output", "-o", help="輸出目錄 (覆蓋配置文件設置)")
    parser.add_argument("--delay", type=float, help="請求延遲秒數 (覆蓋配置文件設置)")
    parser.add_argument("--test", action="store_true", help="測試模式 (覆蓋配置文件設置)")
    
    args = parser.parse_args()
    
    # 創建爬蟲實例
    crawler = QuantangshiCrawler(args.config)
    
    # 獲取配置設置
    config_settings = crawler.config.get('crawler_settings', {})
    
    # 使用命令行參數覆蓋配置文件設置
    start_volume = args.start if args.start is not None else config_settings.get('start_volume', 1)
    end_volume = args.end if args.end is not None else config_settings.get('end_volume', 900)
    output_dir = args.output if args.output is not None else config_settings.get('output_directory', 'quantangshi_volumes')
    delay = args.delay if args.delay is not None else config_settings.get('delay_seconds', 2.0)
    test_mode = args.test or config_settings.get('test_mode', False)
    
    # 更新爬蟲設置
    crawler.output_dir = Path(output_dir)
    crawler.delay = delay
    
    if test_mode:
        print("🧪 測試模式: 只爬取前5卷")
        end_volume = min(5, end_volume)
    
    # 檢查最大卷數限制
    max_volumes = config_settings.get('max_volumes_per_run', 50)
    if end_volume - start_volume + 1 > max_volumes:
        print(f"⚠️  警告: 本次運行將爬取 {end_volume - start_volume + 1} 卷，超過配置的最大限制 {max_volumes}")
        response = input("是否繼續? (y/N): ")
        if response.lower() != 'y':
            print("已取消運行")
            return
    
    print(f"📋 配置信息:")
    print(f"   開始卷號: {start_volume}")
    print(f"   結束卷號: {end_volume}")
    print(f"   輸出目錄: {output_dir}")
    print(f"   請求延遲: {delay} 秒")
    print(f"   測試模式: {test_mode}")
    
    crawler.crawl_volumes(start_volume, end_volume)

if __name__ == "__main__":
    main() 