# ✅ Railway 部署檢查清單

## 準備工作

### 1. 檔案檢查
- [x] `parser-server.py` - 已調整支援 Railway
- [x] `requirements.txt` - Python 依賴清單
- [x] `railway.json` - Railway 設定
- [x] `Procfile` - 啟動指令
- [x] `.gitignore` - Git 忽略檔案

**✅ 所有檔案已準備完成！**

---

## 部署流程

### 第一步：GitHub 準備

- [ ] 註冊/登入 GitHub 帳號
- [ ] 在專案目錄執行 Git 初始化
- [ ] 建立 GitHub Repository
- [ ] Push 程式碼到 GitHub

**命令：**
```bash
cd /Users/yangchenghan/news_parser
git init
git add .
git commit -m "初始提交：Parser API for Railway"
# 然後到 GitHub 建立 repository
git remote add origin https://github.com/你的username/news_parser.git
git branch -M main
git push -u origin main
```

---

### 第二步：Railway 部署

- [ ] 訪問 https://railway.app
- [ ] 使用 GitHub 登入
- [ ] 點擊「New Project」
- [ ] 選擇「Deploy from GitHub repo」
- [ ] 授權並選擇 news_parser repository
- [ ] 等待自動部署完成（1-2 分鐘）

---

### 第三步：獲取 URL

- [ ] 點擊你的服務
- [ ] 進入「Settings」標籤
- [ ] 找到「Networking」區域
- [ ] 點擊「Generate Domain」
- [ ] 複製產生的 URL

**你的 URL 會像：**
```
https://news-parser-production.up.railway.app
```

---

### 第四步：測試部署

- [ ] 在瀏覽器訪問 Railway URL
- [ ] 應該看到 API 資訊
- [ ] 訪問 `/docs` 查看 Swagger UI
- [ ] 訪問 `/health` 確認服務健康

**測試命令：**
```bash
# 測試首頁
curl https://你的網址.railway.app/

# 測試健康檢查
curl https://你的網址.railway.app/health

# 測試解析功能
curl -X POST https://你的網址.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.bbc.com/news"}'
```

---

### 第五步：n8n 整合

- [ ] 打開 n8n workflow
- [ ] 找到 HTTP Request 節點
- [ ] 更新 URL 為 Railway URL
- [ ] 測試執行
- [ ] 確認解析成功

**n8n 設定：**
```
Method: POST
URL: https://你的railway網址.railway.app/api/parse

Body Content Type: JSON
JSON:
{
  "url": "{{ $json.url_rss }}"
}
```

---

## 部署後檢查

### 功能測試

- [ ] 首頁正常顯示
- [ ] Swagger UI 可以訪問（/docs）
- [ ] 健康檢查正常（/health）
- [ ] POST 解析測試成功
- [ ] GET 解析測試成功
- [ ] n8n 整合測試成功

### 監控設定

- [ ] 查看 Railway 日誌
- [ ] 確認沒有錯誤
- [ ] 查看使用量統計
- [ ] 設定使用量提醒（選用）

---

## 🎯 完成！

當所有項目都打勾後，你的 Parser API 就成功部署到雲端了！🎉

### 重要連結

- **Railway 專案**: https://railway.app/project/你的專案ID
- **API URL**: https://你的網址.railway.app
- **API 文件**: https://你的網址.railway.app/docs
- **GitHub Repo**: https://github.com/你的username/news_parser

### 下一步

1. **儲存你的 Railway URL** - 加入書籤或記在安全的地方
2. **監控使用量** - 定期查看 Railway 使用情況
3. **測試 n8n workflow** - 確保整個流程順暢
4. **享受自動化！** 🚀

---

## 📞 需要幫助？

如果遇到問題：

1. 查看 `RAILWAY_DEPLOY.md` 詳細指南
2. 檢查 Railway 日誌找錯誤訊息
3. 重新檢查這個清單的每一步

**部署愉快！** 🎉

