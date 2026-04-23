"""Product Service — Pydantic schemas."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str
    quantity: int = 0


class ProductCreate(BaseModel):
    name: str
    brand: str
    description: str = ""
    price: float
    image_url: str = ""
    sizes: List[SizeStock] = []


class ProductOut(BaseModel):
    id: str = Field(alias="_id")
    name: str
    brand: str
    description: str
    price: float
    image_url: str
    sizes: List[SizeStock]
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class DropCreate(BaseModel):
    product_id: str
    drop_date: datetime
    is_active: bool = True


class DropOut(BaseModel):
    id: str = Field(alias="_id")
    product_id: str
    drop_date: datetime
    is_active: bool
    product: Optional[ProductOut] = None

    class Config:
        populate_by_name = True
