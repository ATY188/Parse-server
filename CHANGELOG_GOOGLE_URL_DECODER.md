# 🎉 更新日誌 - Google URL 解碼器功能

## 版本 1.5.0 - 2025-11-06

### 🆕 新增功能

#### Google URL 解碼器
為 TSMC 新聞自動化專案新增 Google URL 解碼器功能，可以從 Google Alert 和 Google RSS 的重定向 URL 中提取真實的目標網址。

---

## 📝 更新內容

### 1. 核心功能（parser-server.py）

#### 新增的代碼模組：

**a) Pydantic 模型（第 104-111 行）**
```python
class DecodeGoogleUrlRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必須以 http:// 或 https:// 開頭')
        return v
```

**b) 解碼函數（第 371-417 行）**
```python
def decode_google_url(google_url: str) -> Optional[str]:
    """從 Google 重定向 URL 中提取真實的目標 URL"""
    # 支援 url, q, u 三種參數格式
    # 自動處理 URL 編碼
    # 錯誤時返回原 URL（容錯設計）
```

**c) API 端點**
- `POST /api/decode-google-url` - POST 方法解碼（第 917-965 行）
- `GET /api/decode-google-url` - GET 方法解碼（第 968-1014 行）

**d) 更新首頁資訊（第 478-490 行）**
- 在 API 文件中添加新端點說明
- 更新使用範例

---

### 2. 測試腳本

#### a) test-decode-function.py（獨立測試）⭐ 推薦
- **功能：** 不需要啟動伺服器，直接測試解碼函數
- **測試案例：** 6 個完整的測試案例
- **結果：** ✅ 100% 測試通過率

**測試內容：**
1. 您提供的實際 Google Alert URL
2. 簡單的 Google URL
3. 使用 q 參數的 URL
4. URL 編碼的網址
5. 普通 URL（非 Google）
6. 台積電相關新聞 URL

#### b) test-google-url-decoder.py（完整 API 測試）
- **功能：** 測試完整的 API 端點
- **測試項目：**
  - POST 方法測試
  - GET 方法測試
  - 批次處理測試
  - 邊界情況測試

---

### 3. 文件

#### a) GOOGLE_URL_DECODER.md（完整 API 文件）
**內容包含：**
- 📋 功能說明
- 🚀 使用方法（POST/GET）
- 🔍 實際範例
- 📊 回應欄位說明
- 🔧 在 n8n 中使用
- 🐍 Python 使用範例
- 🟨 JavaScript 使用範例
- 🧪 測試指南
- 💡 使用場景
- 🐛 除錯指南

#### b) EXAMPLE_GOOGLE_URL_DECODE.md（實用範例）
**內容包含：**
- 🎯 實際情境說明
- 🚀 快速開始指南
- 📝 完整工作流程
- 🔧 n8n 節點設定範例
- 💡 實用技巧（批次處理、過濾、錯誤處理）
- 📊 台積電新聞收集案例
- 🔍 除錯範例
- 📈 效能優化建議

#### c) README.md（主文件更新）
**更新內容：**
- 功能特色中新增 Google URL 解碼器說明
- API 使用方式新增第 5 節「解碼 Google URL」
- 測試與工具部分新增測試腳本
- 文件部分新增 2 個新文件
- 更多資源部分新增「Google URL 解碼器」專區

#### d) CHANGELOG_GOOGLE_URL_DECODER.md（本檔案）
- 記錄所有更新內容

---

## 🎯 功能特點

### 支援的 URL 格式
✅ `https://www.google.com/url?url=...`  
✅ `https://www.google.com/url?q=...`  
✅ `https://www.google.com/url?u=...`  
✅ URL 編碼的網址（自動解碼）  
✅ 普通 URL（直接返回，不處理）

### 核心優勢
- ⚡ **極快速** - 純字串處理，毫秒級回應
- 🛡️ **高可靠** - 100% 測試通過率
- 🔄 **容錯設計** - 解碼失敗時返回原 URL
- 📦 **零依賴** - 使用 Python 標準庫
- 🌐 **雙方法** - 支援 POST 和 GET 請求
- 🔗 **完美整合** - 可無縫整合到 n8n 工作流程

---

## 📊 測試結果

### 執行測試
```bash
python3 test-decode-function.py
```

### 測試結果
```
================================================================================
📊 測試總結
================================================================================
總測試數：6
✅ 成功：6
❌ 失敗：0
成功率：100.0%

🎉 所有測試通過！
================================================================================
```

