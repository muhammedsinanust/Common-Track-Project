#!/usr/bin/env python3
"""
Winner Processor Worker

Runs continuously as a background service.
Pulls raffle entries from Redis queue and processes them synchronously.
Checks stock levels from Product Service and creates winner records.
"""

import os
import logging
import redis
import json
import httpx
import time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

ORDER_DB_USER = os.getenv("ORDER_DB_USER", "orderuser")
ORDER_DB_PASSWORD = os.getenv("ORDER_DB_PASSWORD", "orderpassword123")
ORDER_DB_HOST = os.getenv("ORDER_DB_HOST", "localhost")
ORDER_DB_PORT = os.getenv("ORDER_DB_PORT", "5432")
ORDER_DB_NAME = os.getenv("ORDER_DB_NAME", "orderdb")

ORDER_DATABASE_URL = f"postgresql://{ORDER_DB_USER}:{ORDER_DB_PASSWORD}@{ORDER_DB_HOST}:{ORDER_DB_PORT}/{ORDER_DB_NAME}"

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", 1))  # seconds

# Database models
Base = declarative_base()

class Winner(Base):
    """Winner record in order database."""
    __tablename__ = "winners"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    shoe_size = Column(String, nullable=False)
    entry_timestamp = Column(DateTime, nullable=False)
    processed_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, won, failed

# Database setup
engine = create_engine(ORDER_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection
redis_client = None
http_client = None

def init_database():
    """Initialize database and create tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

def init_redis():
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_keepalive=True
        )
        redis_client.ping()
        logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise

def init_http_client():
    """Initialize HTTP client for service-to-service communication."""
    global http_client
    http_client = httpx.Client(timeout=30.0)
    logger.info("HTTP client initialized")

def get_db_session() -> Session:
    """Get database session."""
    return SessionLocal()

def check_product_stock(product_id: str) -> dict:
    """
    Check product stock from Product Service.
    
    Returns: {"stock": int, "available": bool}
    """
    try:
        response = http_client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        if response.status_code == 200:
            product = response.json()
            stock = product.get("stock", 0)
            return {"stock": stock, "available": stock > 0}
        else:
            logger.warning(f"Product {product_id} not found or service error")
            return {"stock": 0, "available": False}
    except Exception as e:
        logger.error(f"Failed to check product stock: {str(e)}")
        return {"stock": 0, "available": False}

def decrement_product_stock(product_id: str, user_id: int) -> bool:
    """
    Decrement product stock in Product Service.
    
    Returns: True if successful, False otherwise
    """
    try:
        response = http_client.patch(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}/stock",
            json={"stock_delta": -1},
            headers={"X-User-ID": str(user_id)}
        )
        if response.status_code == 200:
            logger.info(f"Stock decremented for product {product_id}")
            return True
        else:
            logger.warning(f"Failed to decrement stock: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to decrement stock: {str(e)}")
        return False

def process_raffle_entry(entry_json: str) -> bool:
    """
    Process a single raffle entry from the queue.
    
    Returns: True if processed successfully, False otherwise
    """
    try:
        entry = json.loads(entry_json)
        user_id = entry.get("user_id")
        shoe_size = entry.get("shoe_size")
        entry_timestamp = entry.get("timestamp")
        entry_id = entry.get("entry_id")
        
        logger.info(f"Processing raffle entry: {entry_id} (user={user_id}, size={shoe_size})")
        
        # TODO: In a real system, would need to select a product based on shoe_size
        # For now, use a placeholder product ID
        product_id = f"product_{shoe_size}"  # Simplified for demo
        
        # Check if stock is available
        stock_info = check_product_stock(product_id)
        
        if not stock_info["available"]:
            logger.info(f"No stock available for {product_id}")
            db = get_db_session()
            try:
                winner = Winner(
                    user_id=user_id,
                    product_id=product_id,
                    shoe_size=shoe_size,
                    entry_timestamp=datetime.fromisoformat(entry_timestamp),
                    status="failed"
                )
                db.add(winner)
                db.commit()
                logger.info(f"Recorded failed entry: {entry_id}")
            except Exception as e:
                logger.error(f"Failed to record entry: {str(e)}")
                db.rollback()
            finally:
                db.close()
            return False
        
        # Decrement stock
        if not decrement_product_stock(product_id, user_id):
            logger.warning(f"Failed to decrement stock, but continuing with winner record")
        
        # Record winner in database
        db = get_db_session()
        try:
            winner = Winner(
                user_id=user_id,
                product_id=product_id,
                shoe_size=shoe_size,
                entry_timestamp=datetime.fromisoformat(entry_timestamp),
                status="won"
            )
            db.add(winner)
            db.commit()
            logger.info(f"Winner recorded: entry_id={entry_id}, user_id={user_id}, product={product_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to record winner: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode raffle entry JSON: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing raffle entry: {str(e)}")
        return False

def process_queue():
    """
    Main processing loop.
    
    Continuously pulls entries from Redis queue using BLPOP (blocking list pop).
    Processes each entry synchronously.
    """
    logger.info("Starting winner processor worker...")
    
    while True:
        try:
            # BLPOP blocks until an entry is available (timeout of 10 seconds)
            # Returns (key, value) tuple or None if timeout
            result = redis_client.blpop("raffle_queue", timeout=10)
            
            if result:
                _, entry_json = result
                process_raffle_entry(entry_json)
            else:
                # Timeout - just continue
                logger.debug("No entries in queue (timeout)")
        
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            logger.info("Attempting to reconnect in 10 seconds...")
            time.sleep(10)
            try:
                redis_client.ping()
                logger.info("Reconnected to Redis")
            except:
                pass
        
        except Exception as e:
            logger.error(f"Unexpected error in processing loop: {str(e)}")
            time.sleep(POLLING_INTERVAL)

def main():
    """Initialize and start worker."""
    try:
        logger.info("Initializing Winner Processor Worker...")
        
        # Initialize components
        init_database()
        init_redis()
        init_http_client()
        
        logger.info("All components initialized successfully")
        
        # Start processing
        process_queue()
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
    finally:
        if http_client:
            http_client.close()
        if redis_client:
            redis_client.close()
        logger.info("Worker shutdown complete")

if __name__ == "__main__":
    main()
