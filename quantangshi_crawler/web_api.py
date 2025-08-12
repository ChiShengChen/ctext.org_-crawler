#!/usr/bin/env python3
"""
全唐詩 Web API
提供RESTful API接口來查詢全唐詩數據
"""

from flask import Flask, jsonify, request, render_template_string
import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Optional
import random

app = Flask(__name__)

class QuantangshiAPI:
    def __init__(self, data_file: str = "quantangshi_data.json"):
        self.data_file = data_file
        self.poems_data = []
        self.authors_data = {}
        self.volumes_data = {}
        self.load_data()
    
    def load_data(self):
        """載入詩歌數據"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.poems_data = data.get('poems', [])
                self.authors_data = data.get('authors', {})
                self.volumes_data = data.get('volumes', {})
        else:
            # 如果沒有JSON文件，從文本文件載入
            self.load_from_text_files()
    
    def load_from_text_files(self):
        """從文本文件載入數據"""
        print("正在從文本文件載入數據...")
        volumes_dir = "quantangshi_volumes"
        
        for filename in os.listdir(volumes_dir):
            if filename.endswith('.txt') and filename.startswith('全唐詩_第'):
                file_path = os.path.join(volumes_dir, filename)
                volume_data = self.parse_volume_file(file_path)
                self.poems_data.extend(volume_data)
        
        print(f"載入完成！總共 {len(self.poems_data)} 首詩歌")
    
    def parse_volume_file(self, file_path: str) -> List[Dict]:
        """解析單個卷文件"""
        poems = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取卷號
            volume_match = re.search(r'全唐詩_第(\d+)卷', os.path.basename(file_path))
            volume_num = int(volume_match.group(1)) if volume_match else 0
            
            # 分割詩歌
            poem_sections = content.split('------------------------------')
            
            for section in poem_sections:
                if not section.strip():
                    continue
                    
                lines = section.strip().split('\n')
                if len(lines) < 3:
                    continue
                
                # 提取標題
                title_line = lines[0].strip()
                if title_line and not title_line.startswith('全唐詩'):
                    current_poem = {
                        'title': title_line,
                        'volume': volume_num,
                        'content': ''
                    }
                    
                    # 提取作者
                    for line in lines[1:]:
                        if '作者:' in line:
                            author = line.split('作者:')[1].strip()
                            current_poem['author'] = author
                            break
                    
                    # 提取內容
                    content_started = False
                    for line in lines[1:]:
                        if '內容:' in line:
                            content_started = True
                            continue
                        if content_started:
                            current_poem['content'] += line + '\n'
                    
                    if current_poem.get('title') and current_poem.get('author'):
                        poems.append(current_poem)
                        
        except Exception as e:
            print(f"解析文件 {file_path} 時出錯: {e}")
            
        return poems
    
    def search_poems(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索詩歌"""
        results = []
        query = query.lower()
        
        for poem in self.poems_data:
            title = poem.get('title', '').lower()
            author = poem.get('author', '').lower()
            content = poem.get('content', '').lower()
            
            if query in title or query in author or query in content:
                results.append(poem)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_poems_by_author(self, author: str, limit: int = 10) -> List[Dict]:
        """按作者獲取詩歌"""
        results = []
        author = author.lower()
        
        for poem in self.poems_data:
            if poem.get('author', '').lower() == author:
                results.append(poem)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_poems_by_volume(self, volume: int, limit: int = 10) -> List[Dict]:
        """按卷號獲取詩歌"""
        results = []
        
        for poem in self.poems_data:
            if poem.get('volume') == volume:
                results.append(poem)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_random_poem(self) -> Optional[Dict]:
        """獲取隨機詩歌"""
        if self.poems_data:
            return random.choice(self.poems_data)
        return None
    
    def get_authors_list(self, limit: int = 50) -> List[str]:
        """獲取作者列表"""
        authors = set()
        for poem in self.poems_data:
            authors.add(poem.get('author', ''))
        
        return sorted(list(authors))[:limit]
    
    def get_statistics(self) -> Dict:
        """獲取統計信息"""
        total_poems = len(self.poems_data)
        authors = set()
        volumes = set()
        
        for poem in self.poems_data:
            authors.add(poem.get('author', ''))
            volumes.add(poem.get('volume', 0))
        
        return {
            'total_poems': total_poems,
            'total_authors': len(authors),
            'total_volumes': len(volumes),
            'avg_poems_per_author': total_poems / len(authors) if authors else 0
        }

