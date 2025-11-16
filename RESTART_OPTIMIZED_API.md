# 🔄 重啟優化版 Parser API 指南

## 📋 快速步驟

### 1️⃣ 停止當前運行的服務

**找到並停止 Parser API：**
```bash
# 按 Ctrl+C 停止當前運行的 parser-server.py
```

**找到並停止 ngrok：**
```bash
# 按 Ctrl+C 停止當前運行的 ngrok
```

---

### 2️⃣ 清理 Python 快取（重要！）

```bash
cd /Users/yangchenghan/news_parser
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
```

**為什麼要清理？**
- Python 會快取編譯後的代碼
- 不清理可能導致使用舊版本代碼
- 優化不會生效

---

### 3️⃣ 啟動優化版 Parser API

```bash
cd /Users/yangchenghan/news_parser
source venv/bin/activate  # 如果使用虛擬環境
python parser-server.py
```

**應該看到：**
```
🚀 Parser 伺服器已啟動！（Python 增強版 v1.6.0）
📡 監聽埠號: 3000
🌐 本地訪問: http://localhost:3000
...
```

**確認優化已啟用：**
- 訪問：http://localhost:3000/health
- 查看 `"version": "1.6.0"`
- 查看 `"features"` 包含 `"memory-optimized"` 和 `"concurrency-control"`

---

### 4️⃣ 啟動 ngrok（如果需要）

**在新終端視窗：**
```bash
ngrok http 3000
```

**記下新的 ngrok URL：**
```
https://xxxxxx.ngrok-free.dev
```

**如果 n8n 使用 ngrok，記得更新 URL！**

---

### 5️⃣ 測試優化效果

**方法 A：使用測試腳本（推薦）**
```bash
cd /Users/yangchenghan/news_parser
python test-memory-optimization.py
```

**方法 B：手動測試**
```bash
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.storm.mg/article/5032746"}'
```

**方法 C：在 n8n 中測試**
- 執行 3-5 筆測試
- 觀察速度和穩定性

---

## 🔍 觀察優化效果

### 在 Parser API 終端中，應該看到：

```
[Playwright] 啟動瀏覽器（記憶體優化版）...
[Playwright] 🔒 獲取執行權限（確保同時只有 1 個實例運行，防止記憶體溢出）
[Playwright] 正在訪問: https://...
...
[Playwright] ✅ 成功獲取內容，長度: 12345
[Playwright] 🔒 瀏覽器已關閉，記憶體已釋放
[Playwright] ✅ 第 1 次嘗試成功
[Playwright] 🔓 釋放執行權限
```

**關鍵訊息：**
- ✅ `記憶體優化版` - 確認使用優化版本
- ✅ `獲取執行權限` - 並發控制生效
- ✅ `瀏覽器已關閉，記憶體已釋放` - 記憶體正確釋放
- ✅ `釋放執行權限` - 允許下一個請求執行

---

## ⚠️ 問題排查

### 問題 1：沒看到「記憶體優化版」
**原因：** 使用了舊版代碼
**解決：**
1. 確認停止了所有 Python 進程
2. 清理 `__pycache__`
3. 重新啟動

### 問題 2：速度變慢了
**檢查：**
1. 是否有多個請求在排隊？（正常，並發控制）
2. 網路連線是否正常？
3. 與優化前對比（應該差不多或更快）

### 問題 3：解析失敗
**檢查：**
1. 是否是之前就會失敗的網站？
2. 查看錯誤訊息
3. 與優化前對比

---

## 📊 性能基準

### 預期速度（本地 API）

| 網站類型 | 優化前 | 優化後 | 目標 |
|---------|--------|--------|------|
| 靜態網站 | 2-3 秒 | 2-3 秒 | ✅ 相同 |
| 動態網站 | 5-7 秒 | 4.5-6.5 秒 | ✅ 稍快 |

**如果速度在這個範圍內，說明優化成功！** ✅

---

## 🎯 下一步

### ✅ 優化已完成，現在可以：

**選項 A：繼續用 ngrok（短期）**
- 適合測試和開發
- 免費
- 需要電腦保持運行

**選項 B：部署到 Railway Hobby（長期）**
- 每月 $5
- 24/7 在線
- 不需要本地電腦運行

---

## 📞 需要幫助？

### 查看日誌：
```bash
# Parser API 日誌
查看運行 parser-server.py 的終端視窗

# ngrok 日誌
查看運行 ngrok 的終端視窗

# n8n 執行日誌
在 n8n workflow 執行記錄中查看
```

### 測試腳本：
```bash
python test-memory-optimization.py
```

### 健康檢查：
```bash
curl http://localhost:3000/health
```

---

## ✅ 驗證清單

重啟後請確認：

- [ ] Parser API 顯示版本 1.6.0
- [ ] 健康檢查包含 `memory-optimized` 和 `concurrency-control`
- [ ] 終端顯示「記憶體優化版」
- [ ] 每次 Playwright 執行後看到「記憶體已釋放」
- [ ] 測試 3-5 個網站，功能正常
- [ ] 速度與優化前相當或更快
- [ ] ngrok URL 已在 n8n 中更新（如果使用）

---

**準備好了嗎？開始重啟吧！** 🚀

**記得：先停止 → 清快取 → 重啟 → 測試** 📋

