# 📰 Google Alert 自動化新聞解析系統

## 🎯 這是什麼？

這是一個**完全自動化**的新聞收集和分析系統，可以：

✅ 自動從 Google Alert 郵件提取新聞網址  
✅ 自動解析文章內容（標題、作者、內容、日期）  
✅ 使用 AI 自動生成摘要  
✅ 全部儲存到 Google Sheet  
✅ 24/7 運作，無需人工介入  

---

## 🚀 快速開始（30 分鐘）

### 📝 第一步：閱讀快速設定指南

**檔案：** [`QUICK_SETUP_GUIDE.md`](./QUICK_SETUP_GUIDE.md)

這份指南包含：
- ✅ 前置準備清單
- ✅ 逐步設定教學
- ✅ 測試方法
- ✅ 故障排除

**⏱️ 預估時間：30 分鐘**

---

### 🔧 第二步：匯入 N8N Workflow

**檔案：** [`n8n-google-alert-complete-workflow.json`](./n8n-google-alert-complete-workflow.json)

這是可以直接匯入 N8N 的完整 workflow JSON 檔案。

**匯入方式：**
1. 登入 N8N
2. 點擊右上角「...」→「Import from File」
3. 選擇這個 JSON 檔案
4. 完成！

---

### 📊 第三步：設定 Google Sheet

**檔案：** [`GOOGLE_SHEET_STRUCTURE.md`](./GOOGLE_SHEET_STRUCTURE.md)

這份文檔詳細說明：
- 📋 欄位結構（10 個欄位）
- 📝 每個欄位的用途
- 🎨 格式設定（條件式格式、資料驗證）
- 📊 實際範例

---

## 📚 完整文檔

### 1. 完整流程說明
**檔案：** [`GOOGLE_ALERT_N8N_WORKFLOW.md`](./GOOGLE_ALERT_N8N_WORKFLOW.md)

**內容：**
- 🔄 完整流程圖
- 🎯 每個步驟的詳細說明
- ⚙️ 所有 N8N 節點的配置
- 💡 進階設定和優化
- ⚠️ 故障排除

**適合：** 想深入了解系統運作原理的使用者

---

### 2. 視覺化流程指南
**檔案：** [`WORKFLOW_VISUAL_GUIDE.md`](./WORKFLOW_VISUAL_GUIDE.md)

**內容：**
- 📊 系統架構圖
- 🎨 資料流視覺化
- ⚡ 處理速度分析
- 💡 實際使用場景
- 🎓 關鍵節點詳解

**適合：** 視覺學習者，想要快速理解系統

---

### 3. Google Sheet 結構
**檔案：** [`GOOGLE_SHEET_STRUCTURE.md`](./GOOGLE_SHEET_STRUCTURE.md)

**內容：**
- 📋 完整欄位列表（10 欄）
- 📝 每個欄位的詳細說明
- 🔄 與原本結構的對照
- 📊 實際範例資料
- ⚠️ 常見錯誤和解決方案

**適合：** 需要設定或調整 Google Sheet 的使用者

---

### 4. Parser API 使用說明
**檔案：** [`HOW_TO_USE_PARSER_API.md`](./HOW_TO_USE_PARSER_API.md)

**內容：**
- 🌐 API 端點說明
- 📝 請求和回應格式
- 🔧 使用範例
- ⚠️ 錯誤處理

**適合：** 需要直接使用 Parser API 的開發者

---

## 🎬 系統運作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    完整自動化流程                            │
└─────────────────────────────────────────────────────────────┘

1️⃣  Google Alert 寄送郵件
    └─ 包含 3-10 個新聞連結

2️⃣  Gmail 收到郵件
    └─ 主旨：Google 快訊 - [關鍵字]

3️⃣  N8N 自動觸發（每分鐘檢查）
    └─ 偵測到新的 Google Alert 郵件

4️⃣  提取網址
    └─ 使用正規表達式提取所有新聞網址

5️⃣  檢查重複
    └─ 與 Google Sheet 現有資料比對

6️⃣  寫入 Google Sheet
    └─ 新網址寫入，status = pending

7️⃣  呼叫 Parser API
    └─ 解析文章內容（標題、作者、內容、日期）

8️⃣  AI 生成摘要
    └─ OpenAI 生成 150 字繁體中文摘要

