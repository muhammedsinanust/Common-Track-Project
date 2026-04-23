import os
import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://product-db:27017/productdb")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "productdb")

# MongoDB Connection
mongo_client = None
db = None

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    brand: str
    size: str
    price: float
    stock: int
    drop_timestamp: Optional[datetime] = None  # For scheduled drops
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    drop_timestamp: Optional[datetime] = None
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    brand: str
    size: str
    price: float
    stock: int
    drop_timestamp: Optional[datetime] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Utility functions
def convert_mongo_doc(doc):
    """Convert MongoDB document to response format."""
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global mongo_client, db
    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[MONGO_DB_NAME]
        # Test connection
        mongo_client.server_info()
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
    yield
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")

app = FastAPI(title="Product Service", version="1.0.0", lifespan=lifespan)

# ====================== Health Check ======================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "product-service", "timestamp": datetime.utcnow().isoformat()}

# ====================== Product Endpoints ======================

@app.get("/products")
async def list_products(skip: int = 0, limit: int = 100):
    """List all products (public endpoint)."""
    try:
        products_collection = db["products"]
        products = list(products_collection.find().skip(skip).limit(limit))
        
        return {
            "total": products_collection.count_documents({}),
            "skip": skip,
            "limit": limit,
            "products": [convert_mongo_doc(p) for p in products]
        }
    except Exception as e:
        logger.error(f"List products error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")

@app.post("/products")
async def create_product(
    product: ProductCreate,
    x_user_id: str = Header(None),
    x_role: str = Header(None)
):
    """Create a new product (admin only)."""
    try:
        if x_role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        products_collection = db["products"]
        
        product_doc = {
            "name": product.name,
            "brand": product.brand,
            "size": product.size,
            "price": product.price,
            "stock": product.stock,
            "drop_timestamp": product.drop_timestamp,
            "description": product.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": x_user_id
        }
        
        result = products_collection.insert_one(product_doc)
        
        logger.info(f"Product created: {result.inserted_id}")
        
        return {
            "id": str(result.inserted_id),
            "message": "Product created successfully",
            **product_doc
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create product error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product: ProductUpdate,
    x_user_id: str = Header(None),
    x_role: str = Header(None)
):
    """Update product (admin only)."""
    try:
        if x_role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        products_collection = db["products"]
        
        try:
            obj_id = ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        # Build update dict
        update_data = {}
        for field, value in product.dict().items():
            if value is not None:
                update_data[field] = value
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = products_collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        logger.info(f"Product updated: {product_id}")
        
        return convert_mongo_doc(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    x_user_id: str = Header(None),
    x_role: str = Header(None)
):
    """Delete product (admin only)."""
    try:
        if x_role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        products_collection = db["products"]
        
        try:
            obj_id = ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        result = products_collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        logger.info(f"Product deleted: {product_id}")
        
        return {"message": "Product deleted successfully", "id": product_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete product error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get specific product by ID."""
    try:
        products_collection = db["products"]
        
        try:
            obj_id = ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        product = products_collection.find_one({"_id": obj_id})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return convert_mongo_doc(product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch product")

@app.patch("/products/{product_id}/stock")
async def update_stock(
    product_id: str,
    stock_delta: int,
    x_user_id: str = Header(None)
):
    """Update product stock (used by winner worker)."""
    try:
        products_collection = db["products"]
        
        try:
            obj_id = ObjectId(product_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        result = products_collection.find_one_and_update(
            {"_id": obj_id},
            {
                "$inc": {"stock": stock_delta},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        logger.info(f"Stock updated for product {product_id}: delta={stock_delta}")
        
        return convert_mongo_doc(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update stock error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update stock")

# ====================== Root Route ======================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Product Service",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PRODUCT_SERVICE_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
