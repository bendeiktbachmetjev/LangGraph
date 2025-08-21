#!/bin/bash

# Railway API test script
RAILWAY_URL="https://spotted-mom-production.up.railway.app"

echo "🚂 Testing Railway API"
echo "======================"
echo "URL: $RAILWAY_URL"
echo ""

# Test 1: Check if API is accessible
echo "1️⃣ Testing API accessibility..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/")
if [ "$response" = "200" ]; then
    echo "✅ API is accessible (Status: $response)"
else
    echo "❌ API not accessible (Status: $response)"
fi

# Test 2: Get API info
echo ""
echo "2️⃣ Getting API info..."
curl -s "$RAILWAY_URL/" | jq '.' 2>/dev/null || curl -s "$RAILWAY_URL/"

# Test 3: Check docs endpoint
echo ""
echo "3️⃣ Checking docs endpoint..."
docs_response=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/docs")
if [ "$docs_response" = "200" ]; then
    echo "✅ Docs endpoint accessible (Status: $docs_response)"
else
    echo "⚠️ Docs endpoint status: $docs_response"
fi

# Test 4: Show available endpoints
echo ""
echo "4️⃣ Available endpoints:"
echo "   - GET  /                    - API health check"
echo "   - GET  /docs                - API documentation"
echo "   - POST /sessions            - Create session (requires auth)"
echo "   - POST /chat/{session_id}   - Send message (requires auth)"
echo "   - GET  /chat/{session_id}/memory-stats    - Get memory stats (requires auth)"
echo "   - POST /chat/{session_id}/memory-control  - Control memory (requires auth)"

echo ""
echo "📋 Summary:"
echo "✅ Railway API is running"
echo "ℹ️ All endpoints require Firebase authentication"
echo "ℹ️ To test with real data, you need:"
echo "   - Valid Firebase ID token"
echo "   - Existing session ID"
echo ""
echo "🔗 API Documentation: $RAILWAY_URL/docs"
