"""Auth & User Service — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import router

# Create database tables on startup
Base.metadata.create_all(bind=engine)

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


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
