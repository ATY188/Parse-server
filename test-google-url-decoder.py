"""
測試 Google URL 解碼器功能
使用方法：
python test-google-url-decoder.py
"""

import requests
import json

# API 基礎 URL
BASE_URL = "http://localhost:3000"

def test_decode_google_url_post():
    """測試 POST 方法解碼 Google URL"""
    print("=" * 60)
    print("測試 1: POST 方法解碼 Google URL")
    print("=" * 60)
    
    # 測試的 Google URL
    test_urls = [
        {
            "name": "Google Alert URL",
            "url": "https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/&ct=ga&cd=CAIyHTc0NjM2OWJmZjU0MjYwYzc6Y29tLnR3OmVuOlVT&usg=AOvVaw1VohbQmBL0yFbuqkkM8Hp7"
        },
        {
            "name": "另一個 Google URL",
            "url": "https://www.google.com/url?url=https://example.com/article&sa=U&ved=123"
        },
        {
            "name": "普通 URL（非 Google）",
            "url": "https://technews.tw/2025/10/31/tsmc-news/"
        }
    ]
    
    for test in test_urls:
        print(f"\n📝 測試: {test['name']}")
        print(f"原始 URL: {test['url'][:80]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/decode-google-url",
                json={"url": test['url']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 成功！")
                print(f"   • 是否為 Google URL: {data['is_google_url']}")
                print(f"   • 是否有變化: {data['changed']}")
                print(f"   • 解碼後 URL: {data['decoded_url']}")
            else:
                print(f"❌ 失敗！HTTP {response.status_code}")
                print(f"   錯誤: {response.text}")
                
        except Exception as e:
            print(f"❌ 發生錯誤: {str(e)}")
    
    print("\n" + "=" * 60)


def test_decode_google_url_get():
    """測試 GET 方法解碼 Google URL"""
    print("\n" + "=" * 60)
    print("測試 2: GET 方法解碼 Google URL")
    print("=" * 60)
    
    test_url = "https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/&ct=ga&cd=CAIyHTc0NjM2OWJmZjU0MjYwYzc6Y29tLnR3OmVuOlVT&usg=AOvVaw1VohbQmBL0yFbuqkkM8Hp7"
    
    print(f"\n📝 測試 GET 請求")
    print(f"原始 URL: {test_url[:80]}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/decode-google-url",
            params={"url": test_url},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功！")
            print(f"   • 是否為 Google URL: {data['is_google_url']}")
            print(f"   • 是否有變化: {data['changed']}")
            print(f"   • 解碼後 URL: {data['decoded_url']}")
            
            # 顯示完整的解碼結果
            print("\n📊 完整回應：")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 失敗！HTTP {response.status_code}")
            print(f"   錯誤: {response.text}")
            
    except Exception as e:
        print(f"❌ 發生錯誤: {str(e)}")
    
    print("\n" + "=" * 60)


def test_batch_decode():
    """測試批次解碼多個 URL"""
    print("\n" + "=" * 60)
    print("測試 3: 批次解碼多個 Google URL")
    print("=" * 60)
    
    urls = [
        "https://www.google.com/url?url=https://techcrunch.com/article1&sa=U",
        "https://www.google.com/url?url=https://theverge.com/article2&sa=U",
        "https://www.google.com/url?url=https://wired.com/article3&sa=U",
        "https://example.com/direct-link",  # 普通 URL
    ]
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n📝 解碼 URL {i}/{len(urls)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/decode-google-url",
                json={"url": url},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "success": True,
                    "original": url,
                    "decoded": data['decoded_url'],
                    "changed": data['changed']
                })
                print(f"   ✅ 成功 → {data['decoded_url'][:60]}...")
            else:
                results.append({
                    "success": False,
                    "original": url,
                    "error": response.text
                })
                print(f"   ❌ 失敗")
                
        except Exception as e:
            results.append({
                "success": False,
                "original": url,
                "error": str(e)
            })
            print(f"   ❌ 錯誤: {str(e)}")
    
    # 統計結果
    success_count = sum(1 for r in results if r['success'])
    changed_count = sum(1 for r in results if r.get('changed', False))
    
    print(f"\n📊 批次處理結果：")
    print(f"   • 總數: {len(urls)}")
    print(f"   • 成功: {success_count}")
    print(f"   • 解碼變化: {changed_count}")
    
    print("\n" + "=" * 60)


def test_edge_cases():
    """測試邊界情況"""
    print("\n" + "=" * 60)
    print("測試 4: 邊界情況測試")
    print("=" * 60)
    
    edge_cases = [
        {
            "name": "空的 url 參數",
            "url": "https://www.google.com/url?url=&sa=U"
        },
        {
            "name": "包含中文的 URL",
            "url": "https://www.google.com/url?url=https://technews.tw/2025/台積電新聞&sa=U"
        },
        {
            "name": "多層編碼的 URL",
            "url": "https://www.google.com/url?url=https%3A%2F%2Fexample.com%2Farticle%3Fid%3D123&sa=U"
        }
    ]
    
    for test in edge_cases:
        print(f"\n📝 測試: {test['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/decode-google-url",
                json={"url": test['url']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功解碼")
                print(f"   • 解碼後: {data['decoded_url']}")
            else:
                print(f"   ⚠️ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 錯誤: {str(e)}")
    
    print("\n" + "=" * 60)


def main():
    """執行所有測試"""
    print("\n🚀 開始測試 Google URL 解碼器")
    print(f"API 地址: {BASE_URL}")
    
    # 檢查 API 是否運行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API 伺服器運行中\n")
        else:
            print("⚠️ API 伺服器回應異常\n")
    except:
        print("❌ 無法連接到 API 伺服器")
        print("請確保伺服器已啟動：python parser-server.py\n")
        return
    
    # 執行測試
    test_decode_google_url_post()
    test_decode_google_url_get()
    test_batch_decode()
    test_edge_cases()
    
    print("\n✨ 所有測試完成！")


if __name__ == "__main__":
    main()

