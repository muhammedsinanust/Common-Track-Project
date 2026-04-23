"""Raffle Ingress Service — API route handlers."""

import json
import os

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .auth import decode_access_token

router = APIRouter()
security = HTTPBearer()

# ── Redis connection (no standard database) ──────────────────────────────────

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

RAFFLE_QUEUE = "raffle_queue"


# ── Schemas ──────────────────────────────────────────────────────────────────

class RaffleEntry(BaseModel):
    shoe_size: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/enter-raffle", status_code=status.HTTP_202_ACCEPTED)
def enter_raffle(
    payload: RaffleEntry,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Accept a raffle entry.

    1. Authenticate the JWT from the Authorization header.
    2. Extract the user_id from the token payload.
    3. Push {user_id, shoe_size} into the Redis list "raffle_queue".
    4. Return 202 Accepted immediately.
    """
    token_payload = decode_access_token(credentials.credentials)
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = token_payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token missing user ID")

    entry = json.dumps({"user_id": user_id, "shoe_size": payload.shoe_size})
    redis_client.rpush(RAFFLE_QUEUE, entry)

    return {
        "message": "You have been entered into the raffle!",
        "queue": RAFFLE_QUEUE,
    }
