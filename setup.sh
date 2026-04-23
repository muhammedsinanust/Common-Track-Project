#!/bin/bash
# =============================================================
# setup.sh — Install ALL system dependencies and configure DBs
# Run once as root (or with sudo) on a fresh Ubuntu instance
# =============================================================
set -e

echo ""
echo "=========================================="
echo " Sneaker Store — System Setup"
echo "=========================================="

# ---- 1. System packages ----
echo ""
echo "[1/7] Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    postgresql postgresql-client \
    redis-server \
    gnupg curl wget \
    nginx \
    git

# ---- 2. Node.js 18 ----
echo ""
echo "[2/7] Installing Node.js 18..."
if ! command -v node &>/dev/null || [[ "$(node --version)" != v18* ]]; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y -qq nodejs
fi
echo "Node: $(node --version), npm: $(npm --version)"

# ---- 3. MongoDB 6 ----
echo ""
echo "[3/7] Installing MongoDB 6..."
if ! command -v mongod &>/dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" \
        > /etc/apt/sources.list.d/mongodb-org-6.0.list
    apt-get update -qq
    apt-get install -y -qq mongodb-org
fi
systemctl enable mongod
systemctl start mongod
echo "MongoDB started"

# ---- 4. PostgreSQL — create users and databases ----
echo ""
echo "[4/7] Configuring PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

# Auth DB
sudo -u postgres psql -c "CREATE USER authuser WITH PASSWORD 'authpassword123';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE authdb OWNER authuser;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE authdb TO authuser;" 2>/dev/null || true

# Order DB (winner worker)
sudo -u postgres psql -c "CREATE USER orderuser WITH PASSWORD 'orderpassword123';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE orderdb OWNER orderuser;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE orderdb TO orderuser;" 2>/dev/null || true

echo "PostgreSQL databases ready: authdb, orderdb"

# ---- 5. Redis ----
echo ""
echo "[5/7] Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server
echo "Redis started"

# ---- 6. Python virtual envs and pip install ----
echo ""
echo "[6/7] Installing Python dependencies..."

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

for service in auth-service product-service raffle-service winner-worker load-tester; do
    if [ -d "$REPO_DIR/$service" ]; then
        echo "  → $service"
        python3 -m venv "$REPO_DIR/$service/.venv"
        "$REPO_DIR/$service/.venv/bin/pip" install -q --upgrade pip
        "$REPO_DIR/$service/.venv/bin/pip" install -q -r "$REPO_DIR/$service/requirements.txt"
    fi
done

# ---- 7. Frontend npm install ----
echo ""
echo "[7/7] Installing frontend dependencies..."
cd "$REPO_DIR/frontend"
npm install --silent

echo ""
echo "=========================================="
echo " Setup complete!"
echo " Next: run ./start.sh"
echo "=========================================="
