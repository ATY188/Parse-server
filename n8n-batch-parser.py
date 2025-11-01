"""
n8n 批次處理腳本 (Python 版本)
用途：批次解析 n8n 產出的文章列表

使用方式：
python n8n-batch-parser.py input.json output.json

輸入格式 (input.json)：
[
  {"url": "https://example.com/article1", "id": "001"},
  {"url": "https://example.com/article2", "id": "002"}
]
"""

import sys
import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import os

# 設定
API_URL = os.getenv('PARSER_API_URL', 'http://localhost:3000/api/parse')
DELAY_MS = int(os.getenv('DELAY_MS', '2000'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

print('📋 n8n 批次文章解析器 (Python 版本)')
print('=' * 60)
print(f'🔗 API 端點: {API_URL}')
print(f'⏱️  請求間隔: {DELAY_MS}ms')
print(f'🔄 最大重試: {MAX_RETRIES} 次\n')


async def parse_article(
    client: httpx.AsyncClient,
    article_data: Dict[str, Any],
    retry_count: int = 0
) -> Dict[str, Any]:
    """
    解析單一文章
    
    Args:
        client: httpx 客戶端
        article_data: 文章資料（包含 url）
        retry_count: 當前重試次數
        
    Returns:
        解析結果
    """
    try:
        response = await client.post(
            API_URL,
            json={'url': article_data['url']},
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        result = response.json()
        
        if result.get('success'):
            return {
                **article_data,
                'success': True,
                'parsed_data': result['data'],
                'parsed_at': datetime.now().isoformat()
            }
        else:
            raise Exception('解析失敗')
            
    except Exception as e:
        print(f"❌ 解析失敗 (第 {retry_count + 1} 次): {article_data['url']}")
        print(f"   錯誤: {str(e)}")
        
        # 重試邏輯
        if retry_count < MAX_RETRIES:
            print(f"   ⏳ 等待 {DELAY_MS * 2}ms 後重試...")
            await asyncio.sleep((DELAY_MS * 2) / 1000)
            return await parse_article(client, article_data, retry_count + 1)
        
        return {
            **article_data,
            'success': False,
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


async def batch_parse(input_file: str, output_file: str):
    """
    批次處理文章
    
    Args:
        input_file: 輸入檔案路徑
        output_file: 輸出檔案路徑
    """
    try:
        # 讀取輸入檔案
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"❌ 找不到輸入檔案: {input_file}")
            sys.exit(1)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        if not isinstance(input_data, list):
            print('❌ 輸入檔案格式錯誤：必須是陣列')
            sys.exit(1)
        
        print(f'📥 載入 {len(input_data)} 篇文章待解析\n')
        
        results = []
        success_count = 0
        fail_count = 0
        
        # 建立 HTTP 客戶端
        async with httpx.AsyncClient() as client:
            # 逐一處理每篇文章
            for i, article in enumerate(input_data):
                progress = f"[{i + 1}/{len(input_data)}]"
                
                print(f"{progress} 🔍 解析中: {article['url']}")
                
                result = await parse_article(client, article)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    parsed_data = result['parsed_data']
                    title = parsed_data.get('title', '無標題')
                    word_count = parsed_data.get('word_count', 0)
                    author = parsed_data.get('author', '未知')
                    
                    print(f"{progress} ✅ 成功: {title}")
                    print(f"{progress}    字數: {word_count}, 作者: {author}")
                else:
                    fail_count += 1
                    print(f"{progress} ❌ 失敗")
                
                # 避免請求過快（最後一個不需要延遲）
                if i < len(input_data) - 1:
                    await asyncio.sleep(DELAY_MS / 1000)
                
                print()  # 空行分隔
        
        # 儲存結果
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print('=' * 60)
        print('✨ 批次處理完成！')
        print(f'📊 統計資訊:')
        print(f'   總計: {len(input_data)} 篇')
        print(f'   成功: {success_count} 篇 ({success_count/len(input_data)*100:.1f}%)')
        print(f'   失敗: {fail_count} 篇 ({fail_count/len(input_data)*100:.1f}%)')
        print(f'\n💾 結果已儲存至: {output_file}')
        
        # 如果有失敗的項目，另外儲存失敗清單
        if fail_count > 0:
            failed_items = [r for r in results if not r['success']]
            failed_file = str(output_path).replace('.json', '-failed.json')
            
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_items, f, ensure_ascii=False, indent=2)
            
            print(f'⚠️  失敗項目已儲存至: {failed_file}')
        
    except Exception as e:
        print(f'\n❌ 批次處理發生錯誤: {str(e)}')
        sys.exit(1)


def main():
    """主程式"""
    if len(sys.argv) < 3:
        print('使用方式：')
        print('  python n8n-batch-parser.py <輸入檔案.json> <輸出檔案.json>')
        print('')
        print('範例：')
        print('  python n8n-batch-parser.py articles.json results.json')
        print('')
        print('環境變數：')
        print('  PARSER_API_URL - Parser API 位址（預設: http://localhost:3000/api/parse）')
        print('  DELAY_MS - 請求間隔毫秒數（預設: 2000）')
        print('  MAX_RETRIES - 最大重試次數（預設: 3）')
        print('')
        print('輸入檔案格式：')
        print('  [')
        print('    {"url": "https://example.com/article1", "id": "001"},')
        print('    {"url": "https://example.com/article2", "id": "002"}')
        print('  ]')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # 執行批次處理
    asyncio.run(batch_parse(input_file, output_file))


if __name__ == '__main__':
    main()

