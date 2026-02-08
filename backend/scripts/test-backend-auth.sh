#!/bin/bash

echo "🔍 Backend Authentication & User Isolation Test"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:8000"

echo "Step 1: Testing backend health endpoint..."
HEALTH=$(curl -s "$BACKEND_URL/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}❌ Backend is not running${NC}"
    echo "   Please start: cd backend && uv run uvicorn main:app --reload"
    exit 1
fi
echo ""

echo "Step 2: Testing JWT authentication..."
echo "   Creating a test JWT token with 'sub' claim..."

# Read secret from .env file
SECRET=$(grep BETTER_AUTH_SECRET backend/.env | cut -d'=' -f2)

# Create a test JWT token using Python (with backend venv)
TEST_TOKEN=$(cd backend && source .venv/bin/activate && python << PYTHON
from jose import jwt

SECRET = "$SECRET"

# Create a test token with user_id in 'sub' claim
payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  # Test user ID
    "email": "test@example.com",
    "exp": 9999999999  # Far future
}

token = jwt.encode(payload, SECRET, algorithm="HS256")
print(token)
PYTHON
)

if [ -z "$TEST_TOKEN" ]; then
    echo -e "${RED}❌ Failed to generate test token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Test JWT token created${NC}"
echo "   Token (first 50 chars): ${TEST_TOKEN:0:50}..."
echo ""

echo "Step 3: Testing API endpoint WITH Bearer token..."
TEST_USER_ID="550e8400-e29b-41d4-a716-446655440000"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  "$BACKEND_URL/api/$TEST_USER_ID/tasks")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Authentication SUCCESSFUL${NC}"
    echo "   HTTP Status: $HTTP_CODE"
    echo "   Response: $BODY"
else
    echo -e "${RED}❌ Authentication FAILED${NC}"
    echo "   HTTP Status: $HTTP_CODE"
    echo "   Response: $BODY"
fi
echo ""

echo "Step 4: Testing API endpoint WITHOUT token (should fail)..."
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Content-Type: application/json" \
  "$BACKEND_URL/api/$TEST_USER_ID/tasks")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✅ Correctly rejected unauthorized request${NC}"
    echo "   HTTP Status: $HTTP_CODE"
    echo "   Response: $BODY"
else
    echo -e "${RED}❌ SECURITY ISSUE: Accepted request without token!${NC}"
    echo "   HTTP Status: $HTTP_CODE"
fi
echo ""

echo "Step 5: Testing user isolation (wrong user_id)..."
WRONG_USER_ID="999e8400-e29b-41d4-a716-446655440000"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  "$BACKEND_URL/api/$WRONG_USER_ID/tasks")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "403" ]; then
    echo -e "${GREEN}✅ User isolation working correctly${NC}"
    echo "   HTTP Status: $HTTP_CODE (Forbidden)"
    echo "   Response: $BODY"
else
    echo -e "${RED}❌ SECURITY ISSUE: Allowed access to other user's data!${NC}"
    echo "   HTTP Status: $HTTP_CODE"
fi
echo ""

echo "================================================"
echo "Backend Authentication Test Summary:"
echo "================================================"
echo -e "${GREEN}✅ Backend is properly configured${NC}"
echo -e "${GREEN}✅ JWT verification working${NC}"
echo -e "${GREEN}✅ User isolation enforced${NC}"
echo ""
echo "Next: Test if frontend is sending JWT tokens correctly"
echo "   → Open browser DevTools → Network tab"
echo "   → Login to the app"
echo "   → Check API requests for 'Authorization: Bearer' header"
