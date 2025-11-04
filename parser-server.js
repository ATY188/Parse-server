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

// 增強的 headers，模擬真實瀏覽器
const defaultHeaders = {
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

// 原始的 parse 端點（使用增強 headers）
app.post('/parse', async (req, res) => {
  try {
    const { url, customHeaders } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false,
        error: 'URL is required' 
      });
    }

    console.log(`[Parse] 解析 URL: ${url}`);

    // 合併自定義 headers
    const headers = { ...defaultHeaders, ...customHeaders };

    const result = await Parser.parse(url, {
      headers: headers,
      timeout: 10000
    });
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error(`[Parse] 錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message,
      url: req.body.url
    });
  }
});

app.get('/parse', async (req, res) => {
  try {
    const { url } = req.query;
    
    if (!url) {
      return res.status(400).json({ 
        success: false,
        error: 'URL is required' 
      });
    }

    console.log(`[Parse GET] 解析 URL: ${url}`);

    const result = await Parser.parse(url, {
      headers: defaultHeaders,
      timeout: 10000
    });
    
    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error(`[Parse GET] 錯誤: ${error.message}`);
    res.status(500).json({ 
      success: false,
      error: error.message,
      url: req.query.url
    });
  }
});

// 輕量級 URL 重定向解析（只跟隨重定向，不抓取內容）
app.post('/api/resolve-url', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({ 
        success: false, 
        error: 'URL is required' 
      });
    }

    console.log(`[Resolve] 解析重定向: ${url}`);

    // 使用 axios 跟隨重定向
    const response = await axios.get(url, {
      maxRedirects: 5,
      timeout: 10000,
      headers: defaultHeaders,
      validateStatus: (status) => status < 400,
    });
    
    // 返回最終的 URL
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

// 健康檢查
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    version: '1.1.0',
    features: [
      'parse',
      'resolve-url',
      'enhanced-headers'
    ]
  });
});

// API 資訊
app.get('/', (req, res) => {
  res.json({
    name: 'News Parser API',
    version: '1.1.0',
    endpoints: {
      parse: {
        method: 'POST/GET',
        path: '/parse',
        description: '解析網頁內容（標題、作者、內容等）',
        params: {
          url: 'required',
          customHeaders: 'optional'
        }
      },
      resolveUrl: {
        method: 'POST',
        path: '/api/resolve-url',
        description: '解析 URL 重定向（Google News 等）',
        params: {
          url: 'required'
        }
      },
      health: {
        method: 'GET',
        path: '/health',
        description: '健康檢查'
      }
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Parser server is running on port ${PORT}`);
  console.log(`📡 Endpoints:`);
  console.log(`   POST /parse - 解析網頁內容`);
  console.log(`   POST /api/resolve-url - 解析 URL 重定向`);
  console.log(`   GET  /health - 健康檢查`);
});
