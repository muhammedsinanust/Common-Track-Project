# 🔥 SneakerDrop — Microservices E-Commerce Platform

A containerized microservices e-commerce application for a sneaker store featuring a high-traffic **"Fresh Drops"** queuing system with raffle-based purchasing.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────┐
│   Frontend   │────▶│ Auth Service  │────▶│   PostgreSQL    │     │       │
│  React + TW  │     │  :8001       │     │  (users)        │     │       │
└──────┬───────┘     └──────────────┘     └─────────────────┘     │       │
       │                                                           │ Redis │
       │             ┌──────────────┐     ┌─────────────────┐     │       │
       ├────────────▶│Product Service│────▶│    MongoDB       │     │       │
       │             │  :8002       │     │  (products)     │     │       │
       │             └──────────────┘     └─────────────────┘     │       │
       │                                                           │       │
       │             ┌──────────────┐            │                 │       │
       └────────────▶│Raffle Ingress│───LPUSH───▶│  raffle_queue  │◀─BLPOP─┐
                     │  :8003       │            │                 │        │
                     └──────────────┘            └────────┘        │        │
                                                                   │        │
                                                    ┌──────────────┘        │
                                                    │ Winner Worker         │
                                                    │ (background)          │
                                                    │        │              │
                                                    │        ▼              │
                                                    │  PostgreSQL           │
                                                    │  (winners)            │
                                                    └───────────────────────┘
```

## Services

| Service | Tech | Port | Description |
|---------|------|------|-------------|
| **Frontend** | React + Tailwind CSS | 3000 | SPA with registration, login, storefront, and Fresh Drop UI |
| **Auth Service** | Python FastAPI | 8001 | User registration, login, JWT authentication |
| **Product Service** | Python FastAPI | 8002 | Sneaker inventory and drop timestamp management |
| **Raffle Ingress** | Python FastAPI | 8003 | Accepts raffle entries, pushes to Redis queue |
| **Winner Worker** | Python | — | Background processor, picks winners from Redis queue |
| **Load Tester** | Python Locust | 8089 | Simulates 5,000 concurrent raffle entries |

## Environment Variables

All inter-service communication and database connections are configured via environment variables. See each service's README or Dockerfile for required variables.

### Auth Service
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — Secret key for JWT signing
- `JWT_ALGORITHM` — Algorithm (default: HS256)

### Product Service
- `MONGO_URL` — MongoDB connection string
- `MONGO_DB_NAME` — Database name

### Raffle Ingress
- `REDIS_HOST` — Redis hostname
- `REDIS_PORT` — Redis port
- `JWT_SECRET` — Shared JWT secret

### Winner Worker
- `REDIS_HOST` — Redis hostname
- `REDIS_PORT` — Redis port
- `DATABASE_URL` — PostgreSQL connection string

## Building & Running

Each service has its own `Dockerfile`. Build individually:

```bash
docker build -t sneakerdrop-frontend ./frontend
docker build -t sneakerdrop-auth ./auth-service
docker build -t sneakerdrop-product ./product-service
docker build -t sneakerdrop-raffle ./raffle-service
docker build -t sneakerdrop-worker ./winner-worker
docker build -t sneakerdrop-loadtest ./load-tester
```

Run each container with the appropriate environment variables and network configuration for your deployment target.
