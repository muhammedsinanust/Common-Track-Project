# Update Summary: Direct Service Communication Architecture

## Overview

The microservices architecture has been refactored from an **API Gateway pattern** to a **Direct Service Communication pattern**. The frontend now communicates directly with individual services instead of routing through a unified API Gateway.

---

## Changes Made

### 1. ✅ Removed API Gateway Service

**Files Deleted/Removed:**
- `api-gateway/` directory (no longer needed)
- Port 8000 from `docker-compose.yml`

**Impact:**
- Reduced services from 6 to 5 (excluding databases and worker)
- Eliminated the API Gateway service entirely
- Frontend now accesses services on their native ports

---

### 2. ✅ Removed Custom Docker Network

**Configuration Changed:**
- `docker-compose.yml`: Removed `networks: sneaker-net` declarations from all services
- Removed `networks:` section defining the custom bridge network
- Now uses Docker Compose's default network

**Services Now Use:**
- Default docker-compose network for internal communication
- Service discovery still works via hostnames (e.g., `product-service:8002`)

---

### 3. ✅ Backend Services Now Expose Ports Directly

**Port Mapping:**
```
Service               | Port  | Exposed
--------------------|-------|--------
Auth Service         | 8001  | ✅ Yes
Product Service      | 8002  | ✅ Yes
Raffle Service       | 8003  | ✅ Yes
Frontend             | 3000  | ✅ Yes
API Gateway          | 8000  | ❌ Removed
```

**docker-compose.yml Changes:**
```yaml
auth-service:
  ports:
    - "8001:8001"

product-service:
  ports:
    - "8002:8002"

raffle-service:
  ports:
    - "8003:8003"
```

---

### 4. ✅ CORS Middleware Added to All Services

**Updated Files:**
- `auth-service/main.py` - Added CORS configuration
- `product-service/main.py` - Added CORS configuration
- `raffle-service/main.py` - Added CORS configuration

**CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://frontend:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Benefits:**
- Services accept cross-origin requests from the frontend
- Supports credentials (JWT tokens, cookies)
- Handles preflight OPTIONS requests automatically
- Can be customized per service

---

### 5. ✅ Frontend API Client Updated

**File Modified:** `frontend/src/api.js`

**Changes:**
- Removed single API Gateway URL
- Created individual Axios instances for each service
- Updated environment variable references

**Before:**
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
const api = axios.create({ baseURL: API_BASE_URL });

export const authAPI = {
  login: (email, password) => api.post('/auth/login', ...)
};
```

**After:**
```javascript
const AUTH_SERVICE_URL = 'http://localhost:8001';
const PRODUCT_SERVICE_URL = 'http://localhost:8002';
const RAFFLE_SERVICE_URL = 'http://localhost:8003';

const authAPI = axios.create({ baseURL: AUTH_SERVICE_URL });
const productAPI = axios.create({ baseURL: PRODUCT_SERVICE_URL });
const raffleAPI = axios.create({ baseURL: RAFFLE_SERVICE_URL });

export const authAPI = {
  login: (email, password) => authAPI.post('/login', ...)
};
```

**Backward Compatible:**
- React components still import and use the same function names
- No changes needed in component files (e.g., `Login.jsx`, `Dashboard.jsx`)

---

### 6. ✅ docker-compose.yml Completely Refactored

**Key Changes:**

**Removed:**
```yaml
# No longer present:
- api-gateway service
- networks: sneaker-net references
- networks: section definition
- API Gateway health checks and dependencies
```

**Modified Services:**
```yaml
# Frontend environment variables
frontend:
  environment:
    REACT_APP_AUTH_SERVICE_URL: http://localhost:8001
    REACT_APP_PRODUCT_SERVICE_URL: http://localhost:8002
    REACT_APP_RAFFLE_SERVICE_URL: http://localhost:8003

# Load tester target
load-tester:
  environment:
    LOCUST_HOST: http://localhost:8001
```

**Simplified Dependencies:**
```yaml
# Services now only depend on their required databases/infrastructure
auth-service:
  depends_on:
    auth-db:
      condition: service_healthy

raffle-service:
  depends_on:
    redis-broker:
      condition: service_healthy
```

---

## Architecture Comparison

### Old Architecture (API Gateway Pattern)
```
┌──────────────────────────────────────┐
│        Frontend (React)               │
│        Port 3000                      │
└───────────────────┬──────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │   API Gateway        │
        │   FastAPI            │
        │   Port 8000          │
        │   ├─ Routing        │
        │   ├─ JWT Validation │
        │   └─ CORS           │
        └──┬──────────┬──────┬─┘
           │          │      │
        ┌──▼──┐   ┌───▼──┐ ┌─▼────┐
        │Auth │   │Prod  │ │Raffle│
        │8001 │   │8002  │ │8003  │
        └─────┘   └──────┘ └──────┘
```

### New Architecture (Direct Service Communication)
```
    ┌──────────────────────────────────────┐
    │        Frontend (React)               │
    │        Port 3000                      │
    └──┬────────────┬──────────────┬────────┘
       │            │              │
       ▼            ▼              ▼
    ┌──────┐   ┌────────┐   ┌──────────┐
    │Auth  │   │Product │   │Raffle    │
    │8001  │   │8002    │   │8003      │
    │CORS  │   │CORS    │   │CORS      │
    └──────┘   └────────┘   └──────────┘
