import express from 'express';
import Parser from '@postlight/parser';
import axios from 'axios';
import https from 'https';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// 多組 User-Agent 輪流使用
const userAgents = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
];

// 隨機選擇 User-Agent
function getRandomUserAgent() {
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}

// 基礎 headers
function getBaseHeaders(url) {
  const urlObj = new URL(url);
  return {
    'User-Agent': getRandomUserAgent(),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': `https://${urlObj.hostname}/`,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
  };
}

// 重試邏輯（exponential backoff）
async function parseWithRetry(url, options = {}, maxRetries = 2) {
  const { headers, skipSSL = false } = options;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`[Parse] 嘗試 ${attempt}/${maxRetries}: ${url}`);
      
      const parserOptions = {
        headers: headers || getBaseHeaders(url),
        timeout: 15000
      };

      // 如果需要跳過 SSL 驗證
      if (skipSSL) {
        parserOptions.agent = new https.Agent({
          rejectUnauthorized: false
        });
      }

      const result = await Parser.parse(url, parserOptions);
      
      console.log(`[Parse] 成功: ${result.title?.substring(0, 50) || 'No title'}`);
      return {
        success: true,
        data: result,
        attempt: attempt
      };
      
    } catch (error) {
      console.error(`[Parse] 嘗試 ${attempt} 失敗: ${error.message}`);
      
      // 如果是最後一次嘗試，返回錯誤
      if (attempt === maxRetries) {
        return {
          success: false,
          error: error.message,
          attempt: attempt,
          url: url
        };
      }
      
      // 如果是 429 或 403，等待後重試
      if (error.message.includes('429') || error.message.includes('403')) {
        const waitTime = Math.pow(2, attempt) * 1000; // 2秒、4秒、8秒...
        console.log(`[Parse] 等待 ${waitTime}ms 後重試...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      } else if (error.message.includes('SSL') || error.message.includes('certificate')) {
        // SSL 錯誤，下次嘗試時跳過驗證
        console.log(`[Parse] SSL 錯誤，下次將跳過驗證...`);
        options.skipSSL = true;
      } else {
        // 其他錯誤，短暫等待後重試
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }
}

// ===== 原始端點（保持不變）===== 

app.post('/parse', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    const result = await Parser.parse(url);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/parse', async (req, res) => {
  try {
    const { url } = req.query;
    
    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    const result = await Parser.parse(url);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ===== 增強版端點（帶重試和錯誤處理）=====

app.post('/api/parse-enhanced', async (req, res) => {
  try {
    const { url, customHeaders, maxRetries = 2, skipSSL = false } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false,
        error: 'URL is required' 
      });
    }

    console.log(`[Enhanced] 開始解析: ${url}`);

    // 合併 headers
    const headers = customHeaders 
      ? { ...getBaseHeaders(url), ...customHeaders }
      : getBaseHeaders(url);

    // 使用重試機制
    const result = await parseWithRetry(url, { headers, skipSSL }, maxRetries);
    
    // 根據結果返回適當的狀態碼
    if (result.success) {
      res.json(result);
    } else {
      // 仍然返回 200，但 success: false
      res.json(result);
    }
    
  } catch (error) {
    console.error(`[Enhanced] 未預期的錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message,
      url: req.body.url
    });
  }
});

// ===== URL 重定向解析 =====