9️⃣  更新 Google Sheet
    └─ 填入所有資料，status = completed

🔟 標記郵件為已讀
    └─ 避免重複處理

✅  完成！
    └─ 打開 Google Sheet 查看結果
```

---

## 📋 檔案清單

### 📄 主要文檔

| 檔案 | 用途 | 適合 |
|------|------|------|
| **QUICK_SETUP_GUIDE.md** | 快速設定指南（從零開始） | 🟢 新手必讀 |
| **GOOGLE_ALERT_N8N_WORKFLOW.md** | 完整流程說明 | 🟡 進階使用者 |
| **WORKFLOW_VISUAL_GUIDE.md** | 視覺化流程圖 | 🟢 視覺學習者 |
| **GOOGLE_SHEET_STRUCTURE.md** | Google Sheet 結構說明 | 🟢 所有人 |
| **HOW_TO_USE_PARSER_API.md** | Parser API 使用說明 | 🔴 開發者 |

### 📦 可匯入檔案

| 檔案 | 用途 |
|------|------|
| **n8n-google-alert-complete-workflow.json** | N8N Workflow（可直接匯入） |
| **n8n-google-sheet-workflow.json** | N8N Workflow（手動貼上網址版） |

### 🗂️ 其他資源

| 檔案 | 用途 |
|------|------|
| **AI_PROMPT_FOR_N8N.md** | AI Prompt 範例 |
| **n8n-integration.md** | N8N 整合指南 |

---

## 🎯 使用場景

### 場景 1：個人新聞追蹤

**需求：** 追蹤 3-5 家公司的新聞

**設定：**
- 建立 5 個 Google Alert（每家公司一個）
- 全部指向同一個 Gmail
- N8N 自動處理所有郵件

**結果：**
- 每天自動收集 20-50 篇新聞
- 全部整理在 Google Sheet
- 可以隨時查看摘要

---

### 場景 2：產業研究

**需求：** 追蹤整個半導體產業動態

**設定：**
- 建立 10+ 個 Google Alert（不同關鍵字）
  - 半導體、AI 晶片、5G、台積電、聯發科...
- 使用 keyword 欄位分類

**結果：**
- 每天收集 100+ 篇產業新聞
- 自動分類和摘要
- 可以匯出分析趨勢

---

### 場景 3：競品監控

**需求：** 監控競爭對手的新聞和動態

**設定：**
- 建立特定的 Google Alert
  - "競品 A" + "新產品"
  - "競品 B" + "財報"
- 設定為即時快訊

**結果：**
- 即時收到競品動態
- 自動生成摘要
- 快速了解市場變化

---

## 💰 成本估算

### 基本方案（每天 50 篇文章）

| 服務 | 費用 | 說明 |
|------|------|------|
| Google Alert | 免費 | 無限制 |
| Gmail | 免費 | 15 GB 儲存空間 |
| Google Sheets | 免費 | 可儲存 10 萬筆資料 |
| N8N Cloud | $20/月 | Starter 方案 |
| Parser API | 免費 | 已部署在 Railway |
| OpenAI API | $15/月 | GPT-3.5-turbo |
| **總計** | **$35/月** | |

### 進階方案（每天 200 篇文章）

| 服務 | 費用 | 說明 |
|------|------|------|
| N8N Cloud | $50/月 | Pro 方案 |
| OpenAI API | $60/月 | GPT-4 |
| **總計** | **$110/月** | |

### 省錢方案

| 服務 | 費用 | 說明 |
|------|------|------|
| N8N 自架 | 免費 | 使用 Railway/Render 免費方案 |
| OpenAI API | $15/月 | 使用 GPT-3.5-turbo |
| **總計** | **$15/月** | |

---

## ⚡ 系統效能

### 處理速度

| 項目 | 時間 |
|------|------|
| 單一文章 | 15-20 秒 |
| 10 篇文章（順序） | 2-3 分鐘 |
| 10 篇文章（平行） | 20-30 秒 |

### 容量限制

| 項目 | 限制 |
|------|------|
| Google Sheet | 1000 萬個儲存格 |
| 可儲存文章數 | 約 10 萬篇 |
| N8N 執行次數 | 依方案而定 |
| OpenAI API | 依帳戶額度 |

---

## 🔧 系統需求

### 必要條件

- ✅ Gmail 帳號
- ✅ Google Sheets
- ✅ N8N 帳號（雲端或自架）
- ✅ OpenAI API Key
- ✅ Parser API（已提供）

### 可選條件

- ⭕ Slack（通知）
- ⭕ Notion（儲存）
- ⭕ Airtable（進階資料庫）

---

## 📞 支援和幫助

### 故障排除

1. **檢查系統狀態**
   - Parser API: https://web-production-32568.up.railway.app/health
   - N8N Executions: 查看執行歷史
   - Google Sheet: 確認資料寫入

2. **常見問題**
   - 參考 `QUICK_SETUP_GUIDE.md` 的故障排除章節
   - 參考 `GOOGLE_ALERT_N8N_WORKFLOW.md` 的常見問題

3. **除錯技巧**
   - 在 N8N 中測試單一節點
   - 查看每個節點的輸出
   - 檢查 console.log 輸出

---

## 🎓 學習資源

### 官方文檔

- [N8N 官方文檔](https://docs.n8n.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [OpenAI API 文檔](https://platform.openai.com/docs)

### 相關教學

- [N8N 入門教學](https://docs.n8n.io/getting-started/)
- [Google Apps Script](https://developers.google.com/apps-script)
- [正規表達式教學](https://regexr.com/)

---

## 🚀 進階功能

### 1. 自動分類

使用 AI 自動分類文章：
- 產品發布
- 財報新聞
- 人事異動
- 合作案

### 2. 情緒分析

使用 AI 分析新聞情緒：
- 正面
- 中性
- 負面

### 3. 關鍵字提取

自動提取文章中的關鍵字：
- 公司名稱
- 產品名稱
- 技術術語

### 4. 通知系統

整合通知服務：
- Slack（團隊通知）
- Telegram（個人通知）
- Email（週報）

---

## 📈 未來擴展

### 計劃中的功能

- [ ] 支援更多新聞來源（RSS、Twitter）
- [ ] 自動去重（標題相似度比對）
- [ ] 文章相關性評分
- [ ] 自動標籤和分類
- [ ] 趨勢分析和視覺化
- [ ] 自動產出週報/月報

---

## 🎉 立即開始

### 推薦閱讀順序

1. **新手：**
   1. [`QUICK_SETUP_GUIDE.md`](./QUICK_SETUP_GUIDE.md) - 快速設定
   2. [`WORKFLOW_VISUAL_GUIDE.md`](./WORKFLOW_VISUAL_GUIDE.md) - 視覺化理解
   3. [`GOOGLE_SHEET_STRUCTURE.md`](./GOOGLE_SHEET_STRUCTURE.md) - Sheet 設定

2. **進階使用者：**
   1. [`GOOGLE_ALERT_N8N_WORKFLOW.md`](./GOOGLE_ALERT_N8N_WORKFLOW.md) - 完整說明
   2. [`HOW_TO_USE_PARSER_API.md`](./HOW_TO_USE_PARSER_API.md) - API 文檔

---

## 💡 小提示

### 省時技巧

✅ 使用 Google Alert 的「即時」選項，第一時間收到新聞  
✅ 在 Google Sheet 中使用篩選功能，快速找到特定新聞  
✅ 定期檢查 `failed` 項目，確保沒有遺漏重要新聞  
✅ 使用條件式格式，一眼看出文章狀態  

### 最佳實踐

✅ 每週檢查一次系統狀態  
✅ 每月歸檔舊資料（避免 Sheet 太大）  
✅ 定期更新 OpenAI API Key（避免過期）  
✅ 備份 N8N Workflow（匯出 JSON）  

---

## 📄 授權

此系統使用的技術：
- N8N: Fair-code license
- Google Services: Google Terms of Service
- OpenAI: OpenAI Terms of Use
- Parser API: 自建服務

---

## 🙏 感謝使用

希望這個自動化系統能幫助你：
- 💰 節省時間（每天 30 分鐘 → 2 分鐘）
- 📊 不錯過重要新聞
- 🎯 專注於分析而非收集
- 🚀 提升工作效率

**如有任何問題，歡迎隨時詢問！** 🎉

---

**最後更新：** 2025-11-02  
**版本：** 1.0.0