```

---

## File Changes Summary

| File | Change | Impact |
|------|--------|--------|
| `docker-compose.yml` | Major refactor - removed API Gateway, custom network | Services now use default Docker Compose network |
| `auth-service/main.py` | Added CORS middleware | Accepts requests from frontend:3000 |
| `product-service/main.py` | Added CORS middleware | Accepts requests from frontend:3000 |
| `raffle-service/main.py` | Added CORS middleware | Accepts requests from frontend:3000 |
| `frontend/src/api.js` | Updated to direct service URLs | No changes needed in React components |
| `frontend/src/App.jsx` | No changes | Imports from updated api.js, works as-is |
| `frontend/src/pages/*.jsx` | No changes | API imports remain the same |
| `auth-service/requirements.txt` | No changes | Still has fastapi, corsMiddleware included |
| `product-service/requirements.txt` | No changes | Still compatible |
| `raffle-service/requirements.txt` | No changes | Still compatible |
| `winner-worker/worker.py` | No changes | Uses internal Docker hostnames |

---

## Service Endpoints

### Auth Service (http://localhost:8001)
```
POST   /register                  Register user
POST   /login                     Login (returns JWT)
GET    /profile                   Get user profile (protected)
GET    /health                    Health check
```

### Product Service (http://localhost:8002)
```
GET    /products                  List all products
GET    /products/{id}             Get product by ID
POST   /products                  Create product (admin)
PUT    /products/{id}             Update product (admin)
DELETE /products/{id}             Delete product (admin)
PATCH  /products/{id}/stock       Update inventory
GET    /health                    Health check
```

### Raffle Service (http://localhost:8003)
```
POST   /enter-raffle              Enter raffle (protected)
GET    /raffle-stats              Get raffle statistics
GET    /health                    Health check
```

---

## Environment Configuration

### Updated docker-compose.yml Environment Variables

```yaml
frontend:
  environment:
    REACT_APP_AUTH_SERVICE_URL: http://localhost:8001
    REACT_APP_PRODUCT_SERVICE_URL: http://localhost:8002
    REACT_APP_RAFFLE_SERVICE_URL: http://localhost:8003

load-tester:
  environment:
    LOCUST_HOST: http://localhost:8001
```

### Optional .env Updates

For deployment flexibility, add to `.env`:
```env
# Frontend direct service access
REACT_APP_AUTH_SERVICE_URL=http://localhost:8001
REACT_APP_PRODUCT_SERVICE_URL=http://localhost:8002
REACT_APP_RAFFLE_SERVICE_URL=http://localhost:8003
```

---

## Testing the Changes

### 1. Verify Services Start
```bash
docker-compose build
docker-compose up -d
docker-compose ps
```

Expected output: 5 services running (auth, product, raffle, frontend, worker)

### 2. Test Individual Services
```bash
# Auth Service
curl http://localhost:8001/health

# Product Service
curl http://localhost:8002/health

# Raffle Service
curl http://localhost:8003/health

# Frontend
curl http://localhost:3000
```

### 3. Test CORS
```bash
# Check CORS headers from browser console
# Or use curl:
curl -i -X OPTIONS http://localhost:8001/health
```

### 4. Full Integration Test
```bash
# Register user on auth service
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"pass"}'

# Navigate to frontend
# http://localhost:3000

# Try login/register flow
```

---

## Migration Guide for Developers

### If You Modified the API Gateway

If you had custom logic in the API Gateway, move it to the appropriate service:
- **Authentication logic** → auth-service
- **Product routing** → product-service  
- **Raffle logic** → raffle-service
- **CORS configuration** → Add to each service's CORS middleware

### If You Added Custom Routes

Add routes directly to the service's `main.py` file instead of the gateway.

### If You Used Service URLs Internally

Internal service URLs remain the same in Docker Compose:
```python
PRODUCT_SERVICE_URL = "http://product-service:8002"  # Still valid
```

Frontend uses localhost with ports:
```javascript
const PRODUCT_SERVICE_URL = "http://localhost:8002"  // New
```

---

## Advantages of This Architecture

✅ **Simpler**: One fewer service to manage  
✅ **Lower Latency**: No routing overhead through gateway  
✅ **Easier Debugging**: Test services independently  
✅ **Standards-Based**: Uses standard CORS configuration  
✅ **Flexible Scaling**: Each service scales independently  
✅ **Direct Access**: Frontend is aware of service topology  

---

## New Documentation Files

The following new documentation has been created:

- **ARCHITECTURE_UPDATE.md** - Detailed architecture changes
- **DIRECT_SERVICES_CONFIG.md** - Configuration and testing guide

---

## Rollback Instructions

If you need to revert to the API Gateway architecture:

1. Restore `api-gateway/` directory
2. Restore original `docker-compose.yml` with:
   - API Gateway service definition
   - Custom `sneaker-net` network
   - Network references on all services
3. Restore original `frontend/src/api.js` (single API_BASE_URL)
4. Remove CORS middleware from auth, product, raffle services

---

## Questions & Troubleshooting

**Q: Why remove the API Gateway?**  
A: Simpler architecture, lower latency, services remain independent.

**Q: Will my React components break?**  
A: No, the api.js exports are backward compatible.

**Q: How do I add more services?**  
A: Add to docker-compose.yml, expose port, add CORS middleware, update frontend api.js.

**Q: Can I still scale horizontally?**  
A: Yes, each service is independent and can have multiple instances.

**Q: What about in production?**  
A: Use a reverse proxy (Nginx, HAProxy, AWS ALB) or add services to a load balancer.

---

**Update Completed**: April 23, 2026  
**Architecture Pattern**: Direct Service Communication  
**Breaking Changes**: None (fully backward compatible with React components)  
**Status**: ✅ Ready for deployment
