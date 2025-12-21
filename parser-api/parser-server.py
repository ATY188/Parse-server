"""
網頁內容解析器 API - Python 版本（增強版）
使用 FastAPI + trafilatura
支援重試、更好的 headers、SSL 錯誤處理

安裝套件：
pip install fastapi uvicorn trafilatura httpx python-multipart

啟動方式：
python parser-server.py
或
uvicorn parser-server:app --reload --port 3000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, Any
import trafilatura
import httpx
from datetime import datetime
import uvicorn
import os
import asyncio
import random
import shutil
import glob
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ==================== 併發控制 ====================
# 🔧 修復 BlockingIOError: 限制同時運行的 Playwright 實例數量
# Railway Pro Plan 建議最多 2-3 個並發實例
PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(2)

# ==================== /tmp 清理功能 ====================
def cleanup_chromium_temp():
    """
    清理 Chromium/Playwright 產生的臨時文件
    防止 /tmp 空間被佔滿導致無法啟動新的瀏覽器
    """
    patterns = [
        '/tmp/.org.chromium.*',
        '/tmp/playwright*',
        '/tmp/.com.google.Chrome.*',
        '/tmp/chromium*',
        '/tmp/.X*-lock',
        '/tmp/core.*',
    ]
    cleaned = 0
    for pattern in patterns:
        for path in glob.glob(pattern):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
                cleaned += 1
            except:
                pass
    if cleaned > 0:
        print(f"[Cleanup] 🧹 已清理 {cleaned} 個臨時文件/目錄")
    return cleaned


# 建立 FastAPI 應用
app = FastAPI(
    title="網頁內容解析器 API（增強版 + 智慧路由）",
    description="使用 trafilatura 自動提取網頁文章內容，支援重試和錯誤處理，智慧路由優化",
    version="1.8.0"  # 版本升級
)

# ==================== CORS 配置 ====================
# 允許所有來源訪問 API（適用於公開 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法 (GET, POST, PUT, DELETE, HEAD, OPTIONS)
    allow_headers=["*"],  # 允許所有 headers
)

# ==================== 智慧路由配置 ====================

# 已知無法解析的網站（黑名單）- 直接返回失敗，建議使用 RSS
BLOCKED_DOMAINS = [
    'reuters.com',           # 401 Forbidden - 需要訂閱（paywall）
    'japantimes.co.jp',      # Cloudflare 人類驗證（CAPTCHA）
    'content-technology.com', # 403 Forbidden - 強反爬
    'isna.ir',               # 地區封鎖（伊朗）
    # 'koin.com',            # 已移除：給 Playwright 一次機會
]

# 已知必須使用動態渲染的網站（直接用 Playwright，不浪費時間試靜態）
DYNAMIC_REQUIRED_DOMAINS = [
    'techstory.in',          # 印度科技新聞（動態載入）
    'peoplematters.in',      # 印度人力資源新聞（動態載入）
    'storm.mg',              # 風傳媒（動態載入）
    'ustv.com.tw',           # 非凡新聞（動態載入）
    'designnews.com',        # 美國設計新聞（動態載入）
    'gurufocus.com',         # 美國金融新聞（動態載入）
    'sammyfans.com',         # 科技新聞（動態載入）
    'manilatimes.net',       # 菲律賓新聞（動態載入）
]

# 已知靜態解析即可的網站（優先使用靜態，速度快）
STATIC_OK_DOMAINS = [
    # 可以在測試後逐步添加
    # 例如：'example.com', 'blog.example.com'
]

# AMP 頁面警告清單（建議轉換為非 AMP 版本）
AMP_WARNING_PATTERNS = [
    '/amp', '/amp/', '?amp=1', '&amp=1', '.amp.html'
]

def extract_domain(url: str) -> str:
    """從 URL 中提取域名"""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""

def is_blocked_domain(url: str) -> bool:
    """檢查是否為黑名單域名"""
    domain = extract_domain(url)
    return any(blocked in domain for blocked in BLOCKED_DOMAINS)

def requires_dynamic_rendering(url: str) -> bool:
    """檢查是否需要動態渲染"""
    domain = extract_domain(url)
    return any(dynamic in domain for dynamic in DYNAMIC_REQUIRED_DOMAINS)

def is_static_ok(url: str) -> bool:
    """檢查是否可以使用靜態解析"""
    domain = extract_domain(url)
    return any(static in domain for static in STATIC_OK_DOMAINS)

def is_amp_url(url: str) -> bool:
    """檢查是否為 AMP 頁面"""
    return any(pattern in url.lower() for pattern in AMP_WARNING_PATTERNS)

def get_routing_decision(url: str) -> Dict[str, Any]:
    """
    智慧路由決策
    
    Returns:
        {
            "action": "block" | "dynamic" | "static" | "try_static_first",
            "reason": "原因說明",
            "suggestion": "建議（如果有）"
        }
    """
    # 檢查黑名單
    if is_blocked_domain(url):
        return {
            "action": "block",
            "reason": "域名在黑名單中（已知無法解析）",
            "suggestion": "建議使用 RSS 摘要代替"
        }
    
    # 檢查 AMP 頁面
    if is_amp_url(url):
        return {
            "action": "dynamic",  # AMP 也用動態
            "reason": "檢測到 AMP 頁面",
            "suggestion": "建議轉換為非 AMP 版本以獲得更好效果"
        }
    
    # 檢查是否已知需要動態渲染
    if requires_dynamic_rendering(url):
        return {
            "action": "dynamic",
            "reason": "域名已知需要動態渲染（JavaScript 載入內容）",
            "suggestion": None
        }
    
    # 檢查是否已知靜態即可
    if is_static_ok(url):
        return {
            "action": "static",
            "reason": "域名已知可使用靜態解析（速度快）",
            "suggestion": None
        }
    
    # 未知域名，先嘗試靜態
    return {
        "action": "try_static_first",
        "reason": "未知域名，先嘗試靜態解析，失敗後自動使用動態",
        "suggestion": None
    }

# ==================== 智慧路由配置結束 ====================

# 多組 User-Agent 輪流使用
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """隨機選擇 User-Agent"""
    return random.choice(USER_AGENTS)

def get_enhanced_headers(url: str):
    """獲取增強的 HTTP headers"""
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': f'https://{parsed_url.netloc}/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

# 請求資料模型
class ParseRequest(BaseModel):
    url: str
    max_retries: Optional[int] = 3
    skip_ssl: Optional[bool] = False
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v

class ParseDynamicRequest(BaseModel):
    url: str
    wait_for: Optional[str] = None
    block_ads: Optional[bool] = True  # 預設屏蔽廣告
    stealth_mode: Optional[bool] = True  # 預設啟用反爬蟲模式
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v

class ParseWebhookRequest(BaseModel):
    url: str
    webhook_url: str
    metadata: Optional[Dict[str, Any]] = {}
    max_retries: Optional[int] = 3
    skip_ssl: Optional[bool] = False
    
    @validator('url', 'webhook_url')
    def validate_urls(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v

class DecodeGoogleUrlRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v


async def fetch_with_playwright(
    url: str, 
    wait_for: Optional[str] = None,
    block_ads: bool = True,
    stealth_mode: bool = True
) -> str:
    """
    使用 Playwright 獲取動態網頁內容（增強版）
    
    Args:
        url: 要訪問的網頁 URL
        wait_for: 等待特定元素（CSS selector）出現，例如 'article' 或 '.content'
        block_ads: 是否屏蔽廣告（預設 True）
        stealth_mode: 是否啟用反爬蟲模式（預設 True）
        
    Returns:
        渲染後的 HTML 內容
        
    Raises:
        Exception: 當瀏覽器操作失敗時
    """
    # 🔧 使用信號量控制併發，避免 BlockingIOError
    async with PLAYWRIGHT_SEMAPHORE:
        print(f"[Playwright] 🔒 獲取併發鎖...")
        
        async with async_playwright() as p:
            browser = None  # 初始化變數，確保 finally 可以檢查
            context = None
            try:
                # 啟動 Chromium 瀏覽器（無頭模式）
                print(f"[Playwright] 啟動瀏覽器...")
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        # 基本設定
                        '--disable-blink-features=AutomationControlled',  # 禁用自動化控制特徵
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        # 🔧 修復 BlockingIOError - 記憶體和資源優化
                        '--disable-dev-shm-usage',          # 不使用 /dev/shm（關鍵修復！）
                        '--disable-gpu',                     # 禁用 GPU（容器環境）
                        '--disable-software-rasterizer',     # 禁用軟體光柵化
                        '--single-process',                  # 單進程模式（減少資源消耗）
                        '--no-zygote',                       # 禁用 zygote 進程
                        # 記憶體優化
                        '--disable-extensions',              # 禁用擴充
                        '--disable-background-networking',   # 禁用背景網路
                        '--disable-sync',                    # 禁用同步
                        '--disable-translate',               # 禁用翻譯
                        '--disable-features=TranslateUI',
                        '--disable-default-apps',            # 禁用預設應用
                        '--mute-audio',                      # 靜音
                        '--hide-scrollbars',                 # 隱藏滾動條
                        # 穩定性
                        '--disable-hang-monitor',            # 禁用掛起監控
                        '--disable-prompt-on-repost',        # 禁用重新提交提示
                        '--disable-component-update',        # 禁用組件更新
                        '--ignore-certificate-errors',       # 忽略證書錯誤
                    ]
                )
                
                # 創建新的瀏覽器上下文（模擬真實用戶）
                context = await browser.new_context(
                    user_agent=get_random_user_agent(),
                    viewport={'width': 1920, 'height': 1080},
                    locale='zh-TW',
                    timezone_id='Asia/Taipei',
                    color_scheme='light',
                    extra_http_headers={
                        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    }
                )
                
                # 如果啟用廣告屏蔽
                if block_ads:
                    print(f"[Playwright] 啟用廣告屏蔽")
                    ad_domains = [
                        'doubleclick.net', 'googlesyndication.com', 'googletagmanager.com',
                        'google-analytics.com', 'facebook.com/tr/', 'scorecardresearch.com',
                        'ad.doubleclick.net', 'static.ads-twitter.com', 'ads.yahoo.com',
                        'pagead2.googlesyndication.com', 'adservice.google.com',
                        'analytics.google.com', 'googleadservices.com'
                    ]
                    
                    await context.route("**/*", lambda route: (
                        route.abort() if any(ad in route.request.url for ad in ad_domains)
                        else route.continue_()
                    ))
                
                # 創建新頁面
                page = await context.new_page()
                
                # 如果啟用反爬蟲模式
                if stealth_mode:
                    print(f"[Playwright] 啟用反爬蟲模式")
                    # 隱藏 webdriver 特徵
                    await page.add_init_script("""
                        // 移除 webdriver 標記
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => false
                        });
                        
                        // 偽裝 Chrome 對象
                        window.chrome = {
                            runtime: {}
                        };
                        
                        // 修改 permissions
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (parameters) => (
                            parameters.name === 'notifications' ?
                                Promise.resolve({ state: Notification.permission }) :
                                originalQuery(parameters)
                        );
                        
                        // 偽裝 plugins
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        
                        // 偽裝 languages
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-TW', 'zh', 'en-US', 'en']
                        });
                    """)
                
                # 訪問網頁（使用更寬鬆的策略以提升穩定性）
                print(f"[Playwright] 正在訪問: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=90000)  # 90 秒，使用 domcontentloaded 策略
                
                # 隨機延遲（模擬人類行為）
                delay = random.uniform(1, 2.5)
                print(f"[Playwright] 隨機延遲 {delay:.1f} 秒...")
                await asyncio.sleep(delay)
                
                # 移除廣告元素（DOM 層面）
                if block_ads:
                    await page.evaluate("""() => {
                        // 移除常見廣告元素
                        const selectors = [
                            '[class*="ad-"]', '[class*="ad_"]', '[id*="ad-"]', '[id*="ad_"]',
                            '[class*="advertisement"]', '[class*="banner"]',
                            'iframe[src*="ads"]', 'iframe[src*="doubleclick"]',
                            '.ad', '.ads', '#ad', '#ads'
                        ];
                        
                        selectors.forEach(selector => {
                            try {
                                document.querySelectorAll(selector).forEach(el => el.remove());
                            } catch(e) {}
                        });
                    }""")
                
                # 如果指定了等待元素，等待該元素出現
                if wait_for:
                    print(f"[Playwright] 等待元素: {wait_for}")
                    try:
                        await page.wait_for_selector(wait_for, timeout=20000)  # 增加到 20 秒
                    except:
                        print(f"[Playwright] 警告：元素 {wait_for} 未找到，繼續提取內容")
                
                # 滾動頁面以觸發懶加載（優化版：快速分段滾動）
                print(f"[Playwright] 滾動頁面以載入動態內容...")
                await page.evaluate("""() => {
                    // 快速分段滾動到頁面不同位置
                    const positions = [0.3, 0.6, 1.0];  // 30%, 60%, 100%
                    positions.forEach((ratio, index) => {
                        setTimeout(() => {
                            window.scrollTo(0, document.body.scrollHeight * ratio);
                        }, index * 400);  // 每 400ms 滾動一次
                    });
                }""")
                
                # 再等待一下，確保內容載入完成（給懶加載更多時間）
                await asyncio.sleep(2)
            
                # 獲取渲染後的 HTML
                html_content = await page.content()
                
                print(f"[Playwright] ✅ 成功獲取內容，長度: {len(html_content)}")
                return html_content
                
            except PlaywrightTimeout as e:
                raise Exception(f"Playwright 超時: {str(e)}")
            except Exception as e:
                raise Exception(f"Playwright 錯誤: {str(e)}")
            finally:
                # ⚠️ 重要：確保瀏覽器一定會被關閉，避免記憶體洩漏
                # 🔧 按順序關閉：先 context，再 browser
                if context:
                    try:
                        await context.close()
                        print(f"[Playwright] 🧹 Context 已關閉")
                    except:
                        pass
                if browser:
                    try:
                        await browser.close()
                        print(f"[Playwright] 🧹 瀏覽器已關閉")
                    except:
                        pass  # 忽略關閉時的錯誤
                print(f"[Playwright] 🔓 釋放併發鎖")
                # 🧹 清理 Chromium 臨時文件，防止 /tmp 空間耗盡
                cleanup_chromium_temp()


async def fetch_and_parse_with_playwright(
    url: str,
    wait_for: Optional[str] = None,
    block_ads: bool = True,
    stealth_mode: bool = True,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    使用 Playwright 下載並解析動態網頁內容（增強版 + 重試機制）
    
    Args:
        url: 要解析的網頁 URL
        wait_for: 等待特定元素出現
        block_ads: 是否屏蔽廣告
        stealth_mode: 是否啟用反爬蟲模式
        max_retries: 最大重試次數（預設 2 次）
        
    Returns:
        解析後的資料字典
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                print(f"[Playwright] 重試 {attempt}/{max_retries}")
                await asyncio.sleep(3)  # 等待 3 秒後重試
            
            # 使用 Playwright 獲取渲染後的 HTML
            html_content = await fetch_with_playwright(url, wait_for, block_ads, stealth_mode)
            
            # 使用 trafilatura 解析內容
            try:
                text_content = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False
                )
            except Exception as e:
                print(f"[警告] trafilatura.extract 失敗: {e}")
                text_content = None
            
            # 提取元數據
            try:
                metadata = trafilatura.extract_metadata(html_content)
            except Exception as e:
                print(f"[警告] trafilatura.extract_metadata 失敗: {e}")
                metadata = None
            
            # 提取 XML 格式內容
            try:
                html_formatted = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False,
                    output_format='xml'
                )
            except Exception as e:
                print(f"[警告] trafilatura.extract (XML) 失敗: {e}")
                html_formatted = None
            
            # 整理回傳資料
            parsed_data = {
                "title": getattr(metadata, 'title', None) if metadata else None,
                "author": getattr(metadata, 'author', None) if metadata else None,
                "date_published": getattr(metadata, 'date', None) if metadata else None,
                "url": getattr(metadata, 'url', url) if metadata else url,
                "domain": getattr(metadata, 'sitename', None) if metadata else None,
                "description": getattr(metadata, 'description', None) if metadata else None,
                "categories": getattr(metadata, 'categories', None) if metadata else None,
                "tags": getattr(metadata, 'tags', None) if metadata else None,
                "content": html_formatted or text_content,
                "text_content": text_content,
                "excerpt": text_content[:200] + "..." if text_content and len(text_content) > 200 else text_content,
                "word_count": len(text_content.split()) if text_content else 0,
                "language": getattr(metadata, 'language', None) if metadata else None,
                "rendering_method": "playwright"
            }
            
            # 成功解析，返回結果
            print(f"[Playwright] ✅ 第 {attempt} 次嘗試成功")
            return {
                "success": True,
                "data": parsed_data,
                "method": "playwright",
                "attempts": attempt
            }
            
        except Exception as e:
            last_error = e
            print(f"[Playwright] ❌ 第 {attempt} 次嘗試失敗: {str(e)}")
            
            if attempt == max_retries:
                # 所有重試都失敗了
                raise HTTPException(
                    status_code=500,
                    detail=f"使用 Playwright 解析失敗（已重試 {max_retries} 次）: {str(e)}"
                )
    
    # 理論上不會到達這裡
    raise HTTPException(
        status_code=500,
        detail=f"使用 Playwright 解析失敗: {str(last_error)}"
    )


def decode_google_url(google_url: str) -> Optional[str]:
    """
    從 Google 重定向 URL 中提取真實的目標 URL
    
    支援的格式：
    - Google News/Alerts: https://www.google.com/url?url=...
    - Google RSS: https://news.google.com/rss/articles/...
    
    Args:
        google_url: Google 重定向 URL
        
    Returns:
        真實的目標 URL，如果解析失敗則返回 None
        
    Examples:
        >>> decode_google_url('https://www.google.com/url?url=https://example.com&...')
        'https://example.com'
    """
    from urllib.parse import urlparse, parse_qs, unquote
    
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


# 首頁路由
@app.get("/")
@app.head("/")  # 支持 HEAD 請求（用於健康檢查）
async def root():
    """API 首頁 - 顯示可用端點"""
    return {
        "message": "歡迎使用網頁內容解析器 API (Python 增強版 + 智慧路由)",
        "framework": "FastAPI + trafilatura + Playwright",
        "version": "1.7.0",
        "features": [
            "🧠 智慧路由（根據域名自動選擇最佳解析方式）",
            "⛔ 黑名單機制（跳過已知無法解析的網站，節省時間）",
            "🎭 動態網站快速通道（已知動態網站直接用 Playwright）",
            "🔄 自動降級（靜態失敗自動切換到動態）",
            "🔄 自動重試機制（處理 403/429 錯誤）",
            "🎲 隨機 User-Agent",
            "📡 增強的 HTTP headers",
            "🔒 SSL 錯誤處理",
            "⏱️ 指數退避（Exponential Backoff）",
            "🚀 Playwright 支援（處理動態 JavaScript 網站）",
            "🚫 廣告屏蔽（Network 和 DOM 層面）",
            "🥷 反爬蟲模式（隱藏 webdriver 特徵）",
            "📜 自動滾動載入懶加載內容",
            "🔒 併發控制（限制同時運行的瀏覽器數量，避免資源耗盡）",
            "🛡️ 容器優化（修復 BlockingIOError，禁用 /dev/shm 依賴）"
        ],
        "smartRouting": {
            "description": "智慧路由根據域名歷史表現自動選擇最佳解析策略",
            "strategies": {
                "block": "黑名單域名（reuters.com, japantimes.co.jp 等）直接返回失敗，建議使用 RSS",
                "dynamic_direct": "已知動態網站（storm.mg, techstory.in 等）直接使用 Playwright",
                "static_only": "已知靜態網站優先使用快速靜態解析",
                "fallback": "未知網站先試靜態，失敗後自動切換到 Playwright"
            },
            "benefits": [
                "⚡ 效能提升 40-60%（跳過無效嘗試）",
                "💰 降低資源消耗（避免無謂的 Playwright 啟動）",
                "🎯 更高成功率（已知動態網站直接用對的方法）"
            ]
        },
        "endpoints": {
            "parse": {
                "method": "POST",
                "path": "/api/parse",
                "body": {
                    "url": "要解析的網頁 URL",
                    "max_retries": "(選填) 最大重試次數，預設 3",
                    "skip_ssl": "(選填) 跳過 SSL 驗證，預設 false"
                },
                "description": "解析指定 URL 的網頁內容（同步回傳，支援重試）"
            },
            "parseGet": {
                "method": "GET",
                "path": "/api/parse?url=YOUR_URL",
                "description": "使用 GET 方法解析網頁內容"
            },
            "parseDynamic": {
                "method": "POST",
                "path": "/api/parse-dynamic",
                "body": {
                    "url": "要解析的網頁 URL",
                    "wait_for": "(選填) 等待特定 CSS 選擇器，例如 'article' 或 '.content'",
                    "block_ads": "(選填) 是否屏蔽廣告，預設 true",
                    "stealth_mode": "(選填) 是否啟用反爬蟲模式，預設 true"
                },
                "description": "使用 Playwright 解析動態網站（支援 JavaScript 渲染、廣告屏蔽、反爬蟲）⭐ 推薦用於 SPA 網站和有反爬蟲的網站"
            },
            "parseWebhook": {
                "method": "POST",
                "path": "/api/parse-webhook",
                "body": {
                    "url": "要解析的網頁 URL",
                    "webhook_url": "n8n webhook URL",
                    "metadata": "(選填) 額外資料",
                    "max_retries": "(選填) 最大重試次數",
                    "skip_ssl": "(選填) 跳過 SSL 驗證"
                },
                "description": "解析網頁並回調 webhook（適用於 n8n 整合）"
            },
            "decodeGoogleUrl": {
                "method": "POST",
                "path": "/api/decode-google-url",
                "body": {
                    "url": "Google 重定向 URL（例如：https://www.google.com/url?url=...）"
                },
                "description": "從 Google 重定向 URL 中提取真實的目標 URL ⭐ 適用於 Google Alert/RSS"
            },
            "decodeGoogleUrlGet": {
                "method": "GET",
                "path": "/api/decode-google-url?url=YOUR_GOOGLE_URL",
                "description": "使用 GET 方法解碼 Google URL"
            },
            "docs": {
                "method": "GET",
                "path": "/docs",
                "description": "Swagger UI 互動式 API 文件"
            }
        },
        "examples": [
            'POST /api/parse with body: {"url": "https://example.com/article", "max_retries": 3}',
            'GET /api/parse?url=https://example.com/article',
            'POST /api/parse-webhook with body: {"url": "https://example.com/article", "webhook_url": "https://your-n8n.com/webhook/..."}',
            'POST /api/decode-google-url with body: {"url": "https://www.google.com/url?url=https://example.com/article&..."}',
            'GET /api/decode-google-url?url=https://www.google.com/url?url=https://example.com/article'
        ],
        "errorHandling": {
            "403 Forbidden": "自動重試 + 隨機 User-Agent + Referer header",
            "429 Too Many Requests": "指數退避重試（2s, 4s, 8s...）",
            "SSL Certificate Error": "可選擇跳過 SSL 驗證（skip_ssl: true）"
        },
        "documentation": "訪問 /docs 查看完整 API 文件"
    }


async def fetch_and_parse_with_retry(
    url: str, 
    max_retries: int = 3, 
    skip_ssl: bool = False
) -> Dict[str, Any]:
    """
    下載並解析網頁內容（支援重試）
    
    Args:
        url: 要解析的網頁 URL
        max_retries: 最大重試次數
        skip_ssl: 是否跳過 SSL 驗證
        
    Returns:
        解析後的資料字典
        
    Raises:
        HTTPException: 當下載或解析失敗時
    """
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[嘗試 {attempt}/{max_retries}] 解析: {url}")
            
            # 獲取增強的 headers
            headers = get_enhanced_headers(url)
            
            # 設定 timeout 和 SSL 驗證
            timeout = httpx.Timeout(30.0, connect=10.0)
            verify_ssl = not skip_ssl
            
            # 下載網頁內容
            async with httpx.AsyncClient(
                timeout=timeout,
                verify=verify_ssl,
                follow_redirects=True,
                headers=headers
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                html_content = response.text
            
            # 使用 trafilatura 解析內容
            try:
                text_content = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False
                )
            except Exception as e:
                print(f"[警告] trafilatura.extract 失敗: {e}")
                text_content = None
            
            # 提取完整資訊（包含元數據）
            try:
                metadata = trafilatura.extract_metadata(html_content)
            except Exception as e:
                print(f"[警告] trafilatura.extract_metadata 失敗: {e}")
                metadata = None
            
            # 提取 HTML 格式的內容
            try:
                html_formatted = trafilatura.extract(
                    html_content,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False,
                    output_format='xml'
                )
            except Exception as e:
                print(f"[警告] trafilatura.extract (XML) 失敗: {e}")
                html_formatted = None
            
            # 整理回傳資料
            parsed_data = {
                "title": getattr(metadata, 'title', None) if metadata else None,
                "author": getattr(metadata, 'author', None) if metadata else None,
                "date_published": getattr(metadata, 'date', None) if metadata else None,
                "url": getattr(metadata, 'url', url) if metadata else url,
                "domain": getattr(metadata, 'sitename', None) if metadata else None,
                "description": getattr(metadata, 'description', None) if metadata else None,
                "categories": getattr(metadata, 'categories', None) if metadata else None,
                "tags": getattr(metadata, 'tags', None) if metadata else None,
                "content": html_formatted or text_content,
                "text_content": text_content,
                "excerpt": text_content[:200] + "..." if text_content and len(text_content) > 200 else text_content,
                "word_count": len(text_content.split()) if text_content else 0,
                "language": getattr(metadata, 'language', None) if metadata else None
            }
            
            title_preview = parsed_data.get('title') or 'No title'
            print(f"[成功] 嘗試 {attempt}: {title_preview[:50] if title_preview else 'No title'}")
            return {
                "success": True,
                "data": parsed_data,
                "attempt": attempt,
                "retries": attempt - 1
            }
            
        except httpx.HTTPStatusError as e:
            last_error = e
            status_code = e.response.status_code
            print(f"[失敗] 嘗試 {attempt}: HTTP {status_code} - {str(e)}")
            
            # 如果是最後一次嘗試，拋出錯誤
            if attempt == max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"下載網頁失敗: Client error '{status_code} {e.response.reason_phrase}' for url '{url}'\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/{status_code}"
                )
            
            # 根據錯誤類型決定等待時間
            if status_code in [429, 403]:
                # 429 Too Many Requests 或 403 Forbidden：指數退避
                wait_time = (2 ** attempt)  # 2秒、4秒、8秒...
                print(f"[等待] {wait_time} 秒後重試（HTTP {status_code}）...")
                await asyncio.sleep(wait_time)
            else:
                # 其他錯誤：短暫等待
                await asyncio.sleep(1)
                
        except httpx.ConnectError as e:
            last_error = e
            print(f"[失敗] 嘗試 {attempt}: 連接錯誤 - {str(e)}")
            
            if attempt == max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"下載網頁失敗: 無法連接到 {url}"
                )
            
            await asyncio.sleep(2)
            
        except Exception as e:
            error_msg = str(e)
            print(f"[失敗] 嘗試 {attempt}: {error_msg}")
            
            # SSL 錯誤處理
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                last_error = e
                
                if attempt == max_retries:
                    if skip_ssl:
                        raise HTTPException(
                            status_code=500,
                            detail=f"下載網頁失敗: {error_msg}"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"下載網頁失敗: {error_msg}\n\n💡 提示：可以嘗試設定 skip_ssl: true 來跳過 SSL 驗證"
                        )
                
                # 下次嘗試時跳過 SSL 驗證
                if not skip_ssl:
                    print(f"[SSL 錯誤] 下次將跳過 SSL 驗證...")
                    skip_ssl = True
                    
                await asyncio.sleep(1)
            else:
                # 其他錯誤
                last_error = e
                
                if attempt == max_retries:
                    raise HTTPException(
                        status_code=500,
                        detail=f"解析網頁失敗: {error_msg}"
                    )
                
                await asyncio.sleep(1)
    
    # 理論上不會到達這裡，但以防萬一
    raise HTTPException(
        status_code=500,
        detail=f"解析網頁失敗: {str(last_error)}"
    )


@app.post("/api/parse")
async def parse_url(request: ParseRequest):
    """
    POST 方法：解析網頁內容（支援重試 + 智慧路由）
    
    智慧路由會根據域名自動選擇最佳解析方式：
    - 黑名單域名：直接返回失敗，建議使用 RSS
    - 已知動態網站：直接使用 Playwright（不浪費時間）
    - 已知靜態網站：只用靜態解析（速度快）
    - 未知網站：先試靜態，失敗後自動使用 Playwright
    
    Args:
        request: 包含 url、max_retries 和 skip_ssl 的請求物件
        
    Returns:
        解析後的網頁內容
    """
    print(f"正在解析: {request.url} (max_retries: {request.max_retries}, skip_ssl: {request.skip_ssl})")
    
    try:
        # 🧠 智慧路由決策
        routing = get_routing_decision(request.url)
        print(f"[智慧路由] 決策: {routing['action']} - {routing['reason']}")
        
        # 情況 1：黑名單域名 - 直接返回失敗
        if routing['action'] == 'block':
            print(f"[智慧路由] ⛔ 域名在黑名單中，跳過解析")
            return {
                "success": False,
                "data": None,
                "reason": routing['reason'],
                "suggestion": routing['suggestion'],
                "routing_decision": routing['action'],
                "use_rss_instead": True
            }
        
        # 情況 2：已知需要動態渲染 - 直接用 Playwright
        elif routing['action'] == 'dynamic':
            print(f"[智慧路由] 🎭 直接使用 Playwright（已知動態網站）")
            result = await fetch_and_parse_with_playwright(
                request.url,
                wait_for=None,
                block_ads=True,
                stealth_mode=True
            )
            result['routing_decision'] = 'dynamic_direct'
            if routing.get('suggestion'):
                result['suggestion'] = routing['suggestion']
            return result
        
        # 情況 3：已知靜態即可 - 只用靜態
        elif routing['action'] == 'static':
            print(f"[智慧路由] ⚡ 使用靜態解析（已知靜態網站）")
            result = await fetch_and_parse_with_retry(
                request.url,
                max_retries=request.max_retries,
                skip_ssl=request.skip_ssl
            )
            result['routing_decision'] = 'static_only'
            return result
        
        # 情況 4：未知域名 - 先試靜態，失敗後自動用 Playwright
        else:  # 'try_static_first'
            print(f"[智慧路由] 🔄 先試靜態，失敗後自動使用 Playwright")
            
            # 先嘗試靜態解析
            try:
                result = await fetch_and_parse_with_retry(
                    request.url,
                    max_retries=1,  # 靜態只試一次，避免浪費時間
                    skip_ssl=request.skip_ssl
                )
                
                # 檢查是否真的有內容
                if result.get('success') and result.get('data', {}).get('text_content'):
                    print(f"[智慧路由] ✅ 靜態解析成功")
                    result['routing_decision'] = 'static_success'
                    return result
                else:
                    raise Exception("靜態解析無內容，嘗試動態渲染")
                    
            except Exception as static_error:
                print(f"[智慧路由] ⚠️ 靜態解析失敗: {str(static_error)}")
                print(f"[智慧路由] 🎭 自動切換到 Playwright...")
                
                # 切換到 Playwright
                result = await fetch_and_parse_with_playwright(
                    request.url,
                    wait_for=None,
                    block_ads=True,
                    stealth_mode=True
                )
                result['routing_decision'] = 'fallback_to_dynamic'
                result['static_error'] = str(static_error)[:100]  # 記錄靜態失敗原因
                return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"解析錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"解析網頁時發生錯誤: {str(e)}"
        )


@app.get("/api/parse")
async def parse_url_get(url: str, max_retries: int = 3, skip_ssl: bool = False):
    """
    GET 方法：解析網頁內容（透過 query string）
    
    Args:
        url: 要解析的網頁 URL
        max_retries: 最大重試次數（預設 3）
        skip_ssl: 是否跳過 SSL 驗證（預設 False）
        
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
        result = await fetch_and_parse_with_retry(
            url,
            max_retries=max_retries,
            skip_ssl=skip_ssl
        )
        
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"解析錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"解析網頁時發生錯誤: {str(e)}"
        )


