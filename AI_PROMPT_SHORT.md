# n8n 整合快速請求

## 我的目標
建立 n8n workflow，從 Google Sheet 讀取網址 → 呼叫 Parser API → AI 生成摘要 → 寫回 Google Sheet

## 資源
- **Parser API**: https://web-production-32568.up.railway.app/api/parse
- **API 文件**: https://web-production-32568.up.railway.app/docs
- **n8n**: 雲端版
- **Google Sheet**: 8 欄（url, title, author, content, date, summary, status, time）

## API 格式
**請求：**
```json
POST /api/parse
{"url": "https://example.com"}
```

**回應：**
```json
{
  "status": "success",
  "data": {
    "title": "標題",
    "author": "作者",
    "content": "內容",
    "date_published": "日期"
  }
}
```

## Workflow 邏輯
```
Schedule (30min) 
→ Read Sheet (filter status=pending)
→ HTTP Request (呼叫 API)
→ OpenAI (生成摘要)
→ Update Sheet (寫回資料, status=completed)
```

## 我需要知道
1. 各節點的詳細參數設定
2. 如何在表達式中引用上一個節點的資料
3. 如何動態更新 Google Sheet 的特定行
4. 如何處理錯誤（API 失敗時標記 status=failed）

請提供逐步設定教學，謝謝！


