# Parser API 使用指南

## 🌐 你的 Parser API 網址

**主要網址：** https://web-production-32568.up.railway.app

**API 文件（Swagger UI）：** https://web-production-32568.up.railway.app/docs

---

## 📖 Swagger UI 介面說明

### 什麼是 Swagger UI？

Swagger UI 是一個 **互動式 API 文件介面**，讓你可以：
- 📖 查看所有可用的 API 端點
- 🧪 直接在網頁上測試 API
- 📋 查看請求和回應格式
- 💡 了解每個參數的用途

---

## 🎯 如何打開 API 文件

### 步驟 1：開啟網址
在瀏覽器輸入：
```
https://web-production-32568.up.railway.app/docs
```

### 步驟 2：你會看到什麼

**頁面標題：**
```
FastAPI - Swagger UI
```

**頁面內容：**
你會看到 3-4 個可展開的 API 端點區塊：

```
GET  /                     首頁（API 資訊）
POST /api/parse            解析網頁（同步）
GET  /api/parse            解析網頁（GET 方法）
POST /api/parse-webhook    解析網頁（異步 + webhook）
```

每個區塊都可以點擊展開。

---

## 🔧 如何使用 API（在 Swagger UI 中）

### 方法 1：使用 POST /api/parse（最常用）⭐

#### 步驟 1：展開 API 區塊
點擊這個區塊：
```
POST /api/parse
解析指定 URL 的網頁內容
```

#### 步驟 2：點擊「Try it out」
右上角有個藍色按鈕 **"Try it out"**，點擊它。

#### 步驟 3：填入測試資料
你會看到一個 JSON 編輯器，裡面有範例：
```json
{
  "url": "string"
}
```

**修改為實際網址：**
```json
{
  "url": "https://technews.tw/2025/10/31/tsmc-news/"
}
```

#### 步驟 4：執行測試
點擊藍色的 **"Execute"** 按鈕。

#### 步驟 5：查看結果
往下滾動，你會看到：

**Response（回應）：**
```json
{
  "success": true,
  "data": {
    "url": "https://technews.tw/2025/10/31/tsmc-news/",
    "title": "台積電宣布擴大徵才計畫",
    "author": "王小明",
    "date_published": "2025-10-31",
    "content": "台積電今日宣布...",
    "excerpt": "台積電今日宣布...",
    "word_count": 1234,
    "domain": "technews.tw",
    "description": "台積電新聞",
    "language": "zh-TW"
  }
}
```

**Response Code（狀態碼）：**
```
200 OK
```

---

### Swagger UI 各欄位說明

當你展開一個 API 端點後，你會看到：

#### 1. Request body（請求內容）
```
這是你要發送給 API 的資料

範例：
{
  "url": "https://example.com/article"
}
```

**欄位說明：**
- `url` (string, required): 你想解析的文章網址

#### 2. Responses（可能的回應）
展開後會看到：

**200 Successful Response（成功）**
```json
{
  "success": true,
  "data": {
    "url": "...",
    "title": "...",
    "content": "..."
  }
}
```

**422 Validation Error（驗證錯誤）**
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error（伺服器錯誤）**
```json
{
  "detail": "下載網頁失敗: ..."
}
```

#### 3. curl 指令（複製使用）
點擊 **"curl"** 分頁，你會看到等效的 curl 指令：
```bash
curl -X 'POST' \
  'https://web-production-32568.up.railway.app/api/parse' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://technews.tw/2025/10/31/tsmc-news/"
}'
```

你可以複製這個指令，在終端機執行！

---

## 🧪 實際測試範例

### 範例 1：解析科技新聞

**在 Swagger UI 中：**

1. 展開 `POST /api/parse`
2. 點擊 "Try it out"
3. 輸入：
```json
{
  "url": "https://technews.tw/2025/10/28/amd-supercomputer/"
}
```
4. 點擊 "Execute"
5. 查看回應

**預期結果：**
- ✅ Status code: 200
- ✅ success: true
- ✅ 回傳完整文章內容

---

### 範例 2：解析 BBC 新聞

```json
{
  "url": "https://www.bbc.com/news"
}
```

**預期結果：**
- ✅ 提取 BBC 首頁的新聞列表
- ✅ 約 1000-2000 字

---

### 範例 3：錯誤的網址

```json
{
  "url": "https://example.com/not-exist"
}
```

**預期結果：**
- ❌ Status code: 500
- ❌ 錯誤訊息：`下載網頁失敗: Client error '404 Not Found'`

---

## 🔍 回應資料結構詳解

### 成功回應的 JSON 結構

```json
{
  "success": true,              // 是否成功
  "data": {                     // 實際資料
    "url": "...",              // 原始網址
    "title": "...",            // 文章標題
    "author": "..." or null,   // 作者（可能是 null）
    "date_published": "...",   // 發布日期（YYYY-MM-DD）
    "content": "<doc>...</doc>", // HTML 格式的完整內容
    "text_content": "...",     // 純文字內容
    "excerpt": "...",          // 摘要（前 200 字）
    "word_count": 1234,        // 字數統計
    "domain": "...",           // 網域名稱
    "description": "...",      // 網頁描述
    "categories": [],          // 分類（可能為空）
    "tags": [],                // 標籤（可能為空）
    "language": "en" or null   // 語言代碼
  }
}
```

### 各欄位說明

