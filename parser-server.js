import express from 'express';
import Parser from '@postlight/parser';
import axios from 'axios';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// 增強的 headers（用於新端點）
const enhancedHeaders = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
  'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Cache-Control': 'max-age=0'
};

// ===== 原始端點（100% 保持不變）===== 

// 原始的 parse 端點（POST）
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

// 原始的 parse 端點（GET）
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

// ===== 新增：增強版端點 =====

// 增強版 parse 端點（使用更好的 headers）
app.post('/api/parse-enhanced', async (req, res) => {
  try {
    const { url, customHeaders } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false,
        error: 'URL is required' 
      });
    }

    console.log(`[Enhanced] 解析 URL: ${url}`);

    // 合併自定義 headers
    const headers = { ...enhancedHeaders, ...customHeaders };

    const result = await Parser.parse(url, {
      headers: headers,
      timeout: 10000
    });
    
    res.json({
      success: true,
      data: result,
      method: 'enhanced'
    });
  } catch (error) {
    console.error(`[Enhanced] 錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message,
      url: req.body.url,
      method: 'enhanced'
    });
  }
});

// ===== URL 重定向解析 =====

app.post('/api/resolve-url', async (req, res) => {
  try {
    const { url, useEnhancedHeaders } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false, 
        error: 'URL is required' 
      });
    }

    console.log(`[Resolve] 解析重定向: ${url}`);

    // 可選使用增強 headers
    const headers = useEnhancedHeaders ? enhancedHeaders : {};

    const response = await axios.get(url, {
      maxRedirects: 5,
      timeout: 10000,
      headers: headers,
      validateStatus: (status) => status < 400,
    });
    
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

// ===== 健康檢查和 API 資訊 =====

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    version: '1.1.0',
    endpoints: {
      legacy: '/parse (POST/GET)',
      enhanced: '/api/parse-enhanced (POST)',
      resolve: '/api/resolve-url (POST)'
    }
  });
});

app.get('/', (req, res) => {
  res.json({
    name: 'News Parser API',
    version: '1.1.0',
    description: '支援新舊兩種解析方式，可逐步遷移',
    endpoints: {
      parse: {
        method: 'POST/GET',
        path: '/parse',
        description: '原始解析端點（保持 100% 不變）',
        status: 'stable',
        params: {
          url: 'required'
        },
        example: {
          url: 'https://example.com/article'
        }
      },
      parseEnhanced: {
        method: 'POST',
        path: '/api/parse-enhanced',
        description: '增強版解析端點（更好的 headers，適用於難抓的網站）',
        status: 'experimental',
        params: {
          url: 'required',
          customHeaders: 'optional'
        },
        example: {
          url: 'https://example.com/article',
          customHeaders: {
            'Referer': 'https://google.com'
          }
        }
      },
      resolveUrl: {
        method: 'POST',
        path: '/api/resolve-url',
        description: '解析 URL 重定向（Google News 等）',
        status: 'stable',
        params: {
          url: 'required',
          useEnhancedHeaders: 'optional (boolean)'
        },
        example: {
          url: 'https://news.google.com/rss/articles/...',
          useEnhancedHeaders: true
        }
      },
      health: {
        method: 'GET',
        path: '/health',
        description: '健康檢查'
      }
    },
    migration: {
      step1: '先用 /parse 測試（現有功能）',
      step2: '對失敗的 URL 嘗試 /api/parse-enhanced',
      step3: '比較兩者的成功率',
      step4: '逐步遷移到成功率更高的端點'
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Parser server is running on port ${PORT}`);
  console.log(`📡 Endpoints:`);
  console.log(`   POST/GET /parse - 原始解析（穩定版）`);
  console.log(`   POST     /api/parse-enhanced - 增強解析（實驗版）`);
  console.log(`   POST     /api/resolve-url - URL 重定向`);
  console.log(`   GET      /health - 健康檢查`);
  console.log(`   GET      / - API 說明文件`);
});
