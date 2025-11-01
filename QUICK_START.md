# 快速上手指南 - n8n 整合

## 🎯 三種整合方式

### 方式 1：HTTP Request 節點（最簡單） ⭐ 推薦

適合：每天文章數量不多，需要即時處理

**在 n8n workflow 中：**

```
1. 你的資料源 → 2. HTTP Request → 3. 處理結果
```

**HTTP Request 節點設定：**
- Method: `POST`
- URL: `http://localhost:3000/api/parse`
- Body: `{"url": "{{ $json.article_url }}"}`

**優點：**
- ✅ 最簡單，5 分鐘設定完成
- ✅ 即時取得結果
- ✅ 完全在 n8n 內控制

---

### 方式 2：批次處理腳本（大量文章）

適合：每天有大量文章，可以離線處理

**步驟：**

1. **n8n 匯出文章列表到 JSON：**
```json
[
  {"url": "https://example.com/article1", "id": "001"},
  {"url": "https://example.com/article2", "id": "002"}
]
```

2. **執行批次處理：**
```bash
node n8n-batch-parser.js articles.json results.json
```

3. **n8n 讀取結果檔案並處理**

**優點：**
- ✅ 自動重試失敗項目
- ✅ 控制請求速率
- ✅ 產生錯誤報告

**測試批次處理：**
```bash
npm run batch
```

---

### 方式 3：Webhook 回調（非同步）

適合：解析時間長，不想等待回應

**流程：**

1. **n8n 建立 Webhook 節點**
   - 複製 webhook URL（例如：`https://your-n8n.com/webhook/abc123`）

2. **呼叫 Parser API：**
```bash
curl -X POST http://localhost:3000/api/parse-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "webhook_url": "https://your-n8n.com/webhook/abc123",
    "metadata": {"article_id": "001", "source": "RSS"}
  }'
```

3. **Parser 解析完成後自動推送到你的 n8n webhook**

**優點：**
- ✅ 立即回應，不用等待解析完成
- ✅ 適合長時間解析
- ✅ 可以附帶 metadata

---

## 🚀 快速開始

### Step 1: 啟動 Parser API

```bash
npm start
```

看到這個畫面表示成功：
```
🚀 Parser 伺服器已啟動！
📡 監聽埠號: 3000
🌐 本地訪問: http://localhost:3000
```

### Step 2: 測試 API

**終端機測試：**
```bash
npm test
```

**測試指定 URL：**
```bash
npm run test:url https://www.bbc.com/news/world
```

### Step 3: 選擇整合方式

#### 選項 A：使用 HTTP Request（推薦）

1. 在 n8n 加入 **HTTP Request** 節點
2. 設定如下：
   - Method: `POST`
   - URL: `http://localhost:3000/api/parse`
   - Body: `{"url": "{{ $json.url }}"}`
3. 完成！

#### 選項 B：使用批次處理

1. 修改 `example-articles.json`，加入你的文章 URL
2. 執行：`npm run batch`
3. 查看 `results.json`

#### 選項 C：使用 Webhook

1. 在 n8n 建立 Webhook 節點
2. 複製 webhook URL
3. 使用 `/api/parse-webhook` 端點

---

## 📋 完整 n8n Workflow 範例

我已經為你準備了一個完整的 n8n workflow：

**檔案：** `n8n-workflow-example.json`

**如何使用：**

1. 打開 n8n
2. 點選 Import
3. 選擇 `n8n-workflow-example.json`
4. 根據需要調整設定
5. 啟用 workflow

**Workflow 包含：**
- ⏰ 排程觸發器（每天執行）
- 📥 取得文章列表
- 🔄 分批處理
- 🔍 呼叫 Parser API
- ✅ 成功處理分支
- ❌ 錯誤處理分支
- 💾 儲存到資料庫
- 📢 發送通知

---

## 🛠️ n8n 節點配置詳解

### HTTP Request 節點完整配置

```yaml
節點名稱: 解析文章內容
類型: HTTP Request

基本設定:
  Method: POST
  URL: http://localhost:3000/api/parse
  Authentication: None
  Response Format: JSON

Headers:
  Content-Type: application/json

Body:
  {
    "url": "{{ $json.url }}"
  }

選項:
  Timeout: 30000 (30秒)
  Batch Size: 1
  Batch Interval: 2000 (2秒)
```

