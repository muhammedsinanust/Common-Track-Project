import os
import time
import json
import random
import redis
import psycopg2
from psycopg2 import pool

print("Initializing Worker Service...")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=6379, 
    decode_responses=True
)

# Initialize Connection Pooling (Crucial for high throughput writing)
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20, # Min 1 connection, Max 20 connections
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "sneaker_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres")
    )
    if db_pool:
        print("Database connection pool created successfully.")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    exit(1)

def process_queue():
    print("Worker is now actively polling the queue...")
    while True:
        try:
            # Block until an item hits the queue (avoids CPU thrashing)
            result = redis_client.blpop("raffle_queue", timeout=0)
            if not result:
                continue
            
            _, payload_str = result
            payload = json.loads(payload_str)
            
            # Simulate CPU/Processing delay
            time.sleep(0.05)
            
            # 5% Win Logic
            is_winner = random.random() < 0.05 
            
            # Borrow connection from pool
            conn = db_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO raffle_entries (user_id, shoe_size, is_winner, processed_at) VALUES (%s, %s, %s, NOW())",
                        (payload["user_id"], payload["shoe_size"], is_winner)
                    )
                conn.commit()
                print(f"Processed User: {payload['user_id']} | Winner: {is_winner}")
            except Exception as db_err:
                print(f"Database insertion failed: {db_err}")
                conn.rollback()
            finally:
                # Always return connection to the pool
                db_pool.putconn(conn)
                
        except Exception as queue_err:
            print(f"Queue processing error: {queue_err}")
            time.sleep(1) # Backoff on failure

if __name__ == "__main__":
    process_queue()
