#!/usr/bin/env python3
"""
重試失敗卷的腳本
專門處理之前爬取失敗的卷，使用更保守的策略
"""

import json
import time
import random
from pathlib import Path
from urllib import request, error
import html
import re

class FailedVolumeRetry:
    def __init__(self, failed_volumes_file="failed_volumes.json", delay=10.0):
        self.delay = delay
        self.failed_volumes_file = failed_volumes_file
        self.output_dir = Path("quantangshi_volumes")
        
        # 更保守的請求頭
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 載入失敗的卷列表
        self.failed_volumes = self.load_failed_volumes()
    
    def load_failed_volumes(self):
        """載入失敗的卷列表"""
        try:
            with open(self.failed_volumes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('failed_volumes', [])
        except FileNotFoundError:
            print(f"⚠️  失敗卷文件 {self.failed_volumes_file} 不存在")
            return []
        except json.JSONDecodeError:
            print(f"❌ 失敗卷文件格式錯誤")
            return []
    
    def save_failed_volumes(self):
        """保存失敗的卷列表"""
        data = {
            'failed_volumes': self.failed_volumes,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.failed_volumes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_poems_from_page(self, content: str):
        """從網頁內容中提取詩歌"""
        poems = []
        
        # 移除 script 和 style 標籤
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # 找到所有的詩歌標題和作者
        title_author_blocks = re.findall(r'<table width=\'100%\'>.*?<h2>《<a[^>]*>([^<]+)</a>》</h2>.*?<span[^>]*><b>\s*([^<]+)</b></span>.*?</table>', content, re.DOTALL)
        
        # 找到所有的詩歌內容
        content_blocks = re.findall(r'<table border="0">.*?</table>', content, re.DOTALL)
        
        # 組合標題和內容
        for i, (title, author) in enumerate(title_author_blocks):
            # 清理作者名稱
            clean_author = author.strip().replace('著', '').strip()
            
            # 尋找對應的內容區塊
            if i < len(content_blocks):
                content_block = content_blocks[i]
                
                # 提取詩歌內容
                content_matches = re.findall(r'<div id="comm[^"]*"></div>([^<]+)<p class="ctext"></p>', content_block, re.DOTALL)
                
                if content_matches:
                    poem_content = content_matches[0].strip()
                    # 清理HTML標籤
                    poem_content = re.sub(r'<[^>]+>', '', poem_content)
                    poem_content = re.sub(r'\s+', ' ', poem_content).strip()
                    
                    poems.append({
                        'title': title.strip(),
                        'author': clean_author,
                        'content': poem_content
                    })
        
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
    
    def fetch_volume(self, volume_num: int):
        """獲取指定卷的內容"""
        url = f"https://ctext.org/quantangshi/{volume_num}/zh"
        print(f"正在重試第 {volume_num} 卷: {url}")
        
        try:
            # 更長的延遲
            delay = self.delay + random.uniform(5, 15)
            print(f"   等待 {delay:.1f} 秒...")
            time.sleep(delay)
            
            req = request.Request(url, headers=self.headers)
            
            with request.urlopen(req, timeout=60) as resp:
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
                
                # HTML解碼
                content = html.unescape(content)
                
                # 檢查是否需要驗證碼
                if self.check_for_captcha(content):
                    print(f"⚠️  第 {volume_num} 卷仍然需要驗證碼")
                    return None, "captcha"
                
                # 檢查是否包含詩歌內容
                required_keywords = ['全唐詩', 'quantangshi', '帝京篇', '李世民', '<h2>《<a', '<td class="ctext">']
                has_poetry_content = any(keyword in content for keyword in required_keywords)
                
                if not has_poetry_content:
                    print(f"⚠️  第 {volume_num} 卷仍然不是有效的詩歌頁面")
                    return None, "invalid_page"
                
                # 提取詩歌
                poems = self.extract_poems_from_page(content)
                
                if poems:
                    print(f"✅ 第 {volume_num} 卷重試成功，提取 {len(poems)} 首詩")
                    return poems, "success"
                else:
                    print(f"⚠️  第 {volume_num} 卷重試後仍未找到詩歌內容")
                    return [], "no_poems"
                    
        except error.HTTPError as e:
            print(f"❌ 第 {volume_num} 卷重試 HTTP 錯誤: {e.code}")
            return None, f"http_error_{e.code}"
        except error.URLError as e:
            print(f"❌ 第 {volume_num} 卷重試 URL 錯誤: {e.reason}")
            return None, "url_error"
        except Exception as e:
            print(f"❌ 第 {volume_num} 卷重試失敗: {e}")
            return None, "unknown_error"
    
    def save_volume_to_file(self, poems, volume_num: int):
        """保存單卷詩歌到文件"""
        filename = f"全唐詩_第{volume_num:03d}卷.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"全唐詩 第{volume_num}卷\n")
            f.write("=" * 50 + "\n\n")
            
            for i, poem in enumerate(poems, 1):
                f.write(f"{i}. {poem.get('title', '未知標題')}\n")
                f.write(f"   作者: {poem.get('author', '未知作者')}\n")
                f.write(f"   內容:\n{poem.get('content', '無內容')}\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"💾 已保存第 {volume_num} 卷到 {filepath}")
    
    def retry_failed_volumes(self):
        """重試所有失敗的卷"""
        if not self.failed_volumes:
            print("沒有需要重試的卷")
            return
        
        print(f"開始重試 {len(self.failed_volumes)} 個失敗的卷")
        print(f"延遲設置: {self.delay} 秒")
        print("=" * 50)
        
        success_count = 0
        still_failed = []
        
        for i, volume_info in enumerate(self.failed_volumes, 1):
            volume_num = volume_info['volume']
            original_status = volume_info['status']
            
            print(f"\n進度: {i}/{len(self.failed_volumes)}")
            print(f"重試第 {volume_num} 卷 (原狀態: {original_status})")
            
            poems, status = self.fetch_volume(volume_num)
            
            if status == "success":
                success_count += 1
                self.save_volume_to_file(poems, volume_num)
            else:
                still_failed.append({
                    'volume': volume_num,
                    'original_status': original_status,
                    'retry_status': status
                })
            
            # 每5個卷顯示一次統計
            if i % 5 == 0:
                print(f"\n📊 當前統計: 成功 {success_count}, 仍然失敗 {len(still_failed)}")
        
        # 更新失敗卷列表
        self.failed_volumes = still_failed
        self.save_failed_volumes()
        
        # 最終統計
        print("\n" + "=" * 50)
        print("🎉 重試完成！")
        print(f"✅ 重試成功: {success_count} 卷")
        print(f"❌ 仍然失敗: {len(still_failed)} 卷")
        
        if still_failed:
            print("\n仍然失敗的卷:")
            for volume_info in still_failed:
                print(f"  第 {volume_info['volume']} 卷: {volume_info['retry_status']}")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="重試失敗的卷")
    parser.add_argument("--delay", type=float, default=10.0, help="請求延遲（秒）")
    parser.add_argument("--file", type=str, default="failed_volumes.json", help="失敗卷文件")
    
    args = parser.parse_args()
    
    retry = FailedVolumeRetry(
        failed_volumes_file=args.file,
        delay=args.delay
    )
    
    retry.retry_failed_volumes()

if __name__ == "__main__":
    main() 