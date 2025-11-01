# 🚂 Railway 部署指南

## ✅ 準備完成

你的專案已經準備好部署到 Railway 了！所有必要的檔案都已建立：

- ✅ `requirements.txt` - Python 依賴套件
- ✅ `parser-server.py` - 已調整支援 Railway 環境變數
- ✅ `railway.json` - Railway 設定檔
- ✅ `Procfile` - 啟動指令
- ✅ `.gitignore` - Git 忽略檔案

---

## 🚀 部署步驟（10 分鐘）

### 步驟 1：註冊 Railway

1. 訪問 https://railway.app
2. 點擊「Login」
3. 使用 **GitHub 帳號登入**（推薦）
   - 這樣可以直接從 GitHub 部署
   - 或使用 Email 註冊也可以

---

### 步驟 2：準備 GitHub Repository

#### 選項 A：如果你還沒有 Git Repository

**在專案目錄執行：**

```bash
cd /Users/yangchenghan/news_parser

# 初始化 Git
git init

# 加入所有檔案
git add .

# 第一次提交
git commit -m "初始提交：Parser API 專案"

# 在 GitHub 建立新 repository
# 1. 訪問 https://github.com/new
# 2. Repository name: news_parser
# 3. 設為 Private（建議）
# 4. 不要勾選 "Initialize this repository with a README"
# 5. 點擊 "Create repository"

# 連接到 GitHub（替換成你的 username）
git remote add origin https://github.com/你的username/news_parser.git
git branch -M main
git push -u origin main
```

#### 選項 B：如果你已有 Git Repository

```bash
cd /Users/yangchenghan/news_parser

# 確認所有新檔案都已加入
git add .
git commit -m "準備 Railway 部署"
git push
```

---

### 步驟 3：在 Railway 建立專案

1. **登入 Railway 後，點擊「New Project」**

2. **選擇「Deploy from GitHub repo」**

3. **授權 Railway 訪問 GitHub**
   - 點擊「Configure GitHub App」
   - 選擇你的 Repository（news_parser）
   - 點擊「Install & Authorize」

4. **選擇 Repository**
   - 找到並點擊 `news_parser`

5. **Railway 會自動開始部署！** 🎉

---

### 步驟 4：等待部署完成

**你會看到部署進度：**

```
✓ Building...
✓ Installing dependencies...
✓ Starting application...
✓ Deployment successful!
```

**大約 1-2 分鐘後完成。**

---

### 步驟 5：獲取公開 URL

1. **在 Railway 專案頁面，點擊你的服務**

2. **點擊「Settings」標籤**

3. **向下滾動找到「Networking」區域**

4. **點擊「Generate Domain」**

5. **複製產生的 URL**，例如：
   ```
   https://news-parser-production.up.railway.app
   ```

---

### 步驟 6：測試部署

**在瀏覽器測試：**

```
https://你的railway網址.railway.app
```

應該看到 API 資訊！

**測試 API：**

```bash
curl https://你的railway網址.railway.app/api/parse?url=https://www.bbc.com/news
```

---

### 步驟 7：在 n8n 中使用

**在 n8n 的 HTTP Request 節點，把 URL 改成：**

```
https://你的railway網址.railway.app/api/parse
```

**JSON Body 保持：**
```json
{
  "url": "{{ $json.url_rss }}"
}
```

**點擊「Execute step」** → ✅ 成功！

---

## 🎯 完整設定範例

### n8n HTTP Request 節點設定

```
Method: POST
URL: https://news-parser-production.up.railway.app/api/parse
Authentication: None

Body Content Type: JSON
Specify Body: json

JSON:
{
  "url": "{{ $json.url_rss }}"
}
```

---

## 📊 監控與管理

### 查看日誌

1. 在 Railway 專案頁面
2. 點擊「Deployments」標籤
3. 點擊最新的部署
4. 查看即時日誌

### 查看使用量

1. 點擊「Usage」標籤
2. 查看本月使用時間和費用

### 重新部署

**方法 1：從 GitHub 自動部署**
```bash
# 修改程式碼後
git add .
git commit -m "更新功能"
git push
# Railway 會自動重新部署！
```

**方法 2：手動重新部署**
1. 在 Railway 專案頁面
2. 點擊「Deployments」
3. 點擊「Redeploy」

---

## 🔧 進階設定（選用）

### 設定環境變數

如果未來需要設定環境變數：

1. 點擊「Variables」標籤
2. 點擊「New Variable」
3. 加入變數（例如 API_KEY）

### 自訂網域

如果你有自己的網域：

1. 點擊「Settings」
2. 在「Networking」區域
3. 點擊「Custom Domain」
4. 輸入你的網域
5. 設定 DNS CNAME 記錄

---

## ⚠️ 注意事項

### 免費額度

- Railway 提供 **$5/月 免費額度**
- 約 500 小時執行時間
- 對於你的使用量應該足夠（或稍微超出一點）

### 監控使用量

建議每週檢查一次使用量：
1. 登入 Railway
2. 點擊右上角頭像
3. 選擇「Account」
4. 查看「Usage」

### 如果超過免費額度

- 會收到 Email 通知
- 可以升級到付費方案（$5/月起）
- 或改用 Render 免費方案

---

## 🎉 部署後測試清單

部署完成後，測試這些端點：

- [ ] **首頁**
  ```
  https://你的網址.railway.app/
  ```

- [ ] **API 文件（Swagger UI）**
  ```
  https://你的網址.railway.app/docs
  ```

- [ ] **健康檢查**
  ```
  https://你的網址.railway.app/health
  ```

- [ ] **解析測試**
  ```bash
  curl -X POST https://你的網址.railway.app/api/parse \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.bbc.com/news"}'
  ```

- [ ] **n8n 整合測試**
  - 在 n8n 更新 URL
  - 執行 workflow
  - 確認解析成功

---

## 🐛 問題排除

### 部署失敗

**檢查 Railway 日誌：**
1. 點擊「Deployments」
2. 點擊失敗的部署
3. 查看錯誤訊息

**常見問題：**
- ❌ `requirements.txt` 格式錯誤
- ❌ Python 版本不符
- ❌ 套件安裝失敗

**解決方式：**
```bash
# 確保 requirements.txt 正確
pip freeze > requirements.txt
git add requirements.txt
git commit -m "更新 requirements.txt"
git push
```

### 應用無法啟動

**檢查日誌中的錯誤**

**常見原因：**
- PORT 環境變數問題（已修正）
- 套件依賴問題

### API 回應慢

- Railway 免費方案資源有限
- 考慮升級到付費方案
- 或優化程式碼效能

---

## 📚 有用的連結

- **Railway 文件**: https://docs.railway.app
- **Railway 社群**: https://discord.gg/railway
- **專案 GitHub**: https://github.com/你的username/news_parser
- **FastAPI 文件**: https://fastapi.tiangolo.com

---

## 🎯 下一步

部署成功後：

1. ✅ 在 n8n 更新 API URL
2. ✅ 測試完整的 workflow
3. ✅ 監控 Railway 使用量
4. ✅ 享受自動化！🎉

---

**需要幫助？隨時回來查看這份指南！**

