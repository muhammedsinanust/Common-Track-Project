import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from typing import Optional
import jwt
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002")
RAFFLE_SERVICE_URL = os.getenv("RAFFLE_SERVICE_URL", "http://raffle-service:8003")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Global HTTP client for service-to-service communication
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("API Gateway started - HTTP client initialized")
    yield
    await http_client.aclose()
    logger.info("API Gateway shutdown - HTTP client closed")

app = FastAPI(title="API Gateway", version="1.0.0", lifespan=lifespan)

# CORS Configuration - Allow frontend and all services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== JWT Utilities ======================

def decode_jwt(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ====================== Middleware & Dependencies ======================

async def verify_jwt_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify JWT token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    payload = decode_jwt(token)
    return payload

# ====================== Routes ======================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway", "timestamp": datetime.utcnow().isoformat()}

# ====================== Auth Routes (Public) ======================

@app.post("/api/auth/register")
async def register(request: Request):
    """Route: POST /api/auth/register -> Auth Service"""
    try:
        body = await request.json()
        response = await http_client.post(f"{AUTH_SERVICE_URL}/register", json=body)
        return response.json()
    except Exception as e:
        logger.error(f"Auth registration error: {str(e)}")
        raise HTTPException(status_code=502, detail="Auth service unavailable")

@app.post("/api/auth/login")
async def login(request: Request):
    """Route: POST /api/auth/login -> Auth Service"""
    try:
        body = await request.json()
        response = await http_client.post(f"{AUTH_SERVICE_URL}/login", json=body)
        return response.json()
    except Exception as e:
        logger.error(f"Auth login error: {str(e)}")
        raise HTTPException(status_code=502, detail="Auth service unavailable")

@app.get("/api/auth/profile")
async def get_profile(payload: dict = Depends(verify_jwt_token)):
    """Route: GET /api/auth/profile -> Auth Service (Protected)"""
    try:
        user_id = payload.get("user_id")
        response = await http_client.get(
            f"{AUTH_SERVICE_URL}/profile",
            headers={"X-User-ID": str(user_id)}
        )
        return response.json()
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        raise HTTPException(status_code=502, detail="Auth service unavailable")

# ====================== Product Routes ======================

@app.get("/api/products")
async def get_products(skip: int = 0, limit: int = 100):
    """Route: GET /api/products -> Product Service (Public)"""
    try:
        response = await http_client.get(
            f"{PRODUCT_SERVICE_URL}/products",
            params={"skip": skip, "limit": limit}
        )
        return response.json()
    except Exception as e:
        logger.error(f"Get products error: {str(e)}")
        raise HTTPException(status_code=502, detail="Product service unavailable")

@app.post("/api/products")
async def create_product(request: Request, payload: dict = Depends(verify_jwt_token)):
    """Route: POST /api/products -> Product Service (Admin only)"""
    try:
        user_id = payload.get("user_id")
        role = payload.get("role", "user")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        body = await request.json()
        response = await http_client.post(
            f"{PRODUCT_SERVICE_URL}/products",
            json=body,
            headers={"X-User-ID": str(user_id), "X-Role": role}
        )
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create product error: {str(e)}")
        raise HTTPException(status_code=502, detail="Product service unavailable")

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, request: Request, payload: dict = Depends(verify_jwt_token)):
    """Route: PUT /api/products/{product_id} -> Product Service (Admin only)"""
    try:
        user_id = payload.get("user_id")
        role = payload.get("role", "user")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        body = await request.json()
        response = await http_client.put(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            json=body,
            headers={"X-User-ID": str(user_id), "X-Role": role}
        )
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product error: {str(e)}")
        raise HTTPException(status_code=502, detail="Product service unavailable")

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, payload: dict = Depends(verify_jwt_token)):
    """Route: DELETE /api/products/{product_id} -> Product Service (Admin only)"""
    try:
        user_id = payload.get("user_id")
        role = payload.get("role", "user")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        response = await http_client.delete(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            headers={"X-User-ID": str(user_id), "X-Role": role}
        )
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete product error: {str(e)}")
        raise HTTPException(status_code=502, detail="Product service unavailable")

# ====================== Raffle Routes ======================

@app.post("/api/raffle/enter-raffle")
async def enter_raffle(request: Request, payload: dict = Depends(verify_jwt_token)):
    """Route: POST /api/raffle/enter-raffle -> Raffle Service (Protected)"""
    try:
        user_id = payload.get("user_id")
        body = await request.json()
        
        # Inject user_id from JWT
        body["user_id"] = user_id
        
        response = await http_client.post(
            f"{RAFFLE_SERVICE_URL}/enter-raffle",
            json=body,
            headers={"X-User-ID": str(user_id)}
        )
        
        # Return 202 Accepted if raffle service does
        if response.status_code == 202:
            return {"status": "accepted", "message": "Raffle entry queued"}
        
        return response.json()
    except Exception as e:
        logger.error(f"Enter raffle error: {str(e)}")
        raise HTTPException(status_code=502, detail="Raffle service unavailable")

# ====================== Root Route ======================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Sneaker Store API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "auth": "/api/auth/*",
            "products": "/api/products*",
            "raffle": "/api/raffle/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_GATEWAY_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
