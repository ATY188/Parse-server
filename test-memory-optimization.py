#!/usr/bin/env python3
"""
記憶體優化測試腳本
測試優化後的 Parser API 的速度和功能
"""

import httpx
import asyncio
import time
from datetime import datetime

# 測試 URL（包含靜態和動態網站）
TEST_URLS = [
    # 動態網站（使用 Playwright）
    {
        "url": "https://www.storm.mg/article/5032746",
        "name": "風傳媒",
        "type": "dynamic"
    },
    {
        "url": "https://technews.tw/2024/11/14/tsmc-arizona-expansion/",
        "name": "科技新報",
        "type": "static"
    },
    {
        "url": "https://money.udn.com/money/story/5612/8344895",
        "name": "經濟日報",
        "type": "static"
    }
]

API_URL = "http://localhost:3000/api/parse"

async def test_single_url(url_data: dict) -> dict:
    """測試單個 URL"""
    print(f"\n{'='*60}")
    print(f"🧪 測試: {url_data['name']} ({url_data['type']})")
    print(f"🔗 URL: {url_data['url']}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                API_URL,
                json={"url": url_data['url']}
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    parsed = data.get('data', {})
                    title = parsed.get('title', '無標題')
                    word_count = parsed.get('word_count', 0)
                    method = parsed.get('rendering_method', 'static')
                    routing = data.get('routing_decision', 'unknown')
                    
                    print(f"\n✅ 解析成功!")
                    print(f"   標題: {title[:50]}...")
                    print(f"   字數: {word_count}")
                    print(f"   方法: {method}")
                    print(f"   路由: {routing}")
                    print(f"   ⏱️  耗時: {elapsed:.2f} 秒")
                    
                    return {
                        "name": url_data['name'],
                        "success": True,
                        "elapsed": elapsed,
                        "method": method,
                        "word_count": word_count
                    }
                else:
                    print(f"\n❌ 解析失敗")
                    return {
                        "name": url_data['name'],
                        "success": False,
                        "elapsed": elapsed,
                        "error": "API returned success=False"
                    }
            else:
                print(f"\n❌ HTTP 錯誤: {response.status_code}")
                return {
                    "name": url_data['name'],
                    "success": False,
                    "elapsed": elapsed,
                    "error": f"HTTP {response.status_code}"
                }
                
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 錯誤: {str(e)}")
        return {
            "name": url_data['name'],
            "success": False,
            "elapsed": elapsed,
            "error": str(e)
        }

async def main():
    """主測試流程"""
    print("\n" + "="*60)
    print("🚀 Parser API 記憶體優化測試")
    print("="*60)
    print(f"📅 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 API 端點: {API_URL}")
    print(f"📊 測試數量: {len(TEST_URLS)} 個網站")
    print("="*60)
    
    # 先檢查 API 是否在線
    print("\n🔍 檢查 API 健康狀態...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:3000/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ API 在線!")
                print(f"   版本: {health.get('version')}")
                print(f"   服務: {health.get('service')}")
                features = health.get('features', [])
                if 'memory-optimized' in features:
                    print(f"   ✨ 記憶體優化: 已啟用")
                if 'concurrency-control' in features:
                    print(f"   🔒 並發控制: 已啟用")
            else:
                print(f"❌ API 健康檢查失敗: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ 無法連接到 API: {str(e)}")
        print(f"\n💡 請確認 Parser API 是否正在運行:")
        print(f"   python parser-server.py")
        return
    
    # 執行測試
    results = []
    for url_data in TEST_URLS:
        result = await test_single_url(url_data)
        results.append(result)
        
        # 在測試之間稍作延遲
        await asyncio.sleep(2)
    
    # 輸出總結
    print("\n" + "="*60)
    print("📊 測試總結")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"\n✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失敗: {total_count - success_count}/{total_count}")
    
    if success_count > 0:
        print(f"\n⏱️  速度統計:")
        static_times = [r['elapsed'] for r in results if r['success'] and r.get('method') == 'static']
        dynamic_times = [r['elapsed'] for r in results if r['success'] and r.get('method') == 'playwright']
        
        if static_times:
            avg_static = sum(static_times) / len(static_times)
            print(f"   靜態網站平均: {avg_static:.2f} 秒")
        
        if dynamic_times:
            avg_dynamic = sum(dynamic_times) / len(dynamic_times)
            print(f"   動態網站平均: {avg_dynamic:.2f} 秒")
    
    print(f"\n📝 詳細結果:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        name = result['name']
        elapsed = result['elapsed']
        if result['success']:
            method = result.get('method', 'unknown')
            wc = result.get('word_count', 0)
            print(f"   {status} {name}: {elapsed:.2f}秒 ({method}, {wc} 字)")
        else:
            error = result.get('error', 'unknown')
            print(f"   {status} {name}: {error}")
    
    print("\n" + "="*60)
    print("🎉 測試完成!")
    print("="*60)
    
    # 給出建議
    if success_count == total_count:
        print("\n✅ 所有測試通過！優化成功！")
        print("\n💡 下一步:")
        print("   1. 在 n8n 中測試完整 workflow")
        print("   2. 考慮部署到 Railway Hobby ($5/月)")
        print("   3. 監控 Railway 記憶體使用")
    elif success_count > 0:
        print("\n⚠️  部分測試通過，請檢查失敗的項目")
    else:
        print("\n❌ 所有測試失敗，請檢查:")
        print("   1. Parser API 是否正確啟動")
        print("   2. 是否使用了優化版代碼")
        print("   3. Playwright 是否正確安裝")

if __name__ == "__main__":
    asyncio.run(main())

