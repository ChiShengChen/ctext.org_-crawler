#!/usr/bin/env python3
"""
書籍下載器 - 根據書名直接下載 ctext.org 書籍內容
基於現有的 crawler 和 get_book_list 代碼
"""

import json
import re
import time
import os
from pathlib import Path
from urllib import request, error
from typing import Optional, Dict, List

# 嘗試導入 opencc，如果沒有安裝則使用備用方案
try:
    import opencc
    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False
    print("注意: opencc 包未安裝，將使用備用的簡繁轉換方法")
    print("建議安裝: pip install opencc-python-reimplemented")

BASE_URL = "https://api.ctext.org"


def check_book_authentication_required(urn: str) -> bool:
    """檢查書籍是否需要認證"""
    try:
        url = f"{BASE_URL}/gettext?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'error' in data and 'code' in data['error']:
                if data['error']['code'] == 'ERR_REQUIRES_AUTHENTICATION':
                    return True
        return False
    except Exception:
        return False


def convert_traditional_to_simplified(text: str) -> str:
    """將繁體中文轉換為簡體中文"""
    if not text:
        return text
    
    if OPENCC_AVAILABLE:
        # 使用 opencc 進行轉換
        converter = opencc.OpenCC('t2s')  # Traditional to Simplified
        return converter.convert(text)
    else:
        # 備用方案：使用基本的字符映射
        # 這是一個簡化的映射，僅包含常見字符
        traditional_to_simplified = {
            '書': '书', '詩': '诗', '經': '经', '論': '论', '語': '语',
            '學': '学', '習': '习', '時': '时', '說': '说', '樂': '乐',
            '遠': '远', '來': '来', '慍': '愠', '君': '君', '子': '子',
            '為': '为', '人': '人', '孝': '孝', '弟': '弟', '犯': '犯',
            '上': '上', '者': '者', '鮮': '鲜', '亂': '乱', '務': '务',
            '本': '本', '立': '立', '道': '道', '生': '生', '仁': '仁',
            '巧': '巧', '言': '言', '令': '令', '色': '色', '吾': '吾',
            '日': '日', '三': '三', '省': '省', '身': '身', '謀': '谋',
            '忠': '忠', '朋': '朋', '友': '友', '交': '交', '信': '信',
            '傳': '传', '國': '国', '敬': '敬', '事': '事', '節': '节',
            '用': '用', '愛': '爱', '民': '民', '時': '时', '弟': '弟',
            '入': '入', '出': '出', '謹': '谨', '泛': '泛', '眾': '众',
            '親': '亲', '行': '行', '餘': '余', '力': '力', '文': '文',
            '賢': '贤', '易': '易', '父': '父', '母': '母', '竭': '竭',
            '君': '君', '致': '致', '雖': '虽', '謂': '谓', '重': '重',
            '威': '威', '固': '固', '主': '主', '無': '无', '過': '过',
            '勿': '勿', '憚': '惮', '改': '改', '慎': '慎', '終': '终',
            '追': '追', '德': '德', '歸': '归', '厚': '厚', '禽': '禽',
            '問': '问', '貢': '贡', '夫': '夫', '至': '至', '於': '于',
            '邦': '邦', '必': '必', '聞': '闻', '政': '政', '求': '求',
            '抑': '抑', '溫': '温', '良': '良', '恭': '恭', '儉': '俭',
            '讓': '让', '得': '得', '諸': '诸', '異': '异', '觀': '观',
            '志': '志', '沒': '没', '年': '年', '改': '改', '禮': '礼',
            '和': '和', '貴': '贵', '先': '先', '王': '王', '斯': '斯',
            '美': '美', '小': '小', '大': '大', '由': '由', '知': '知',
            '節': '节', '近': '近', '義': '义', '復': '复', '恭': '恭',
            '恥': '耻', '辱': '辱', '因': '因', '失': '失', '宗': '宗',
            '食': '食', '飽': '饱', '居': '居', '安': '安', '敏': '敏',
            '慎': '慎', '就': '就', '正': '正', '好': '好', '貧': '贫',
            '諂': '谄', '富': '富', '驕': '骄', '何': '何', '如': '如',
            '切': '切', '磋': '磋', '琢': '琢', '磨': '磨', '賜': '赐',
            '始': '始', '告': '告', '往': '往', '患': '患', '不': '不',
            '己': '己', '知': '知', '人': '人', '全': '全', '唐': '唐',
            '詩': '诗', '集': '集', '文': '文', '選': '选', '史': '史',
            '記': '记', '漢': '汉', '書': '书', '後': '后', '三': '三',
            '國': '国', '志': '志', '晉': '晋', '宋': '宋', '齊': '齐',
            '梁': '梁', '陳': '陈', '魏': '魏', '北': '北', '周': '周',
            '隋': '隋', '唐': '唐', '五': '五', '代': '代', '宋': '宋',
            '元': '元', '明': '明', '清': '清', '朝': '朝', '代': '代',
            '春': '春', '秋': '秋', '戰': '战', '國': '国', '秦': '秦',
            '漢': '汉', '魏': '魏', '晉': '晋', '南': '南', '北': '北',
            '朝': '朝', '隋': '隋', '唐': '唐', '五': '五', '代': '代',
            '宋': '宋', '元': '元', '明': '明', '清': '清', '民': '民',
            '國': '国', '中': '中', '華': '华', '人': '人', '民': '民',
            '共': '共', '和': '和', '國': '国', '台': '台', '灣': '湾',
            '香': '香', '港': '港', '澳': '澳', '門': '门', '新': '新',
            '加': '加', '坡': '坡', '馬': '马', '來': '来', '西': '西',
            '亞': '亚', '印': '印', '尼': '尼', '泰': '泰', '國': '国',
            '越': '越', '南': '南', '菲': '菲', '律': '律', '賓': '宾',
            '緬': '缅', '甸': '甸', '老': '老', '撾': '挝', '柬': '柬',
            '埔': '埔', '寨': '寨', '新': '新', '加': '加', '坡': '坡',
            '馬': '马', '來': '来', '西': '西', '亞': '亚', '印': '印',
            '尼': '尼', '泰': '泰', '國': '国', '越': '越', '南': '南',
            '菲': '菲', '律': '律', '賓': '宾', '緬': '缅', '甸': '甸',
            '老': '老', '撾': '挝', '柬': '柬', '埔': '埔', '寨': '寨'
        }
        
        result = text
        for traditional, simplified in traditional_to_simplified.items():
            result = result.replace(traditional, simplified)
        return result