### 實際測試案例

**測試 1：您提供的 Google Alert URL**
```
輸入：https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/...
輸出：https://247sports.com/longformarticle/...
結果：✅ 正確！
```

**測試 6：台積電相關新聞**
```
輸入：https://www.google.com/url?url=https://www.bnext.com.tw/article/80198/tsmc-2024
輸出：https://www.bnext.com.tw/article/80198/tsmc-2024
結果：✅ 正確！
```

---

## 🔧 使用方式

### 方法 1：API 端點（POST）

```bash
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?url=https://example.com/article"}'
```

### 方法 2：API 端點（GET）

```bash
curl "http://localhost:3000/api/decode-google-url?url=https://www.google.com/url?url=https://example.com/article"
```

### 方法 3：在 n8n 中使用

```
HTTP Request 節點：
  Method: POST
  URL: http://localhost:3000/api/decode-google-url
  Body: { "url": "{{ $json.google_url }}" }
  
取得結果：{{ $json.decoded_url }}
```

---

## 💡 實際應用場景

### 場景 1：Google Alert 自動化
```
Gmail → 提取 URL → 解碼 Google URL → 解析文章 → AI 摘要 → 儲存 Sheets
```

### 場景 2：台積電新聞監控
```
Google Alert (TSMC, 台積電) 
  ↓
解碼 Google URL
  ↓
解析文章內容
  ↓
AI 生成摘要
  ↓
通知 Slack / Email
```

### 場景 3：批次處理新聞連結
```python
google_urls = [
    "https://www.google.com/url?url=https://article1.com",
    "https://www.google.com/url?url=https://article2.com",
    # ... 更多
]

decoded_urls = [decode_google_url(url) for url in google_urls]
```

---

## 📁 新增的檔案清單

```
/Users/yangchenghan/news_parser/
├── parser-server.py                      (已更新)
├── README.md                             (已更新)
├── test-decode-function.py               (新增) ⭐
├── test-google-url-decoder.py            (新增)
├── GOOGLE_URL_DECODER.md                 (新增)
├── EXAMPLE_GOOGLE_URL_DECODE.md          (新增)
└── CHANGELOG_GOOGLE_URL_DECODER.md       (新增，本檔案)
```

---

## 🚀 下一步建議

### 1. 立即測試
```bash
# 測試解碼功能（推薦）
python3 test-decode-function.py

# 啟動伺服器
python3 parser-server.py

# 測試 API（需要先啟動伺服器）
python3 test-google-url-decoder.py
```

### 2. 整合到現有工作流程

在您的 n8n 工作流程中添加新的 HTTP Request 節點：
- 在提取 Google Alert URL 之後
- 在解析文章內容之前
- 用來解碼 Google 重定向 URL

### 3. 部署到 Railway

如果您的 parser API 已部署在 Railway：
```bash
# 推送更新
git add .
git commit -m "feat: add Google URL decoder"
git push

# Railway 會自動重新部署
```

更新後的 API 端點：
```
https://your-app.railway.app/api/decode-google-url
```

---

## 📚 相關文件

| 文件 | 說明 |
|------|------|
| [GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md) | 完整的 API 文件 |
| [EXAMPLE_GOOGLE_URL_DECODE.md](EXAMPLE_GOOGLE_URL_DECODE.md) | 實際使用範例 |
| [README.md](README.md) | 專案總覽（已更新） |
| [GOOGLE_ALERT_SETUP.md](GOOGLE_ALERT_SETUP.md) | Google Alert 設定指南 |
| [n8n-integration.md](n8n-integration.md) | n8n 整合完整指南 |

---

## ✨ 總結

這次更新為您的 TSMC 新聞自動化專案新增了一個非常實用的功能：

✅ **解決痛點** - 自動處理 Google Alert 中的重定向 URL  
✅ **完整測試** - 100% 測試通過，可靠穩定  
✅ **易於使用** - 提供 POST/GET 兩種方法  
✅ **完善文件** - 3 個詳細的使用文件  
✅ **無縫整合** - 可直接整合到現有 n8n 工作流程  

**現在您可以完全自動化處理 Google Alert 郵件中的新聞連結了！** 🎉

---

## 🙏 感謝

感謝您使用這個專案！如果有任何問題或建議，歡迎隨時反饋。

---

**版本：** 1.5.0  
**日期：** 2025-11-06  
**作者：** AI Assistant  
**專案：** News Parser API - TSMC 專案

