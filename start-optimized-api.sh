#!/bin/bash

echo "🔄 準備啟動優化版 Parser API..."
echo ""

# 切換到專案目錄
cd /Users/yangchenghan/news_parser

# 檢查並停止舊進程
echo "1️⃣ 檢查並停止舊進程..."
OLD_PID=$(ps aux | grep "parser-server.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$OLD_PID" ]; then
    echo "   找到舊進程 PID: $OLD_PID，正在停止..."
    kill $OLD_PID
    sleep 2
    echo "   ✅ 已停止"
else
    echo "   ✅ 沒有舊進程"
fi

# 清理 Python 快取
echo ""
echo "2️⃣ 清理 Python 快取..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
echo "   ✅ 快取已清理"

# 確認文件版本
echo ""
echo "3️⃣ 確認 parser-server.py 版本..."
VERSION=$(grep "version.*1.6.0" parser-server.py)
if [ ! -z "$VERSION" ]; then
    echo "   ✅ 版本 1.6.0 (優化版)"
else
    echo "   ⚠️  警告：可能不是優化版"
fi

# 啟動 API
echo ""
echo "4️⃣ 啟動 Parser API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查是否在虛擬環境中
if [ ! -z "$VIRTUAL_ENV" ]; then
    echo "✅ 虛擬環境已啟用: $VIRTUAL_ENV"
elif [ -d "venv" ]; then
    echo "🔄 啟用虛擬環境..."
    source venv/bin/activate
else
    echo "⚠️  沒有虛擬環境，使用系統 Python"
fi

echo ""
echo "🚀 正在啟動..."
echo ""

# 啟動 API
python parser-server.py

