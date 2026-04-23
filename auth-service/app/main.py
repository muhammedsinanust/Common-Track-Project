"""Auth & User Service — FastAPI application entry point."""

import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from .database import engine, Base
from .routes import router

logger = logging.getLogger("auth-service")

app = FastAPI(
    title="SneakerDrop Auth Service",
    version="1.0.0",
    description="Handles user registration, login, and JWT-based authentication.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/auth", tags=["Auth"])


@app.on_event("startup")
def create_tables():
    """Create DB tables on startup, retrying until PostgreSQL is ready."""
    retries = 10
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ready.")
            return
        except OperationalError as exc:
            if attempt < retries - 1:
                logger.warning(f"DB not ready (attempt {attempt + 1}/{retries}), retrying in 3s…")
                time.sleep(3)
            else:
                raise exc


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
