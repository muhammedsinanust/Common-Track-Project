#!/bin/bash
# =============================================================
# start.sh — Start all services natively (no Docker)
# Run from the repo root
# =============================================================

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

# Load .env into this shell
set -a
source "$REPO_DIR/.env"
set +a

echo ""
echo "=========================================="
echo " Sneaker Store — Starting All Services"
echo "=========================================="

# ---- Helper: kill previous instances on a port ----
kill_port() {
    local port=$1
    local pid
    pid=$(lsof -ti tcp:"$port" 2>/dev/null) || true
    if [ -n "$pid" ]; then
        echo "  Killing existing process on port $port (PID $pid)"
        kill -9 "$pid" 2>/dev/null || true
        sleep 0.5
    fi
}

# ---- 1. Infrastructure checks ----
echo ""
echo "[infra] Checking Redis..."
if ! redis-cli ping &>/dev/null; then
    echo "  Starting Redis..."
    systemctl start redis-server 2>/dev/null || redis-server --daemonize yes
fi
echo "  Redis OK"

echo "[infra] Checking PostgreSQL..."
if ! pg_isready -q; then
    echo "  Starting PostgreSQL..."
    systemctl start postgresql 2>/dev/null
fi
echo "  PostgreSQL OK"

echo "[infra] Checking MongoDB..."
if ! mongosh --eval "db.adminCommand('ping')" --quiet &>/dev/null; then
    echo "  Starting MongoDB..."
    systemctl start mongod 2>/dev/null
    sleep 2
fi
echo "  MongoDB OK"

# ---- 2. Auth Service ----
echo ""
echo "[1/4] Starting Auth Service on port 8001..."
kill_port 8001
cd "$REPO_DIR/auth-service"
source .venv/bin/activate
DATABASE_URL="$DATABASE_URL" \
AUTH_SERVICE_PORT=8001 \
JWT_SECRET_KEY="$JWT_SECRET_KEY" \
nohup python main.py > "$LOG_DIR/auth-service.log" 2>&1 &
echo "  Auth Service PID=$! → logs/auth-service.log"
deactivate

# ---- 3. Product Service ----
echo ""
echo "[2/4] Starting Product Service on port 8002..."
kill_port 8002
cd "$REPO_DIR/product-service"
source .venv/bin/activate
MONGO_URI="$MONGO_URI" \
PRODUCT_SERVICE_PORT=8002 \
nohup python main.py > "$LOG_DIR/product-service.log" 2>&1 &
echo "  Product Service PID=$! → logs/product-service.log"
deactivate

# ---- 4. Raffle Service ----
echo ""
echo "[3/4] Starting Raffle Service on port 8003..."
kill_port 8003
cd "$REPO_DIR/raffle-service"
source .venv/bin/activate
REDIS_HOST=localhost \
REDIS_PORT=6379 \
RAFFLE_SERVICE_PORT=8003 \
nohup python main.py > "$LOG_DIR/raffle-service.log" 2>&1 &
echo "  Raffle Service PID=$! → logs/raffle-service.log"
deactivate

# ---- 5. Winner Worker ----
echo ""
echo "[4/4] Starting Winner Worker..."
cd "$REPO_DIR/winner-worker"
source .venv/bin/activate
REDIS_HOST=localhost \
REDIS_PORT=6379 \
ORDER_DB_HOST=localhost \
ORDER_DB_USER="$ORDER_DB_USER" \
ORDER_DB_PASSWORD="$ORDER_DB_PASSWORD" \
ORDER_DB_NAME="$ORDER_DB_NAME" \
PRODUCT_SERVICE_URL="$PRODUCT_SERVICE_URL" \
nohup python worker.py > "$LOG_DIR/winner-worker.log" 2>&1 &
echo "  Winner Worker PID=$! → logs/winner-worker.log"
deactivate

# ---- 6. Frontend (dev server on port 3000) ----
echo ""
echo "[frontend] Starting React dev server on port 3000..."
kill_port 3000
cd "$REPO_DIR/frontend"
REACT_APP_AUTH_SERVICE_URL=http://localhost:8001 \
REACT_APP_PRODUCT_SERVICE_URL=http://localhost:8002 \
REACT_APP_RAFFLE_SERVICE_URL=http://localhost:8003 \
HOST=0.0.0.0 \
nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
echo "  Frontend PID=$! → logs/frontend.log"

# ---- Done ----
echo ""
echo "=========================================="
echo " All services started!"
echo ""
echo " Frontend    → http://localhost:3000"
echo " Auth API    → http://localhost:8001/docs"
echo " Product API → http://localhost:8002/docs"
echo " Raffle API  → http://localhost:8003/docs"
echo ""
echo " Logs in: $LOG_DIR/"
echo ""
echo " To stop all: ./stop.sh"
echo "=========================================="