def _sanitize(name: str) -> str:
    """返回文件系統友好的文件名"""
    return "".join(c for c in name if c.isalnum() or c in " -_").strip()


def search_book_by_name(book_name: str) -> Optional[Dict]:
    """根據書名搜索書籍信息"""
    print(f"正在搜索書籍: {book_name}")
    
    try:
        # 獲取所有書籍列表
        url = f"{BASE_URL}/gettexttitles?if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            books = data['books']
            
            # 精確匹配
            for book in books:
                if book['title'] == book_name:
                    print(f"找到精確匹配: {book['title']} ({book['urn']})")
                    return book
            
            # 如果沒有找到精確匹配，嘗試繁體轉簡體
            simplified_name = convert_traditional_to_simplified(book_name)
            if simplified_name != book_name:
                print(f"嘗試繁體轉簡體搜索: {simplified_name}")
                for book in books:
                    if book['title'] == simplified_name:
                        print(f"找到精確匹配 (轉換後): {book['title']} ({book['urn']})")
                        return book
            
            # 模糊匹配
            matches = []
            for book in books:
                if book_name.lower() in book['title'].lower():
                    matches.append(book)
            
            # 如果模糊匹配沒有結果，嘗試繁體轉簡體
            if not matches and simplified_name != book_name:
                print(f"嘗試繁體轉簡體模糊搜索: {simplified_name}")
                for book in books:
                    if simplified_name.lower() in book['title'].lower():
                        matches.append(book)
            
            if matches:
                print(f"找到 {len(matches)} 個模糊匹配:")
                for i, book in enumerate(matches):
                    print(f"  {i+1}. {book['title']} ({book['urn']})")
                
                if len(matches) == 1:
                    return matches[0]
                else:
                    # 讓用戶選擇
                    while True:
                        try:
                            choice = input(f"請選擇書籍 (1-{len(matches)}): ")
                            idx = int(choice) - 1
                            if 0 <= idx < len(matches):
                                return matches[idx]
                            else:
                                print("無效的選擇，請重試")
                        except ValueError:
                            print("請輸入數字")
            
            print(f"未找到包含 '{book_name}' 的書籍")
            if simplified_name != book_name:
                print(f"已嘗試繁體轉簡體搜索: '{simplified_name}'")
            return None
            
    except Exception as e:
        print(f"搜索書籍時出錯: {e}")
        return None


