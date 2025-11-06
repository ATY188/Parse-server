# n8n 整合請求 Prompt

## 📋 我的需求

我需要建立一個 **全自動的新聞文章解析和摘要系統**，流程如下：

1. 我在 Google Sheet 中貼上待爬取的新聞網址
2. n8n 定期自動檢查 Google Sheet
3. 將待處理的網址發送到我的 Parser API 進行內容解析
4. 將解析後的內容發送到 AI（OpenAI/Claude）生成摘要
5. 將所有結果（標題、作者、內容、摘要等）寫回 Google Sheet
6. 整個過程完全自動化，24/7 運作

---

## 🔧 我現有的資源

### 1. Parser API（已部署在 Railway）

**API 端點：**
```
Base URL: https://web-production-32568.up.railway.app
API 文件：https://web-production-32568.up.railway.app/docs
```

**可用的 API 端點：**

#### POST /api/parse
解析單一網址的文章內容

**請求格式：**
```json
{
  "url": "https://www.bbc.com/news/article-123"
}
```

**回應格式：**
```json
{
  "status": "success",
  "data": {
    "url": "https://www.bbc.com/news/article-123",
    "title": "文章標題",
    "author": "作者名稱",
    "content": "完整文章內容...",
    "excerpt": "文章摘要",
    "date_published": "2025-11-02T10:30:00Z",
    "lead_image_url": "https://example.com/image.jpg",
    "word_count": 1234
  }
}
```

**錯誤回應：**
```json
{
  "status": "error",
  "message": "Failed to parse URL",
  "error": "詳細錯誤訊息"
}
```

---

### 2. Google Sheet 結構

**Sheet 名稱：** `News_Queue`

**欄位結構：**

| 欄位 | 說明 | 由誰填入 | 範例 |
|------|------|----------|------|
| A: url | 待爬取的網址 | 我手動填入 | https://www.bbc.com/news/article-123 |
| B: title | 文章標題 | API 回傳 | "Breaking News: Tech Update" |
| C: author | 作者 | API 回傳 | "John Smith" |
| D: content | 文章內容 | API 回傳 | "完整文章內容..." |
| E: published_date | 發布日期 | API 回傳 | "2025-11-02" |
| F: summary | AI 生成的摘要 | AI 生成 | "本文討論了..." |
| G: status | 處理狀態 | 系統自動更新 | pending/processing/completed/failed |
| H: processed_time | 處理時間 | 系統自動填入 | "2025-11-02 14:30:00" |

---

### 3. n8n 環境

**使用版本：** n8n Cloud（雲端託管版本）

**需要整合的服務：**
- Google Sheets（已有 OAuth 認證）
- HTTP Request（呼叫 Parser API）
- OpenAI 或 Claude（生成摘要）

---

## 🎯 期望的 Workflow 邏輯

```
[Schedule Trigger] 每 30 分鐘執行一次
    ↓
[Google Sheets: Read] 讀取 News_Queue Sheet（A2:H）
    ↓
[Filter] 篩選 status = "pending" 的項目
    ↓
[Google Sheets: Update] 將狀態更新為 "processing"（防止重複處理）
    ↓
[HTTP Request] 呼叫 Parser API
    POST https://web-production-32568.up.railway.app/api/parse
    Body: {"url": "{{ $json.url }}"}
    ↓
[IF] 檢查 API 是否成功
    ↓
    成功 → [OpenAI/Claude] 生成摘要
           Prompt: "請根據以下文章內容，生成 150 字以內的中文摘要..."
           ↓
           [Set] 整理所有欄位資料
           ↓
           [Google Sheets: Update] 寫回所有欄位（B-H）
           狀態更新為 "completed"
    
    失敗 → [Google Sheets: Update] 更新狀態為 "failed"
           記錄失敗時間
```

---

## 🔍 我需要的具體幫助

請詳細說明在 **n8n 雲端版**中如何：

### 1. Google Sheets 節點設定
- 如何設定讀取 Google Sheet（包含正確的 Range 設定）
- 如何設定更新特定儲存格（動態 row number）
- 如何處理多行資料（批次處理）
- 如何在回寫時保留格式

### 2. HTTP Request 節點設定
- 如何正確配置 POST 請求到我的 Parser API
- Headers 應該怎麼設定
- Body 格式應該如何填寫（使用 Google Sheet 的 url 欄位）
- 如何處理 API 超時（設定 timeout）
- 如何啟用 "Continue On Fail" 以處理錯誤

