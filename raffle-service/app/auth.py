"""Raffle Ingress Service — JWT authentication utilities."""

import os
from jose import jwt, JWTError

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-dev-key-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT. Returns the payload dict or None on failure."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