def get_book_info(urn: str) -> Dict:
    """獲取書籍詳細信息"""
    try:
        url = f"{BASE_URL}/gettextinfo?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"獲取書籍信息時出錯: {e}")
        return {}


def fetch_chapter_content(urn: str) -> str:
    """遞歸獲取章節內容"""
    try:
        url = f"{BASE_URL}/gettext?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            # 如果有直接文本內容
            if 'fulltext' in data:
                title = data.get('title', '')
                if title:
                    result = f"\n{title}\n"
                else:
                    result = ""
                
                chapter_text = '\n'.join(data['fulltext'])
                result += chapter_text
                # 只在調試模式下顯示詳細信息
                # print(f"成功獲取章節內容，長度: {len(chapter_text)} 字符")
                return result
            
            # 如果有子章節，遞歸獲取
            elif 'subsections' in data:
                title = data.get('title', '')
                if title:
                    result = f"\n{title}\n"
                else:
                    result = ""
                
                all_sections = []
                for subsection in data['subsections']:
                    section_text = fetch_chapter_content(subsection)
                    if section_text:
                        all_sections.append(section_text)
                
                if all_sections:
                    result += '\n'.join(all_sections)
                    # print(f"成功獲取子章節，共 {len(all_sections)} 個")
                    return result
            
            return ""
            
    except Exception as e:
        print(f"獲取章節 {urn} 時出錯: {e}")
        return ""


