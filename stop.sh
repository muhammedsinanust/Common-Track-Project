#!/bin/bash
# =============================================================
# stop.sh — Stop all Sneaker Store services
# =============================================================

echo ""
echo "Stopping all Sneaker Store services..."

for port in 8001 8002 8003 3000; do
    pid=$(lsof -ti tcp:"$port" 2>/dev/null) || true
    if [ -n "$pid" ]; then
        echo "  Killing port $port (PID $pid)"
        kill -9 "$pid" 2>/dev/null || true
    fi
done

# Kill winner worker by name (no fixed port)
pkill -f "worker.py" 2>/dev/null && echo "  Killed winner-worker" || true

echo "Done. All services stopped."
