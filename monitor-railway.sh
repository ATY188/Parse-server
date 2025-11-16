#!/bin/bash
# Railway Decoder API 監控腳本

API_URL="https://web-production-32568.up.railway.app"

echo "======================================"
echo "🔍 Railway Decoder API 監控"
echo "======================================"
echo ""

# 1. 檢查健康狀態
echo "1️⃣ 健康檢查..."
HEALTH=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>&1)
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
RESPONSE=$(echo "$HEALTH" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 服務健康"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "❌ 服務異常 (HTTP $HTTP_CODE)"
    echo "$RESPONSE"
fi

echo ""
echo "======================================"

# 2. 測試 Decoder API
echo "2️⃣ 測試 URL 解碼功能..."
TEST_URL="https://www.google.com/url?url=https://news.cnyes.com/news/id/6238949&sa=X"

DECODE_RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/decode-google-url" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"$TEST_URL\"}" 2>&1)

DECODE_HTTP_CODE=$(echo "$DECODE_RESULT" | tail -n1)
DECODE_RESPONSE=$(echo "$DECODE_RESULT" | head -n-1)

if [ "$DECODE_HTTP_CODE" = "200" ]; then
    echo "✅ 解碼功能正常"
    echo "$DECODE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DECODE_RESPONSE"
else
    echo "❌ 解碼功能異常 (HTTP $DECODE_HTTP_CODE)"
    echo "$DECODE_RESPONSE"
fi

echo ""
echo "======================================"

# 3. 測試 5 次請求並計算平均響應時間
echo "3️⃣ 效能測試（5次請求）..."
TOTAL_TIME=0
SUCCESS_COUNT=0

for i in {1..5}; do
    START=$(date +%s%3N)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
    END=$(date +%s%3N)
    
    ELAPSED=$((END - START))
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   第 $i 次: ✅ ${ELAPSED}ms"
        TOTAL_TIME=$((TOTAL_TIME + ELAPSED))
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "   第 $i 次: ❌ HTTP $HTTP_CODE"
    fi
    
    sleep 0.5
done

if [ $SUCCESS_COUNT -gt 0 ]; then
    AVG_TIME=$((TOTAL_TIME / SUCCESS_COUNT))
    echo ""
    echo "📊 平均響應時間: ${AVG_TIME}ms"
    echo "✅ 成功率: $SUCCESS_COUNT/5"
fi

echo ""
echo "======================================"
echo "💡 更詳細的資源監控請前往："
echo "   https://railway.app/project/9b847907-61fc-4274-9613-80e3880831be"
echo "======================================"

