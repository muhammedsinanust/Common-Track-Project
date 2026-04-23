# Updated Architecture - Direct Service Communication

## Changes Made

This document outlines the modifications made to the microservices architecture to remove the API Gateway and enable direct service-to-service communication.

### 1. **Removed API Gateway Service**

- ❌ Deleted: `api-gateway/` service
- ❌ Removed: Port 8000 from docker-compose.yml
- **Impact**: Frontend now communicates directly with backend services instead of routing through a unified gateway

### 2. **Removed Custom Docker Network**

- ❌ Deleted: `sneaker-net` custom bridge network from docker-compose.yml
- ✅ Uses: Default docker-compose network (automatically created)
- **Impact**: Services still communicate via hostname, but now use implicit default networking

### 3. **Backend Services Now Expose Ports Directly**

Each service now exposes its port directly to the host:

| Service | Port | Exposed |
|---------|------|---------|
| Auth Service | 8001 | ✅ Yes |
| Product Service | 8002 | ✅ Yes |
| Raffle Service | 8003 | ✅ Yes |
| Frontend | 3000 | ✅ Yes |
| ~~API Gateway~~ | ~~8000~~ | ❌ Removed |

### 4. **CORS Configuration Added to All Services**

All FastAPI services now include CORS middleware:

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

This allows the React frontend to make direct CORS requests from port 3000 to each service.

### 5. **Updated Services with CORS**

✅ **auth-service/main.py** - Added CORSMiddleware  
✅ **product-service/main.py** - Added CORSMiddleware  
✅ **raffle-service/main.py** - Added CORSMiddleware  

### 6. **Frontend API Client Updated**

The frontend now makes direct calls to each service:

**Before (API Gateway Pattern):**
```javascript
// Single gateway URL
const API_BASE_URL = 'http://localhost:8000/api';
const api = axios.create({ baseURL: API_BASE_URL });

// All calls through gateway
api.post('/auth/login')      // → gateway → auth service
api.post('/products')        // → gateway → product service
api.post('/raffle/enter')    // → gateway → raffle service
```

**After (Direct Service Pattern):**
```javascript
// Separate URLs for each service
const AUTH_SERVICE_URL = 'http://localhost:8001';
const PRODUCT_SERVICE_URL = 'http://localhost:8002';
const RAFFLE_SERVICE_URL = 'http://localhost:8003';

// Create individual axios instances
const authAPI = axios.create({ baseURL: AUTH_SERVICE_URL });
const productAPI = axios.create({ baseURL: PRODUCT_SERVICE_URL });
const raffleAPI = axios.create({ baseURL: RAFFLE_SERVICE_URL });

// Direct calls to services
authAPI.post('/login')       // → auth service (8001)
productAPI.post('/products') // → product service (8002)
raffleAPI.post('/enter-raffle') // → raffle service (8003)
```

### 7. **Updated docker-compose.yml**

Key changes:

1. **Removed network references** from all services
2. **Removed API Gateway service** completely
3. **Removed network definition** section
4. **Updated frontend environment variables**:
   ```yaml
   environment:
     REACT_APP_AUTH_SERVICE_URL: http://localhost:8001
     REACT_APP_PRODUCT_SERVICE_URL: http://localhost:8002
     REACT_APP_RAFFLE_SERVICE_URL: http://localhost:8003
   ```
5. **Simplified service dependencies** (only database dependencies now)
6. **Updated load tester** to target auth service directly

## Architecture Comparison

### Old Architecture (API Gateway Pattern)
```
Frontend (3000)
    ↓
API Gateway (8000)
    ├→ Auth Service (8001)
    ├→ Product Service (8002)
    └→ Raffle Service (8003)
```

### New Architecture (Direct Service Pattern)
```
Frontend (3000)
    ├→ Auth Service (8001)
    ├→ Product Service (8002)
    └→ Raffle Service (8003)
```

## Service Endpoints

### Authentication Service (Port 8001)
```
POST   /register      - Register new user
POST   /login         - Login (returns JWT)
GET    /profile       - Get user profile (protected)
GET    /health        - Health check
```

### Product Service (Port 8002)
```
GET    /products                    - List products
GET    /products/{id}              - Get product
POST   /products                   - Create product (admin)
PUT    /products/{id}              - Update product (admin)
DELETE /products/{id}              - Delete product (admin)
PATCH  /products/{id}/stock        - Update stock
GET    /health                     - Health check
```

### Raffle Service (Port 8003)
```
POST   /enter-raffle               - Enter raffle (protected)
GET    /raffle-stats               - Get raffle statistics
GET    /health                     - Health check
```

## CORS Behavior

With CORS enabled on all services, the frontend can now:

1. ✅ Make cross-origin requests to each service
2. ✅ Include credentials (cookies, authorization headers)
3. ✅ Handle preflight OPTIONS requests automatically
4. ✅ Access service endpoints from http://localhost:3000

## Migration Notes

### For Developers

1. **Update API Calls**: If you had hardcoded API gateway URLs anywhere, update them to point to the specific service ports.

2. **Testing**: When testing individual services, you can now hit them directly:
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   curl http://localhost:8003/health
   ```

3. **Port Mapping**: Each service is now directly accessible from the host.

### For Deployment

1. **Simpler Load Balancing**: No API Gateway to scale; balance requests directly to services.

2. **Direct Service Access**: Services are now accessible individually, enabling more flexible routing (e.g., via external load balancer like Nginx, HAProxy, or cloud load balancers).

3. **CORS Management**: CORS is configured at service level; modify allowed origins in each service's main.py if needed.

4. **Service Discovery**: In Docker Compose, services still use hostnames for internal communication (e.g., `http://product-service:8002`).

## Files Modified

- ✅ `docker-compose.yml` - Removed API Gateway, removed custom network, updated frontend env vars
- ✅ `auth-service/main.py` - Added CORS middleware
- ✅ `product-service/main.py` - Added CORS middleware
- ✅ `raffle-service/main.py` - Added CORS middleware
- ✅ `frontend/src/api.js` - Updated to use individual service URLs

## Files Not Modified (Still Compatible)

- ✓ `auth-service/requirements.txt` - Same dependencies
- ✓ `product-service/requirements.txt` - Same dependencies
- ✓ `raffle-service/requirements.txt` - Same dependencies
- ✓ All Dockerfiles - Still functional
- ✓ Frontend React components - Use same api.js exports
- ✓ Winner Worker - Uses direct service URLs internally
- ✓ Database configurations - Unchanged

## Advantages of Direct Service Pattern

✅ **Simpler Architecture**: Fewer moving parts (one less service)  
✅ **Lower Latency**: No routing overhead through gateway  
✅ **Direct Debugging**: Test services independently  
✅ **Easier Scaling**: Each service can scale independently  
✅ **Standard CORS**: Uses standard CORS middleware instead of custom routing  

## Potential Considerations

⚠ **Frontend Coupling**: Frontend is now aware of all service URLs (consider environment configuration)  
⚠ **CORS Setup**: CORS must be configured correctly on each service  
⚠ **Port Management**: More ports exposed directly to host  
⚠ **Load Balancing**: May need external load balancer in production  

## Quick Start with Updated Architecture

```bash
# Build and start services
docker-compose build
docker-compose up -d

# Services are directly accessible
curl http://localhost:8001/health    # Auth Service
curl http://localhost:8002/health    # Product Service
curl http://localhost:8003/health    # Raffle Service
curl http://localhost:3000           # Frontend

# Frontend will automatically connect to services on their respective ports
```

---

**Updated**: April 23, 2026  
**Architecture Pattern**: Direct Service Communication  
**Network Mode**: Docker Compose Default Network
