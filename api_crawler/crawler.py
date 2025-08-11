import argparse
import json
import time
import re
from pathlib import Path
from urllib import error, request

BASE_URL = "https://api.ctext.org"


def _sanitize(name: str) -> str:
    """Return a filesystem-friendly representation of *name*.

    Keeps alphanumeric characters, spaces, dashes and underscores and
    strips anything else. The result is also trimmed.
    """
    return "".join(c for c in name if c.isalnum() or c in " -_").strip()


def fetch_text_from_webpage(urn: str) -> str:
    """Fetch text content from the ctext.org webpage using the URN."""
    try:
        # 使用 getlink API 獲取網頁鏈接
        url = f"{BASE_URL}/getlink?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "ctext-crawler"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'url' in data:
                webpage_url = data['url']
                print(f"Fetching webpage: {webpage_url}")
                
                # 抓取網頁內容
                req = request.Request(webpage_url, headers={"User-Agent": "ctext-crawler"})
                with request.urlopen(req) as resp:
                    content = resp.read().decode('utf-8')
                    
                    # 改進的文本提取
                    # 移除 script 和 style 標籤及其內容
                    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
                    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
                    
                    # 移除 HTML 標籤
                    text = re.sub(r'<[^>]+>', '', content)
                    
                    # 移除 HTML 實體
                    text = re.sub(r'&[^;]+;', '', text)
                    
                    # 移除多餘的空白字符
                    text = re.sub(r'\s+', ' ', text)
                    
                    # 移除導航和頁腳等不需要的內容
                    lines = text.split('\n')
                    filtered_lines = []
                    skip_sections = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 跳過導航和頁腳內容
                        if any(keyword in line for keyword in [
                            '中国哲学书电子化计划', '简体字版', '繁体', 'English', 
                            '本站介绍', '简介', '工具', '系统统计', '先秦两汉',
                            '喜欢我们的网站', '网站的设计与内容', '版权', '沪ICP',
                            '若有任何意见或建议', 'Do not click this'
                        ]):
                            continue
                        
                        # 跳過 JavaScript 代碼
                        if 'function' in line or 'var ' in line or 'if(' in line:
                            continue
                        
                        filtered_lines.append(line)
                    
                    # 合併並清理文本
                    result = '\n'.join(filtered_lines)
                    result = re.sub(r'\n\s*\n', '\n', result)  # 移除多餘的空行
                    result = result.strip()
                    
                    return result
    except Exception as e:
        print(f"Error fetching webpage for {urn}: {e}")
        return ""


def fetch_node(node: str, language: str) -> dict:
    """Fetch *node* from the ctext API and return the parsed JSON."""
    # 使用正確的 API 端點
    if node == "zhs" or node == "root":
        # 獲取所有文本列表
        url = f"{BASE_URL}/gettexttitles?if=zh&remap=gb"
    elif node.startswith("ctp:"):
        # 獲取特定文本的信息
        url = f"{BASE_URL}/gettextinfo?urn={node}&if=zh&remap=gb"
    else:
        # 嘗試獲取文本信息
        url = f"{BASE_URL}/gettextinfo?urn={node}&if=zh&remap=gb"
    
    print(f"Fetching URL: {url}")
    req = request.Request(url, headers={"User-Agent": "ctext-crawler"})
    
    try:
        with request.urlopen(req) as resp:
            response_text = resp.read().decode('utf-8')
            print(f"Response status: {resp.status}")
            print(f"Response content (first 200 chars): {response_text[:200]}")
            
            if not response_text.strip():
                print("WARNING: Empty response received")
                return {}
            
            # Check if response is HTML instead of JSON
            if response_text.strip().startswith('<!DOCTYPE html>') or response_text.strip().startswith('<html'):
                print("WARNING: Received HTML instead of JSON. API endpoint may not exist.")
                print("The API endpoint appears to be returning HTML pages instead of JSON data.")
                return {}
            
            try:
                data = json.loads(response_text)
                
                # 處理不同的 API 響應格式
                if node == "zhs" or node == "root":
                    # 這是 gettexttitles 的響應，需要轉換為爬蟲期望的格式
                    if "books" in data:
                        return {
                            "title": "Chinese Texts",
                            "children": [
                                {
                                    "id": book["urn"],
                                    "title": book["title"],
                                    "path": book["urn"]
                                }
                                for book in data["books"]
                            ]
                        }
                elif node.startswith("ctp:"):
                    # 這是 gettextinfo 的響應
                    if "title" in data:
                        # 嘗試從網頁獲取文本內容
                        text_content = fetch_text_from_webpage(node)
                        return {
                            "title": data.get("title", node),
                            "text": text_content,
                            "content": text_content,
                            "info": data
                        }
                
                return data
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print("Response appears to be invalid JSON.")
                return {}
                
    except error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return {}
    except error.URLError as e:
        print(f"URL Error: {e.reason}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {}


def crawl(root: str = "zhs", out_dir: Path = Path("texts"), delay: float = 1.0) -> None:
    """Recursively crawl the ctext API starting from *root*.

    ``root`` is the starting node (usually ``"zhs"`` for Chinese texts).
    ``out_dir`` is the directory where downloaded texts are stored.
    ``delay`` specifies the delay (in seconds) between requests.
    """
    stack = [(root, out_dir)]
    visited = set()

    while stack:
        node, path = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        try:
            data = fetch_node(node, "zhs")
        except (error.HTTPError, error.URLError) as e:
            print(f"Failed to fetch {node}: {e}")
            continue
        title = data.get("title") or node
        content = data.get("text") or data.get("content")
        if content:
            filename = _sanitize(title) or f"{node}.txt"
            target = path / f"{filename}.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        children = (
            data.get("children")
            or data.get("sub")
            or data.get("sections")
            or []
        )
        for child in children:
            child_id = child.get("id") or child.get("path") or child.get("uri")
            child_title = child.get("title", str(child_id))
            stack.append((child_id, path / _sanitize(child_title)))
        time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl texts from ctext.org")
    parser.add_argument("--output", default="texts", help="Output directory")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--root", default="zhs", help="Root node to start crawling")
    args = parser.parse_args()
    crawl(root=args.root, out_dir=Path(args.output), delay=args.delay)


if __name__ == "__main__":
    main()
