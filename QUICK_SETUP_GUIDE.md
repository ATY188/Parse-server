# 🚀 Google Alert 自動化系統 - 快速設定指南

## ⏱️ 預估時間：30 分鐘

---

## 📋 前置準備清單

在開始之前，請確認你有以下帳號：

- ✅ Gmail 帳號（用於接收 Google Alert）
- ✅ Google Sheets（用於儲存新聞資料）
- ✅ N8N 帳號（[N8N Cloud](https://n8n.io/) 或自架）
- ✅ OpenAI API Key（[取得位置](https://platform.openai.com/api-keys)）
- ✅ Parser API 已部署（已有：https://web-production-32568.up.railway.app）

---

## 第一步：設定 Google Alert（5 分鐘）

### 1. 前往 Google Alerts

開啟 [https://www.google.com/alerts](https://www.google.com/alerts)

### 2. 建立第一個 Alert

在搜尋框輸入關鍵字：
```
聯發科
```

### 3. 點擊「顯示選項」並設定：

| 設定項目 | 選擇 |
|---------|------|
| 頻率 | **即時** 或 **每天一次** |
| 來源 | **新聞** |
| 語言 | **中文** |
| 地區 | **台灣** |
| 數量 | **只傳送最佳結果** |
| 傳送至 | **你的 Gmail 信箱** |

### 4. 點擊「建立快訊」

### 5. 重複步驟建立更多 Alert

建議的關鍵字：
- 台積電
- 鴻海
- 輝達
- 半導體
- AI 晶片

### 6. 測試

等待幾分鐘到幾小時，你應該會收到第一封 Google Alert 郵件。

---

## 第二步：建立 Google Sheet（5 分鐘）

### 1. 建立新的 Google Sheet

前往 [https://sheets.google.com](https://sheets.google.com)

點擊「空白」建立新試算表

### 2. 命名試算表

將試算表命名為：`News_Automation`

### 3. 重新命名 Sheet

將「Sheet1」重新命名為：`News_Queue`

### 4. 設定欄位標題

在第一行（Row 1）輸入以下標題：

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| url | title | author | content | published_date | summary | keyword | source | status | processed_time |

### 5. 設定欄位寬度

選取所有欄位，調整寬度：
- A (url): 300px
- B (title): 250px
- C (author): 100px
- D (content): 400px
- E (published_date): 120px
- F (summary): 300px
- G (keyword): 100px
- H (source): 80px
- I (status): 100px
- J (processed_time): 150px

### 6. 設定條件式格式

選取 I 欄（status 欄位）

點擊「格式」→「條件式格式」

新增以下規則：

**規則 1：**
- 格式規則：文字等於 `completed`
- 格式設定：綠色背景

**規則 2：**
- 格式規則：文字等於 `pending`
- 格式設定：黃色背景

**規則 3：**
- 格式規則：文字等於 `failed`
- 格式設定：紅色背景

### 7. 凍結首行

點擊「檢視」→「凍結」→「1 列」

### 8. 複製 Sheet ID

從網址列複製你的 Google Sheet ID：

```
https://docs.google.com/spreadsheets/d/【這段就是 Sheet ID】/edit
```

範例：
```
https://docs.google.com/spreadsheets/d/1abc123XYZ-def456/edit
                                      ^^^^^^^^^^^^^^^^
                                      這段就是 Sheet ID
```

**重要：請記下這個 ID，稍後會用到！**

---

## 第三步：設定 N8N Workflow（15 分鐘）

### 1. 登入 N8N

前往你的 N8N 平台：
- N8N Cloud: [https://app.n8n.cloud](https://app.n8n.cloud)
- 或你的自架版本

### 2. 匯入 Workflow

1. 點擊右上角「☰」選單
2. 選擇「Import from File」
3. 選擇檔案：`n8n-google-alert-complete-workflow.json`
4. 點擊「Import」

### 3. 設定 Gmail Credential

1. 點擊「Gmail Trigger」節點
2. 在「Credential to connect with」點擊「Create New」
3. 選擇「Gmail OAuth2」
4. 點擊「Sign in with Google」
5. 選擇你的 Gmail 帳號並授權
6. 完成後點擊「Save」

### 4. 設定 Google Sheets Credential

1. 點擊「Read Existing URLs」節點
2. 在「Credential to connect with」點擊「Create New」
3. 選擇「Google Sheets OAuth2」
4. 點擊「Sign in with Google」
5. 選擇你的 Google 帳號並授權
6. 完成後點擊「Save」

### 5. 設定 OpenAI Credential

1. 點擊「Generate AI Summary」節點
2. 在「Credential to connect with」點擊「Create New」
3. 選擇「OpenAI」
4. 輸入你的 OpenAI API Key
5. 點擊「Save」

**如何取得 OpenAI API Key：**
- 前往 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- 點擊「Create new secret key」
- 複製 API Key（只會顯示一次！）

### 6. 更新 Google Sheet ID

在以下節點中，將 `YOUR_GOOGLE_SHEET_ID` 替換為你的 Sheet ID：

1. **Read Existing URLs** 節點
2. **Append to Google Sheet** 節點
3. **Read Google Sheet All** 節點
4. **Update Google Sheet Success** 節點
5. **Read Google Sheet All Failed** 節點
6. **Update Google Sheet Failed** 節點

**替換方式：**
1. 點擊節點
2. 找到「Document」欄位
3. 點擊「From List」切換到「By ID」
4. 將 `YOUR_GOOGLE_SHEET_ID` 替換為你複製的 Sheet ID
5. 點擊「Save」

### 7. 測試 Parser API

在瀏覽器開啟：
```
https://web-production-32568.up.railway.app/health
```

應該看到：
```json
{"status": "ok"}
```

### 8. 啟用 Workflow

點擊右上角的「Inactive」開關，變成「Active」

---

## 第四步：測試系統（5 分鐘）

### 方法 1：等待真實郵件

1. 等待 Google Alert 寄送郵件
2. N8N 會自動觸發並處理
3. 打開 Google Sheet 查看結果

### 方法 2：手動測試（推薦）

1. **發送測試郵件到你的 Gmail**

**主旨：**
```
Google 快訊 - 測試關鍵字
```

**內容：**
```
測試新聞 1
科技新報 - 1 小時前
https://technews.tw/2025/11/02/mediatek-dimensity-9400/

測試新聞 2
數位時代 - 2 小時前
https://www.bnext.com.tw/article/80198/tsmc-2024
```

2. **在 N8N 中檢查執行結果**

- 點擊左側「Executions」
- 查看最新的執行記錄
- 確認每個節點都成功執行（綠色勾勾）

3. **在 Google Sheet 中查看結果**

應該會看到 2 筆新資料：
- url: 測試網址
- status: completed（綠色）
- summary: AI 生成的摘要

---

## ✅ 完成檢查清單

確認以下項目都成功：

- [ ] Google Alert 已建立並收到測試郵件
- [ ] Google Sheet 已建立並設定好格式
- [ ] N8N Workflow 已匯入
- [ ] Gmail Credential 已設定並授權
- [ ] Google Sheets Credential 已設定並授權
- [ ] OpenAI Credential 已設定
- [ ] 所有節點的 Google Sheet ID 已更新
- [ ] Workflow 已啟用（Active）
- [ ] 測試郵件已成功處理
- [ ] Google Sheet 中有測試資料且 status 為 completed

---

## 🎉 恭喜！系統已設定完成

### 現在系統會自動：

1. ✅ 每當收到 Google Alert 郵件
2. ✅ 自動提取所有新聞網址
3. ✅ 檢查是否重複（自動去重）
4. ✅ 將新網址寫入 Google Sheet
5. ✅ 呼叫 Parser API 解析文章
6. ✅ 使用 AI 生成摘要
7. ✅ 將所有資料更新回 Google Sheet
8. ✅ 標記郵件為已讀

### 你只需要：

- 📱 打開 Google Sheet 查看結果
- 🔍 搜尋、篩選、分析新聞資料
- 📊 匯出資料做進一步分析

---

## 📊 日常使用

### 查看新聞

1. 開啟你的 Google Sheet
2. 查看 `status` 欄位：
   - 🟢 `completed` - 處理成功，可以查看摘要
   - 🟡 `pending` - 等待處理
   - 🔴 `failed` - 處理失敗

### 重新處理失敗項目

1. 找到 `status = failed` 的行
2. 檢查 `url` 是否正確
3. 將 `status` 改為 `pending`
4. 系統會自動重新處理

### 查看執行歷史

1. 登入 N8N
2. 點擊左側「Executions」
3. 查看所有執行記錄和錯誤

---

## ⚠️ 常見問題

### Q1: 沒有收到 Google Alert 郵件？

**檢查：**
- Google Alert 是否已建立
- 傳送至的信箱是否正確
- 郵件是否被歸類到垃圾郵件

**解決：**
- 前往 Gmail 的垃圾郵件資料夾
- 找到 Google Alert 郵件
- 點擊「不是垃圾郵件」

### Q2: N8N Workflow 沒有觸發？

**檢查：**
- Workflow 是否已啟用（Active）
- Gmail Trigger 的 Filter 設定是否正確
- Gmail Credential 是否已授權

**解決：**
- 確認 Workflow 右上角顯示「Active」
- 重新測試 Gmail Credential
- 查看 Executions 的錯誤訊息

### Q3: Parser API 解析失敗？

**檢查：**
- API 服務是否正常：https://web-production-32568.up.railway.app/health
- 網址是否正確且可訪問
- 網站是否需要登入

**解決：**
- 確認 API 回傳 `{"status": "ok"}`
- 手動在瀏覽器開啟該網址測試
- 某些網站可能無法解析（付費牆、需登入）

### Q4: AI 摘要生成失敗？

**檢查：**
- OpenAI API Key 是否正確
- OpenAI 帳戶是否有餘額
- Prompt 是否正確

**解決：**
- 前往 OpenAI 查看帳戶餘額
- 更新 API Key
- 檢查 OpenAI 的使用限制

### Q5: Google Sheet 沒有更新？

**檢查：**
- Google Sheets Credential 是否已授權
- Sheet 名稱是否為 `News_Queue`
- 欄位順序是否正確

**解決：**
- 重新授權 Google Sheets
- 確認 Sheet 名稱拼寫正確
- 檢查欄位標題是否完全一致

---

## 📞 需要幫助？

### 檢查系統狀態

1. **Parser API 健康檢查**
   ```
   https://web-production-32568.up.railway.app/health
   ```

2. **N8N Executions**
   - 查看最近的執行記錄
   - 找到失敗的節點
   - 查看錯誤訊息

3. **Google Sheet**
   - 確認資料是否正確寫入
   - 查看 `status` 欄位

### 除錯技巧

1. **測試單一節點**
   - 在 N8N 中點擊節點
   - 點擊「Execute node」
   - 查看輸出結果

2. **查看節點輸出**
   - 執行完 Workflow 後
   - 點擊每個節點
   - 查看「Output」標籤

3. **啟用錯誤通知**
   - 在 Workflow 設定中
   - 啟用「Error Workflow」
   - 當有錯誤時會收到通知

---

## 🚀 進階功能

### 1. 增加更多 Google Alerts

建立不同主題的 Alert，所有郵件都會自動處理！

### 2. 定期重新處理

建立第二個 Workflow，每小時檢查 `pending` 項目並重新處理。

### 3. 匯出報告

使用 Google Sheets 的功能：
- 篩選特定關鍵字
- 匯出為 CSV
- 建立圖表分析趨勢

### 4. 整合其他服務

N8N 可以整合：
- Slack（發送通知）
- Notion（儲存筆記）
- Airtable（進階資料庫）
- Telegram（即時通知）

---

## 📚 相關文檔

- [完整流程說明](./GOOGLE_ALERT_N8N_WORKFLOW.md)
- [Google Sheet 結構說明](./GOOGLE_SHEET_STRUCTURE.md)
- [Parser API 使用說明](./HOW_TO_USE_PARSER_API.md)
- [N8N 整合指南](./n8n-integration.md)

---

**享受自動化的樂趣！** 🎊



