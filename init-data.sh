#!/bin/bash

# Sample data initialization script
# This script creates test data in the databases for development

set -e

API_GATEWAY="http://localhost:8000"
ADMIN_EMAIL="admin@sneaker.store"
ADMIN_PASSWORD="AdminPass123"

echo "Initializing sample data..."

# Function to retry curl requests
retry_curl() {
    local max_attempts=5
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if response=$(curl -s "$@"); then
            echo "$response"
            return 0
        fi
        echo "Attempt $attempt failed, retrying..." >&2
        attempt=$((attempt + 1))
        sleep 2
    done
    echo "Failed after $max_attempts attempts" >&2
    return 1
}

echo "Step 1: Register admin user..."
REGISTER_RESPONSE=$(retry_curl -X POST "$API_GATEWAY/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"username\": \"admin\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

echo "Registration response: $REGISTER_RESPONSE"

echo ""
echo "Step 2: Login as admin..."
LOGIN_RESPONSE=$(retry_curl -X POST "$API_GATEWAY/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"password\": \"$ADMIN_PASSWORD\"
  }")

echo "Login response: $LOGIN_RESPONSE"
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to obtain token"
    exit 1
fi

echo "Token obtained: ${TOKEN:0:20}..."

echo ""
echo "Step 3: Create sample sneaker products..."

# Create multiple products
PRODUCTS=(
    '{
        "name": "Air Max 90",
        "brand": "Nike",
        "size": "10",
        "price": 130.00,
        "stock": 50,
        "drop_timestamp": "2024-12-25T15:00:00Z",
        "description": "Classic Nike Air Max 90 in white and black"
    }'
    '{
        "name": "Jordan 1 Retro",
        "brand": "Jordan",
        "size": "11",
        "price": 170.00,
        "stock": 30,
        "drop_timestamp": "2024-12-26T12:00:00Z",
        "description": "Limited edition Jordan 1 Retro High OG"
    }'
    '{
        "name": "Yeezy 350",
        "brand": "Adidas",
        "size": "9",
        "price": 200.00,
        "stock": 25,
        "drop_timestamp": "2024-12-27T10:00:00Z",
        "description": "Adidas Yeezy Boost 350 V2 Zebra"
    }'
    '{
        "name": "Dunk Low",
        "brand": "Nike",
        "size": "10.5",
        "price": 110.00,
        "stock": 75,
        "drop_timestamp": "2024-12-28T14:00:00Z",
        "description": "Nike SB Dunk Low Pro"
    }'
)

for i in "${!PRODUCTS[@]}"; do
    echo "Creating product $((i+1))/${#PRODUCTS[@]}..."
    PRODUCT_RESPONSE=$(retry_curl -X POST "$API_GATEWAY/api/products" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "${PRODUCTS[$i]}")
    
    echo "Product created: $(echo $PRODUCT_RESPONSE | grep -o '"name":"[^"]*')"
done

echo ""
echo "Step 4: Register test users..."

# Create test users
for i in {1..5}; do
    EMAIL="user$i@example.com"
    echo "Registering user: $EMAIL"
    
    retry_curl -X POST "$API_GATEWAY/api/auth/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$EMAIL\",
        \"username\": \"user$i\",
        \"password\": \"UserPass123\"
      }" > /dev/null
done

echo ""
echo "Step 5: Fetch product list..."
PRODUCTS_LIST=$(retry_curl -X GET "$API_GATEWAY/api/products?limit=10")
PRODUCT_COUNT=$(echo "$PRODUCTS_LIST" | grep -o '"id"' | wc -l)
echo "Total products: $PRODUCT_COUNT"

echo ""
echo "✓ Sample data initialization complete!"
echo ""
echo "You can now:"
echo "1. Visit http://localhost:3000 to view the frontend"
echo "2. Login with admin account: admin@sneaker.store / AdminPass123"
echo "3. Access the admin dashboard at http://localhost:3000/dashboard"
echo "4. Test user credentials: user1@example.com - user5@example.com (password: UserPass123)"
echo "5. Run load tests with: docker-compose exec load-tester locust -f locustfile.py --host=http://api-gateway:8000"
