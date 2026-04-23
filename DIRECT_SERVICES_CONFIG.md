# Direct Service Architecture - Updated Configuration

## Environment Variables for Direct Service Access

Update your `.env` file with the new service URLs for the frontend:

```env
# Frontend Service URLs (direct access, no gateway)
REACT_APP_AUTH_SERVICE_URL=http://localhost:8001
REACT_APP_PRODUCT_SERVICE_URL=http://localhost:8002
REACT_APP_RAFFLE_SERVICE_URL=http://localhost:8003

# Services still use internal hostnames (Docker network)
AUTH_SERVICE_URL=http://auth-service:8001
PRODUCT_SERVICE_URL=http://product-service:8002
RAFFLE_SERVICE_URL=http://raffle-service:8003
```

## CORS Configuration Reference

Each FastAPI service now includes this CORS configuration:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development
        "http://127.0.0.1:3000",           # Localhost variant
        "http://localhost",                 # Simplified localhost
        "http://frontend:3000"              # Docker Compose hostname
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Customizing CORS Origins

To add additional allowed origins (e.g., production domain), modify the service's main.py:

**auth-service/main.py:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://yourdomain.com",  # Add your domain
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Apply the same change to `product-service/main.py` and `raffle-service/main.py`.

## Testing the Updated Architecture

### 1. Health Checks
```bash
# Test each service health endpoint
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "timestamp": "2024-04-23T10:30:45.123456"
}
```

### 2. Authentication Flow
```bash
# Register user
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "Password123"
  }'

# Login
TOKEN=$(curl -s -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123"
  }' | jq -r '.access_token')

# Get profile
curl http://localhost:8001/profile \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Product Service
```bash
# List products (no auth required)
curl http://localhost:8002/products

# Create product (requires admin token)
curl -X POST http://localhost:8002/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Air Max 90",
    "brand": "Nike",
    "size": "10",
    "price": 130.00,
    "stock": 50
  }'
```

### 4. Raffle Service
```bash
# Get raffle stats (no auth required)
curl http://localhost:8003/raffle-stats

# Enter raffle (requires auth token)
curl -X POST http://localhost:8003/enter-raffle \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"shoe_size": "10"}'
```

### 5. Frontend Integration
```bash
# Frontend running on port 3000
# Automatically connects to:
# - Auth Service: http://localhost:8001
# - Product Service: http://localhost:8002
# - Raffle Service: http://localhost:8003

curl http://localhost:3000
```

## Docker Compose Network

### Internal Service-to-Service Communication

Services still use their hostnames within Docker Compose's default network:

```python
# In winner-worker or other internal services:
PRODUCT_SERVICE_URL = "http://product-service:8002"  # Works within Docker
```

### Frontend to Service Communication

The frontend uses localhost with explicit ports:

```javascript
// In frontend/src/api.js:
const AUTH_SERVICE_URL = "http://localhost:8001";
const PRODUCT_SERVICE_URL = "http://localhost:8002";
const RAFFLE_SERVICE_URL = "http://localhost:8003";
```

## Debugging CORS Issues

If you encounter CORS errors in the browser console:

### Check 1: Service is running
```bash
docker-compose ps
```

Expected: All services should show "Up"

### Check 2: Service responds
```bash
curl http://localhost:8001/health
```

### Check 3: CORS headers are present
```bash
curl -i -X OPTIONS http://localhost:8001/health
```

Look for headers like:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

### Check 4: Frontend origin is whitelisted
In the service's main.py, verify frontend origin is in `allow_origins`:

```python
allow_origins=[
    "http://localhost:3000",  # Must be here
    ...
]
```

## Load Testing

The load tester now targets individual services instead of the gateway:

```bash
# Update load tester for specific service
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://localhost:8001 \
  -u 1000 \
  -r 50 \
  --run-time 5m \
  --headless
```

## Production Deployment

For production, update CORS origins and service URLs:

```python
# production/auth-service/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```javascript
// production/frontend/.env.production
REACT_APP_AUTH_SERVICE_URL=https://api1.yourdomain.com
REACT_APP_PRODUCT_SERVICE_URL=https://api2.yourdomain.com
REACT_APP_RAFFLE_SERVICE_URL=https://api3.yourdomain.com
```

Or use a reverse proxy (Nginx, HAProxy) to route all services under a single domain:

```nginx
# Example Nginx configuration
upstream auth-service {
  server auth-service:8001;
}

upstream product-service {
  server product-service:8002;
}

upstream raffle-service {
  server raffle-service:8003;
}

server {
  listen 443 ssl;
  server_name api.yourdomain.com;

  location /auth {
    proxy_pass http://auth-service;
  }

  location /products {
    proxy_pass http://product-service;
  }

  location /raffle {
    proxy_pass http://raffle-service;
  }
}
```

---

**Architecture**: Direct Service Communication  
**Network**: Docker Compose Default Network  
**CORS**: Enabled on all services
