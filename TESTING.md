# Testing Guide - Sneaker Store Microservices

## Manual API Testing

### 1. Health Checks

```bash
# API Gateway health
curl http://localhost:8000/health

# Auth Service health
curl http://localhost:8001/health

# Product Service health
curl http://localhost:8002/health

# Raffle Service health
curl http://localhost:8003/health
```

### 2. Authentication Flow

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "TestPassword123"
  }'

# Login and get JWT token
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123"
  }')

# Extract token (Linux/Mac)
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

# Get user profile
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Product Management

```bash
# List all products (public endpoint)
curl -X GET "http://localhost:8000/api/products?skip=0&limit=10"

# Get specific product
curl -X GET http://localhost:8000/api/products/{product_id}

# Create product (admin only - requires TOKEN)
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Air Force 1",
    "brand": "Nike",
    "size": "10",
    "price": 110.00,
    "stock": 100,
    "drop_timestamp": "2024-12-31T18:00:00Z",
    "description": "Classic Nike Air Force 1"
  }'

# Update product (admin only)
curl -X PUT http://localhost:8000/api/products/{product_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "stock": 50,
    "price": 105.00
  }'

# Delete product (admin only)
curl -X DELETE http://localhost:8000/api/products/{product_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Raffle Functionality

```bash
# Enter raffle (requires JWT token and must wait until drop time)
curl -X POST http://localhost:8000/api/raffle/enter-raffle \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "shoe_size": "10"
  }'

# Get raffle statistics
curl -X GET http://localhost:8000/api/raffle/raffle-stats
```

## Load Testing with Locust

### Option 1: Web UI (Recommended for Visualization)

```bash
# Start load tester with web UI
docker-compose up -d load-tester

# Open browser and navigate to:
# http://localhost:8089

# In the UI:
# 1. Number of users to simulate: 5000
# 2. Spawn rate (users/sec): 100
# 3. Host: http://api-gateway:8000
# 4. Click "Start swarming"
```

### Option 2: Headless Testing (Batch)

```bash
# Run 5000 users for 5 minutes
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 5000 \
  -r 100 \
  --run-time 5m \
  --headless \
  --csv=results

# Results will be saved in CSV format
docker-compose exec load-tester ls -la results/
```

### Option 3: Custom Load Profile

```bash
# Progressive load test (gradual increase)
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 1000 \
  -r 50 \
  --run-time 10m \
  --headless

# Spike test (sudden load)
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 10000 \
  -r 500 \
  --run-time 2m \
  --headless
```

## Database Testing

### PostgreSQL (Auth & Order Databases)

```bash
# Connect to Auth DB
docker-compose exec auth-db psql -U authuser -d authdb

# Useful queries:
SELECT * FROM users;
SELECT COUNT(*) FROM users;

# Connect to Order DB
docker-compose exec order-db psql -U orderuser -d orderdb

# Check winners table
SELECT * FROM winners LIMIT 10;
SELECT COUNT(*) as total_winners FROM winners WHERE status='won';
```

### MongoDB (Product Database)

```bash
# Connect to MongoDB
docker-compose exec product-db mongosh -u root -p password

# In mongo shell:
use productdb
db.products.find()
db.products.find().count()
db.products.findOne()
```

### Redis (Raffle Queue)

```bash
# Connect to Redis
docker-compose exec redis-broker redis-cli

# Useful commands:
LLEN raffle_queue          # Queue length
LRANGE raffle_queue 0 10   # View first 10 entries
GET raffle_total_entries   # Total entries received
FLUSHALL                   # Clear all data (be careful!)
```

## Performance Testing Scenarios

### Scenario 1: Pre-Drop Warm-up
```bash
# Light load 1 hour before drop
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 100 \
  -r 10 \
  --run-time 60m \
  --headless
```

### Scenario 2: Drop Event (Extreme Load)
```bash
# Massive load during actual drop
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 5000 \
  -r 500 \
  --run-time 30m \
  --headless
```

### Scenario 3: Post-Drop Cooldown
```bash
# Gradual load decrease after drop
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 500 \
  -r 50 \
  --run-time 30m \
  --headless
```

## Performance Metrics to Monitor

### During Load Test

1. **Response Time (p50, p95, p99)**
   - Target: p50 < 100ms, p95 < 500ms, p99 < 1000ms

2. **Error Rate**
   - Target: < 0.1%

3. **Requests per Second (RPS)**
   - Monitor sustainable RPS

4. **Connection Pool Utilization**
   - Ensure no pool exhaustion

### Resource Utilization

```bash
# Monitor container stats during test
docker stats

# Specific service
docker stats api-gateway raffle-service winner-worker
```

### Database Performance

```bash
# PostgreSQL active connections
docker-compose exec auth-db psql -U authuser -d authdb \
  -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# MongoDB connection status
docker-compose exec product-db mongosh -u root -p password \
  --eval "db.serverStatus().connections"

# Redis memory usage
docker-compose exec redis-broker redis-cli INFO memory
```

## Automated Testing Script

```bash
#!/bin/bash
# test-load.sh - Automated load testing

echo "Starting load test..."

# Register test users (optional)
for i in {1..10}; do
    curl -s -X POST http://localhost:8000/api/auth/register \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"loadtest$i@example.com\",
        \"username\": \"loadtest$i\",
        \"password\": \"LoadTest123\"
      }" > /dev/null &
done
wait

echo "Test users created. Starting load test..."

# Run load test
docker-compose exec -T load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 5000 \
  -r 100 \
  --run-time 10m \
  --headless \
  --csv=results/load_test_$(date +%Y%m%d_%H%M%S)

echo "Load test complete!"
```

## Troubleshooting Failed Tests

### High Error Rate

```bash
# Check API Gateway logs
docker-compose logs api-gateway --tail=100

# Check service health
docker-compose ps

# Test connectivity between services
docker-compose exec api-gateway ping raffle-service
docker-compose exec raffle-service ping redis-broker
```

### Slow Response Times

```bash
# Check Redis queue depth
docker-compose exec redis-broker redis-cli LLEN raffle_queue

# Check database connections
docker-compose exec order-db psql -U orderuser -d orderdb \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Check worker processing
docker-compose logs winner-worker --tail=50
```

### Connection Pool Exhaustion

```bash
# Restart affected service
docker-compose restart auth-service

# Scale workers (if supported)
docker-compose up -d --scale winner-worker=3
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Load Test

on:
  schedule:
    - cron: '0 22 * * 5'  # Every Friday at 10 PM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 30
      - name: Run load test
        run: |
          docker-compose exec -T load-tester locust \
            -f locustfile.py \
            --host=http://api-gateway:8000 \
            -u 5000 \
            -r 100 \
            --run-time 5m \
            --headless
      - name: Collect results
        if: always()
        run: docker cp load-tester:/app/results ./test-results/
```

---

For more information, see README.md
