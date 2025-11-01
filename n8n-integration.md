# n8n 整合指南

## 整合方式 1：在 n8n 中使用 HTTP Request 節點

### 工作流程設計

```
[觸發器] → [文章列表] → [HTTP Request] → [解析結果處理] → [儲存/發送]
```

### 步驟 1：HTTP Request 節點配置

1. 在 n8n workflow 中加入 **HTTP Request** 節點
2. 配置如下：

**基本設定：**
- Method: `POST`
- URL: `http://localhost:3000/api/parse`
- Authentication: None
- Response Format: JSON

**Headers：**
```
Content-Type: application/json
```

**Body (JSON)：**
```json
{
  "url": "{{ $json.article_url }}"
}
```

**選項：**
- Batch Size: 1（一次處理一個，避免過載）
- Batch Interval: 2000（每批次間隔 2 秒）

### 步驟 2：解析返回的資料

Parser 回傳的資料結構：
```json
{
  "success": true,
  "data": {
    "title": "文章標題",
    "author": "作者",
    "date_published": "發布日期",
    "content": "完整內容（HTML）",
    "excerpt": "摘要",
    "word_count": 字數,
    "lead_image_url": "主圖片 URL"
  }
}
```

在後續節點中使用：
- `{{ $json.data.title }}` - 標題
- `{{ $json.data.content }}` - 內容
- `{{ $json.data.excerpt }}` - 摘要

### 步驟 3：完整 n8n Workflow 範例

```
1. [Schedule Trigger] - 每天特定時間執行
   ↓
2. [HTTP Request] - 取得你的文章列表 API
   ↓
3. [Split In Batches] - 分批處理文章（避免同時請求太多）
   ↓
4. [HTTP Request] - 呼叫 Parser API 解析每篇文章
   Method: POST
   URL: http://localhost:3000/api/parse
   Body: {"url": "{{ $json.url }}"}
   ↓
5. [Set] - 整理資料格式
   ↓
6. [條件分支]
   ├─ 成功 → [儲存到資料庫] → [發送通知]
   └─ 失敗 → [錯誤記錄]
```

---

## 整合方式 2：批次處理腳本（推薦用於大量文章）

如果你每天有很多文章要處理，可以使用批次處理腳本。

### 使用方式：

1. n8n 產出文章列表 JSON 檔案：
```json
[
  {"url": "https://example.com/article1", "id": "001"},
  {"url": "https://example.com/article2", "id": "002"}
]
```

2. 執行批次處理：
```bash
node n8n-batch-parser.js articles.json output.json
```

3. 將處理結果導入回 n8n 或資料庫

---

## 整合方式 3：Webhook 接收器（即時處理）

Parser API 新增 n8n webhook 回調功能。

### n8n Workflow 配置：

```
1. [Webhook] - 接收 Parser 的結果
   Webhook URL: https://your-n8n.com/webhook/parsed-article
   Method: POST
   ↓
2. [處理解析結果]
   ↓
3. [儲存/發送]
```

### 呼叫方式：

```bash
curl -X POST http://localhost:3000/api/parse-and-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "webhook_url": "https://your-n8n.com/webhook/parsed-article"
  }'
```

---

## 整合方式 4：直接在 n8n 中使用 Code 節點

如果你想要更靈活的控制，可以直接在 n8n 的 Code 節點中呼叫 API：

```javascript
// n8n Code 節點
const items = [];

for (const item of $input.all()) {
  const url = item.json.article_url;
  
  try {
    const response = await fetch('http://localhost:3000/api/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url })
    });
    
    const result = await response.json();
    
    if (result.success) {
      items.push({
        json: {
          original_url: url,
          title: result.data.title,
          author: result.data.author,
          content: result.data.content,
          excerpt: result.data.excerpt,
          published_date: result.data.date_published,
          word_count: result.data.word_count,
          image: result.data.lead_image_url
        }
      });
    }
    
    // 避免請求過快
    await new Promise(resolve => setTimeout(resolve, 1000));
    
  } catch (error) {
    console.error(`解析失敗: ${url}`, error);
    // 可以選擇記錄錯誤或跳過
  }
}

return items;
```

---

## 效能建議

### 1. 速率限制
- 每秒不超過 5 個請求
- 使用 n8n 的 Split In Batches 節點控制速率

### 2. 錯誤處理
- 在 n8n 中加入 Error Trigger 節點
- 記錄失敗的 URL 以便重試

### 3. 快取機制
- 避免重複解析相同 URL
- 可以在 n8n workflow 中加入檢查邏輯

### 4. 超時設定
- HTTP Request 節點設定 Timeout: 30000ms（30 秒）
- 某些大型文章可能需要更長時間

---

## 常見問題

### Q: n8n 和 Parser API 在不同機器上怎麼辦？

如果 Parser API 在不同的伺服器：
1. 將 `http://localhost:3000` 改為實際的 IP 或域名
2. 確保防火牆允許該端口訪問
3. 考慮使用 HTTPS（生產環境建議）

### Q: 如何處理失敗的請求？

在 n8n 中加入錯誤處理：
1. 使用 IF 節點檢查 `{{ $json.success }}`
2. 失敗的項目可以存入「待重試」列表
3. 設定另一個 workflow 定期重試失敗項目

### Q: 大量文章會不會過載？

建議措施：
1. 使用 Split In Batches 節點（每批 5-10 個）
2. 設定批次間隔（2-5 秒）
3. 考慮在非尖峰時段執行
4. 必要時部署多個 Parser API 實例

---

## 下一步

選擇適合你的整合方式後，我可以幫你：
1. ✅ 建立具體的 n8n workflow JSON 檔案（可直接匯入）
2. ✅ 建立批次處理腳本
3. ✅ 加入 webhook 回調功能
4. ✅ 優化 API 效能和錯誤處理

請告訴我你的 n8n 工作流程是如何產生文章列表的，我可以提供更具體的整合方案！

