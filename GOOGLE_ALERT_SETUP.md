# 🚀 Google Alert Workflow 設定指南

## 📋 目錄
1. [準備工作](#準備工作)
2. [Google Sheets 設定](#google-sheets-設定)
3. [n8n Workflow 匯入](#n8n-workflow-匯入)
4. [Gmail 連線設定](#gmail-連線設定)
5. [測試執行](#測試執行)
6. [常見問題](#常見問題)

---

## 1️⃣ 準備工作

### ✅ 檢查清單

- [ ] 已設定 Google Alert（關鍵字：TSMC, 台積電等）
- [ ] Google Alert 設定為「即時」或「每天一次」
- [ ] 傳送方式設為「電子郵件」（不是 RSS）
- [ ] 有 n8n 帳號（雲端版或自架版）
- [ ] 有 Google 帳號（用於 Gmail 和 Sheets）

---

## 2️⃣ Google Sheets 設定

### 步驟 1: 建立工作表

1. **開啟你的 Google Sheet**
   ```
   https://docs.google.com/spreadsheets/d/17vbNRbZGXvvsAVmBK7JuvB0kTZtwg3jFOIW9Opss2lk/edit
   ```

2. **確認有 `Google_Alerts (in)` 工作表**
   - 如果沒有，請建立一個新的工作表並命名為 `Google_Alerts (in)`

3. **設定標題列（第 1 行）**
   
   在第一行輸入以下標題：
   
   | A | B | C | D | E |
   |---|---|---|---|---|
   | url | keyword | title | source_name | publicdate |

### 欄位說明

| 欄位 | 說明 | 範例 |
|------|------|------|
| **url** | 文章網址 | https://www.axios.com/... |
| **keyword** | Google Alert 關鍵字 | TSMC |
| **title** | 文章標題（初始為空） | Can TSMC fill thousands of jobs... |
| **source_name** | 來源名稱 | Google Alert |
| **publicdate** | 發布日期 | 2025-11-02T14:30:00Z |

---

## 3️⃣ n8n Workflow 匯入

### 步驟 1: 匯入 Workflow

1. **登入 n8n**

2. **點擊右上角的選單（三個點）**

3. **選擇 "Import from File"**

4. **選擇檔案：**
   ```
   google-alert-workflow.json
   ```

5. **點擊 "Import"**

### 步驟 2: 檢查節點

匯入後，你會看到以下節點：

```
1. Gmail Trigger
   ↓
2. Extract URLs from Email
   ↓
3. Read Google Alerts Output
   ↓
4. Filter Duplicates
   ↓
5. Append to Google Alerts
```

---

## 4️⃣ Gmail 連線設定

### 步驟 1: 設定 Gmail Trigger 節點

1. **點擊 "Gmail Trigger" 節點**

2. **點擊 "Credential to connect with"**

3. **選擇 "Create New"**

4. **選擇你的 Google 帳號登入**

5. **授權 n8n 存取你的 Gmail**

### 步驟 2: 檢查篩選條件

**確認以下設定：**
- **From:** `googlealerts-noreply@google.com`
- **Subject:** `Google 快訊`
- **Read Status:** `unread`（只讀未讀郵件）

**如果你的 Google Alert 主旨不同：**
- 如果是英文版：改成 `Google Alert`
- 如果有自訂：改成你實際收到的主旨

### 步驟 3: 設定 Google Sheets 節點

**有兩個 Google Sheets 節點需要設定：**

#### 3.1 Read Google Alerts Output 節點

1. **點擊該節點**
2. **Credential:** 選擇或建立 Google Sheets 連線
3. **確認設定：**
   - Document ID: `17vbNRbZGXvvsAVmBK7JuvB0kTZtwg3jFOIW9Opss2lk`
   - Sheet: `Google_Alerts (in)`
   - Range: `A:A`（讀取 A 欄）

#### 3.2 Append to Google Alerts 節點

1. **點擊該節點**
2. **Credential:** 同上
3. **確認設定：**
   - Document ID: `17vbNRbZGXvvsAVmBK7JuvB0kTZtwg3jFOIW9Opss2lk`
   - Sheet: `Google_Alerts (in)`
   - Operation: `Append`

---

## 5️⃣ 測試執行

### 方法 1: 使用測試郵件（推薦）

1. **先暫停 Gmail Trigger**
   - 點擊 Gmail Trigger 節點
   - 點擊右上角的「啟用/停用」開關（設為停用）

2. **確保有一封 Google Alert 郵件在收件匣中**
   - 必須是「未讀」狀態

3. **手動執行 Workflow**
   - 點擊右上角的「Execute Workflow」

4. **檢查結果**
   - 查看每個節點的 OUTPUT
   - 檢查 Google Sheets 是否新增了資料

### 方法 2: 啟用自動執行

1. **確認測試成功後**

2. **啟用 Gmail Trigger**
   - 點擊 Gmail Trigger 節點
   - 開啟「啟用/停用」開關

3. **啟用整個 Workflow**
   - 點擊右上角的「Active」開關

4. **等待 Google Alert 郵件到來**
   - Workflow 會自動執行

---

## 6️⃣ 檢查執行結果

### 在 n8n 中檢查

1. **點擊左側的 "Executions"**
2. **查看最近的執行記錄**
3. **點擊任一執行記錄查看詳細資訊**

### 在 Google Sheets 中檢查

1. **開啟 Google_Alerts (in) 工作表**
2. **確認有新增的資料列**
3. **檢查欄位是否正確填入**

---

## 🎯 預期結果

### 單次執行的資料量

**典型的 Google Alert 郵件：**
- 📧 每封郵件包含：3-10 篇新聞
- 🔍 提取真實 URL 後：2-8 個有效連結
- ✅ 去重後寫入表格：1-8 筆新資料

### 每日執行情況

**假設每天收到 4 封 Google Alert：**
- 每天新增：10-30 筆資料
- 每週累積：70-210 筆資料

---

## ❓ 常見問題

### Q1: Gmail Trigger 沒有觸發？

**可能原因：**
1. ❌ 沒有未讀的 Google Alert 郵件
2. ❌ 主旨篩選條件不正確
3. ❌ Gmail 權限未授權

**解決方法：**
1. 檢查是否有未讀郵件
2. 調整主旨篩選條件
3. 重新授權 Gmail 連線

### Q2: 提取不到 URL？

**可能原因：**
1. ❌ 郵件格式改變
2. ❌ 郵件中只有 Google News 連結（會被過濾掉）

**解決方法：**
1. 檢查 "Extract URLs from Email" 節點的 Console Log
2. 如果需要，調整 URL 過濾規則

### Q3: 表格沒有寫入資料？

**可能原因：**
1. ❌ 所有 URL 都是重複的
2. ❌ Google Sheets 權限不足
3. ❌ 工作表名稱不正確

**解決方法：**
1. 檢查 "Filter Duplicates" 節點的輸出
2. 重新授權 Google Sheets
3. 確認工作表名稱為 `Google_Alerts (in)`

### Q4: 如何調整執行頻率？

**預設：** 每小時檢查一次

**修改方法：**
1. 點擊 "Gmail Trigger" 節點
2. 修改 "Poll Times"
   - `Every Minute` - 每分鐘
   - `Every Hour` - 每小時（推薦）
   - `Every 6 Hours` - 每 6 小時
   - `Custom` - 自訂

---

## 🎉 成功標準

**當你看到以下情況，表示設定成功：**

✅ n8n Executions 中有成功的執行記錄  
✅ Google Sheets 的 Google_Alerts (in) 工作表有新資料  
✅ URL 欄位填入了完整的新聞網址  
✅ keyword 欄位填入了 Google Alert 的關鍵字  

---

## 📞 下一步

**完成 Google Alert 收集後，你可以：**

1. ✅ **建立 Google News 收集 Workflow**
2. ✅ **建立 RSS 收集 Workflow**
3. ✅ **建立 Master 彙整 Workflow**
4. ✅ **建立 AI 分析與摘要 Workflow**

---

## 💡 小技巧

### 提高 URL 提取準確度

如果發現提取的 URL 不準確，可以：
1. 打開一封 Google Alert 郵件
2. 查看郵件的原始碼（顯示原始郵件）
3. 觀察 URL 的實際格式
4. 調整 "Extract URLs from Email" 的正規表達式

### 監控執行狀態

建議設定：
1. **n8n 的錯誤通知**
   - Settings → Workflows → Error Workflow
2. **每日執行報告**
   - 可以用 n8n 發送每日統計郵件

---

**祝你設定順利！🚀**

