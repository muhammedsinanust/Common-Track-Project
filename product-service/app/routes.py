"""Product Service — API route handlers."""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from .database import products_collection, drops_collection
from .schemas import ProductCreate, ProductOut, DropCreate, DropOut

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────────────

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ── Product Endpoints ────────────────────────────────────────────────────────

@router.post("/products", status_code=201)
async def create_product(payload: ProductCreate):
    """Create a new sneaker product."""
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await products_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return serialize_doc(doc)


@router.get("/products")
async def list_products():
    """List all sneaker products."""
    products = []
    async for doc in products_collection.find():
        products.append(serialize_doc(doc))
    return products


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get a single product by ID."""
    doc = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_doc(doc)


# ── Drop Endpoints ───────────────────────────────────────────────────────────

@router.post("/drops", status_code=201)
async def create_drop(payload: DropCreate):
    """Schedule a new Fresh Drop."""
    # Verify product exists
    product = await products_collection.find_one({"_id": ObjectId(payload.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    doc = payload.model_dump()
    result = await drops_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return serialize_doc(doc)


@router.get("/drops")
async def list_drops():
    """List all scheduled drops with embedded product data."""
    drops = []
    async for doc in drops_collection.find({"is_active": True}):
        doc = serialize_doc(doc)
        # Embed the product document
        try:
            product = await products_collection.find_one(
                {"_id": ObjectId(doc["product_id"])}
            )
            if product:
                doc["product"] = serialize_doc(product)
        except Exception:
            pass
        drops.append(doc)
    return drops


@router.get("/drops/{drop_id}")
async def get_drop(drop_id: str):
    """Get a single drop by ID with embedded product data."""
    doc = await drops_collection.find_one({"_id": ObjectId(drop_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Drop not found")
    doc = serialize_doc(doc)
    try:
        product = await products_collection.find_one(
            {"_id": ObjectId(doc["product_id"])}
        )
        if product:
            doc["product"] = serialize_doc(product)
    except Exception:
        pass
    return doc