### 資料映射

Parser API 回傳後，在後續節點使用：

```javascript
// 標題
{{ $json.data.title }}

// 內容（HTML 格式）
{{ $json.data.content }}

// 摘要
{{ $json.data.excerpt }}

// 作者
{{ $json.data.author }}

// 發布日期
{{ $json.data.date_published }}

// 字數
{{ $json.data.word_count }}

// 主圖片 URL
{{ $json.data.lead_image_url }}
```

---

## 🔧 環境變數

在啟動 Parser API 時可以設定：

```bash
# 變更埠號
PORT=8080 npm start

# 批次處理設定
PARSER_API_URL=http://localhost:8080/api/parse \
DELAY_MS=3000 \
MAX_RETRIES=5 \
npm run batch
```

---

## 📊 常見使用情境

### 情境 1：每日新聞摘要

```
[Schedule: 每天早上 8:00]
  ↓
[RSS Feed 節點: 讀取新聞源]
  ↓
[Filter: 過濾今日文章]
  ↓
[HTTP Request: 呼叫 Parser API]
  ↓
[AI 節點: 生成摘要]
  ↓
[Email: 發送每日摘要]
```

### 情境 2：文章監控與通知

```
[Webhook: 收到新文章通知]
  ↓
[HTTP Request: 解析文章]
  ↓
[IF: 檢查關鍵字]
  ├─ 符合 → [Slack: 發送通知]
  └─ 不符合 → [儲存到資料庫]
```

### 情境 3：批次匯入歷史文章

```
[Manual Trigger]
  ↓
[Read File: articles.json]
  ↓
[Split In Batches: 每批 10 篇]
  ↓
[HTTP Request: 解析文章]
  ↓
[Database: 儲存結果]
```

---

## ⚡ 效能優化建議

### 1. 控制請求速率

在 n8n 中使用 **Split In Batches** 節點：
- Batch Size: 5-10 篇
- Batch Interval: 2000-5000 ms

### 2. 錯誤處理

加入 **Error Trigger** 節點：
- 記錄失敗的 URL
- 自動重試機制
- 發送錯誤通知

### 3. 快取機制

在 n8n 中加入檢查邏輯：
```javascript
// Code 節點
const url = $json.url;
const cached = await checkCache(url);
if (cached) {
  return cached;
}
// 否則呼叫 Parser API
```

---

## 🐛 問題排除

### Parser API 連線失敗

**症狀：** n8n 無法連接到 `http://localhost:3000`

**解決：**
1. 確認 Parser API 已啟動：`npm start`
2. 確認埠號正確（預設 3000）
3. 如果 n8n 在 Docker 中，使用 `http://host.docker.internal:3000`
4. 如果在不同機器，使用實際 IP 位址

### 解析失敗

**症狀：** API 回傳錯誤或無法解析

**解決：**
1. 確認 URL 可訪問
2. 某些網站有反爬蟲保護
3. 增加 timeout 時間（30 秒以上）
4. 檢查網站是否需要 JavaScript 渲染（Parser 無法處理）

### n8n Workflow 太慢

**症狀：** 處理大量文章時很慢

**解決：**
1. 使用批次處理腳本（方式 2）
2. 減少 Batch Size
3. 增加 Batch Interval
4. 考慮在非尖峰時段執行

---

## 📞 更多協助

查看詳細文件：
- `README.md` - 完整 API 文件
- `n8n-integration.md` - 詳細整合指南
- `n8n-workflow-example.json` - 可直接匯入的 workflow

測試工具：
- `npm test` - 測試 API
- `npm run batch` - 測試批次處理

---

## ✨ 下一步

選擇一種整合方式開始：

1. **簡單測試？** → 使用 HTTP Request 節點
2. **大量文章？** → 使用批次處理腳本  
3. **複雜流程？** → 匯入 workflow 範例並修改

需要幫助？告訴我你的 n8n 工作流程，我可以提供更具體的建議！

