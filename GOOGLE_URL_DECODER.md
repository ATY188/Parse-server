# 🔗 Google URL 解碼器

從 Google 重定向 URL 中提取真實的目標 URL。

## 📋 功能說明

Google Alert 和 Google RSS 經常使用重定向 URL，例如：

```
https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/article&ct=ga&...
```

真實的網址其實是：

```
https://247sports.com/article
```

本功能可以自動從 Google 重定向 URL 中提取真實網址。

---

## 🚀 使用方法

### 方法 1: POST 請求

**請求：**
```bash
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com/url?url=https://example.com/article&sa=U"
  }'
```

**回應：**
```json
{
  "success": true,
  "original_url": "https://www.google.com/url?url=https://example.com/article&sa=U",
  "decoded_url": "https://example.com/article",
  "is_google_url": true,
  "changed": true
}
```

---

### 方法 2: GET 請求

**請求：**
```bash
curl "http://localhost:3000/api/decode-google-url?url=https://www.google.com/url?url=https://example.com/article"
```

**回應：**
```json
{
  "success": true,
  "original_url": "https://www.google.com/url?url=https://example.com/article",
  "decoded_url": "https://example.com/article",
  "is_google_url": true,
  "changed": true
}
```

---

## 🔍 實際範例

### 範例 1: 解碼 Google Alert URL

**輸入：**
```
https://www.google.com/url?rct=j&sa=t&url=https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/&ct=ga&cd=CAIyHTc0NjM2OWJmZjU0MjYwYzc6Y29tLnR3OmVuOlVT&usg=AOvVaw1VohbQmBL0yFbuqkkM8Hp7
```

**輸出：**
```
https://247sports.com/longformarticle/recruiting-intel-latest-on-eight-schools-leading-for-ed-dj-jacobs-2027s-no-1-recruit-260127331/
```

### 範例 2: 普通 URL（非 Google）

**輸入：**
```
https://technews.tw/2025/10/31/tsmc-news/
```

**輸出：**
```
https://technews.tw/2025/10/31/tsmc-news/
```
（不變，因為不是 Google URL）

---

## 📊 回應欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `success` | boolean | 是否成功解碼 |
| `original_url` | string | 原始輸入的 URL |
| `decoded_url` | string | 解碼後的真實 URL |
| `is_google_url` | boolean | 是否為 Google URL |
| `changed` | boolean | URL 是否有變化 |

---

## 🔧 在 n8n 中使用

### 情境：處理 Google Alert 郵件

```
1. Gmail Trigger
   ↓
2. Extract URLs from Email（提取所有 URL）
   ↓
3. HTTP Request: 解碼 Google URL ⬅️ 新增這一步
   - Method: POST
   - URL: https://your-api.railway.app/api/decode-google-url
   - Body: {{ { "url": $json.url } }}
   ↓
4. Get decoded_url from response
   ↓
5. Write to Google Sheets
```

### n8n HTTP Request 節點設定

**方法 1：單一 URL**

- **Method:** POST
- **URL:** `https://your-parser-api.com/api/decode-google-url`
- **Body:**
  ```json
  {
    "url": "{{ $json.url }}"
  }
  ```
- **取得結果：** `{{ $json.decoded_url }}`

**方法 2：批次處理多個 URL**

使用 n8n 的 Loop Over Items 或 Split in Batches：

```javascript
// Code node 範例
const items = $input.all();
const results = [];

for (const item of items) {
  const response = await $http.request({
    method: 'POST',
    url: 'https://your-api.com/api/decode-google-url',
    body: {
      url: item.json.url
    }
  });
  
  results.push({
    json: {
      original_url: item.json.url,
      decoded_url: response.decoded_url
    }
  });
}

return results;
```

---

## 🐍 在 Python 中使用

```python
import requests

def decode_google_url(google_url):
    """解碼 Google URL"""
    response = requests.post(
        'http://localhost:3000/api/decode-google-url',
        json={'url': google_url}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['decoded_url']
    else:
        return google_url  # 解碼失敗，返回原 URL

# 使用範例
url = "https://www.google.com/url?url=https://example.com/article&sa=U"
decoded = decode_google_url(url)
print(f"解碼後：{decoded}")
```

---

## 🟨 在 JavaScript 中使用

