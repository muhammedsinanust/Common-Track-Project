"""Product Service — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="SneakerDrop Product Service",
    version="1.0.0",
    description="Manages sneaker inventory, product details, and drop timestamps.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/products", tags=["Products"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "product"}