### 3. AI 節點設定（OpenAI 或 Claude）
- 如何配置 Credential
- Prompt 應該如何撰寫（使用 Parser API 回傳的資料）
- 如何限制摘要長度
- 如何確保使用繁體中文輸出

### 4. 資料轉換和傳遞
- 如何在不同節點之間傳遞資料（使用表達式）
- 如何取得 Google Sheet 的 row number（用於更新特定行）
- 如何使用 Set 節點整理資料
- 如何處理 API 回傳的 nested JSON

### 5. 錯誤處理
- 如何實作 IF 節點判斷 API 成功或失敗
- 如何設定不同的錯誤處理分支
- 如何記錄錯誤訊息到 Google Sheet

### 6. Schedule Trigger 設定
- 如何設定每 30 分鐘執行一次
- 或如何設定在特定時間執行（如每天 9:00, 12:00, 15:00, 18:00）

### 7. 測試和除錯
- 如何手動測試單一節點
- 如何查看每個節點的輸出資料
- 如何除錯失敗的執行

---

## ⚙️ 技術細節

### Parser API 技術棧
- 框架：Python FastAPI
- 解析引擎：trafilatura
- 部署平台：Railway（Docker）
- 運行狀態：24/7 線上

### API 限制和特性
- 無需認證（目前）
- 回應時間：3-10 秒（視網頁複雜度）
- 支援大部分新聞網站
- 自動處理 JavaScript 渲染的頁面

### Google Sheet 要求
- 需要保持第一行為標題行
- 資料從第 2 行開始
- status 欄位只有四種狀態：pending, processing, completed, failed
- 需要自動記錄處理時間

### AI 摘要要求
- 長度：不超過 150 字
- 語言：繁體中文
- 風格：客觀、精煉、重點明確
- 格式：單一段落，無項目符號

---

## 📊 預期行為

### 正常流程
1. 我在 Google Sheet A 欄貼上 5 個網址
2. 我在 G 欄都填入 "pending"
3. n8n 在下一個執行週期（最多 30 分鐘後）自動處理
4. 狀態先變成 "processing"
5. API 解析完成後，B-E 欄填入文章資料
6. AI 生成摘要後，F 欄填入摘要
7. 狀態變成 "completed"，H 欄記錄完成時間
8. 我可以隨時打開 Google Sheet 查看結果

### 錯誤處理
- 如果 API 解析失敗（如網址無效），狀態應該變成 "failed"
- 如果 AI 生成失敗，應該重試或記錄錯誤
- 失敗的項目我可以手動改回 "pending" 重新處理

---

## ❓ 我的具體問題

1. **在 n8n 中如何配置每個節點的詳細參數？**（請提供截圖或逐步說明）

2. **如何在 Google Sheets 節點中動態指定要更新的 row？**
   - 例如：如何更新第 5 行的 G 欄和 H 欄？

3. **如何在 HTTP Request 節點中正確使用 Google Sheet 的資料？**
   - 表達式應該怎麼寫？

4. **如何在 OpenAI 節點的 Prompt 中引用 Parser API 的回傳資料？**
   - 例如：如何取得 `$node["HTTP Request"].json.data.content`？

5. **如何處理批次資料？**
   - 如果有 10 個 pending 項目，是一次處理一個，還是並行處理？

6. **如何確保不會重複處理同一個 URL？**
   - 是否需要額外的去重邏輯？

7. **如何在 Workflow 失敗時收到通知？**
   - 可以發送 Email 或 Slack 訊息嗎？

---

## 🎯 最終目標

建立一個：
- ✅ 完全自動化的系統
- ✅ 不需要我的電腦保持開機
- ✅ 每天可處理 50-100 篇文章
- ✅ 錯誤自動處理或通知
- ✅ 可以在手機上管理（透過 Google Sheets App）
- ✅ 成本低廉（< $50/月）

---

## 📎 補充資訊

### 我可以提供的測試資料

**測試 URL 列表：**
```
https://www.bbc.com/news
https://www.cnn.com/world
https://www.nytimes.com/
https://techcrunch.com/
```

### 我的技術背景
- 熟悉：Google Sheets、基本的 API 概念
- 學習中：n8n workflow、資料自動化
- 不熟悉：複雜的程式邏輯、正規表達式

### 偏好的說明方式
- 請用截圖或逐步說明
- 提供可以直接複製的設定值
- 說明為什麼要這樣設定（幫助我理解原理）

---

**請根據以上資訊，提供 n8n 的詳細設定教學，謝謝！** 🙏


