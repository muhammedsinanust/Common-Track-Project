# 🔥 SneakerDrop — Microservices E-Commerce Platform

A containerized microservices sneaker store with a high-traffic **"Fresh Drops"** raffle queuing system. One command to run everything.

## Architecture

```
                        ┌─────────────────────────────────────────────────┐
                        │              Docker Compose Network             │
  Browser ─── :3000 ──▶ │                                                 │
                        │  ┌──────────┐   nginx reverse proxy             │
                        │  │ Frontend │──────────────────────┐             │
                        │  └──────────┘                      │             │
                        │       │                            │             │
                        │  /api/auth/*    /api/products/*  /api/raffle/*   │
                        │       │              │              │             │
                        │       ▼              ▼              ▼             │
                        │  ┌──────────┐  ┌───────────┐  ┌────────────┐    │
                        │  │   Auth   │  │  Product   │  │   Raffle   │    │
                        │  │  :8001   │  │   :8002    │  │   :8003    │    │
                        │  └────┬─────┘  └─────┬──────┘  └─────┬──────┘    │
                        │       │              │               │           │
                        │       ▼              ▼               ▼           │
                        │  ┌──────────┐  ┌───────────┐  ┌───────────┐     │
                        │  │ Postgres │  │  MongoDB   │  │   Redis   │     │
                        │  └──────────┘  └───────────┘  └─────┬─────┘     │
                        │       ▲                             │           │
                        │       │         BLPOP               │           │
                        │  ┌────┴──────────────────────────────┘           │
                        │  │  Winner Worker (background)      │           │
                        │  └──────────────────────────────────┘           │
                        └─────────────────────────────────────────────────┘
```

## Quick Start (EC2)

### 1. SSH into your Ubuntu EC2 and install Docker

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
exit
```

### 2. Clone and launch

```bash
git clone <YOUR_REPO_URL> sneakerdrop && cd sneakerdrop
docker compose up --build -d
```

That's it. The entire stack is running. Open `http://<EC2_PUBLIC_IP>:3000` in your browser.

### 3. Seed test data

```bash
# Create a sneaker
curl -s -X POST http://localhost:3000/api/products/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Air Max Phantom",
    "brand": "Nike",
    "description": "Limited edition phantom colorway with reactive foam sole",
    "price": 249.99,
    "image_url": "",
    "sizes": [
      {"size": "9", "quantity": 50},
      {"size": "10", "quantity": 50},
      {"size": "11", "quantity": 50}
    ]
  }'

# Copy the _id from the response, then schedule a drop (set time ~2 min from now):
curl -s -X POST http://localhost:3000/api/products/drops \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "<PASTE_PRODUCT_ID>",
    "drop_date": "2026-04-24T00:00:00Z",
    "is_active": true
  }'
```

### 4. Run load test (optional)

```bash
docker compose --profile loadtest up --build -d load-tester
```

Then open `http://<EC2_PUBLIC_IP>:8089`, set **5000 users**, spawn rate **100**, and start.

## Services

| Service | Tech | Internal Port | Description |
|---------|------|:---:|-------------|
| **frontend** | React + Tailwind + Nginx | 3000 (exposed) | SPA + reverse proxy for all API routes |
| **auth-service** | FastAPI + PostgreSQL | 8001 | Registration, login, JWT auth |
| **product-service** | FastAPI + MongoDB | 8002 | Sneaker inventory & drop scheduling |
| **raffle-service** | FastAPI + Redis | 8003 | Accepts raffle entries → Redis queue |
| **winner-worker** | Python | — | BLPOP from Redis, 10% win → PostgreSQL |
| **load-tester** | Locust | 8089 (exposed) | Simulates 5,000 concurrent users |

## Useful Commands

```bash
# View all logs
docker compose logs -f

# View a single service log
docker compose logs -f winner-worker

# Check running containers
docker compose ps

# Check winners in the database
docker compose exec postgres psql -U postgres -d sneakerdrop_auth \
  -c "SELECT * FROM winners ORDER BY won_at DESC LIMIT 20;"

# Check Redis queue length
docker compose exec redis redis-cli LLEN raffle_queue

# Stop everything
docker compose down

# Stop and wipe all data
docker compose down -v
```

## Environment Variables

All inter-service connections use env vars (set in `docker-compose.yml`):

| Variable | Used By | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | auth-service, winner-worker | PostgreSQL connection |
| `JWT_SECRET` | auth-service, raffle-service | Shared JWT signing key |
| `MONGO_URL` | product-service | MongoDB connection |
| `REDIS_HOST/PORT` | raffle-service, winner-worker | Redis connection |
| `WIN_PROBABILITY` | winner-worker | Chance of winning (default 0.10) |
| `AUTH_SERVICE_URL` | load-tester | Auth endpoint for test user login |

## Security Group

Ensure your EC2 security group allows inbound:

| Port | Purpose |
|------|---------|
| **3000** | Frontend + all API traffic |
| **8089** | Locust dashboard (optional) |
| **22** | SSH |
