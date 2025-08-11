#!/usr/bin/env python3
import json
import re
from urllib import request

def test_api():
    """測試 ctext.org API 功能"""
    
    # 測試 gettexttitles
    print("=== 測試 gettexttitles ===")
    url = "https://api.ctext.org/gettexttitles?if=zh&remap=gb"
    req = request.Request(url, headers={"User-Agent": "test-crawler"})
    
    with request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"找到 {len(data['books'])} 本書")
        for i, book in enumerate(data['books'][:5]):  # 只顯示前5本
            print(f"  {i+1}. {book['title']} - {book['urn']}")
    
    # 測試 gettextinfo
    print("\n=== 測試 gettextinfo ===")
    url = "https://api.ctext.org/gettextinfo?urn=ctp:analects&if=zh&remap=gb"
    req = request.Request(url, headers={"User-Agent": "test-crawler"})
    
    with request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"論語信息: {data['title']}")
        print(f"朝代: {data['dynasty']['from']['name']} - {data['dynasty']['to']['name']}")
    
    # 測試 getlink
    print("\n=== 測試 getlink ===")
    url = "https://api.ctext.org/getlink?urn=ctp:analects&if=zh&remap=gb"
    req = request.Request(url, headers={"User-Agent": "test-crawler"})
    
    with request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        webpage_url = data['url']
        print(f"網頁鏈接: {webpage_url}")
        
        # 測試網頁抓取
        print("\n=== 測試網頁抓取 ===")
        req = request.Request(webpage_url, headers={"User-Agent": "test-crawler"})
        with request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            print(f"網頁大小: {len(content)} 字符")
            
            # 簡單的文本提取
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\s+', ' ', text).strip()
            print(f"提取的文本前200字符: {text[:200]}")

if __name__ == "__main__":
    test_api() 