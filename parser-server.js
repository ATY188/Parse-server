import express from 'express';
import Parser from '@postlight/parser';

const app = express();
const PORT = process.env.PORT || 3000;

// 中介軟體：解析 JSON 請求
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 首頁路由
app.get('/', (req, res) => {
  res.json({
    message: '歡迎使用網頁內容解析器 API',
    endpoints: {
      parse: {
        method: 'POST',
        path: '/api/parse',
        body: {
          url: '要解析的網頁 URL'
        },
        description: '解析指定 URL 的網頁內容（同步回傳）'
      },
      parseGet: {
        method: 'GET',
        path: '/api/parse?url=YOUR_URL',
        description: '使用 GET 方法解析網頁內容'
      },
      parseWebhook: {
        method: 'POST',
        path: '/api/parse-webhook',
        body: {
          url: '要解析的網頁 URL',
          webhook_url: 'n8n webhook URL',
          metadata: '(選填) 額外資料'
        },
        description: '解析網頁並回調 webhook（適用於 n8n 整合）'
      }
    },
    examples: [
      'POST /api/parse with body: {"url": "https://example.com/article"}',
      'GET /api/parse?url=https://example.com/article',
      'POST /api/parse-webhook with body: {"url": "https://example.com/article", "webhook_url": "https://your-n8n.com/webhook/..."}'
    ]
  });
});

// POST 方法：解析網頁內容
app.post('/api/parse', async (req, res) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({
        error: '請提供 URL',
        example: { url: 'https://example.com/article' }
      });
    }

    // 驗證 URL 格式
    try {
      new URL(url);
    } catch (e) {
      return res.status(400).json({
        error: 'URL 格式不正確',
        provided: url
      });
    }

    console.log(`正在解析: ${url}`);
    
    // 使用 @postlight/parser 解析網頁
    const result = await Parser.parse(url);

    res.json({
      success: true,
      data: {
        title: result.title,
        author: result.author,
        date_published: result.date_published,
        lead_image_url: result.lead_image_url,
        dek: result.dek,
        url: result.url,
        domain: result.domain,
        excerpt: result.excerpt,
        word_count: result.word_count,
        direction: result.direction,
        total_pages: result.total_pages,
        rendered_pages: result.rendered_pages,
        next_page_url: result.next_page_url,
        content: result.content // HTML 格式的文章內容
      }
    });

  } catch (error) {
    console.error('解析錯誤:', error);
    res.status(500).json({
      error: '解析網頁時發生錯誤',
      message: error.message,
      url: req.body.url
    });
  }
});

// GET 方法：解析網頁內容（透過 query string）
app.get('/api/parse', async (req, res) => {
  try {
    const { url } = req.query;

    if (!url) {
      return res.status(400).json({
        error: '請在 URL 參數中提供要解析的網址',
        example: '/api/parse?url=https://example.com/article'
      });
    }

    // 驗證 URL 格式
    try {
      new URL(url);
    } catch (e) {
      return res.status(400).json({
        error: 'URL 格式不正確',
        provided: url
      });
    }

    console.log(`正在解析: ${url}`);
    
    // 使用 @postlight/parser 解析網頁
    const result = await Parser.parse(url);

    res.json({
      success: true,
      data: {
        title: result.title,
        author: result.author,
        date_published: result.date_published,
        lead_image_url: result.lead_image_url,
        dek: result.dek,
        url: result.url,
        domain: result.domain,
        excerpt: result.excerpt,
        word_count: result.word_count,
        direction: result.direction,
        total_pages: result.total_pages,
        rendered_pages: result.rendered_pages,
        next_page_url: result.next_page_url,
        content: result.content // HTML 格式的文章內容
      }
    });

  } catch (error) {
    console.error('解析錯誤:', error);
    res.status(500).json({
      error: '解析網頁時發生錯誤',
      message: error.message,
      url: req.query.url
    });
  }
});

// POST 方法：解析網頁並回調 webhook（用於 n8n 整合）
app.post('/api/parse-webhook', async (req, res) => {
  try {
    const { url, webhook_url, metadata } = req.body;

    if (!url) {
      return res.status(400).json({
        error: '請提供 URL',
        example: { url: 'https://example.com/article', webhook_url: 'https://your-n8n.com/webhook/...' }
      });
    }

    if (!webhook_url) {
      return res.status(400).json({
        error: '請提供 webhook_url',
        example: { url: 'https://example.com/article', webhook_url: 'https://your-n8n.com/webhook/...' }
      });
    }

    // 驗證 URL 格式
    try {
      new URL(url);
      new URL(webhook_url);
    } catch (e) {
      return res.status(400).json({
        error: 'URL 格式不正確',
        provided: { url, webhook_url }
      });
    }

    // 立即回應請求已接收（非同步處理）
    res.json({
      success: true,
      message: '解析任務已接收，將在完成後回調 webhook',
      url,
      webhook_url
    });

    // 背景處理解析和回調
    console.log(`正在解析 (webhook 模式): ${url}`);
    
    try {
      const result = await Parser.parse(url);
      
      // 準備回調資料
      const webhookData = {
        success: true,
        original_url: url,
        metadata: metadata || {},
        parsed_data: {
          title: result.title,
          author: result.author,
          date_published: result.date_published,
          lead_image_url: result.lead_image_url,
          dek: result.dek,
          url: result.url,
          domain: result.domain,
          excerpt: result.excerpt,
          word_count: result.word_count,
          direction: result.direction,
          total_pages: result.total_pages,
          rendered_pages: result.rendered_pages,
          next_page_url: result.next_page_url,
          content: result.content
        },
        parsed_at: new Date().toISOString()
      };

      // 回調 webhook
      const webhookResponse = await fetch(webhook_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(webhookData)
      });

      if (webhookResponse.ok) {
        console.log(`✅ Webhook 回調成功: ${webhook_url}`);
      } else {
        console.error(`❌ Webhook 回調失敗 (${webhookResponse.status}): ${webhook_url}`);
      }

    } catch (error) {
      console.error('解析或回調錯誤:', error);
      
      // 嘗試回調錯誤訊息
      try {
        await fetch(webhook_url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            success: false,
            original_url: url,
            metadata: metadata || {},
            error: error.message,
            failed_at: new Date().toISOString()
          })
        });
      } catch (webhookError) {
        console.error('無法回調錯誤訊息:', webhookError);
      }
    }

  } catch (error) {
    console.error('請求處理錯誤:', error);
    res.status(500).json({
      error: '處理請求時發生錯誤',
      message: error.message
    });
  }
});

// 404 處理
app.use((req, res) => {
  res.status(404).json({
    error: '找不到該路由',
    availableEndpoints: [
      'GET /',
      'POST /api/parse',
      'GET /api/parse?url=YOUR_URL',
      'POST /api/parse-webhook'
    ]
  });
});

// 啟動伺服器
app.listen(PORT, () => {
  console.log(`🚀 Parser 伺服器已啟動！`);
  console.log(`📡 監聽埠號: ${PORT}`);
  console.log(`🌐 本地訪問: http://localhost:${PORT}`);
  console.log(`\n使用範例:`);
  console.log(`  POST http://localhost:${PORT}/api/parse`);
  console.log(`  Body: {"url": "https://example.com/article"}`);
  console.log(`\n  或使用 GET:`);
  console.log(`  http://localhost:${PORT}/api/parse?url=https://example.com/article`);
});