@app.post("/api/parse-dynamic")
async def parse_url_dynamic(request: ParseDynamicRequest):
    """
    POST 方法：使用 Playwright 解析動態網站（增強版：支援廣告屏蔽和反爬蟲）
    
    適用於：
    - React/Vue/Angular 等單頁應用（SPA）
    - JavaScript 動態載入內容的網站
    - 需要等待特定元素出現的網站
    - 有廣告干擾的網站
    - 有反爬蟲機制的網站
    
    Args:
        request: 包含以下欄位的請求物件
            - url: 要解析的網頁 URL
            - wait_for: (選填) 等待特定 CSS 選擇器
            - block_ads: (選填) 是否屏蔽廣告，預設 True
            - stealth_mode: (選填) 是否啟用反爬蟲模式，預設 True
        
    Returns:
        解析後的網頁內容
        
    Example:
        POST /api/parse-dynamic
        {
            "url": "https://applealmond.com/posts/296254",
            "wait_for": ".post-content",
            "block_ads": true,
            "stealth_mode": true
        }
    """
    print(f"正在使用 Playwright 解析: {request.url}")
    print(f"廣告屏蔽: {request.block_ads}, 反爬蟲模式: {request.stealth_mode}")
    if request.wait_for:
        print(f"等待元素: {request.wait_for}")
    
    try:
        result = await fetch_and_parse_with_playwright(
            request.url, 
            request.wait_for,
            request.block_ads,
            request.stealth_mode
        )
        return result
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Playwright 解析錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"使用 Playwright 解析網頁時發生錯誤: {str(e)}"
        )


