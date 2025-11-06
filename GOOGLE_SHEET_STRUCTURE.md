# Google Sheet 欄位結構建議

## 📊 優化後的欄位結構

### 完整欄位列表（11 欄）

| 欄位 | 說明 | 範例 | 由誰填入 | 必填 |
|------|------|------|----------|------|
| A: company | 公司名稱 | 聯發科、台積電 | 手動 | ✅ |
| B: category | 分類標籤 | 半導體、AI、5G | 手動 | ⭕ |
| C: article_url | **文章完整網址** | https://technews.tw/2025/10/31/article-123 | 手動 | ✅ |
| D: title | 文章標題 | 《半導體》聯發科推出新晶片 | API 回傳 | ✅ |
| E: author | 作者 | 王小明 | API 回傳 | ⭕ |
| F: content | 文章完整內容 | 聯發科今日宣布... | API 回傳 | ✅ |
| G: publicdate | 發布日期 | 2025-10-31 | API 回傳 | ✅ |
| H: summary | AI 生成摘要 | 本文討論聯發科... | AI 生成 | ✅ |
| I: source | 資料來源 | RSS, 手動, API | 手動 | ⭕ |
| J: status | 處理狀態 | pending, processing, completed, failed | 系統 | ✅ |
| K: proceed_time | 處理時間 | 2025-11-02 14:30:00 | 系統 | ✅ |

**圖例：**
- ✅ 必填
- ⭕ 選填
- **粗體** = 最關鍵的欄位

---

## 📋 欄位詳細說明

### A: company（公司名稱）
**用途：** 追蹤哪家公司的新聞  
**範例：** 聯發科、台積電、鴻海、輝達  
**填入方式：** 手動輸入  
**格式要求：** 純文字

---

### B: category（分類標籤）
**用途：** 文章分類，方便後續篩選  
**範例：** 半導體、AI、5G、財報、人事異動  
**填入方式：** 手動輸入  
**格式要求：** 純文字，可多個標籤用逗號分隔

**建議值：**
- 半導體
- AI / 人工智慧
- 5G / 通訊
- 財報
- 人事異動
- 產品發布
- 合作案
- 其他

---

### C: article_url（文章完整網址）⭐ 最重要！
**用途：** 提供給 Parser API 解析  
**範例：** 
```
✅ 正確：https://technews.tw/2025/10/31/tsmc-news/
✅ 正確：https://www.bnext.com.tw/article/12345
❌ 錯誤：https://news.google.com/rss
❌ 錯誤：https://news.google.com（首頁）
```

**填入方式：** 手動貼上文章網址  
**格式要求：** 
- 必須是完整的 https:// 開頭
- 必須是單一文章頁面，不是列表或首頁
- 必須是可公開訪問的網址

**如何取得正確網址：**
1. 開啟新聞網站
2. 點進單一文章
3. 複製瀏覽器網址列的完整網址
4. 貼到這個欄位

---

### D: title（文章標題）
**用途：** 文章標題，由 Parser API 自動提取  
**範例：** 《半導體》聯發科推出 5nm 新晶片  
**填入方式：** Parser API 自動填入  
**格式要求：** 保留原文標題

**留空：** 這個欄位在處理前可以是空白

---

### E: author（作者）
**用途：** 文章作者，由 Parser API 自動提取  
**範例：** 王小明、John Smith  
**填入方式：** Parser API 自動填入  
**格式要求：** 純文字

**注意：** 
- 不是所有文章都有作者
- 新聞網站通常沒有作者名稱
- 這個欄位可能是空白

---

### F: content（文章完整內容）
**用途：** 文章的完整文字內容  
**範例：** 
```
聯發科今日（31日）宣布推出最新 5nm 製程的旗艦晶片，
該晶片採用最新的 AI 架構，效能較前代提升 30%...
（以下 1000-2000 字的完整內容）
```

**填入方式：** Parser API 自動填入  
**格式要求：** 純文字，保留段落結構

**用途：**
- 提供給 AI 分析
- 生成摘要的原始資料
- 後續全文搜尋

**注意：**
- 內容可能很長（1000-3000 字）
- Google Sheet 單一儲存格最多 50,000 字元
- 如果內容太長，可以截斷後半部

---