| 欄位 | 型別 | 說明 | 可能是 null? |
|------|------|------|-------------|
| `success` | boolean | 是否成功解析 | ❌ |
| `data.url` | string | 原始網址 | ❌ |
| `data.title` | string | 文章標題 | ❌ |
| `data.author` | string | 作者名稱 | ✅ |
| `data.date_published` | string | 發布日期（ISO 格式） | ✅ |
| `data.content` | string | HTML 格式的完整內容 | ❌ |
| `data.text_content` | string | 純文字內容（無 HTML） | ❌ |
| `data.excerpt` | string | 文章摘要（前 200 字） | ❌ |
| `data.word_count` | integer | 字數統計 | ❌ |
| `data.domain` | string | 網域（如 bbc.com） | ❌ |
| `data.description` | string | 網頁描述（meta） | ✅ |
| `data.categories` | array | 分類列表 | ❌ (但可能是空陣列) |
| `data.tags` | array | 標籤列表 | ❌ (但可能是空陣列) |
| `data.language` | string | 語言代碼（如 en, zh） | ✅ |

---

## 🎯 在 n8n 中如何使用這些資料

### 取得標題
```
{{ $json.data.title }}
```

### 取得作者（帶預設值）
```
{{ $json.data.author || "未知作者" }}
```

### 取得純文字內容
```
{{ $json.data.text_content }}
```

### 取得發布日期
```
{{ $json.data.date_published }}
```

### 取得字數
```
{{ $json.data.word_count }}
```

---

## 🛠️ 在終端機使用 API

### 基本用法（macOS/Linux）

```bash
curl -X POST https://web-production-32568.up.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://technews.tw/2025/10/31/article-123"}'
```

### 美化輸出（使用 jq）

```bash
curl -s -X POST https://web-production-32568.up.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://technews.tw/2025/10/31/article-123"}' \
  | jq .
```

### 只顯示關鍵欄位

```bash
curl -s -X POST https://web-production-32568.up.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://technews.tw/2025/10/31/article-123"}' \
  | jq '{title: .data.title, author: .data.author, word_count: .data.word_count}'
```

### 儲存結果到檔案

```bash
curl -s -X POST https://web-production-32568.up.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://technews.tw/2025/10/31/article-123"}' \
  > result.json
```

---

## 🔗 在程式中使用 API

### Python

```python
import requests

url = "https://web-production-32568.up.railway.app/api/parse"
data = {"url": "https://technews.tw/2025/10/31/article-123"}

response = requests.post(url, json=data)
result = response.json()

print(f"標題：{result['data']['title']}")
print(f"字數：{result['data']['word_count']}")
print(f"內容：{result['data']['text_content'][:200]}...")
```

### JavaScript

```javascript
const url = "https://web-production-32568.up.railway.app/api/parse";
const data = { url: "https://technews.tw/2025/10/31/article-123" };

fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(res => res.json())
.then(result => {
  console.log('標題：', result.data.title);
  console.log('字數：', result.data.word_count);
  console.log('內容：', result.data.text_content.substring(0, 200) + '...');
});
```

---

## 🚨 常見錯誤和解決方案

### 錯誤 1：422 Validation Error

**錯誤訊息：**
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "field required"
    }
  ]
}
```

**原因：** 沒有提供 `url` 欄位

**解決：** 確保 JSON 中包含 `url`
```json
{
  "url": "https://example.com"
}
```

---

### 錯誤 2：404 Not Found

**錯誤訊息：**
```json
{
  "detail": "下載網頁失敗: Client error '404 Not Found'"
}
```

**原因：** 網址不存在或已被刪除

**解決：** 
- 檢查網址是否正確
- 在瀏覽器中開啟網址，確認可訪問

---

### 錯誤 3：Timeout

**錯誤訊息：**
```
Request timeout
```

**原因：** 網頁載入時間過長（超過 30 秒）

**解決：**
- 重試一次
- 選擇載入較快的網站

---

### 錯誤 4：Empty Content

**成功但內容是空的：**
```json
{
  "success": true,
  "data": {
    "content": "",
    "text_content": ""
  }
}
```

**原因：** 
- 網頁需要 JavaScript 渲染
- 網頁是動態載入內容
- 網站有反爬蟲機制

**解決：**
- 換個類似的新聞網址試試
- 使用主流新聞網站（BBC, CNN, TechNews 等）

---

## 📊 建議的使用限制

### 速率限制（Rate Limit）
目前沒有硬性限制，但建議：
- **每次請求間隔：** 至少 1 秒
- **每分鐘請求數：** < 30 次
- **每小時請求數：** < 500 次
- **每天請求數：** < 5000 次

### 為什麼要限制？
- 避免被目標網站封鎖
- 保持 Railway 服務穩定
- 減少成本

### 在 n8n 中如何控制？
- 使用 **Wait** 節點在請求之間加入延遲
- 使用 **Split In Batches** 分批處理
- 設定 **Schedule Trigger** 間隔（如每 30 分鐘）

---

## 🎯 最佳實踐

### 1. 選擇適合的網址
```
✅ 好的：單一文章頁面
   https://technews.tw/2025/10/31/specific-article/

❌ 不好的：首頁或列表頁
   https://technews.tw/
   https://news.google.com/
```

### 2. 處理可能的 null 值
在使用資料前檢查：
```javascript
const author = result.data.author || "未知作者";
const date = result.data.date_published || "日期不明";
```

### 3. 截斷過長的內容
Google Sheet 單一儲存格最多 50,000 字元：
```javascript
const content = result.data.text_content.substring(0, 10000);
```

### 4. 錯誤處理
在 n8n 中：
- 啟用 **Continue On Fail**
- 設定錯誤分支
- 記錄失敗原因

---

## 🎉 你現在會了！

你已經了解：
- ✅ 如何打開 API 文件（/docs）
- ✅ 如何在 Swagger UI 中測試
- ✅ 回應資料的結構
- ✅ 如何在終端機使用
- ✅ 如何處理錯誤
- ✅ 最佳實踐

**下一步：** 開始在 n8n 中使用這個 API！🚀


