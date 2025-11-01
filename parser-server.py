"""
網頁內容解析器 API - Python 版本
使用 FastAPI + trafilatura

安裝套件：
pip install fastapi uvicorn trafilatura httpx python-multipart

啟動方式：
python parser-server.py
或
uvicorn parser-server:app --reload --port 3000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, Any
import trafilatura
import httpx
from datetime import datetime
import uvicorn

# 建立 FastAPI 應用
app = FastAPI(
    title="網頁內容解析器 API",
    description="使用 trafilatura 自動提取網頁文章內容",
    version="1.0.0"
)

# 請求資料模型
class ParseRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v

class ParseWebhookRequest(BaseModel):
    url: str
    webhook_url: str
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('url', 'webhook_url')
    def validate_urls(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v


# 首頁路由
@app.get("/")
async def root():
    """API 首頁 - 顯示可用端點"""
    return {
        "message": "歡迎使用網頁內容解析器 API (Python 版本)",
        "framework": "FastAPI + trafilatura",
        "endpoints": {
            "parse": {
                "method": "POST",
                "path": "/api/parse",
                "body": {
                    "url": "要解析的網頁 URL"
                },
                "description": "解析指定 URL 的網頁內容（同步回傳）"
            },
            "parseGet": {
                "method": "GET",
                "path": "/api/parse?url=YOUR_URL",
                "description": "使用 GET 方法解析網頁內容"
            },
            "parseWebhook": {
                "method": "POST",
                "path": "/api/parse-webhook",
                "body": {
                    "url": "要解析的網頁 URL",
                    "webhook_url": "n8n webhook URL",
                    "metadata": "(選填) 額外資料"
                },
                "description": "解析網頁並回調 webhook（適用於 n8n 整合）"
            },
            "docs": {
                "method": "GET",
                "path": "/docs",
                "description": "Swagger UI 互動式 API 文件"
            }
        },
        "examples": [
            'POST /api/parse with body: {"url": "https://example.com/article"}',
            'GET /api/parse?url=https://example.com/article',
            'POST /api/parse-webhook with body: {"url": "https://example.com/article", "webhook_url": "https://your-n8n.com/webhook/..."}'
        ],
        "documentation": "訪問 /docs 查看完整 API 文件"
    }


async def fetch_and_parse(url: str) -> Dict[str, Any]:
    """
    下載並解析網頁內容
    
    Args:
        url: 要解析的網頁 URL
        
    Returns:
        解析後的資料字典
        
    Raises:
        HTTPException: 當下載或解析失敗時
    """
    try:
        # 下載網頁內容
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            html_content = response.text
        
        # 使用 trafilatura 解析內容
        # 提取純文字內容
        text_content = trafilatura.extract(
            html_content,
            include_comments=False,
            include_tables=True,
            no_fallback=False
        )
        
        # 提取完整資訊（包含元數據）
        metadata = trafilatura.extract_metadata(html_content)
        
        # 提取 HTML 格式的內容（保留格式）
        html_formatted = trafilatura.extract(
            html_content,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            output_format='xml'  # 或使用 'xml' 來保留更多結構
        )
        
        # 整理回傳資料
        parsed_data = {
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "date_published": metadata.date if metadata else None,
            "url": metadata.url if metadata else url,
            "domain": metadata.sitename if metadata else None,
            "description": metadata.description if metadata else None,
            "categories": metadata.categories if metadata else None,
            "tags": metadata.tags if metadata else None,
            "content": html_formatted or text_content,  # HTML 格式優先
            "text_content": text_content,  # 純文字版本
            "excerpt": text_content[:200] + "..." if text_content and len(text_content) > 200 else text_content,
            "word_count": len(text_content.split()) if text_content else 0,
            "language": metadata.language if metadata else None
        }
        
        return parsed_data
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"下載網頁失敗: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解析網頁失敗: {str(e)}"
        )


@app.post("/api/parse")
async def parse_url(request: ParseRequest):
    """
    POST 方法：解析網頁內容
    
    Args:
        request: 包含 url 的請求物件
        
    Returns:
        解析後的網頁內容
    """
    print(f"正在解析: {request.url}")
    
    try:
        parsed_data = await fetch_and_parse(request.url)
        
        return {
            "success": True,
            "data": parsed_data
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"解析錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"解析網頁時發生錯誤: {str(e)}"
        )


@app.get("/api/parse")
async def parse_url_get(url: str):
    """
    GET 方法：解析網頁內容（透過 query string）
    
    Args:
        url: 要解析的網頁 URL
        
    Returns:
        解析後的網頁內容
    """
    if not url:
        raise HTTPException(
            status_code=400,
            detail="請在 URL 參數中提供要解析的網址"
        )
    
    print(f"正在解析 (GET): {url}")
    
    try:
        parsed_data = await fetch_and_parse(url)
        
        return {
            "success": True,
            "data": parsed_data
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"解析錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"解析網頁時發生錯誤: {str(e)}"
        )


async def process_and_webhook(url: str, webhook_url: str, metadata: Dict[str, Any]):
    """
    背景任務：解析網頁並回調 webhook
    
    Args:
        url: 要解析的網頁 URL
        webhook_url: webhook 回調 URL
        metadata: 額外的元數據
    """
    print(f"正在解析 (webhook 模式): {url}")
    
    try:
        # 解析網頁
        parsed_data = await fetch_and_parse(url)
        
        # 準備回調資料
        webhook_data = {
            "success": True,
            "original_url": url,
            "metadata": metadata,
            "parsed_data": parsed_data,
            "parsed_at": datetime.now().isoformat()
        }
        
        # 回調 webhook
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=webhook_data
            )
            
            if response.status_code == 200:
                print(f"✅ Webhook 回調成功: {webhook_url}")
            else:
                print(f"❌ Webhook 回調失敗 ({response.status_code}): {webhook_url}")
                
    except Exception as e:
        print(f"解析或回調錯誤: {str(e)}")
        
        # 嘗試回調錯誤訊息
        try:
            error_data = {
                "success": False,
                "original_url": url,
                "metadata": metadata,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(webhook_url, json=error_data)
                
        except Exception as webhook_error:
            print(f"無法回調錯誤訊息: {str(webhook_error)}")


@app.post("/api/parse-webhook")
async def parse_url_webhook(request: ParseWebhookRequest, background_tasks: BackgroundTasks):
    """
    POST 方法：解析網頁並回調 webhook（用於 n8n 整合）
    
    Args:
        request: 包含 url、webhook_url 和 metadata 的請求物件
        background_tasks: FastAPI 背景任務管理器
        
    Returns:
        任務接收確認
    """
    # 加入背景任務
    background_tasks.add_task(
        process_and_webhook,
        request.url,
        request.webhook_url,
        request.metadata
    )
    
    return {
        "success": True,
        "message": "解析任務已接收，將在完成後回調 webhook",
        "url": request.url,
        "webhook_url": request.webhook_url
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "parser-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    # 從環境變數讀取埠號（Railway 會提供），預設 3000
    import os
    port = int(os.getenv("PORT", 3000))
    
    print("🚀 Parser 伺服器已啟動！（Python 版本）")
    print(f"📡 監聽埠號: {port}")
    print(f"🌐 本地訪問: http://localhost:{port}")
    print(f"📚 API 文件: http://localhost:{port}/docs")
    print("\n使用範例:")
    print(f"  POST http://localhost:{port}/api/parse")
    print("  Body: {\"url\": \"https://example.com/article\"}")
    print("\n  或使用 GET:")
    print(f"  http://localhost:{port}/api/parse?url=https://example.com/article")
    print("\n按 Ctrl+C 停止伺服器\n")
    
    # 啟動伺服器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

