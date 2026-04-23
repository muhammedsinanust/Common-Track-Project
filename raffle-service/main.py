import os
import logging
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import redis
from contextlib import asynccontextmanager
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis-broker")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis Connection
redis_client = None

# Pydantic models
class RaffleEntry(BaseModel):
    user_id: Optional[int] = None  # Will be injected by gateway
    shoe_size: str

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_keepalive=True
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        redis_client = None
    yield
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")

app = FastAPI(title="Raffle Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== Health Check ======================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "raffle-service", "timestamp": datetime.utcnow().isoformat()}

# ====================== Raffle Endpoints ======================

@app.post("/enter-raffle")
async def enter_raffle(entry: RaffleEntry, x_user_id: str = Header(None)):
    """
    Enter raffle - High throughput endpoint.
    
    Returns 202 Accepted immediately after queuing entry to Redis.
    Does NOT connect to any standard database to avoid connection exhaustion.
    Entry is pushed to Redis list "raffle_queue" for async processing.
    """
    try:
        if not redis_client:
            logger.error("Redis client not available")
            raise HTTPException(status_code=503, detail="Raffle service temporarily unavailable")
        
        # Use user_id from header (injected by gateway from JWT)
        user_id = x_user_id or entry.user_id
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # Create raffle entry
        raffle_entry = {
            "user_id": int(user_id),
            "shoe_size": entry.shoe_size,
            "timestamp": datetime.utcnow().isoformat(),
            "entry_id": f"{user_id}_{datetime.utcnow().timestamp()}"
        }
        
        # Push to Redis queue synchronously (non-blocking)
        # Using LPUSH for FIFO queue processing
        redis_client.lpush("raffle_queue", json.dumps(raffle_entry))
        
        # Also track total entries for monitoring
        redis_client.incr("raffle_total_entries")
        
        logger.info(f"Raffle entry queued: user_id={user_id}, shoe_size={entry.shoe_size}")
        
        # Return 202 Accepted immediately
        return {
            "status": "accepted",
            "message": "Raffle entry queued for processing",
            "entry_id": raffle_entry["entry_id"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enter raffle error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to queue raffle entry")

@app.get("/raffle-stats")
async def get_raffle_stats():
    """Get raffle statistics (for monitoring)."""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis unavailable")
        
        queue_length = redis_client.llen("raffle_queue")
        total_entries = redis_client.get("raffle_total_entries") or "0"
        
        return {
            "queue_length": queue_length,
            "total_entries": int(total_entries),
            "service": "raffle-service",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

# ====================== Root Route ======================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Raffle Service",
        "version": "1.0.0",
        "status": "operational",
        "purpose": "High-throughput raffle entry ingestion via Redis"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("RAFFLE_SERVICE_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