def fetch_text_from_webpage(urn: str) -> str:
    """從網頁獲取文本內容"""
    try:
        # 嘗試使用 API 直接獲取文本內容
        # 首先嘗試獲取文本的段落信息
        url = f"{BASE_URL}/gettext?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'text' in data:
                print("使用 API 直接獲取文本內容")
                return data['text']
            elif 'fulltext' in data:
                print("使用 API 直接獲取完整文本內容")
                return '\n'.join(data['fulltext'])
            elif 'subsections' in data:
                print(f"找到 {len(data['subsections'])} 個章節，正在獲取各章節內容...")
                print("這可能需要一些時間，請耐心等待...")
                all_text = []
                
                for i, subsection in enumerate(data['subsections']):
                    print(f"正在獲取第 {i+1}/{len(data['subsections'])} 章: {subsection}")
                    
                    # 遞歸獲取章節內容
                    chapter_text = fetch_chapter_content(subsection)
                    if chapter_text:
                        all_text.append(chapter_text)
                    
                    # 添加延遲避免請求過於頻繁
                    time.sleep(0.5)
                
                if all_text:
                    return '\n\n'.join(all_text)
        
        # 如果 API 方法失敗，嘗試網頁方法
        print("API 方法失敗，嘗試網頁方法...")
        
        # 使用 getlink API 獲取網頁鏈接
        url = f"{BASE_URL}/getlink?urn={urn}&if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'url' in data:
                webpage_url = data['url']
                print(f"正在獲取網頁內容: {webpage_url}")
                
                # 抓取網頁內容
                req = request.Request(webpage_url, headers={"User-Agent": "book-downloader"})
                with request.urlopen(req) as resp:
                    content = resp.read().decode('utf-8', errors='ignore')
                    
                    # 改進的文本提取
                    # 移除 script 和 style 標籤及其內容
                    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
                    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
                    
                    # 嘗試提取主要內容區域
                    # 尋找包含文本內容的 div
                    content_match = re.search(r'<div[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</div>', content, flags=re.DOTALL)
                    if content_match:
                        content = content_match.group(1)
                        print(f"找到文本內容區域，長度: {len(content)}")
                        
                        # 檢查是否包含實際的文本內容
                        text_check = re.sub(r'<[^>]+>', '', content)
                        text_check = re.sub(r'\s+', '', text_check)
                        if len(text_check) < 100:  # 如果提取的文本太短，可能是動態加載的
                            print("警告: 提取的文本內容過短，可能是動態加載的內容")
                            print(f"實際文本長度: {len(text_check)} 字符")
                            print("這本書可能需要認證或使用不同的訪問方式")
                    else:
                        print("未找到文本內容區域，使用整個頁面")
                    
                    # 移除 HTML 標籤，但保留換行
                    text = re.sub(r'<br\s*/?>', '\n', content)
                    text = re.sub(r'<p[^>]*>', '\n', text)
                    text = re.sub(r'</p>', '\n', text)
                    text = re.sub(r'<[^>]+>', '', text)
                    
                    # 處理 HTML 實體
                    import html
                    text = html.unescape(text)
                    
                    # 移除多餘的空白字符
                    text = re.sub(r'\s+', ' ', text)
                    
                    # 移除導航和頁腳等不需要的內容
                    lines = text.split('\n')
                    filtered_lines = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 跳過導航和頁腳內容
                        if any(keyword in line for keyword in [
                            '中国哲学书电子化计划', '简体字版', '繁体', 'English', 
                            '本站介绍', '简介', '工具', '系统统计', '先秦两汉',
                            '喜欢我们的网站', '网站的设计与内容', '版权', '沪ICP',
                            '若有任何意见或建议', 'Do not click this', 'function', 'var ',
                            'margin', 'padding', 'position', 'height', 'width'
                        ]):
                            continue
                        
                        # 跳過純數字或符號的行
                        if re.match(r'^[\d\s\-_]+$', line):
                            continue
                        
                        # 如果行太短且不包含中文字符，跳過
                        if len(line) < 3 and not re.search(r'[\u4e00-\u9fff]', line):
                            continue
                        
                        filtered_lines.append(line)
                    
                    # 合併並清理文本
                    result = '\n'.join(filtered_lines)
                    result = re.sub(r'\n\s*\n', '\n', result)  # 移除多餘的空行
                    result = result.strip()
                    
                    return result
    except Exception as e:
        print(f"獲取網頁內容時出錯: {e}")
        return ""


