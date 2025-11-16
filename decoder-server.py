"""
Google URL Decoder API - 輕量級版本
專門用於 Railway 部署，不包含重量級的 Playwright 解析功能

功能：
- 解碼 Google Alert/RSS 重定向 URL
- 輕量級、快速、低資源消耗
- 專門給 n8n workflow 使用

安裝套件：
pip install fastapi uvicorn

啟動方式：
python decoder-server.py
或
uvicorn decoder-server:app --reload --port 3000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn
import os
from urllib.parse import urlparse, parse_qs, unquote

# 建立 FastAPI 應用
app = FastAPI(
    title="Google URL Decoder API (輕量版)",
    description="專門用於解碼 Google Alert/RSS 重定向 URL，輕量級部署到 Railway",
    version="2.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 資料模型 ====================

class DecodeRequest(BaseModel):
    """解碼請求"""
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.google.com/url?url=https://example.com/article&..."
            }
        }


# ==================== 核心功能 ====================

def decode_google_url(google_url: str) -> str:
    """
    從 Google 重定向 URL 中提取真實的目標 URL
    
    支援的格式：
    - Google News/Alerts: https://www.google.com/url?url=...
    - Google RSS: https://news.google.com/rss/articles/...
    
    Args:
        google_url: Google 重定向 URL
        
    Returns:
        真實的目標 URL，如果解析失敗則返回原 URL
        
    Examples:
        >>> decode_google_url('https://www.google.com/url?url=https://example.com&...')
        'https://example.com'
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
        print(f"⚠️  解析失敗: {str(e)}")
        return google_url


# ==================== API 端點 ====================

@app.get("/")
async def root():
    """API 首頁"""
    return {
        "service": "Google URL Decoder API",
        "version": "2.0.0",
        "description": "輕量級 Google URL 解碼服務（專門部署到 Railway）",
        "features": [
            "🔗 解碼 Google Alert/RSS 重定向 URL",
            "⚡ 輕量級、快速、低資源消耗",
            "🎯 專門給 n8n workflow 使用",
            "❌ 不包含重量級的網頁解析功能"
        ],
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "健康檢查"
            },
            "decode_post": {
                "method": "POST",
                "path": "/api/decode-google-url",
                "body": {"url": "Google 重定向 URL"},
                "description": "解碼 Google URL (POST)"
            },
            "decode_get": {
                "method": "GET",
                "path": "/api/decode-google-url?url=YOUR_URL",
                "description": "解碼 Google URL (GET)"
            }
        },
        "examples": [
            'POST /api/decode-google-url with body: {"url": "https://www.google.com/url?url=https://example.com/..."}',
            'GET /api/decode-google-url?url=https://www.google.com/url?url=https://example.com/...'
        ],
        "note": "此版本不包含 /api/parse 功能，如需解析文章內容請使用本地 API"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "decoder-api",
        "version": "2.0.0",
        "type": "lightweight"
    }


@app.post("/api/decode-google-url")
async def decode_url_post(request: DecodeRequest):
    """
    POST 方法：解碼 Google 重定向 URL
    
    Args:
        request: 包含 url 的請求
        
    Returns:
        解碼結果
        
    Example:
        POST /api/decode-google-url
        {
            "url": "https://www.google.com/url?url=https://example.com/article&..."
        }
        
        Response:
        {
            "success": true,
            "original_url": "https://www.google.com/url?url=...",
            "decoded_url": "https://example.com/article",
            "is_google_url": true,
            "changed": true
        }
    """
    try:
        original_url = request.url
        decoded_url = decode_google_url(original_url)
        
        # 檢查是否為 Google URL
        is_google_url = 'google.com' in original_url
        
        return {
            "success": True,
            "original_url": original_url,
            "decoded_url": decoded_url,
            "is_google_url": is_google_url,
            "changed": original_url != decoded_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解碼 URL 時發生錯誤: {str(e)}"
        )


@app.get("/api/decode-google-url")
async def decode_url_get(url: str):
    """
    GET 方法：解碼 Google 重定向 URL
    
    Args:
        url: Google 重定向 URL（查詢參數）
        
    Returns:
        解碼結果
        
    Example:
        GET /api/decode-google-url?url=https://www.google.com/url?url=https://example.com/...
    """
    if not url:
        raise HTTPException(
            status_code=400,
            detail="請提供 URL 參數"
        )
    
    try:
        decoded_url = decode_google_url(url)
        
        # 檢查是否為 Google URL
        is_google_url = 'google.com' in url
        
        return {
            "success": True,
            "original_url": url,
            "decoded_url": decoded_url,
            "is_google_url": is_google_url,
            "changed": url != decoded_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解碼 URL 時發生錯誤: {str(e)}"
        )


# ==================== 啟動設定 ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print("=" * 60)
    print("🚀 Google URL Decoder API (輕量版) 啟動中...")
    print("=" * 60)
    print(f"📍 監聽端口: {port}")
    print(f"🌐 API 文件: http://localhost:{port}/docs")
    print(f"💚 健康檢查: http://localhost:{port}/health")
    print(f"🔗 解碼端點: http://localhost:{port}/api/decode-google-url")
    print("=" * 60)
    print("⚡ 輕量級版本 - 不包含重量級的 Playwright 解析功能")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