app.post('/api/resolve-url', async (req, res) => {
  try {
    const { url, useEnhancedHeaders = true, skipSSL = false } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false, 
        error: 'URL is required' 
      });
    }

    console.log(`[Resolve] 解析重定向: ${url}`);

    const headers = useEnhancedHeaders ? getBaseHeaders(url) : {};
    
    const axiosConfig = {
      maxRedirects: 5,
      timeout: 10000,
      headers: headers,
      validateStatus: (status) => status < 400
    };

    // 如果需要跳過 SSL 驗證
    if (skipSSL) {
      axiosConfig.httpsAgent = new https.Agent({
        rejectUnauthorized: false
      });
    }

    const response = await axios.get(url, axiosConfig);
    
    res.json({
      success: true,
      data: {
        original_url: url,
        resolved_url: response.request.res.responseUrl || response.config.url || url,
        status_code: response.status
      }
    });
  } catch (error) {
    console.error(`[Resolve] 錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message,
      original_url: req.body.url
    });
  }
});

// ===== 批次解析（新增）=====

app.post('/api/parse-batch', async (req, res) => {
  try {
    const { urls, delay = 1000, maxRetries = 2 } = req.body;
    
    if (!urls || !Array.isArray(urls)) {
      return res.status(400).json({ 
        success: false,
        error: 'URLs array is required' 
      });
    }

    console.log(`[Batch] 開始批次解析 ${urls.length} 個 URLs`);

    const results = [];
    
    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      console.log(`[Batch] 處理 ${i + 1}/${urls.length}: ${url}`);
      
      const result = await parseWithRetry(url, { 
        headers: getBaseHeaders(url) 
      }, maxRetries);
      
      results.push(result);
      
      // 延遲，避免 429 錯誤
      if (i < urls.length - 1 && delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    const successCount = results.filter(r => r.success).length;
    
    res.json({
      success: true,
      total: urls.length,
      successful: successCount,
      failed: urls.length - successCount,
      results: results
    });
    
  } catch (error) {
    console.error(`[Batch] 錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message
    });
  }
});

// ===== 健康檢查和 API 資訊 =====

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    version: '1.2.0',
    features: [
      'parse (original)',
      'parse-enhanced (with retry)',
      'resolve-url',
      'parse-batch'
    ]
  });
});

app.get('/', (req, res) => {
  res.json({
    name: 'News Parser API',
    version: '1.2.0',
    description: '支援多種解析模式，自動處理常見錯誤',
    endpoints: {
      parse: {
        method: 'POST/GET',
        path: '/parse',
        description: '原始解析端點（穩定版）',
        status: 'stable'
      },
      parseEnhanced: {
        method: 'POST',
        path: '/api/parse-enhanced',
        description: '增強版解析（自動重試、處理 403/429/SSL 錯誤）',
        status: 'recommended',
        params: {
          url: 'required',
          customHeaders: 'optional',
          maxRetries: 'optional (default: 2)',
          skipSSL: 'optional (default: false)'
        },
        example: {
          url: 'https://example.com/article',
          maxRetries: 3,
          skipSSL: false
        }
      },
      resolveUrl: {
        method: 'POST',
        path: '/api/resolve-url',
        description: '解析 URL 重定向',
        status: 'stable',
        params: {
          url: 'required',
          useEnhancedHeaders: 'optional (default: true)',
          skipSSL: 'optional (default: false)'
        }
      },
      parseBatch: {
        method: 'POST',
        path: '/api/parse-batch',
        description: '批次解析多個 URLs（自動延遲避免 429）',
        status: 'experimental',
        params: {
          urls: 'required (array)',
          delay: 'optional (ms, default: 1000)',
          maxRetries: 'optional (default: 2)'
        },
        example: {
          urls: ['https://url1.com', 'https://url2.com'],
          delay: 2000,
          maxRetries: 3
        }
      }
    },
    errorHandling: {
      '403 Forbidden': '自動重試 + 隨機 User-Agent + Referer header',
      '429 Too Many Requests': '指數退避重試（2s, 4s, 8s...）',
      'SSL Certificate Error': '可選擇跳過 SSL 驗證（skipSSL: true）'
    },
    bestPractices: {
      singleUrl: '使用 /api/parse-enhanced（自動處理錯誤）',
      batchUrls: '使用 /api/parse-batch（自動控制速率）',
      googleNews: '先用 /api/resolve-url，再用 /api/parse-enhanced'
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Parser server v1.2.0 is running on port ${PORT}`);
  console.log(`📡 Endpoints:`);
  console.log(`   POST/GET /parse - 原始解析`);
  console.log(`   POST     /api/parse-enhanced - 增強解析（推薦）⭐`);
  console.log(`   POST     /api/resolve-url - URL 重定向`);
  console.log(`   POST     /api/parse-batch - 批次解析`);
  console.log(`   GET      /health - 健康檢查`);
  console.log(`\n🛡️  錯誤處理:`);
  console.log(`   ✓ 403/429 自動重試`);
  console.log(`   ✓ SSL 錯誤處理`);
  console.log(`   ✓ 隨機 User-Agent`);
  console.log(`   ✓ 批次速率控制`);
});