```javascript
async function decodeGoogleUrl(googleUrl) {
  try {
    const response = await fetch('http://localhost:3000/api/decode-google-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: googleUrl })
    });
    
    const data = await response.json();
    return data.decoded_url;
    
  } catch (error) {
    console.error('解碼失敗:', error);
    return googleUrl;  // 失敗時返回原 URL
  }
}

// 使用範例
const url = "https://www.google.com/url?url=https://example.com/article&sa=U";
const decoded = await decodeGoogleUrl(url);
console.log(`解碼後：${decoded}`);
```

---

## 🧪 測試

執行測試腳本：

```bash
# 啟動伺服器（終端機 1）
python parser-server.py

# 執行測試（終端機 2）
python test-google-url-decoder.py
```

測試腳本會自動執行：
- ✅ POST 方法測試
- ✅ GET 方法測試
- ✅ 批次處理測試
- ✅ 邊界情況測試

---

## 📝 支援的 URL 格式

### ✅ 支援

- `https://www.google.com/url?url=...`
- `https://www.google.com/url?q=...`
- `https://www.google.com/url?u=...`
- `https://news.google.com/url?url=...`
- URL 編碼的網址（自動解碼）

### ⚠️ 自動處理

- 普通 URL（非 Google URL）：直接返回原 URL
- 解碼失敗：返回原 URL（不會出錯）
- 空的 url 參數：返回原 URL

---

## 💡 使用場景

### 1. Google Alert 自動化
```
Gmail → 提取 URL → 解碼 Google URL → 解析文章 → 儲存到 Sheets
```

### 2. Google RSS Feed 處理
```
RSS Reader → 解碼 Google URL → 解析文章內容 → AI 摘要
```

### 3. 批次處理新聞連結
```python
google_urls = [
    "https://www.google.com/url?url=https://article1.com",
    "https://www.google.com/url?url=https://article2.com",
    # ... 更多
]

decoded_urls = [decode_google_url(url) for url in google_urls]
```

---

## 🔗 與其他功能整合

### 解碼後直接解析文章

**方法 1：兩步驟（推薦）**
```bash
# 1. 先解碼 URL
curl -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?url=https://example.com/article"}'

# 2. 用解碼後的 URL 解析文章
curl -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

**方法 2：在 n8n 中串連**
```
HTTP Request (Decode) → Set Variable → HTTP Request (Parse)
```

---

## ⚙️ API 配置

### 環境變數

不需要額外的環境變數，此功能使用 Python 標準庫。

### 效能

- ⚡ 極快速（純字串處理，無網路請求）
- 🔄 支援高並發
- 💾 無需資料庫

### 限制

- URL 長度：最大 8,192 字元
- 並發請求：無限制（純計算，無 I/O）

---

## 🐛 除錯

### 問題 1：解碼後的 URL 不正確

**可能原因：**
- Google 改變了 URL 格式

**解決方法：**
```python
# 手動檢查 URL 參數
from urllib.parse import urlparse, parse_qs

url = "你的 Google URL"
parsed = urlparse(url)
params = parse_qs(parsed.query)
print(params)  # 查看所有參數
```

### 問題 2：特殊字元處理

**範例：**
```
輸入：https://www.google.com/url?url=https%3A%2F%2Fexample.com%2Farticle%3Fid%3D123
輸出：https://example.com/article?id=123
```

自動處理 URL 編碼（%3A, %2F 等）。

---

## 📚 相關文件

- [HOW_TO_USE_PARSER_API.md](HOW_TO_USE_PARSER_API.md) - 解析器 API 使用指南
- [GOOGLE_ALERT_SETUP.md](GOOGLE_ALERT_SETUP.md) - Google Alert 設定
- [n8n-integration.md](n8n-integration.md) - n8n 整合指南

---

## 🎉 總結

這個 Google URL 解碼器讓您可以：

✅ 自動提取 Google Alert 中的真實 URL  
✅ 處理 Google RSS Feed 的重定向連結  
✅ 在 n8n 工作流程中無縫整合  
✅ 批次處理大量 URL  
✅ 極快速且可靠  

**開始使用：**
```bash
python parser-server.py
python test-google-url-decoder.py
```

🚀 享受自動化的便利！

