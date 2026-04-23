"""Raffle Ingress Service — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="SneakerDrop Raffle Ingress Service",
    version="1.0.0",
    description="Accepts raffle entries and queues them in Redis for asynchronous processing.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/raffle", tags=["Raffle"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "raffle-ingress"}
