"""
測試三個新聞網站的爬取功能
使用部署在 Railway 的 API
"""

import requests
import json
import time

# Railway 部署的 API
API_BASE_URL = "https://web-production-32568.up.railway.app"

def test_parse_url(url, name):
    """測試單一 URL 的解析"""
    print(f"\n{'='*80}")
    print(f"📰 測試網站：{name}")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"\n⏳ 開始解析...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/parse",
            json={"url": url},
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                article_data = data.get('data', {})
                
                print(f"✅ 解析成功！（耗時：{elapsed_time:.2f} 秒）")
                print(f"\n📋 文章資訊：")
                print(f"   標題：{article_data.get('title', '無標題')}")
                print(f"   作者：{article_data.get('author', '無作者資訊')}")
                print(f"   日期：{article_data.get('date_published', '無日期')}")
                print(f"   字數：{article_data.get('word_count', 0)} 字")
                
                # 顯示內容預覽
                content = article_data.get('content', '')
                text_content = article_data.get('text_content', '')
                
                if text_content:
                    preview = text_content[:200].replace('\n', ' ')
                    print(f"\n📝 內容預覽（前 200 字）：")
                    print(f"   {preview}...")
                elif content:
                    # 簡單移除 HTML 標籤來預覽
                    import re
                    text = re.sub(r'<[^>]+>', '', content)
                    preview = text[:200].replace('\n', ' ')
                    print(f"\n📝 內容預覽（前 200 字）：")
                    print(f"   {preview}...")
                else:
                    print(f"\n⚠️ 無內容")
                
                return {
                    "success": True,
                    "name": name,
                    "url": url,
                    "title": article_data.get('title'),
                    "word_count": article_data.get('word_count', 0),
                    "time": elapsed_time
                }
            else:
                print(f"❌ API 回應失敗")
                print(f"   訊息：{data.get('error', '未知錯誤')}")
                return {
                    "success": False,
                    "name": name,
                    "error": data.get('error', '未知錯誤')
                }
        else:
            print(f"❌ HTTP 錯誤：{response.status_code}")
            print(f"   回應：{response.text[:200]}")
            return {
                "success": False,
                "name": name,
                "error": f"HTTP {response.status_code}"
            }
            
    except requests.Timeout:
        print(f"❌ 請求超時（>30秒）")
        return {
            "success": False,
            "name": name,
            "error": "請求超時"
        }
    except Exception as e:
        print(f"❌ 發生錯誤：{str(e)}")
        return {
            "success": False,
            "name": name,
            "error": str(e)
        }


def main():
    """執行測試"""
    print("🚀 開始測試三個新聞網站的爬取功能")
    print(f"API 端點：{API_BASE_URL}")
    
    # 先測試 API 是否可用
    print(f"\n⏳ 檢查 API 狀態...")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print(f"✅ API 伺服器運行正常")
        else:
            print(f"⚠️ API 伺服器回應異常：{health_response.status_code}")
    except Exception as e:
        print(f"❌ 無法連接到 API：{str(e)}")
        return
    
    # 測試的網站
    test_sites = [
        {
            "name": "MSN - AMD 分析",
            "url": "https://www.msn.com/en-us/money/savingandinvesting/amd-s-results-and-guidance-were-good-but-wall-street-is-waiting-for-2026/ar-AA1PR5Qh?ocid=finance-verthp-feeds"
        },
        {
            "name": "Investing.com - 裁員新聞",
            "url": "https://www.investing.com/news/stock-market-news/factboxus-companies-step-up-job-cuts-amid-uncertain-economy-4333313"
        },
        {
            "name": "Silicon Valley - HPE & Hitachi 裁員",
            "url": "https://www.siliconvalley.com/2025/11/05/economy-jobs-tech-layoff-hpe-hitachi-san-jose-south-bay-web-software/"
        }
    ]
    
    # 執行測試
    results = []
    for site in test_sites:
        result = test_parse_url(site["url"], site["name"])
        results.append(result)
        
        # 避免請求過快
        if site != test_sites[-1]:
            print(f"\n⏳ 等待 2 秒後繼續...")
            time.sleep(2)
    
    # 顯示總結
    print(f"\n{'='*80}")
    print(f"📊 測試總結")
    print(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n總測試數：{len(results)}")
    print(f"✅ 成功：{success_count}")
    print(f"❌ 失敗：{fail_count}")
    print(f"成功率：{success_count / len(results) * 100:.1f}%")
    
    # 成功的網站
    if success_count > 0:
        print(f"\n✅ 成功解析的網站：")
        for r in results:
            if r['success']:
                print(f"   • {r['name']}")
                print(f"     標題：{r.get('title', '無')}")
                print(f"     字數：{r.get('word_count', 0)} 字")
                print(f"     耗時：{r.get('time', 0):.2f} 秒")
    
    # 失敗的網站
    if fail_count > 0:
        print(f"\n❌ 解析失敗的網站：")
        for r in results:
            if not r['success']:
                print(f"   • {r['name']}")
                print(f"     錯誤：{r.get('error', '未知')}")
    
    # 建議
    print(f"\n{'='*80}")
    print(f"💡 建議")
    print(f"{'='*80}")
    
    if success_count == len(results):
        print("🎉 所有網站都能成功解析！")
        print("✅ 您的 parser API 運作完美")
        print("✅ 可以放心在 n8n 中使用")
    elif success_count > 0:
        print("⚠️ 部分網站解析成功，部分失敗")
        print("💡 失敗的網站可能需要使用 /api/parse-dynamic（Playwright）")
        print("⚠️ 但 Playwright 會消耗較多記憶體，請謹慎使用")
    else:
        print("❌ 所有網站都解析失敗")
        print("💡 請檢查 API 是否正常運作")
        print("💡 或者這些網站可能有反爬蟲機制")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()