### G: publicdate（發布日期）
**用途：** 文章的發布日期  
**範例：** 2025-10-31、2025-11-02 14:30  
**填入方式：** Parser API 自動提取  
**格式要求：** YYYY-MM-DD 或 YYYY-MM-DD HH:MM

**注意：**
- 部分網站可能沒有明確日期
- 如果提取失敗，可能是空白

---

### H: summary（AI 生成摘要）
**用途：** 由 AI 根據完整內容生成的摘要  
**範例：** 
```
聯發科推出 5nm 新晶片，效能提升 30%。該晶片將用於
高階智慧手機，預計 2026 年第一季量產。業界認為此舉
將加強聯發科在旗艦市場的競爭力。
```

**填入方式：** OpenAI/Claude 自動生成  
**格式要求：** 繁體中文，150 字以內

**AI Prompt 範例：**
```
請根據以下文章內容，生成 150 字以內的中文摘要：
1. 提取核心重點（5W1H）
2. 保持客觀中立
3. 使用繁體中文
4. 不超過 150 字
```

---

### I: source（資料來源）
**用途：** 記錄這筆資料從哪裡來  
**範例：** RSS、手動、Google News、API  
**填入方式：** 手動輸入  
**格式要求：** 純文字

**建議值：**
- RSS（從 RSS Feed 來）
- 手動（自己找的）
- Google News（從 Google 新聞）
- Twitter（從社群媒體）
- API（從其他 API）

---

### J: status（處理狀態）⭐ 系統核心欄位
**用途：** 標記這筆資料的處理狀態  
**允許的值：**
- `pending` - 待處理（剛加入，還沒開始）
- `processing` - 處理中（正在呼叫 API）
- `completed` - 已完成（成功處理完畢）
- `failed` - 失敗（處理失敗，需要重試）

**填入方式：**
- 手動輸入：`pending`
- 系統更新：其他狀態

**工作流程：**
```
1. 你手動貼上 article_url
2. 你手動填入 status = "pending"
3. n8n 看到 pending，開始處理
4. n8n 更新為 "processing"
5. 呼叫 Parser API
6. 呼叫 AI 生成摘要
7. 成功 → "completed" / 失敗 → "failed"
```

**如果失敗：**
- 手動把 `failed` 改回 `pending`
- n8n 會自動重新處理

---

### K: proceed_time（處理時間）
**用途：** 記錄何時處理完成  
**範例：** 2025-11-02 14:30:45  
**填入方式：** 系統自動填入  
**格式要求：** YYYY-MM-DD HH:MM:SS

**用途：**
- 追蹤處理歷史
- 計算處理速度
- 除錯時確認時間點

---

## 🔄 與你原本結構的對照

### 你原本的欄位 → 建議的欄位

| 原本 | 建議 | 原因 |
|------|------|------|
| company | company ✅ | 保持不變 |
| name | category | 改為更明確的分類 |
| title | title ✅ | 保持不變 |
| publicdate | publicdate ✅ | 保持不變 |
| url_rss | article_url ⭐ | 改為文章網址（關鍵！） |
| - | author ➕ | 新增作者欄位 |
| - | content ➕ | 新增完整內容欄位 |
| source | source ✅ | 保持不變 |
| summary | summary ✅ | 保持不變 |
| status | status ✅ | 保持不變 |
| proceed_time | proceed_time ✅ | 保持不變 |

---

## 📝 實際範例資料

### 範例 1：待處理的資料（你手動填）

| company | category | article_url | title | author | content | publicdate | summary | source | status | proceed_time |
|---------|----------|-------------|-------|--------|---------|------------|---------|--------|--------|--------------|
| 聯發科 | 半導體 | https://technews.tw/2025/10/31/mtk-5g | | | | | | RSS | pending | |

**說明：**
- 你只填前 3 欄 + source + status
- 其他欄位留空，等系統處理

---

### 範例 2：處理完成的資料（系統自動填）

| company | category | article_url | title | author | content | publicdate | summary | source | status | proceed_time |
|---------|----------|-------------|-------|--------|---------|------------|---------|--------|--------|--------------|
| 聯發科 | 半導體 | https://technews.tw/2025/10/31/mtk-5g | 聯發科推出 5G 新晶片 | 王小明 | 聯發科今日宣布... | 2025-10-31 | 本文討論聯發科新晶片... | RSS | completed | 2025-11-02 14:30:45 |

