# Google Alert 自動化新聞解析系統

## 📧 完整流程圖

```
Google Alert 郵件
    ↓
[Gmail Trigger] 自動讀取新郵件
    ↓
[Extract URLs] 從郵件中提取所有新聞網址
    ↓
[Check Duplicates] 檢查 Google Sheet 是否已存在
    ↓
[Add to Sheet] 將新網址寫入 Google Sheet（status = pending）
    ↓
[Parse Article] 呼叫 Parser API 解析文章內容
    ↓
[Generate Summary] AI 生成摘要
    ↓
[Update Sheet] 更新 Google Sheet（填入所有資料）
    ↓
✅ 完成！
```

---

## 🎯 第一步：設定 Google Alert

### 1. 建立 Google Alert

1. 前往 [Google Alerts](https://www.google.com/alerts)
2. 在搜尋框輸入關鍵字，例如：
   - `聯發科`
   - `台積電 site:technews.tw`
   - `半導體 OR 晶片`
3. 點擊「顯示選項」設定：
   - **頻率**：即時（最快） 或 每天一次
   - **來源**：新聞
   - **語言**：中文
   - **地區**：台灣
   - **數量**：只傳送最佳結果
   - **傳送至**：你的 Gmail 信箱

4. 點擊「建立快訊」

### 2. 確認郵件格式

Google Alert 的郵件會包含：
- **主旨**：`Google 快訊 - 聯發科`
- **寄件者**：`googlealerts-noreply@google.com`
- **內容**：包含多個新聞連結

**郵件範例：**
```html
Google 快訊 - 聯發科

聯發科推出新晶片 挑戰高通霸主地位
科技新報 - 1 小時前
https://technews.tw/2025/11/02/mediatek-new-chip/

聯發科Q3財報亮眼 營收創新高
經濟日報 - 3 小時前
https://money.udn.com/money/story/5612/12345
```

---

## 📊 第二步：建立 Google Sheet

### Sheet 結構

**Sheet 名稱：** `News_Queue`

| 欄位 | 說明 | 範例 |
|------|------|------|
| A: url | 文章網址 | https://technews.tw/2025/11/02/article |
| B: title | 文章標題 | 聯發科推出新晶片 |
| C: author | 作者 | 王小明 |
| D: content | 完整內容 | 聯發科今日宣布... |
| E: published_date | 發布日期 | 2025-11-02 |
| F: summary | AI 摘要 | 本文討論聯發科... |
| G: keyword | 關鍵字（來自 Google Alert） | 聯發科 |
| H: source | 來源 | Google Alert |
| I: status | 狀態 | pending/completed/failed |
| J: processed_time | 處理時間 | 2025-11-02 14:30:00 |

### 建立步驟

1. 開啟 [Google Sheets](https://sheets.google.com)
2. 建立新試算表，命名為 `News_Automation`
3. 將 Sheet1 重新命名為 `News_Queue`
4. 在第一行輸入欄位標題（A1 到 J1）
5. 設定條件式格式（status 欄位）：
   - `pending` → 黃色
   - `completed` → 綠色
   - `failed` → 紅色

---

## 🔧 第三步：建立 N8N Workflow

### 完整 Workflow 節點配置

#### 節點 1：Gmail Trigger（監聽郵件）

**節點類型：** `Gmail Trigger`

**設定：**
```
Event: Message Received
Simple: Off
Filters:
  - From: googlealerts-noreply@google.com
  - Subject Contains: Google 快訊
  - Is Unread: true
```

**說明：** 每當收到 Google Alert 郵件時自動觸發

---

#### 節點 2：Extract URLs from Email（提取網址）

**節點類型：** `Code`

**程式碼：**
```javascript
// 從 Gmail 郵件中提取所有新聞網址
const items = [];
const emailBody = $input.first().json.body;

// 取得郵件主旨（包含關鍵字）
const subject = $input.first().json.subject || '';
const keyword = subject.replace('Google 快訊 - ', '').trim();

// 使用正規表達式提取所有網址
// 排除 Google 的追蹤網址，只保留實際新聞網址
const urlPattern = /https?:\/\/(?!www\.google\.com)(?!google\.com)[^\s<>"]+/g;
const urls = emailBody.match(urlPattern) || [];

// 過濾和清理網址
const cleanUrls = urls
  .filter(url => {
    // 排除 Google 追蹤連結
    if (url.includes('google.com/url')) return false;
    if (url.includes('googleusercontent.com')) return false;
    // 只保留新聞網站
    return url.length > 20;
  })
  .map(url => {
    // 移除網址結尾的特殊字元
    return url.replace(/[.,;!?]+$/, '');
  });

// 去重
const uniqueUrls = [...new Set(cleanUrls)];

// 為每個網址建立一個項目
for (const url of uniqueUrls) {
  items.push({
    json: {
      url: url,
      keyword: keyword,
      source: 'Google Alert',
      email_date: $input.first().json.date,
      status: 'pending'
    }
  });
}

return items;
```

**輸出範例：**
```json
[
  {
    "url": "https://technews.tw/2025/11/02/mediatek-chip/",
    "keyword": "聯發科",
    "source": "Google Alert",
    "email_date": "2025-11-02T08:30:00Z",
    "status": "pending"
  }
]
```

---

#### 節點 3：Read Google Sheet（檢查重複）

**節點類型：** `Google Sheets`

**設定：**
```
Operation: Read
Document: 選擇你的 Sheet
Sheet Name: News_Queue
Range: A:A
Options:
  - RAW Data: false
```

**說明：** 讀取現有的所有網址，用於去重

---

#### 節點 4：Filter Duplicates（過濾重複網址）

**節點類型：** `Code`

**程式碼：**
```javascript
// 取得已存在的網址列表
const existingUrls = $node["Read Google Sheet"].json.map(row => row.url);

// 過濾掉已存在的網址
const newItems = [];
for (const item of $input.all()) {
  const url = item.json.url;
  if (!existingUrls.includes(url)) {
    newItems.push(item);
  }
}

return newItems;
```

---

#### 節點 5：Append to Google Sheet（寫入新網址）

**節點類型：** `Google Sheets`

**設定：**
```
Operation: Append
Document: 選擇你的 Sheet
Sheet Name: News_Queue
Columns:
  - url: {{ $json.url }}
  - title: (留空)
  - author: (留空)
  - content: (留空)
  - published_date: (留空)
  - summary: (留空)
  - keyword: {{ $json.keyword }}
  - source: {{ $json.source }}
  - status: pending
  - processed_time: (留空)
```

**說明：** 將新網址寫入 Sheet，狀態設為 pending

---

#### 節點 6：Wait（等待寫入完成）

**節點類型：** `Wait`

**設定：**
```
Resume: After Time Interval
Amount: 2
Unit: Seconds
```

**說明：** 等待 Google Sheet 寫入完成

---

#### 節點 7：Parse Article（呼叫 Parser API）

**節點類型：** `HTTP Request`

**設定：**
```
Method: POST
URL: https://web-production-32568.up.railway.app/api/parse
Authentication: None
Send Headers: true
Headers:
  - Name: Content-Type
  - Value: application/json
Send Body: true
Body Content Type: JSON
Body:
{
  "url": "={{ $json.url }}"
}
Options:
  - Timeout: 30000
  - Response Format: JSON
  - Continue On Fail: true
```

**說明：** 呼叫你的 Parser API 解析文章內容

---

#### 節點 8：Check Parse Success（檢查解析是否成功）

**節點類型：** `IF`

**設定：**
```
Conditions:
  - Condition 1:
      Value 1: {{ $json.error }}
      Operation: Is Empty
```

**說明：** 判斷 API 是否成功回傳資料

---

#### 節點 9：Generate AI Summary（生成摘要）

**節點類型：** `OpenAI`

**設定：**
```
Resource: Text
Operation: Create a Completion
Model: gpt-4-turbo-preview
Prompt:
請根據以下文章內容，生成一段 150 字以內的繁體中文摘要：

**標題：** {{ $json.title }}
**日期：** {{ $json.date_published }}
**內容：** {{ $json.content.substring(0, 2000) }}

摘要要求：
1. 提取核心重點（Who, What, When, Where, Why, How）
2. 保持客觀中立，不加入個人觀點
3. 使用繁體中文
4. 不超過 150 字
5. 以單一段落呈現

Options:
  - Max Tokens: 300
  - Temperature: 0.5
```

**說明：** 使用 OpenAI 生成摘要（也可以用 Claude）

---

#### 節點 10：Prepare Update Data（整理更新資料）

**節點類型：** `Set`

**設定：**
```
Keep Only Set: false
Values:
  - Name: url
    Value: {{ $node["Parse Article"].json.url }}
  - Name: title
    Value: {{ $node["Parse Article"].json.title }}
  - Name: author
    Value: {{ $node["Parse Article"].json.author || '未提供' }}
  - Name: content
    Value: {{ $node["Parse Article"].json.content }}
  - Name: published_date
    Value: {{ $node["Parse Article"].json.date_published }}
  - Name: summary
    Value: {{ $node["Generate AI Summary"].json.choices[0].message.content }}
  - Name: status
    Value: completed
  - Name: processed_time
    Value: {{ $now.format('YYYY-MM-DD HH:mm:ss') }}
```

---

#### 節點 11：Find Row Number（找到要更新的行號）

**節點類型：** `Code`

**程式碼：**
```javascript
// 讀取整個 Sheet，找到對應 URL 的行號
const sheetData = $node["Read Google Sheet All"].json;
const targetUrl = $json.url;

let rowNumber = -1;
for (let i = 0; i < sheetData.length; i++) {
  if (sheetData[i].url === targetUrl) {
    rowNumber = i + 2; // +2 因為：+1 是標題行，+1 是轉換為 1-based index
    break;
  }
}

return [{
  json: {
    ...$json,
    row_number: rowNumber
  }
}];
```

---

#### 節點 12：Update Google Sheet Success（更新成功）

**節點類型：** `Google Sheets`

**設定：**
```
Operation: Update
Document: 選擇你的 Sheet
Sheet Name: News_Queue
Range: =B{{ $json.row_number }}:J{{ $json.row_number }}
Data Mode: Define Below
Values:
  - Row:
      - {{ $json.title }}
      - {{ $json.author }}
      - {{ $json.content.substring(0, 1000) }}...
      - {{ $json.published_date }}
      - {{ $json.summary }}
      - {{ $json.keyword }}
      - {{ $json.source }}
      - completed
      - {{ $json.processed_time }}
```

---

#### 節點 13：Update Google Sheet Failed（更新失敗）

**節點類型：** `Google Sheets`

**設定：**
```
Operation: Update
Document: 選擇你的 Sheet
Sheet Name: News_Queue
Range: =I{{ $json.row_number }}:J{{ $json.row_number }}
Data Mode: Define Below
Values:
  - Row:
      - failed
      - {{ $now.format('YYYY-MM-DD HH:mm:ss') }}
```

---

## 📦 匯入 Workflow JSON

我已經為你準備好完整的 workflow JSON 檔案，你可以直接匯入 N8N：

### 匯入步驟：

1. 登入你的 N8N（雲端版或自架版）
2. 點擊右上角「...」→「Import from File」
3. 選擇 `n8n-google-alert-workflow.json`
4. 完成！

### 需要設定的項目：

匯入後，你需要設定以下 Credentials：

1. **Gmail Account** - 用於讀取郵件
2. **Google Sheets** - 用於讀寫 Sheet
3. **OpenAI API** - 用於生成摘要

---

## 🎯 第四步：測試 Workflow

### 測試步驟：

#### 1. 手動觸發測試

1. 在 N8N 中點擊「Execute Workflow」
2. 或發送一封測試郵件到你的信箱

#### 2. 寄送測試郵件

**主旨：** `Google 快訊 - 測試關鍵字`  
**寄件者：** `googlealerts-noreply@google.com`（如果可以模擬）  
**內容：**
```
測試新聞標題
科技新報 - 1 小時前
https://technews.tw/2025/11/02/test-article/

另一則測試新聞
經濟日報 - 2 小時前
https://www.bnext.com.tw/article/12345
```

#### 3. 檢查結果

1. 查看 N8N 執行歷史（Executions）
2. 檢查每個節點的輸出
3. 打開 Google Sheet 確認資料是否正確寫入

---

## ⚙️ 進階設定

### 1. 設定定期處理（補充方案）

如果你想要定期檢查 pending 項目並重新處理：

建立第二個 Workflow：

```
[Schedule Trigger] 每 1 小時
    ↓
[Read Google Sheet] 讀取 status = "pending" 的項目
    ↓
[Parse Article] 呼叫 Parser API
    ↓
[Generate Summary] AI 生成摘要
    ↓
[Update Sheet] 更新狀態為 completed
```

### 2. 錯誤通知

在 workflow 最後加入：

**節點類型：** `Send Email` 或 `Slack`

**設定：**
```
Trigger: Only on Error
Message: 
⚠️ N8N Workflow 失敗

URL: {{ $json.url }}
Error: {{ $json.error }}
Time: {{ $now.format('YYYY-MM-DD HH:mm:ss') }}
```

### 3. 批次處理優化

如果 Google Alert 一次寄送很多連結：

**加入 Split In Batches 節點：**
```
Batch Size: 5
Options: Reset
```

這樣可以每次處理 5 個網址，避免 API 過載。

### 4. 去除 Google 追蹤連結

Google Alert 郵件中的連結可能包含追蹤參數，例如：
```
https://www.google.com/url?q=https://technews.tw/article&...
```

在「Extract URLs」節點中已經處理，但如果還有問題，可以加入額外的清理邏輯：

```javascript
function cleanGoogleUrl(url) {
  // 如果是 Google 追蹤連結，提取實際網址
  if (url.includes('google.com/url')) {
    const match = url.match(/[?&]q=([^&]+)/);
    if (match) {
      return decodeURIComponent(match[1]);
    }
  }
  return url;
}
```

---

## 📊 預期效果

### 每天的自動化流程：

**早上 08:00** - Google Alert 寄送第一批郵件
```
✉️ Google 快訊：聯發科 (3 則新聞)
```

**08:01** - N8N 自動處理
```
✅ 提取 3 個網址
✅ 檢查重複（1 個重複，跳過）
✅ 2 個新網址寫入 Google Sheet
✅ 呼叫 Parser API 解析
✅ AI 生成摘要
✅ 更新 Google Sheet
```

**08:03** - 完成！
```
📊 Google Sheet 自動更新
   - 2 筆新資料
   - status = completed
   - 包含標題、內容、摘要
```

**你只需要：** 打開 Google Sheet 查看結果！

---

## 🔍 故障排除

### 問題 1：沒有觸發 Workflow

**可能原因：**
- Gmail Trigger 沒有正確設定
- 郵件被歸類到垃圾郵件
- Filter 條件太嚴格

**解決方式：**
1. 檢查 Gmail Trigger 的 Filter 設定
2. 確認 Google Alert 郵件有進入收件匣
3. 手動執行 Workflow 測試

### 問題 2：無法提取網址

**可能原因：**
- Google Alert 郵件格式改變
- 正規表達式沒有匹配到連結

**解決方式：**
1. 查看 Gmail Trigger 的輸出
2. 檢查 `emailBody` 的內容
3. 調整正規表達式

### 問題 3：Parser API 失敗

**可能原因：**
- API 服務下線
- 網址無效或無法訪問
- 網站需要登入

**解決方式：**
1. 檢查 API 狀態：https://web-production-32568.up.railway.app/health
2. 手動測試網址是否可訪問
3. 查看錯誤訊息

### 問題 4：AI 摘要生成失敗

**可能原因：**
- OpenAI API 額度不足
- API Key 過期
- 內容太長

**解決方式：**
1. 檢查 OpenAI 帳戶餘額
2. 更新 API Key
3. 限制傳給 AI 的內容長度（已在 prompt 中設定）

### 問題 5：Google Sheet 更新失敗

**可能原因：**
- 找不到對應的行號
- 權限不足
- Sheet 名稱錯誤

**解決方式：**
1. 確認 Sheet 名稱為 `News_Queue`
2. 檢查 Google Sheets OAuth 權限
3. 確認「Find Row Number」節點正確執行

---

## 💰 成本估算

### N8N
- **N8N Cloud**：$20/月（Starter 方案）
- **自架**：$0（使用 Railway/Render 免費方案）

### OpenAI API
- **模型**：GPT-4 Turbo
- **每次摘要成本**：約 $0.01
- **每天 50 篇文章**：$0.50/天 = $15/月

### 總成本
- **使用 N8N Cloud + OpenAI**：約 $35/月
- **自架 N8N + OpenAI**：約 $15/月

**建議：** 先用 OpenAI 的 GPT-3.5-turbo（更便宜）測試

---

## 🎉 完成！

你現在擁有一個：
- ✅ 完全自動化的新聞收集系統
- ✅ 從 Google Alert 自動提取新聞
- ✅ 自動解析文章內容
- ✅ AI 自動生成摘要
- ✅ 全部儲存到 Google Sheet
- ✅ 24/7 無需人工介入

**下一步：**
1. 建立多個 Google Alert（不同關鍵字）
2. 所有郵件都會自動處理
3. 每天打開 Google Sheet 查看結果即可！

---

## 📎 相關資源

- [N8N 官方文檔](https://docs.n8n.io/)
- [Google Alerts 設定](https://www.google.com/alerts)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [Parser API 文檔](./HOW_TO_USE_PARSER_API.md)

**有任何問題歡迎隨時詢問！** 🙏



