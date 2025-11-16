# 🚀 ngrok 設定指南

## 快速開始（3步驟）

### 步驟 1：確保 Parser API 正在運行

在**第一個終端視窗**中：

```bash
cd /Users/yangchenghan/news_parser
source venv/bin/activate
python parser-server.py
```

應該看到：
```
🚀 網頁內容解析器 API 啟動中...
INFO:     Uvicorn running on http://0.0.0.0:3000
```

✅ 保持這個終端視窗開著！

---

### 步驟 2：啟動 ngrok

打開**第二個終端視窗**，執行：

```bash
cd /Users/yangchenghan/news_parser
./start-ngrok.sh
```

或者直接執行：

```bash
ngrok http 3000
```

---

### 步驟 3：複製 ngrok URL

ngrok 啟動後，您會看到類似這樣的畫面：

```
ngrok

Session Status                online
Account                       您的帳號 (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123xyz456.ngrok.io -> http://localhost:3000
                              ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                              ✅ 複製這個 HTTPS URL！

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**複製 `Forwarding` 那一行的 HTTPS URL**

例如：`https://abc123xyz456.ngrok.io`

---

## 🎯 在 n8n 中使用

### 更新 HTTP Request (Parser) 節點：

1. **打開 n8n workflow**

2. **點擊 HTTP Request (Parser) 節點**

3. **修改 URL：**
   ```
   舊的（無法使用）:
   http://localhost:3000/api/parse
   
   新的（使用 ngrok URL）:
   https://abc123xyz456.ngrok.io/api/parse
   ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
   替換成您實際的 ngrok URL
   ```

4. **其他設定保持不變：**
   - Method: `POST`
   - Body: `{"url": "={{ $json.body.decoded_url }}"}`
   - Headers: `Content-Type: application/json`
   - Timeout: `90000`

5. **儲存並測試！**

---

## ✅ 測試 ngrok 連接

在瀏覽器中訪問：

```
https://abc123xyz456.ngrok.io/health
```

應該看到：
```json
{
  "status": "healthy",
  "service": "parser-api",
  "version": "1.4.0"
}
```

✅ 如果看到這個，表示 ngrok 設定成功！

---

## 🛑 測試完成後關閉

### 關閉 ngrok：

在運行 ngrok 的終端視窗中：
```
按 Ctrl + C
```

### 關閉 Parser API（可選）：

在運行 parser-server.py 的終端視窗中：
```
按 Ctrl + C
```

---

## ⚠️ 重要提醒

### 安全須知：

1. ✅ **ngrok URL 是隨機的**，不會被輕易發現
2. ✅ **只在測試時開啟**，不用時立即關閉
3. ✅ **不要分享** ngrok URL 給其他人
4. ✅ 每次重啟 ngrok，URL 都會改變（需要重新更新 n8n）

### 使用時間建議：

```
開啟 ngrok → 測試 workflow → 立即關閉
總時間：< 30 分鐘
```

---

## 🔧 常見問題

### Q1: ngrok 要求註冊怎麼辦？

**A:** 如果是第一次使用，ngrok 可能要求註冊：

1. 訪問：https://dashboard.ngrok.com/signup
2. 使用 Google/GitHub 帳號註冊（免費）
3. 複製您的 Authtoken
4. 執行：`ngrok config add-authtoken YOUR_TOKEN`
5. 重新啟動 ngrok

### Q2: ngrok URL 每次都不一樣嗎？

**A:** 是的，免費版每次重啟會得到新的隨機 URL。
- 優點：更安全
- 缺點：需要重新更新 n8n 中的 URL

### Q3: 可以固定 ngrok URL 嗎？

**A:** 需要升級到付費版（約 $8/月）。
但測試用途不需要，每次更新 URL 即可。

### Q4: ngrok 關閉後 n8n 還能用嗎？

**A:** 不能。關閉 ngrok 後，公開 URL 就失效了。
如需再次使用，重新啟動 ngrok 並更新 n8n 中的 URL。

---

## 📊 完整測試流程

```
1. ✅ 確認 Parser API 運行（localhost:3000）
   └─ python parser-server.py

2. ✅ 啟動 ngrok
   └─ ngrok http 3000
   └─ 複製 HTTPS URL

3. ✅ 更新 n8n workflow
   └─ 更改 Parser API URL 為 ngrok URL

4. ✅ 測試 3 個 RSS Feed
   └─ 執行 workflow
   └─ 檢查結果

5. ✅ 關閉 ngrok
   └─ Ctrl + C

完成！🎉
```

---

## 💡 下次使用

每次使用 ngrok 時：

1. 啟動 Parser API
2. 啟動 ngrok
3. **更新 n8n 中的 URL**（因為 ngrok URL 會變）
4. 測試
5. 關閉 ngrok

---

**祝測試順利！** 🚀

如有任何問題，請隨時詢問！

