#!/bin/bash

API_URL="https://web-production-32568.up.railway.app"

echo "=========================================="
echo "🚀 測試三個新聞網站的爬取功能"
echo "=========================================="
echo "API: $API_URL"
echo ""

# 檢查 API 狀態
echo "1️⃣ 檢查 API 狀態..."
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo "   ✅ API 運行正常"
else
    echo "   ❌ API 無法連接"
    exit 1
fi

echo ""
echo "=========================================="
echo "開始測試三個網站"
echo "=========================================="

# 測試 #1: MSN
echo ""
echo "📰 測試 #1: MSN - AMD 分析"
echo "=========================================="
RESPONSE=$(curl -s -X POST "$API_URL/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.msn.com/en-us/money/savingandinvesting/amd-s-results-and-guidance-were-good-but-wall-street-is-waiting-for-2026/ar-AA1PR5Qh?ocid=finance-verthp-feeds"}' \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP 200 - 請求成功"
    
    # 提取標題
    TITLE=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:80])" 2>/dev/null || echo "無法解析")
    WORD_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('word_count', 0))" 2>/dev/null || echo "0")
    
    echo "   標題: $TITLE"
    echo "   字數: $WORD_COUNT"
else
    echo "❌ HTTP $HTTP_CODE - 請求失敗"
    echo "$BODY" | head -n 3
fi

# 等待
sleep 2

# 測試 #2: Investing.com
echo ""
echo "📰 測試 #2: Investing.com - 裁員新聞"
echo "=========================================="
RESPONSE=$(curl -s -X POST "$API_URL/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.investing.com/news/stock-market-news/factboxus-companies-step-up-job-cuts-amid-uncertain-economy-4333313"}' \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP 200 - 請求成功"
    
    TITLE=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:80])" 2>/dev/null || echo "無法解析")
    WORD_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('word_count', 0))" 2>/dev/null || echo "0")
    
    echo "   標題: $TITLE"
    echo "   字數: $WORD_COUNT"
else
    echo "❌ HTTP $HTTP_CODE - 請求失敗"
    echo "$BODY" | head -n 3
fi

# 等待
sleep 2

# 測試 #3: Silicon Valley
echo ""
echo "📰 測試 #3: Silicon Valley - HPE & Hitachi 裁員"
echo "=========================================="
RESPONSE=$(curl -s -X POST "$API_URL/api/parse" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.siliconvalley.com/2025/11/05/economy-jobs-tech-layoff-hpe-hitachi-san-jose-south-bay-web-software/"}' \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP 200 - 請求成功"
    
    TITLE=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('title', '無標題')[:80])" 2>/dev/null || echo "無法解析")
    WORD_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('word_count', 0))" 2>/dev/null || echo "0")
    
    echo "   標題: $TITLE"
    echo "   字數: $WORD_COUNT"
else
    echo "❌ HTTP $HTTP_CODE - 請求失敗"
    echo "$BODY" | head -n 3
fi

echo ""
echo "=========================================="
echo "✨ 測試完成"
echo "=========================================="