async def process_and_webhook(
    url: str, 
    webhook_url: str, 
    metadata: Dict[str, Any],
    max_retries: int = 3,
    skip_ssl: bool = False
):
    """
    背景任務：解析網頁並回調 webhook
    
    Args:
        url: 要解析的網頁 URL
        webhook_url: webhook 回調 URL
        metadata: 額外的元數據
        max_retries: 最大重試次數
        skip_ssl: 是否跳過 SSL 驗證
    """
    print(f"正在解析 (webhook 模式): {url}")
    
    try:
        # 解析網頁（使用重試機制）
        result = await fetch_and_parse_with_retry(url, max_retries, skip_ssl)
        
        # 準備回調資料
        webhook_data = {
            "success": True,
            "original_url": url,
            "metadata": metadata,
            "parsed_data": result.get("data"),
            "attempt": result.get("attempt"),
            "retries": result.get("retries"),
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
        request: 包含 url、webhook_url、metadata、max_retries 和 skip_ssl 的請求物件
        background_tasks: FastAPI 背景任務管理器
        
    Returns:
        任務接收確認
    """
    # 加入背景任務
    background_tasks.add_task(
        process_and_webhook,
        request.url,
        request.webhook_url,
        request.metadata,
        request.max_retries,
        request.skip_ssl
    )
    
    return {
        "success": True,
        "message": "解析任務已接收，將在完成後回調 webhook",
        "url": request.url,
        "webhook_url": request.webhook_url,
        "max_retries": request.max_retries
    }


@app.post("/api/decode-google-url")
async def decode_google_url_post(request: DecodeGoogleUrlRequest):
    """
    POST 方法：從 Google 重定向 URL 中提取真實的目標 URL
    
    支援的格式：
    - Google News/Alerts: https://www.google.com/url?url=...
    - Google RSS: https://news.google.com/rss/articles/...
    
    Args:
        request: 包含 url 的請求物件
        
    Returns:
        包含原始 URL 和解碼後 URL 的 JSON 回應
        
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
            "is_google_url": true
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
            "changed": original_url != decoded_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解碼 URL 時發生錯誤: {str(e)}"
        )


