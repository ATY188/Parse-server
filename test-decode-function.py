"""
直接測試 Google URL 解碼函數（不需要啟動伺服器）
"""

from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional


def decode_google_url(google_url: str) -> Optional[str]:
    """
    從 Google 重定向 URL 中提取真實的目標 URL
    """
    try:
        # 解析 URL
        parsed = urlparse(google_url)
        
        # 檢查是否為 Google URL
        if 'google.com' not in parsed.netloc:
            # 不是 Google URL，直接返回原 URL
            return google_url
        
        # 解析查詢參數
        query_params = parse_qs(parsed.query)
        
        # 嘗試從不同的參數中提取 URL
        # 常見參數：url, q, u
        for param in ['url', 'q', 'u']:
            if param in query_params and query_params[param]:
                decoded_url = unquote(query_params[param][0])
                # 確保是完整的 URL
                if decoded_url.startswith(('http://', 'https://')):
                    return decoded_url
        
        # 如果沒有找到，返回原 URL
        return google_url
        
    except Exception as e:
        # 解析失敗，返回原 URL
        return google_url


def test_decode():
    """測試解碼函數"""
    print("=" * 80)
    print("🧪 測試 Google URL 解碼函數")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "您的 Google Alert URL",
            "input": "https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/&ct=ga&cd=CAIyHTc0NjM2OWJmZjU0MjYwYzc6Y29tLnR3OmVuOlVT&usg=AOvVaw1VohbQmBL0yFbuqkkM8Hp7",
            "expected": "https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/"
        },
        {
            "name": "簡單的 Google URL",
            "input": "https://www.google.com/url?url=https://example.com/article&sa=U",
            "expected": "https://example.com/article"
        },
        {
            "name": "使用 q 參數",
            "input": "https://www.google.com/url?q=https://technews.tw/article",
            "expected": "https://technews.tw/article"
        },
        {
            "name": "URL 編碼的網址",
            "input": "https://www.google.com/url?url=https%3A%2F%2Fexample.com%2Farticle%3Fid%3D123",
            "expected": "https://example.com/article?id=123"
        },
        {
            "name": "普通 URL（非 Google）",
            "input": "https://technews.tw/2025/10/31/tsmc-news/",
            "expected": "https://technews.tw/2025/10/31/tsmc-news/"
        },
        {
            "name": "台積電相關新聞",
            "input": "https://www.google.com/url?url=https://www.bnext.com.tw/article/80198/tsmc-2024",
            "expected": "https://www.bnext.com.tw/article/80198/tsmc-2024"
        }
    ]
    
    success_count = 0
    fail_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {test['name']}")
        print("-" * 80)
        
        result = decode_google_url(test['input'])
        
        # 顯示結果
        print(f"📥 輸入：")
        if len(test['input']) > 100:
            print(f"   {test['input'][:100]}...")
        else:
            print(f"   {test['input']}")
        
        print(f"📤 輸出：")
        print(f"   {result}")
        
        print(f"✅ 預期：")
        print(f"   {test['expected']}")
        
        # 檢查是否正確
        if result == test['expected']:
            print("🎉 結果：✅ 正確！")
            success_count += 1
        else:
            print("❌ 結果：失敗！")
            fail_count += 1
    
    # 總結
    print("\n" + "=" * 80)
    print("📊 測試總結")
    print("=" * 80)
    print(f"總測試數：{len(test_cases)}")
    print(f"✅ 成功：{success_count}")
    print(f"❌ 失敗：{fail_count}")
    print(f"成功率：{success_count / len(test_cases) * 100:.1f}%")
    
    if fail_count == 0:
        print("\n🎉 所有測試通過！")
    else:
        print(f"\n⚠️ 有 {fail_count} 個測試失敗")
    
    print("=" * 80)


if __name__ == "__main__":
    test_decode()

