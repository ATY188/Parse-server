#!/bin/bash

# 快速測試 API 解析功能
# 使用方法：
# 1. 先啟動伺服器：python3 parser-server.py
# 2. 在另一個終端機執行：bash test-api-quick.sh

echo "========================================="
echo "🧪 測試 API 解析功能"
echo "========================================="
echo ""

# 檢查伺服器是否運行
echo "1️⃣ 檢查伺服器狀態..."
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "   ✅ 伺服器正在運行"
else
    echo "   ❌ 伺服器未運行"
    echo "   請先啟動：python3 parser-server.py"
    exit 1
fi

echo ""
echo "2️⃣ 測試 Google URL 解碼 API..."
echo ""

# 測試 Google URL 解碼
echo "   測試 URL #1 (Google Alert)"
curl -s -X POST http://localhost:3000/api/decode-google-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/url?rct=j&sa=t&url=https://today.line.me/tw/v3/article/Kwz9VmN&ct=ga&cd=CAIyHTg2OTkxMDIwNjE2OTIzMzQ6Y29tOnpoLVRXOlVT&usg=AOvVaw1vlpkBTJSkbO0O5X1vazCf"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('   ✅ 解碼成功' if data.get('success') else '   ❌ 解碼失敗'); print(f\"   原始: {data.get('original_url', '')[:60]}...\"); print(f\"   解碼: {data.get('decoded_url', '')}\")"

echo ""
echo "3️⃣ 測試文章解析 API（解碼後的 URL）..."
echo ""

# 測試 #1: LINE Today (中文)
echo "   測試 #1: LINE Today（中文新聞）"
response=$(curl -s -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://today.line.me/tw/v3/article/Kwz9VmN"}')

if echo "$response" | grep -q '"success": true'; then
    echo "   ✅ 解析成功"
    title=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:50])" 2>/dev/null || echo "無法取得標題")
    echo "   標題: $title"
else
    echo "   ⚠️ 解析失敗或無內容"
fi

echo ""

# 測試 #2: 鉅亨網 (中文財經)
echo "   測試 #2: 鉅亨網（中文財經新聞）"
response=$(curl -s -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.cnyes.com/news/id/6215159"}')

if echo "$response" | grep -q '"success": true'; then
    echo "   ✅ 解析成功"
    title=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:50])" 2>/dev/null || echo "無法取得標題")
    echo "   標題: $title"
else
    echo "   ⚠️ 解析失敗或無內容"
fi

echo ""

# 測試 #3: 英文新聞
echo "   測試 #3: SiliconAngle（英文科技新聞）"
response=$(curl -s -X POST http://localhost:3000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://siliconangle.com/2025/11/05/qualcomm-arm-beat-expectations-investors-reactions-mixed/"}')

if echo "$response" | grep -q '"success": true'; then
    echo "   ✅ 解析成功"
    title=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:50])" 2>/dev/null || echo "無法取得標題")
    echo "   標題: $title"
else
    echo "   ⚠️ 解析失敗或無內容"
fi

echo ""
echo "========================================="
echo "✨ 測試完成！"
echo "========================================="
echo ""
echo "📊 測試總結："
echo "   • Google URL 解碼功能：已測試"
echo "   • 文章解析功能：已測試 3 個網站"
echo "   • 中文網站：2 個"
echo "   • 英文網站：1 個"
echo ""
echo "💡 如果上面都顯示 ✅，就可以安全部署了！"
echo ""

