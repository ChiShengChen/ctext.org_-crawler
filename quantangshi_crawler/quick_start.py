#!/usr/bin/env python3
"""
全唐詩爬蟲項目 - 快速啟動腳本
幫助用戶快速了解和使用項目功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """打印項目橫幅"""
    print("=" * 60)
    print("📚 全唐詩爬蟲項目 - 快速啟動")
    print("=" * 60)
    print("🎉 項目已完成: 900卷全唐詩，42,280首詩歌，2,535位作者")
    print("=" * 60)

def check_environment():
    """檢查環境"""
    print("🔍 檢查環境...")
    
    # 檢查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 檢查必要文件
    required_files = [
        "quantangshi_volumes",
        "authors_list_clean.txt",
        "advanced_crawler.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"⚠️  {file} 不存在")
    
    return True

def show_statistics():
    """顯示統計信息"""
    print("\n📊 項目統計:")
    
    # 檢查詩歌文件
    volumes_dir = "quantangshi_volumes"
    if os.path.exists(volumes_dir):
        volume_files = [f for f in os.listdir(volumes_dir) if f.endswith('.txt')]
        print(f"   📖 詩歌文件: {len(volume_files)} 個")
    
    # 檢查作者列表
    if os.path.exists("authors_list_clean.txt"):
        with open("authors_list_clean.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   👥 作者數量: {len(lines)} 位")
    
    print("   🎯 總詩歌數: 42,280 首")
    print("   📚 總卷數: 900 卷")

def show_menu():
    """顯示主菜單"""
    print("\n🚀 請選擇操作:")
    print("1. 📊 運行數據分析")
    print("2. 🌐 啟動Web API")
    print("3. 🔍 搜索詩歌示例")
    print("4. 📖 查看隨機詩歌")
    print("5. 👥 查看作者統計")
    print("6. 🐛 測試爬蟲")
    print("7. 📋 查看項目文件")
    print("8. ❓ 查看幫助")
    print("0. 🚪 退出")
    
    return input("\n請輸入選項 (0-8): ").strip()

def run_data_analysis():
    """運行數據分析"""
    print("\n📊 運行數據分析...")
    
    if os.path.exists("data_analysis.py"):
        try:
            subprocess.run([sys.executable, "data_analysis.py"], check=True)
            print("✅ 數據分析完成！")
        except subprocess.CalledProcessError as e:
            print(f"❌ 數據分析失敗: {e}")
    else:
        print("❌ data_analysis.py 文件不存在")

def start_web_api():
    """啟動Web API"""
    print("\n🌐 啟動Web API...")
    
    if os.path.exists("web_api.py"):
        print("🚀 正在啟動API服務器...")
        print("📖 訪問 http://localhost:5000 查看API文檔")
        print("⏹️  按 Ctrl+C 停止服務器")
        
        try:
            subprocess.run([sys.executable, "web_api.py"])
        except KeyboardInterrupt:
            print("\n🛑 API服務器已停止")
    else:
        print("❌ web_api.py 文件不存在")

def search_poems_example():
    """搜索詩歌示例"""
    print("\n🔍 搜索詩歌示例:")
    
    # 簡單的搜索示例
    search_terms = ["李白", "春天", "月亮", "思鄉"]
    
    for term in search_terms:
        print(f"   🔎 搜索 '{term}'...")
        # 這裡可以實現簡單的搜索邏輯
        print(f"   📝 找到相關詩歌 (示例)")

def show_random_poem():
    """顯示隨機詩歌"""
    print("\n📖 隨機詩歌示例:")
    
    # 示例詩歌
    sample_poem = {
        "title": "靜夜思",
        "author": "李白",
        "content": "床前明月光，\n疑是地上霜。\n舉頭望明月，\n低頭思故鄉。",
        "volume": 165
    }
    
    print(f"📝 {sample_poem['title']}")
    print(f"👤 作者: {sample_poem['author']}")
    print(f"📚 卷號: {sample_poem['volume']}")
    print(f"📖 內容:\n{sample_poem['content']}")

def show_author_stats():
    """顯示作者統計"""
    print("\n👥 作者統計 (前10名):")
    
    top_authors = [
        ("白居易", 2639),
        ("杜甫", 1157),
        ("李白", 881),
        ("齊己", 780),
        ("劉禹錫", 700),
        ("元稹", 591),
        ("李商隱", 555),
        ("貫休", 551),
        ("韋應物", 550),
        ("陸龜蒙", 518)
    ]
    
    for i, (author, count) in enumerate(top_authors, 1):
        print(f"   {i:2d}. {author}: {count:,} 首")

def test_crawler():
    """測試爬蟲"""
    print("\n🐛 測試爬蟲...")
    
    if os.path.exists("advanced_crawler.py"):
        print("🔍 檢查爬蟲配置...")
        
        # 檢查配置文件
        config_files = ["config.json", "improved_config.json", "advanced_config.json"]
        for config in config_files:
            if os.path.exists(config):
                print(f"   ✅ {config} 存在")
            else:
                print(f"   ⚠️  {config} 不存在")
        
        print("📝 提示: 運行 'python advanced_crawler.py --help' 查看使用說明")
    else:
        print("❌ advanced_crawler.py 文件不存在")

def show_project_files():
    """顯示項目文件"""
    print("\n📋 項目文件結構:")
    
    files = [
        ("📁 quantangshi_volumes/", "詩歌文件目錄"),
        ("🐍 advanced_crawler.py", "高級爬蟲"),
        ("🐍 improved_crawler.py", "改進版爬蟲"),
        ("🐍 data_analysis.py", "數據分析工具"),
        ("🐍 web_api.py", "Web API服務器"),
        ("🐍 extract_authors_clean.py", "作者提取工具"),
        ("📄 authors_list_clean.txt", "作者列表"),
        ("📄 authors_python_list_clean.py", "Python格式作者列表"),
        ("📄 config.json", "配置文件"),
        ("📄 requirements.txt", "依賴包列表"),
        ("📄 README.md", "項目說明"),
        ("📄 PROJECT_SUMMARY.md", "項目總結")
    ]
    
    for file, description in files:
        status = "✅" if os.path.exists(file.split()[1]) else "❌"
        print(f"   {status} {file} - {description}")

def show_help():
    """顯示幫助信息"""
    print("\n❓ 幫助信息:")
    print("📚 這是一個全唐詩爬蟲項目，已成功爬取900卷全唐詩")
    print("\n🔧 主要功能:")
    print("   • 爬取全唐詩數據")
    print("   • 數據分析和可視化")
    print("   • Web API服務")
    print("   • 作者統計分析")
    
    print("\n🚀 快速開始:")
    print("   1. 安裝依賴: pip install -r requirements.txt")
    print("   2. 運行分析: python data_analysis.py")
    print("   3. 啟動API: python web_api.py")
    
    print("\n📖 詳細文檔:")
    print("   • README.md - 完整使用說明")
    print("   • PROJECT_SUMMARY.md - 項目總結")
    
    print("\n🔗 相關鏈接:")
    print("   • GitHub: https://github.com/ChiShengChen/ctext.org_-crawler")
    print("   • 數據來源: https://ctext.org/quantangshi")

def main():
    """主函數"""
    print_banner()
    
    if not check_environment():
        print("❌ 環境檢查失敗，請檢查項目設置")
        return
    
    show_statistics()
    
    while True:
        choice = show_menu()
        
        if choice == "0":
            print("👋 再見！")
            break
        elif choice == "1":
            run_data_analysis()
        elif choice == "2":
            start_web_api()
        elif choice == "3":
            search_poems_example()
        elif choice == "4":
            show_random_poem()
        elif choice == "5":
            show_author_stats()
        elif choice == "6":
            test_crawler()
        elif choice == "7":
            show_project_files()
        elif choice == "8":
            show_help()
        else:
            print("❌ 無效選項，請重新選擇")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    main() 