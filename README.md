# 網頁內容解析器 API

自動提取網頁文章內容的 RESTful API 伺服器。

## 🎯 有兩個版本可選擇！

- **🐍 Python 版本** - 使用 FastAPI + trafilatura（推薦給 Python 使用者）
- **🟨 JavaScript 版本** - 使用 Express + @postlight/parser

👉 **不知道選哪個？查看 [PYTHON_VS_JAVASCRIPT.md](PYTHON_VS_JAVASCRIPT.md) 詳細比較**

## 功能特色

✨ 自動提取網頁文章的標題、作者、發布日期、內容等資訊  
🚀 提供 RESTful API 介面  
📝 支援 POST 和 GET 兩種請求方式  
🔍 自動解析 HTML 並提取乾淨的文章內容  
🔗 **Google URL 解碼器** - 從 Google Alert/RSS 重定向 URL 中提取真實網址  
⚡ 快速且易於使用  
🔗 完整的 n8n 整合支援

## 📦 安裝與啟動

### Python 版本 🐍（推薦）

```bash
# 1. 安裝 Python 套件
pip install -r requirements.txt

# 2. 啟動伺服器
python parser-server.py

# 3. 測試
python test-parser.py

# 4. 查看 API 文件
# 瀏覽器開啟：http://localhost:3000/docs
```

### JavaScript 版本 🟨

```bash
# 1. 安裝 Node.js 套件（已完成）
npm install

# 2. 啟動伺服器
npm start

# 3. 測試
npm test
```

伺服器預設會在 `http://localhost:3000` 啟動。

## API 使用方式

### 1. 查看 API 資訊

**請求：**
```bash
curl http://localhost:3000/
```

### 2. 解析網頁內容（POST 方法）

**請求：**
```bash
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

**範例：解析實際新聞文章**
```bash
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news/world"}'
```

### 3. 解析網頁內容（GET 方法）

**請求：**
```bash
curl "http://localhost:3000/api/parse?url=https://example.com/article"
```

**範例：**
```bash
curl "http://localhost:3000/api/parse?url=https://www.bbc.com/news/world"
```

### 4. 使用瀏覽器測試

直接在瀏覽器中開啟：
```
http://localhost:3000/api/parse?url=https://example.com/article
```

### 5. 解碼 Google URL（新功能！）⭐

**從 Google Alert/RSS 重定向 URL 中提取真實網址**

**POST 請求：**
```bash
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?url=https://example.com/article&sa=U"}'
```

**GET 請求：**
```bash
curl "http://localhost:3000/api/decode-google-url?url=https://www.google.com/url?url=https://example.com/article"
```

**回應範例：**
```json
{
  "success": true,
  "original_url": "https://www.google.com/url?url=https://example.com/article&sa=U",
  "decoded_url": "https://example.com/article",
  "is_google_url": true,
  "changed": true
}
```

**使用場景：**
- 處理 Google Alert 郵件中的新聞連結
- 解析 Google RSS Feed 的重定向 URL
- 在 n8n 工作流程中自動提取真實網址

**詳細文件：** 查看 [GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md)

## API 回傳格式

### 成功回應

```json
{
  "success": true,
  "data": {
    "title": "文章標題",
    "author": "作者名稱",
    "date_published": "2024-01-01T00:00:00.000Z",
    "lead_image_url": "https://example.com/image.jpg",
    "dek": "副標題或摘要",
    "url": "https://example.com/article",
    "domain": "example.com",
    "excerpt": "文章摘要...",
    "word_count": 1500,
    "direction": "ltr",
    "total_pages": 1,
    "rendered_pages": 1,
    "next_page_url": null,
    "content": "<div><p>文章內容的 HTML...</p></div>"
  }
}
```

### 錯誤回應

**缺少 URL：**
```json
{
  "error": "請提供 URL",
  "example": { "url": "https://example.com/article" }
}
```

**URL 格式錯誤：**
```json
{
  "error": "URL 格式不正確",
  "provided": "invalid-url"
}
```

**解析失敗：**
```json
{
  "error": "解析網頁時發生錯誤",
  "message": "錯誤訊息",
  "url": "https://example.com/article"
}
```

## 環境變數

可以透過環境變數設定伺服器埠號：

```bash
PORT=8080 npm start
```

預設埠號為 `3000`。

## 程式碼範例

### JavaScript/Node.js

```javascript
// 使用 fetch
const response = await fetch('http://localhost:3000/api/parse', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com/article'
  })
});

const data = await response.json();
console.log(data.data.title);
console.log(data.data.content);
```

### Python

```python
import requests