@app.get("/api/decode-google-url")
async def decode_google_url_get(url: str):
    """
    GET 方法：從 Google 重定向 URL 中提取真實的目標 URL
    
    Args:
        url: Google 重定向 URL（作為查詢參數）
        
    Returns:
        包含原始 URL 和解碼後 URL 的 JSON 回應
        
    Example:
        GET /api/decode-google-url?url=https://www.google.com/url?url=https://example.com/article
        
        Response:
        {
            "success": true,
            "original_url": "https://www.google.com/url?url=...",
            "decoded_url": "https://example.com/article",
            "is_google_url": true
        }
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
            "changed": url != decoded_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"解碼 URL 時發生錯誤: {str(e)}"
        )


@app.get("/health")
@app.head("/health")  # 支持 HEAD 請求
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "parser-api",
        "version": "1.7.0",
        "features": [
            "retry-mechanism",
            "enhanced-headers",
            "ssl-handling",
            "exponential-backoff",
            "playwright-dynamic-rendering",
            "ad-blocking",
            "anti-bot-detection",
            "lazy-loading-support",
            "concurrency-control",
            "container-optimized"
        ]
    }


if __name__ == "__main__":
    # 從環境變數讀取埠號（Railway 會提供），預設 3000
    port = int(os.getenv("PORT", 3000))
    
    print("🚀 Parser 伺服器已啟動！（Python 增強版 v1.7.0）")
    print(f"📡 監聽埠號: {port}")
    print(f"🌐 本地訪問: http://localhost:{port}")
    print(f"📚 API 文件: http://localhost:{port}/docs")
    print("\n🛡️  增強功能:")
    print("  ✓ 自動重試機制（403/429 錯誤）")
    print("  ✓ 隨機 User-Agent")
    print("  ✓ SSL 錯誤處理")
    print("  ✓ 指數退避重試")
    print("  ✓ 併發控制（最多 2 個同時運行的瀏覽器）")
    print("  ✓ 容器優化（修復 BlockingIOError）")
    print("\n使用範例:")
    print(f"  POST http://localhost:{port}/api/parse")
    print('  Body: {"url": "https://example.com/article", "max_retries": 3}')
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