def download_book(book_name: str, output_dir: str = "books") -> bool:
    """下載指定書名的書籍"""
    
    # 搜索書籍
    book = search_book_by_name(book_name)
    if not book:
        return False
    
    # 檢查是否需要認證
    if check_book_authentication_required(book['urn']):
        print(f"⚠️  警告: 此書籍需要認證才能訪問")
        print(f"   書籍: {book['title']} ({book['urn']})")
        print(f"   請訪問 http://ctext.org/tools/subscribe/zhs 了解認證詳情")
        print(f"   或者嘗試其他不需要認證的書籍")
        return False
    
    # 獲取書籍詳細信息
    book_info = get_book_info(book['urn'])
    
    # 創建輸出目錄
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    safe_title = _sanitize(book['title'])
    filename = f"{safe_title}.txt"
    filepath = output_path / filename
    
    print(f"正在下載書籍內容...")
    
    # 獲取文本內容
    text_content = fetch_text_from_webpage(book['urn'])
    
    if not text_content:
        print("未能獲取到書籍內容")
        return False
    
    # 添加書籍信息到文件開頭
    header = f"書名: {book['title']}\n"
    header += f"URN: {book['urn']}\n"
    
    if book_info:
        if 'author' in book_info and book_info['author']:
            header += f"作者: {book_info['author']}\n"
        
        if 'dynasty' in book_info:
            dynasty_from = book_info['dynasty'].get('from', {}).get('name', '')
            dynasty_to = book_info['dynasty'].get('to', {}).get('name', '')
            if dynasty_from or dynasty_to:
                header += f"朝代: {dynasty_from} - {dynasty_to}\n"
        
        if 'compositiondate' in book_info:
            comp_from = book_info['compositiondate'].get('from', '')
            comp_to = book_info['compositiondate'].get('to', '')
            if comp_from or comp_to:
                header += f"創作日期: {comp_from} - {comp_to}\n"
    
    header += f"下載時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += "=" * 50 + "\n\n"
    
    # 保存文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + text_content)
        
        print(f"書籍已成功下載到: {filepath}")
        print(f"文件大小: {len(text_content)} 字符")
        return True
        
    except Exception as e:
        print(f"保存文件時出錯: {e}")
        return False


def list_available_books(limit: int = 20, check_auth: bool = False) -> None:
    """列出可用的書籍（用於參考）"""
    print("正在獲取書籍列表...")
    
    try:
        url = f"{BASE_URL}/gettexttitles?if=zh&remap=gb"
        req = request.Request(url, headers={"User-Agent": "book-downloader"})
        
        with request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            books = data['books']
            
            print(f"總共有 {len(books)} 本書可用")
            
            if check_auth:
                print("正在檢查認證要求...")
                available_books = []
                for i, book in enumerate(books[:limit]):
                    if not check_book_authentication_required(book['urn']):
                        available_books.append(book)
                    if i % 5 == 0:  # 每5本書顯示進度
                        print(f"已檢查 {i+1}/{min(limit, len(books))} 本書...")
                
                print(f"顯示前 {len(available_books)} 本不需要認證的書籍:")
                print("-" * 50)
                
                for i, book in enumerate(available_books):
                    print(f"{i+1:3d}. {book['title']}")
                
                if len(books) > limit:
                    print(f"... 還有更多書籍需要檢查")
                    print("使用 --list-all 查看所有書籍")
            else:
                print(f"顯示前 {limit} 本:")
                print("-" * 50)
                
                for i, book in enumerate(books[:limit]):
                    print(f"{i+1:3d}. {book['title']}")
                
                if len(books) > limit:
                    print(f"... 還有 {len(books) - limit} 本書")
                    print("使用 --list-all 查看所有書籍")
    
    except Exception as e:
        print(f"獲取書籍列表時出錯: {e}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="下載 ctext.org 書籍")
    parser.add_argument("book_name", nargs="?", help="要下載的書籍名稱")
    parser.add_argument("--output", "-o", default="books", help="輸出目錄 (默認: books)")
    parser.add_argument("--list", "-l", action="store_true", help="列出可用書籍")
    parser.add_argument("--list-all", action="store_true", help="列出所有可用書籍")
    parser.add_argument("--check-auth", action="store_true", help="檢查認證要求並只顯示可下載的書籍")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_books(20, args.check_auth)
        return
    
    if args.list_all:
        list_available_books(1000, args.check_auth)  # 顯示所有書籍
        return
    
    if not args.book_name:
        print("請提供書籍名稱")
        print("使用 --help 查看使用說明")
        print("使用 --list 查看可用書籍")
        return
    
    # 下載書籍
    success = download_book(args.book_name, args.output)
    
    if success:
        print("下載完成！")
    else:
        print("下載失敗！")


if __name__ == "__main__":
    main() 