response = requests.post('http://localhost:3000/api/parse', 
    json={'url': 'https://example.com/article'})

data = response.json()
print(data['data']['title'])
print(data['data']['content'])
```

## 技術架構

### Python 版本
- **FastAPI** - 現代化 Web 框架
- **trafilatura** - 學術級網頁內容解析引擎
- **httpx** - 非同步 HTTP 客戶端
- **Python 3.8+** - 執行環境

### JavaScript 版本
- **Express.js** - Web 框架
- **@postlight/parser** - 業界頂尖網頁內容解析引擎
- **Node.js** - 執行環境

## 注意事項

⚠️ 某些網站可能有反爬蟲機制，導致解析失敗  
⚠️ 需要網路連線才能存取目標網頁  
⚠️ 解析時間取決於目標網頁的大小和網路速度  

## 授權

ISC

## 問題排除

### 無法啟動伺服器
- 確認埠號 3000 沒有被其他程式使用
- 嘗試使用不同的埠號：`PORT=8080 npm start`

### 解析失敗
- 確認 URL 格式正確且可訪問
- 某些網站可能阻擋爬蟲，可以嘗試其他新聞網站
- 檢查網路連線是否正常

### 找不到套件
- JavaScript: `npm install`
- Python: `pip install -r requirements.txt`

---

## 📁 專案檔案說明

### 核心檔案
- `parser-server.py` - Python 版本伺服器 🐍
- `parser-server.js` - JavaScript 版本伺服器 🟨
- `requirements.txt` - Python 套件依賴
- `package.json` - Node.js 套件依賴

### 測試與工具
- `test-parser.py` - Python 測試腳本
- `test-parser.js` - JavaScript 測試腳本
- `test-google-url-decoder.py` - Google URL 解碼器測試（需伺服器）
- `test-decode-function.py` - 解碼函數測試（獨立運行）⭐
- `n8n-batch-parser.py` - Python 批次處理工具
- `n8n-batch-parser.js` - JavaScript 批次處理工具
- `example-articles.json` - 範例輸入檔案

### n8n 整合
- `n8n-workflow-example.json` - 可直接匯入的 n8n workflow
- `n8n-integration.md` - 詳細整合指南
- `QUICK_START.md` - 快速上手指南

### 文件
- `README.md` - 本檔案（專案總覽）
- `PYTHON_VS_JAVASCRIPT.md` - 版本比較與選擇指南 ⭐
- `GOOGLE_URL_DECODER.md` - Google URL 解碼器完整文件 🆕
- `EXAMPLE_GOOGLE_URL_DECODE.md` - Google URL 解碼器實用範例 🆕
- `.gitignore` - Git 忽略設定

---

## 🔗 更多資源

### 版本選擇
👉 **[PYTHON_VS_JAVASCRIPT.md](PYTHON_VS_JAVASCRIPT.md)** - 詳細比較兩個版本，幫助你選擇

### n8n 整合
👉 **[QUICK_START.md](QUICK_START.md)** - 快速上手 n8n 整合  
👉 **[n8n-integration.md](n8n-integration.md)** - 完整整合指南  
👉 **[n8n-workflow-example.json](n8n-workflow-example.json)** - 可直接匯入的 workflow

### Google URL 解碼器 🆕
👉 **[GOOGLE_URL_DECODER.md](GOOGLE_URL_DECODER.md)** - 完整 API 文件與使用說明  
👉 **[EXAMPLE_GOOGLE_URL_DECODE.md](EXAMPLE_GOOGLE_URL_DECODE.md)** - 實際使用案例與範例
```bash
# 快速測試解碼功能
python3 test-decode-function.py
```

### 批次處理
```bash
# Python 版本
python n8n-batch-parser.py input.json output.json

# JavaScript 版本
npm run batch
```

---

## 🎯 推薦使用流程

1. **選擇版本** → 查看 [PYTHON_VS_JAVASCRIPT.md](PYTHON_VS_JAVASCRIPT.md)
2. **安裝啟動** → 跟隨上方的安裝指南
3. **測試 API** → 使用測試腳本確認運作
4. **整合 n8n** → 查看 [QUICK_START.md](QUICK_START.md)
5. **開始使用** → 享受自動化的便利！

---

## 💬 需要幫助？

- 📖 查看 [QUICK_START.md](QUICK_START.md) 快速上手
- 🔍 查看 [n8n-integration.md](n8n-integration.md) 了解整合方式
- ⚖️ 查看 [PYTHON_VS_JAVASCRIPT.md](PYTHON_VS_JAVASCRIPT.md) 比較版本

