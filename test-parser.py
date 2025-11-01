"""
測試腳本 - 用於測試 Parser API (Python 版本)
使用方式：python test-parser.py [URL]
"""

import sys
import asyncio
import httpx
from datetime import datetime

# 預設測試 URL
test_url = sys.argv[1] if len(sys.argv) > 1 else 'https://www.bbc.com/news'
api_url = 'http://localhost:3000/api/parse'

print('🧪 開始測試 Parser API (Python 版本)...\n')
print(f'📰 目標 URL: {test_url}')
print(f'🔗 API 端點: {api_url}\n')


async def test_parser():
    """測試解析功能"""
    try:
        print('⏳ 正在解析網頁...')
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                json={'url': test_url}
            )
        
        if response.status_code != 200:
            error = response.json()
            print(f'❌ API 錯誤: {error}')
            return
        
        result = response.json()
        
        print('\n✅ 解析成功！\n')
        print('📋 解析結果：')
        print('=' * 60)
        
        data = result.get('data', {})
        
        print(f'📌 標題: {data.get("title") or "無"}')
        print(f'✍️  作者: {data.get("author") or "無"}')
        print(f'📅 發布日期: {data.get("date_published") or "無"}')
        print(f'🌐 網域: {data.get("domain") or "無"}')
        print(f'🏷️  分類: {data.get("categories") or "無"}')
        print(f'🔖 標籤: {data.get("tags") or "無"}')
        print(f'📝 字數: {data.get("word_count", 0)}')
        print(f'🌍 語言: {data.get("language") or "無"}')
        
        if data.get('description'):
            print(f'\n💬 描述:\n{data["description"]}')
        
        if data.get('excerpt'):
            print(f'\n📄 摘要:\n{data["excerpt"]}')
        
        print('\n' + '=' * 60)
        
        # 顯示文字內容的前 300 個字元
        if data.get('text_content'):
            text_preview = data['text_content'][:300]
            print(f'\n📖 內容預覽 (純文字):\n{text_preview}...\n')
        
        # 顯示 HTML 內容的長度
        if data.get('content'):
            content_length = len(data['content'])
            print(f'📦 HTML 內容長度: {content_length} 字元')
        
        print('\n✨ 測試完成！')
        
    except httpx.TimeoutException:
        print('\n❌ 請求超時')
        print('\n💡 提示：')
        print('1. 增加超時時間')
        print('2. 確認網路連線正常')
        print('3. 嘗試其他 URL\n')
        
    except httpx.ConnectError:
        print('\n❌ 無法連接到 API 伺服器')
        print('\n💡 提示：')
        print('1. 確認伺服器已啟動：python parser-server.py')
        print('2. 確認埠號正確（預設 3000）')
        print('3. 檢查防火牆設定\n')
        
    except Exception as e:
        print(f'\n❌ 測試失敗: {str(e)}')
        print('\n💡 提示：')
        print('1. 確認伺服器已啟動：python parser-server.py')
        print('2. 確認網路連線正常')
        print('3. 確認目標 URL 可訪問\n')


if __name__ == '__main__':
    # 執行測試
    asyncio.run(test_parser())

