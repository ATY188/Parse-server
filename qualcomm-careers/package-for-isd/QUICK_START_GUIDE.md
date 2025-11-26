# Quick Start Guide / 快速入門指南

This guide will help you set up and run the Qualcomm Careers Scraper.

本指南將幫助您設置並運行 Qualcomm Careers 爬蟲。

---

## Prerequisites / 前置需求

- **Python 3.8+** installed on your computer
- **Internet connection** (to access Qualcomm Careers website)
- **Command line access** (Terminal on Mac/Linux, Command Prompt or PowerShell on Windows)

---

## Step-by-Step Instructions / 步驟說明

---

### Step 1: Verify Python Installation / 步驟 1：確認 Python 已安裝

**English:**
Open your terminal/command prompt and run:

**中文：**
打開終端機/命令提示字元，執行：

```bash
python --version
```

or / 或者

```bash
python3 --version
```

**Expected output / 預期輸出：**
```
Python 3.x.x
```

> ⚠️ If you see "command not found", please install Python first from https://www.python.org/downloads/
>
> ⚠️ 如果顯示 "command not found"，請先從 https://www.python.org/downloads/ 安裝 Python

---

### Step 2: Extract the ZIP File / 步驟 2：解壓縮 ZIP 檔案

**English:**
1. Download `qualcomm_careers_scraper_package.zip`
2. Extract it to a folder (e.g., `C:\qualcomm-scraper` on Windows or `~/qualcomm-scraper` on Mac/Linux)

**中文：**
1. 下載 `qualcomm_careers_scraper_package.zip`
2. 解壓縮到一個資料夾（例如：Windows 上的 `C:\qualcomm-scraper` 或 Mac/Linux 上的 `~/qualcomm-scraper`）

---

### Step 3: Navigate to the Folder / 步驟 3：進入資料夾

**English:**
Open terminal and navigate to the extracted folder:

**中文：**
打開終端機，進入解壓縮後的資料夾：

**Windows:**
```bash
cd C:\qualcomm-scraper\package-for-isd
```

**Mac/Linux:**
```bash
cd ~/qualcomm-scraper/package-for-isd
```

---

### Step 4: Install Dependencies / 步驟 4：安裝依賴套件

**English:**
Run the following command to install required Python packages:

**中文：**
執行以下命令安裝所需的 Python 套件：

```bash
pip install -r requirements.txt
```

or (if you have multiple Python versions) / 或者（如果您有多個 Python 版本）：

```bash
pip3 install -r requirements.txt
```

**Expected output / 預期輸出：**
```
Successfully installed pandas-x.x.x requests-x.x.x openpyxl-x.x.x
```

---

### Step 5: Test the Installation / 步驟 5：測試安裝

**English:**
Verify the scraper can run by checking the help message:

**中文：**
驗證爬蟲可以運行，查看說明訊息：

```bash
python qualcomm_careers_scraper.py --help
```

**Expected output / 預期輸出：**
```
usage: qualcomm_careers_scraper.py [-h] [--no-details] [--test] [--output OUTPUT] [--quiet]

Qualcomm Careers Scraper - Extract job listings from Qualcomm Careers website

options:
  -h, --help            show this help message and exit
  --no-details          Skip fetching job details (faster, but less data)
  --test                Test mode - only fetch details for first 10 jobs
  --output OUTPUT, -o OUTPUT
                        Output Excel filename
  --quiet, -q           Quiet mode - suppress progress messages
```

✅ **If you see this output, the installation is successful!**

✅ **如果您看到這個輸出，表示安裝成功！**

---

### Step 6: Run a Quick Test / 步驟 6：執行快速測試

**English:**
Run a quick test to make sure everything works:

**中文：**
執行快速測試，確保一切正常：

```bash
python qualcomm_careers_scraper.py --test
```

**What this does / 這會做什麼：**
- Fetches all job listings (~1,300 jobs) / 獲取所有職缺列表（約 1,300 個）
- Fetches details for only 10 jobs (to save time) / 只獲取 10 個職缺的詳情（節省時間）
- Creates output files / 創建輸出檔案

**Expected runtime / 預期執行時間：** ~3-5 minutes / 約 3-5 分鐘

**Output files / 輸出檔案：**
- `qualcomm_careers_YYYYMMDD_HHMMSS.xlsx`
- `qualcomm_careers_YYYYMMDD_HHMMSS.json`

---

### Step 7: Run Full Scrape (Production) / 步驟 7：執行完整爬取（正式）

**English:**
Once the test is successful, run the full scrape:

**中文：**
測試成功後，執行完整爬取：

```bash
python qualcomm_careers_scraper.py
```

**Expected runtime / 預期執行時間：** ~10-15 minutes / 約 10-15 分鐘

**What you'll get / 您將獲得：**
- All job listings with full details / 所有職缺及完整詳情
- Excel file with structured data / 結構化的 Excel 檔案

---

## Command Options Summary / 命令選項總結

| Command | Description (EN) | 說明 (中文) | Time |
|---------|------------------|-------------|------|
| `python qualcomm_careers_scraper.py` | Full scrape | 完整爬取 | ~15 min |
| `python qualcomm_careers_scraper.py --test` | Test mode (10 details) | 測試模式 | ~3 min |
| `python qualcomm_careers_scraper.py --no-details` | List only | 僅列表 | ~2 min |
| `python qualcomm_careers_scraper.py -o output.xlsx` | Custom filename | 自訂檔名 | - |

---

## Troubleshooting / 問題排解

### Problem: "python not found" / 問題："python 找不到"

**Solution / 解決方案：**
- Try `python3` instead of `python`
- 試試用 `python3` 代替 `python`

### Problem: "pip not found" / 問題："pip 找不到"

**Solution / 解決方案：**
- Try `pip3` instead of `pip`
- 試試用 `pip3` 代替 `pip`
- Or use: `python -m pip install -r requirements.txt`
- 或使用：`python -m pip install -r requirements.txt`

### Problem: Connection timeout / 問題：連線逾時

**Solution / 解決方案：**
- Check your internet connection / 檢查網路連線
- Try again later / 稍後再試
- Check if Qualcomm website is accessible / 確認 Qualcomm 網站可以訪問

### Problem: Permission denied / 問題：權限被拒絕

**Solution / 解決方案：**
- On Mac/Linux, try: `pip install --user -r requirements.txt`
- 在 Mac/Linux 上，試試：`pip install --user -r requirements.txt`

---

## Output File Explanation / 輸出檔案說明

The Excel file contains these columns / Excel 檔案包含以下欄位：

| Column | Description (EN) | 說明 (中文) |
|--------|------------------|-------------|
| `job_id` | Unique job ID | 職缺 ID |
| `title` | Job title | 職缺名稱 |
| `url` | Link to job posting | 職缺連結 |
| `department` | Department/Category | 部門/類別 |
| `location` | Full location | 完整地點 |
| `country` | Country | 國家 |
| `work_type` | onsite/remote/hybrid | 工作類型 |
| `company` | Company entity | 公司實體 |
| `job_area` | Job function area | 職能領域 |
| `general_summary` | Job overview | 職缺概述 |
| `responsibilities` | Job duties | 工作職責 |
| `minimum_qualifications` | Required qualifications | 最低資格要求 |
| `preferred_qualifications` | Nice-to-have skills | 優先條件 |

---

## Need Help? / 需要幫助？

Contact your IT team lead if you encounter any issues.

如有任何問題，請聯繫您的 IT 團隊負責人。

---

*Document Version: 1.0 | Last Updated: November 2024*

