"""
Winner Processor Worker
=======================
Background script that continuously:
  1. Uses BLPOP to pull entries from the Redis "raffle_queue".
  2. Randomly selects winners (10% chance).
  3. Writes winning entries to a PostgreSQL database.
"""

import json
import os
import random
import time
from datetime import datetime, timezone

import psycopg2
import redis

# ── Configuration via environment variables ──────────────────────────────────

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/sneakerdrop_auth",
)
WIN_PROBABILITY = float(os.getenv("WIN_PROBABILITY", "0.10"))

RAFFLE_QUEUE = "raffle_queue"

# ── Database setup ───────────────────────────────────────────────────────────


def get_pg_connection():
    """Create a PostgreSQL connection."""
    return psycopg2.connect(DATABASE_URL)


def ensure_winners_table(conn):
    """Create the winners table if it doesn't already exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS winners (
                id          SERIAL PRIMARY KEY,
                user_id     INTEGER NOT NULL,
                shoe_size   VARCHAR(10) NOT NULL,
                won_at      TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()


def insert_winner(conn, user_id: int, shoe_size: str):
    """Insert a winning entry into the winners table."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO winners (user_id, shoe_size, won_at) VALUES (%s, %s, %s)",
            (user_id, shoe_size, datetime.now(timezone.utc)),
        )
        conn.commit()


# ── Main loop ────────────────────────────────────────────────────────────────


def main():
    print("🏆 Winner Processor Worker starting...")
    print(f"   Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"   PostgreSQL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"   Win probability: {WIN_PROBABILITY * 100:.0f}%")

    # Connect to Redis
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
    )

    # Connect to PostgreSQL and ensure table exists
    pg_conn = get_pg_connection()
    ensure_winners_table(pg_conn)

    processed = 0
    winners = 0

    print("🎯 Listening for raffle entries...\n")

    while True:
        try:
            # BLPOP blocks until an item is available (timeout=0 means block forever)
            result = redis_client.blpop(RAFFLE_QUEUE, timeout=5)

            if result is None:
                # Timeout, just loop back
                continue

            _queue_name, raw_entry = result
            entry = json.loads(raw_entry)

            user_id = entry["user_id"]
            shoe_size = entry["shoe_size"]
            processed += 1

            # 10% chance of winning
            is_winner = random.random() < WIN_PROBABILITY

            if is_winner:
                winners += 1
                insert_winner(pg_conn, user_id, shoe_size)
                print(
                    f"🎉 WINNER! User {user_id} (size {shoe_size}) "
                    f"[{winners}/{processed} total]"
                )
            else:
                print(
                    f"   User {user_id} (size {shoe_size}) — not selected "
                    f"[{processed} processed]"
                )

        except redis.ConnectionError:
            print("⚠️  Redis connection lost, retrying in 5s...")
            time.sleep(5)
        except psycopg2.OperationalError:
            print("⚠️  PostgreSQL connection lost, reconnecting...")
            try:
                pg_conn = get_pg_connection()
                ensure_winners_table(pg_conn)
            except Exception:
                time.sleep(5)
        except KeyboardInterrupt:
            print(f"\n👋 Shutting down. Processed {processed}, Winners: {winners}")
            break
        except Exception as exc:
            print(f"❌ Unexpected error: {exc}")
            time.sleep(1)


if __name__ == "__main__":
    main()