**說明：**
- API 填入：title, author, content, publicdate
- AI 填入：summary
- 系統填入：status, proceed_time

---

## 🎯 你該怎麼操作

### 每天的工作流程

#### 步驟 1：新增待處理項目（1 分鐘）
```
1. 開啟 Google Sheet
2. 找到你想追蹤的新聞文章
3. 填入以下欄位：
   - A (company): 聯發科
   - B (category): 半導體
   - C (article_url): https://technews.tw/2025/10/31/article-123
   - I (source): RSS
   - J (status): pending
4. 其他欄位留空
5. 關閉電腦，讓系統自動處理
```

#### 步驟 2：等待系統處理（自動，0 分鐘）
```
n8n 每 30 分鐘自動：
1. 讀取 Google Sheet
2. 找到 status = "pending" 的項目
3. 呼叫 Parser API 解析文章
4. 呼叫 AI 生成摘要
5. 寫回所有資料到 Google Sheet
6. 更新 status = "completed"
```

#### 步驟 3：查看結果（1 分鐘）
```
1. 開啟 Google Sheet
2. 查看 summary 欄位（AI 生成的摘要）
3. 如果 status = "failed"：
   - 檢查 article_url 是否正確
   - 把 status 改回 "pending"
   - 系統會重新處理
```

---

## ⚠️ 常見錯誤和解決方案

### 錯誤 1：url_rss 填錯
```
❌ 錯誤：https://news.google.com/rss/search?q=台積電
✅ 正確：https://technews.tw/2025/10/31/tsmc-hiring/

解決：article_url 必須是單一文章的完整網址
```

### 錯誤 2：忘記填 status
```
❌ 錯誤：status 留空
✅ 正確：status = "pending"

解決：n8n 靠 status = "pending" 判斷要處理哪些項目
```

### 錯誤 3：網址不可訪問
```
❌ 錯誤：https://paid-content.com/article（需要付費）
✅ 正確：https://free-news.com/article（公開可訪問）

解決：Parser API 無法解析需要登入或付費的內容
```

---

## 📊 建議的 Google Sheet 設定

### 1. 凍結首行
```
檢視 → 凍結 → 1 列
```
這樣標題行永遠可見

### 2. 設定欄位寬度
```
A (company): 100px
B (category): 100px
C (article_url): 300px
D (title): 250px
E (author): 100px
F (content): 400px
G (publicdate): 120px
H (summary): 300px
I (source): 80px
J (status): 100px
K (proceed_time): 150px
```

### 3. 設定資料驗證（status 欄位）
```
點擊 J 欄標題
資料 → 資料驗證
條件：清單中的項目
項目：pending,processing,completed,failed
```

### 4. 設定條件式格式（狀態顏色）
```
選取 J 欄（status）
格式 → 條件式格式

規則 1：如果文字等於 "completed" → 綠色背景
規則 2：如果文字等於 "failed" → 紅色背景
規則 3：如果文字等於 "pending" → 黃色背景
規則 4：如果文字等於 "processing" → 藍色背景
```

---

## 🎨 完成後的視覺效果

你的 Sheet 會像這樣：

```
| company | category | article_url          | status    |
|---------|----------|---------------------|-----------|
| 聯發科   | 半導體    | https://news...     | ✅ completed (綠色) |
| 台積電   | 人事     | https://tech...     | ✅ completed (綠色) |
| 鴻海     | 財報     | https://money...    | ⏳ pending (黃色)   |
| 輝達     | AI      | https://blog...     | ❌ failed (紅色)    |
```

一目了然！

---

## 🚀 立即行動

### 修改你的 Google Sheet

1. **開啟你的 Google Sheet**

2. **調整欄位標題（第 1 行）：**
```
A: company
B: category（改名）
C: article_url（改名，最重要！）
D: title
E: author（新增）
F: content（新增）
G: publicdate
H: summary
I: source
J: status
K: proceed_time
```

3. **更新你的現有資料：**
- 把 `url_rss` 欄的資料改成實際文章網址
- 把 `name` 欄改為分類（如「半導體」）

4. **設定資料驗證和格式**（參考上面的說明）

5. **輸入測試資料**（3-5 筆）

6. **準備串接 n8n**！

---

**這個結構會讓整個自動化系統運作得更順暢！** ✨


