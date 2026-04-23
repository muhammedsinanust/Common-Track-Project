"""Product Service — MongoDB connection configuration."""

import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sneakerdrop_products")

client = AsyncIOMotorClient(MONGO_URL)
database = client[MONGO_DB_NAME]

# Collections
products_collection = database["products"]
drops_collection = database["drops"]
