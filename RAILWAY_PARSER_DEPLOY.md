# 🚀 Parser API 部署到 Railway Pro 指南

## 📋 部署準備清單

### ✅ 已完成的準備工作

- [x] 記憶體優化（減少 48% 使用量）
- [x] 並發控制（Semaphore 限制）
- [x] 本地測試驗證（87% 成功率，156/180）
- [x] 配置文件更新
- [x] requirements.txt 更新（兼容最新 Python）

---

## 🎯 部署步驟

### 步驟 1：提交代碼到 Git

```bash
cd /Users/yangchenghan/news_parser

# 查看變更
git status

# 添加優化版本的文件
git add parser-server.py
git add requirements.txt
git add railway.json
git add Procfile
git add Dockerfile
git add MEMORY_OPTIMIZATION_CHANGELOG.md
git add RAILWAY_PARSER_DEPLOY.md

# 提交
git commit -m "feat: 部署記憶體優化版 Parser API to Railway Pro

- 記憶體優化: 減少 48% Playwright 記憶體使用
- 並發控制: Semaphore(1) 防止記憶體溢出
- 版本: v1.6.0
- 測試驗證: 87% 成功率 (156/180)
"

# 推送到 GitHub
git push origin main
```

---

### 步驟 2：在 Railway 創建新服務

#### 選項 A：使用 Railway Dashboard（推薦）

1. **訪問 Railway Dashboard**
   ```
   https://railway.app/dashboard
   ```

2. **創建新專案或選擇現有專案**
   - 點擊 "New Project"
   - 或選擇現有的專案

3. **添加新服務**
   - 點擊 "+ New Service"
   - 選擇 "GitHub Repo"
   - 選擇 `news_parser` repository
   - 選擇 `main` branch

4. **升級到 Pro 方案**
   - 在專案設置中
   - 選擇 "Pro" plan
   - 確認升級（$20/月）

5. **設置環境變數（如果需要）**
   - 點擊服務 → "Variables"
   - 目前不需要額外變數
   - Railway 會自動提供 `PORT`

6. **部署**
   - Railway 會自動檢測 Dockerfile
   - 開始構建和部署
   - 等待部署完成（約 5-10 分鐘）

---

#### 選項 B：使用 Railway CLI

```bash
# 安裝 Railway CLI（如果還沒安裝）
npm install -g @railway/cli

# 登入
railway login

# 初始化專案
railway init

# 連結到現有專案或創建新專案
railway link

# 部署
railway up
```

---

### 步驟 3：驗證部署

#### 1. 獲取部署 URL

在 Railway Dashboard 中：
- 點擊服務
- 查看 "Deployments" 標籤
- 找到 "Domain"（例如：`your-service.up.railway.app`）

#### 2. 測試健康檢查

```bash
curl https://your-service.up.railway.app/health
```

**應該看到：**
```json
{
  "status": "healthy",
  "version": "1.6.0",
  "features": [
    ...
    "memory-optimized",
    "concurrency-control"
  ]
}
```

#### 3. 測試解析功能

```bash
curl -X POST https://your-service.up.railway.app/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://technews.tw/2024/11/14/tsmc-arizona-expansion/"}'
```

---

### 步驟 4：更新 n8n 配置

**在 n8n HTTP Request (Parser) 節點：**

**從：**
```
https://overhomely-hintingly-maxima.ngrok-free.dev/api/parse
```

**改成：**
```
https://your-service.up.railway.app/api/parse
```

---

### 步驟 5：測試 n8n Workflow

1. 執行單筆測試
2. 執行 10 筆小規模測試
3. 執行完整的 180 筆測試
4. 觀察 Railway 的資源使用

---

## 📊 監控和維護

### 查看部署日誌

**在 Railway Dashboard：**
- 服務 → "Deployments"
- 點擊最新的部署
- 查看 "Logs"

**應該看到：**
```
[Playwright] 啟動瀏覽器（記憶體優化版）...
[Playwright] 🔒 獲取執行權限
[Playwright] ✅ 成功獲取內容
[Playwright] 🔒 瀏覽器已關閉，記憶體已釋放
```

### 監控資源使用

**在 Railway Dashboard：**
- 服務 → "Metrics"
- 查看：
  - Memory Usage（記憶體使用）
  - CPU Usage（CPU 使用）
  - Request Count（請求數量）
  - Response Time（響應時間）

### 預期資源使用

```
Memory（記憶體）:
├─ 基礎: ~100 MB
├─ 處理中（Playwright）: ~300 MB
├─ 峰值: ~400 MB
└─ Railway Pro 限制: 32 GB ✅ 綽綽有餘

CPU:
├─ 閒置: 0-5%
├─ 處理中: 20-50%
└─ 峰值: 70-80%

請求響應時間:
├─ 靜態網站: 2-4 秒
├─ 動態網站: 5-8 秒
└─ 複雜網站: 8-12 秒
```

---

## ⚠️ 故障排除

### 問題 1：部署失敗（構建錯誤）

**可能原因：**
- Playwright 安裝失敗
- 系統依賴缺失

**解決方法：**
```bash
# 檢查 Dockerfile 是否包含所有系統依賴
# 重新部署
railway up --detach
```

### 問題 2：運行時錯誤（OOM）

**可能原因：**
- 並發過高
- 某些網站消耗過多記憶體

**解決方法：**
- 檢查 Semaphore 是否設為 1
- 檢查日誌找出問題網站
- 將問題網站加入黑名單

### 問題 3：解析失敗率高

**可能原因：**
- 網路問題
- Playwright 超時

**解決方法：**
- 檢查 Railway 的網路連接
- 增加 Playwright 超時設定
- 檢查特定網站的問題

### 問題 4：n8n 無法連接

**可能原因：**
- URL 錯誤
- Railway 服務未啟動

**解決方法：**
- 確認 Railway URL 正確
- 檢查 Railway 服務狀態
- 測試健康檢查端點

---

## 🎯 優化建議

### 如果記憶體充足，可以提升並發

**在 parser-server.py 修改：**

```python
# 從
playwright_semaphore = Semaphore(1)

# 改成（如果 Railway Pro 資源充足）
playwright_semaphore = Semaphore(3)  # 同時 3 個 Playwright
```

**效果：**
- 處理速度提升 3 倍
- 記憶體峰值增加到 ~900 MB
- Railway Pro (32 GB) 完全沒問題

---

## 📞 需要幫助？

### Railway 支援

- Dashboard: https://railway.app/dashboard
- 文檔: https://docs.railway.app
- Discord: https://discord.gg/railway

### 本專案文檔

- 優化說明: `MEMORY_OPTIMIZATION_CHANGELOG.md`
- 快速指南: `QUICK_START.md`
- 測試腳本: `test-memory-optimization.py`

---

## ✅ 部署檢查清單

- [ ] 代碼已推送到 GitHub
- [ ] Railway 專案已創建
- [ ] 已升級到 Pro 方案
- [ ] 服務已成功部署
- [ ] 健康檢查通過
- [ ] 解析功能測試通過
- [ ] n8n URL 已更新
- [ ] 完整 workflow 測試通過
- [ ] 資源使用在正常範圍
- [ ] 日誌顯示優化功能生效

---

**🎉 部署完成！享受 24/7 自動化的 Parser API！**

