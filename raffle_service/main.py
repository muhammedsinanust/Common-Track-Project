import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis Message Broker
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=6379, 
    decode_responses=True
)

class EnterRequest(BaseModel):
    user_id: str
    shoe_size: str

@app.post("/enter", status_code=202)
def enter_raffle(req: EnterRequest):
    # 1. Idempotency Check (O(1) time complexity)
    if redis_client.sismember("entered_users", req.user_id):
        raise HTTPException(status_code=409, detail="User already entered the raffle.")
    
    # 2. Add to Set (lock them in) and Push to Queue atomically-ish via pipeline
    pipe = redis_client.pipeline()
    pipe.sadd("entered_users", req.user_id)
    payload = json.dumps({"user_id": req.user_id, "shoe_size": req.shoe_size})
    pipe.rpush("raffle_queue", payload)
    pipe.execute()
    
    return {"status": "Accepted", "message": "Your entry is queued for processing."}
