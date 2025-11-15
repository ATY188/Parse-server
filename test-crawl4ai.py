#!/usr/bin/env python3
"""
測試 Crawl4AI 對困難網站的爬取能力
對比之前失敗的網站
"""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import time

# 測試網站列表（之前失敗的）
FAILED_WEBSITES = [
    {
        "name": "Japan Times (Cloudflare)",
        "url": "https://www.japantimes.co.jp/news/2025/11/14/world/ukraine-uk-spy-chief/",
        "expected": "Intel shows Putin not ready"
    },
    {
        "name": "Reuters (401 Forbidden)",
        "url": "https://www.reuters.com/business/wall-st-week-ahead-skittish-tech-stock-investors-turn-nvidia-results-next-cues-2025-11-14/",
        "expected": "nvidia"
    },
    {
        "name": "KOIN News (403 Forbidden)",
        "url": "https://www.koin.com/news/oregon/intel-laying-off-hundreds-of-employees-in-oregon/",
        "expected": "Intel laying off"
    }
]

# 成功網站（作為對照組）
SUCCESS_WEBSITES = [
    {
        "name": "風傳媒 (成功過)",
        "url": "https://www.storm.mg/article/11081146",
        "expected": "輝達"
    },
    {
        "name": "非凡新聞 (成功過)",
        "url": "https://news.ustv.com.tw/newsdetail/20251113A001001",
        "expected": "台積電"
    }
]

async def test_crawl4ai(url, name, expected_keyword):
    """使用 Crawl4AI 測試單個網站"""
    print(f"\n{'='*80}")
    print(f"🧪 測試: {name}")
    print(f"🔗 URL: {url[:60]}...")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # 配置瀏覽器（使用 patchright 反偵測模式）
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-blink-features=AutomationControlled"]
        )
        
        # 配置爬取器（啟用 magic 模式自動處理反爬）
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="networkidle",
            magic=True,  # 🔥 啟用自動反爬繞過
            page_timeout=30000,  # 30 秒超時
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )
            
            elapsed = time.time() - start_time
            
            # 檢查結果
            if result.success:
                content_length = len(result.markdown or "")
                title = result.metadata.get('title', 'N/A')
                
                # 檢查是否包含預期關鍵字
                has_keyword = expected_keyword.lower() in (result.markdown or "").lower()
                
                print(f"✅ 成功解析")
                print(f"⏱️  時間: {elapsed:.2f} 秒")
                print(f"📰 標題: {title[:80]}")
                print(f"📏 內容長度: {content_length} 字元")
                print(f"🔍 關鍵字 '{expected_keyword}': {'✅ 找到' if has_keyword else '❌ 未找到'}")
                
                # 顯示前 200 字
                preview = (result.markdown or "")[:200].replace('\n', ' ')
                print(f"📄 預覽: {preview}...")
                
                return {
                    "success": True,
                    "name": name,
                    "url": url,
                    "time": elapsed,
                    "content_length": content_length,
                    "has_keyword": has_keyword,
                    "title": title
                }
            else:
                print(f"❌ 解析失敗")
                print(f"⏱️  時間: {elapsed:.2f} 秒")
                print(f"❗ 錯誤: {result.error_message or 'Unknown error'}")
                
                return {
                    "success": False,
                    "name": name,
                    "url": url,
                    "time": elapsed,
                    "error": result.error_message
                }
                
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 異常錯誤")
        print(f"⏱️  時間: {elapsed:.2f} 秒")
        print(f"💥 錯誤: {str(e)}")
        
        return {
            "success": False,
            "name": name,
            "url": url,
            "time": elapsed,
            "error": str(e)
        }

async def main():
    """主測試流程"""
    print("\n" + "="*80)
    print("🚀 Crawl4AI 能力測試")
    print("="*80)
    
    results = []
    
    # 測試失敗網站
    print("\n📋 第一組：之前失敗的網站（Cloudflare、403、401）")
    for site in FAILED_WEBSITES:
        result = await test_crawl4ai(site["url"], site["name"], site["expected"])
        results.append(result)
        await asyncio.sleep(2)  # 避免請求太快
    
    # 測試成功網站（對照組）
    print("\n📋 第二組：之前成功的網站（驗證基本功能）")
    for site in SUCCESS_WEBSITES:
        result = await test_crawl4ai(site["url"], site["name"], site["expected"])
        results.append(result)
        await asyncio.sleep(2)
    
    # 統計結果
    print("\n" + "="*80)
    print("📊 測試結果統計")
    print("="*80)
    
    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    failed_count = total - success_count
    
    print(f"\n總測試數: {total}")
    print(f"✅ 成功: {success_count} ({success_count/total*100:.1f}%)")
    print(f"❌ 失敗: {failed_count} ({failed_count/total*100:.1f}%)")
    
    print("\n詳細結果:")
    for i, r in enumerate(results, 1):
        status = "✅" if r["success"] else "❌"
        print(f"{i}. {status} {r['name']}")
        print(f"   時間: {r['time']:.2f}s")
        if r["success"]:
            print(f"   內容: {r['content_length']} 字元")
            print(f"   關鍵字: {'✅' if r.get('has_keyword') else '❌'}")
        else:
            print(f"   錯誤: {r.get('error', 'Unknown')[:80]}")
    
    print("\n" + "="*80)
    print("🎯 結論")
    print("="*80)
    
    # 分析失敗網站的表現
    failed_sites_results = results[:len(FAILED_WEBSITES)]
    failed_sites_success = sum(1 for r in failed_sites_results if r["success"])
    
    print(f"\n🔥 之前失敗的網站:")
    print(f"   成功突破: {failed_sites_success}/{len(FAILED_WEBSITES)} 個")
    print(f"   成功率: {failed_sites_success/len(FAILED_WEBSITES)*100:.1f}%")
    
    if failed_sites_success > 0:
        print("\n✨ Crawl4AI 展現了突破反爬機制的能力！")
    else:
        print("\n⚠️ Crawl4AI 仍然無法突破這些網站的防護")
    
    # 輸出建議
    print("\n💡 建議:")
    if failed_sites_success >= 2:
        print("   ✅ 值得整合到你的 Parser API")
        print("   ✅ 可以處理 Cloudflare 等反爬機制")
    elif failed_sites_success == 1:
        print("   ⚠️ 有潛力但效果有限")
        print("   ⚠️ 建議針對特定網站使用")
    else:
        print("   ❌ 不建議完全替換現有方案")
        print("   ✅ 建議保持 RSS 降級策略")

if __name__ == "__main__":
    asyncio.run(main())

