# ⚡ Google URL 解碼器 - 快速參考

## 🎯 一句話說明
從 Google Alert/RSS 的重定向 URL 中提取真實網址。

---

## 🚀 快速開始（3 分鐘）

### 1. 測試解碼功能（不需伺服器）
```bash
cd /Users/yangchenghan/news_parser
python3 test-decode-function.py
```

**預期結果：** 
```
✅ 成功：6
❌ 失敗：0
成功率：100.0%
🎉 所有測試通過！
```

### 2. 啟動伺服器
```bash
python3 parser-server.py
```

### 3. 測試 API
```bash
# 在另一個終端機
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?url=https://example.com/article"}'
```

---

## 📝 最常用的指令

### 命令列測試
```bash
# POST 方法
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_GOOGLE_URL"}'

# GET 方法
curl "http://localhost:3000/api/decode-google-url?url=YOUR_GOOGLE_URL"
```

### Python 使用
```python
import requests

url = "https://www.google.com/url?url=https://example.com/article"
response = requests.post(
    'http://localhost:3000/api/decode-google-url',
    json={'url': url}
)
decoded = response.json()['decoded_url']
print(decoded)  # https://example.com/article
```

### n8n HTTP Request 節點
```
Method: POST
URL: http://localhost:3000/api/decode-google-url
Body: {"url": "{{ $json.google_url }}"}
結果: {{ $json.decoded_url }}
```

---

## 📊 回應格式

```json
{
  "success": true,
  "original_url": "https://www.google.com/url?url=...",
  "decoded_url": "https://example.com/article",
  "is_google_url": true,
  "changed": true
}
```

---

## 🔗 實際範例

### 您的 Google Alert URL
```
輸入：
https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/&ct=ga&...

輸出：
https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/
```

### 台積電新聞
```
輸入：
https://www.google.com/url?url=https://www.bnext.com.tw/article/80198/tsmc-2024

輸出：
https://www.bnext.com.tw/article/80198/tsmc-2024
```

---

## 🔧 在 n8n 工作流程中的位置

```
Gmail Trigger (Google Alert)
  ↓
Extract URLs from Email
  ↓
🆕 Decode Google URL ⬅️ 在這裡添加
  ↓
Parse Article Content
  ↓
AI Generate Summary
  ↓
Write to Google Sheets
```

---

## 📚 詳細文件

| 需要什麼 | 看這個檔案 |
|---------|-----------|
| 完整 API 文件 | [GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md) |
| 實際使用範例 | [EXAMPLE_GOOGLE_URL_DECODE.md](EXAMPLE_GOOGLE_URL_DECODE.md) |
| 更新日誌 | [CHANGELOG_GOOGLE_URL_DECODER.md](CHANGELOG_GOOGLE_URL_DECODER.md) |
| 專案總覽 | [README.md](README.md) |

---

## 🐛 快速除錯

### 問題：伺服器無法啟動
```bash
# 檢查埠號是否被佔用
lsof -i :3000

# 使用其他埠號
PORT=8080 python3 parser-server.py
```

### 問題：測試腳本找不到 Python
```bash
# 使用 python3
python3 test-decode-function.py

# 或確認 Python 版本
which python3
python3 --version
```

### 問題：n8n 無法連接
```bash
# 1. 確認伺服器運行
curl http://localhost:3000/health

# 2. 如果伺服器在其他機器，使用完整 URL
# http://your-server-ip:3000/api/decode-google-url
# 或
# https://your-app.railway.app/api/decode-google-url
```

---

## ✅ 檢查清單

### 初次設定
- [ ] 執行 `python3 test-decode-function.py` 確認功能正常
- [ ] 啟動伺服器 `python3 parser-server.py`
- [ ] 測試 API 端點（使用 curl 或瀏覽器）
- [ ] 閱讀 [GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md)

### 整合到 n8n
- [ ] 在 Gmail Trigger 之後添加 HTTP Request 節點
- [ ] 設定 POST 方法和 URL
- [ ] 測試節點執行
- [ ] 確認可以取得 `decoded_url`
- [ ] 將 `decoded_url` 傳遞給下一個節點

### 部署到生產環境
- [ ] 確認所有測試通過
- [ ] 提交代碼到 Git
- [ ] 部署到 Railway（或其他平台）
- [ ] 更新 n8n 中的 API URL
- [ ] 執行端到端測試

---

## 💡 最佳實踐

1. **先解碼，再解析**
   ```
   Decode Google URL → Parse Article
   （不要直接用 Google URL 解析文章）
   ```

2. **處理錯誤**
   ```javascript
   // 如果解碼失敗，使用原 URL
   const url = $json.decoded_url || $json.original_url;
   ```

3. **過濾非文章 URL**
   ```javascript
   // 排除 Google News 首頁等
   const isArticle = !url.includes('news.google.com');
   ```

---

## 🎯 核心優勢

- ⚡ **快速** - 毫秒級回應
- 🛡️ **可靠** - 100% 測試通過
- 🔄 **容錯** - 失敗時返回原 URL
- 📦 **零依賴** - Python 標準庫
- 🌐 **雙方法** - POST/GET 都支援
- 🔗 **易整合** - n8n/Python/JavaScript

---

## 📞 需要幫助？

**測試功能：**
```bash
python3 test-decode-function.py
```

**查看文件：**
- 完整說明：[GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md)
- 使用範例：[EXAMPLE_GOOGLE_URL_DECODE.md](EXAMPLE_GOOGLE_URL_DECODE.md)

**測試 API：**
```bash
# 健康檢查
curl http://localhost:3000/health

# API 資訊
curl http://localhost:3000/

# 解碼測試
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?url=https://example.com"}'
```

---

**祝您使用愉快！🚀**