# 初始化API
api = QuantangshiAPI()

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>全唐詩 API</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .method { background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; }
        .url { background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; margin-left: 10px; }
        .example { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #e9ecef; padding: 20px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 全唐詩 API</h1>
        <p>提供全唐詩數據的RESTful API接口</p>
        
        <h2>📊 統計信息</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_poems }}</div>
                <div>總詩歌數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_authors }}</div>
                <div>總作者數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_volumes }}</div>
                <div>總卷數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ "%.1f"|format(stats.avg_poems_per_author) }}</div>
                <div>平均每作者詩歌數</div>
            </div>
        </div>
        
        <h2>🔗 API 端點</h2>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/random</span></h3>
            <p>獲取隨機詩歌</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/random" target="_blank">/api/random</a>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/search?q=關鍵詞</span></h3>
            <p>搜索詩歌（標題、作者、內容）</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/search?q=李白" target="_blank">/api/search?q=李白</a>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/author/作者名</span></h3>
            <p>按作者獲取詩歌</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/author/李白" target="_blank">/api/author/李白</a>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/volume/卷號</span></h3>
            <p>按卷號獲取詩歌</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/volume/1" target="_blank">/api/volume/1</a>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/authors</span></h3>
            <p>獲取作者列表</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/authors" target="_blank">/api/authors</a>
            </div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span><span class="url">/api/stats</span></h3>
            <p>獲取統計信息</p>
            <div class="example">
                <strong>示例:</strong> <a href="/api/stats" target="_blank">/api/stats</a>
            </div>
        </div>
        
        <h2>📝 使用示例</h2>
        <div class="example">
            <h4>JavaScript 示例:</h4>
            <pre><code>// 獲取隨機詩歌
fetch('/api/random')
  .then(response => response.json())
  .then(data => console.log(data));

// 搜索詩歌
fetch('/api/search?q=春天')
  .then(response => response.json())
  .then(data => console.log(data));

// 獲取李白的詩歌
fetch('/api/author/李白')
  .then(response => response.json())
  .then(data => console.log(data));</code></pre>
        </div>
        
        <h2>🎯 功能特點</h2>
        <ul>
            <li>支持全文搜索（標題、作者、內容）</li>
            <li>按作者查詢詩歌</li>
            <li>按卷號查詢詩歌</li>
            <li>隨機詩歌推薦</li>
            <li>完整的統計信息</li>
            <li>RESTful API設計</li>
            <li>JSON格式響應</li>
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """主頁"""
    stats = api.get_statistics()
    return render_template_string(HTML_TEMPLATE, stats=stats)

@app.route('/api/random')
def random_poem():
    """獲取隨機詩歌"""
    poem = api.get_random_poem()
    if poem:
        return jsonify({
            'success': True,
            'data': poem
        })
    else:
        return jsonify({
            'success': False,
            'message': '沒有找到詩歌數據'
        }), 404

@app.route('/api/search')
def search_poems():
    """搜索詩歌"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({
            'success': False,
            'message': '請提供搜索關鍵詞 (q 參數)'
        }), 400
    
    results = api.search_poems(query, limit)
    return jsonify({
        'success': True,
        'query': query,
        'count': len(results),
        'data': results
    })

@app.route('/api/author/<author>')
def get_poems_by_author(author):
    """按作者獲取詩歌"""
    limit = int(request.args.get('limit', 10))
    results = api.get_poems_by_author(author, limit)
    
    return jsonify({
        'success': True,
        'author': author,
        'count': len(results),
        'data': results
    })

@app.route('/api/volume/<int:volume>')
def get_poems_by_volume(volume):
    """按卷號獲取詩歌"""
    limit = int(request.args.get('limit', 10))
    results = api.get_poems_by_volume(volume, limit)
    
    return jsonify({
        'success': True,
        'volume': volume,
        'count': len(results),
        'data': results
    })

@app.route('/api/authors')
def get_authors():
    """獲取作者列表"""
    limit = int(request.args.get('limit', 50))
    authors = api.get_authors_list(limit)
    
    return jsonify({
        'success': True,
        'count': len(authors),
        'data': authors
    })

@app.route('/api/stats')
def get_stats():
    """獲取統計信息"""
    stats = api.get_statistics()
    
    return jsonify({
        'success': True,
        'data': stats
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '端點不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服務器內部錯誤'
    }), 500

if __name__ == '__main__':
    print("🚀 啟動全唐詩 Web API...")
    print("📖 載入詩歌數據...")
    print(f"✅ 載入完成！總共 {len(api.poems_data)} 首詩歌")
    print("🌐 服務器地址: http://localhost:5000")
    print("📚 API文檔: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 