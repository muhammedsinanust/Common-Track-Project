# Quick Reference - Sneaker Store Microservices

## 🚀 Quick Start

```bash
# Build and start all services
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 📋 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Web UI (React + Nginx) |
| API Gateway | 8000 | Main API entry point |
| Auth Service | 8001 | Authentication |
| Product Service | 8002 | Product catalog |
| Raffle Service | 8003 | Raffle entries |
| Locust UI | 8089 | Load testing UI |
| PostgreSQL Auth | 5432 | Auth database |
| PostgreSQL Order | 5433 | Winners database |
| MongoDB | 27017 | Products database |
| Redis | 6379 | Raffle queue |

## 🔑 Default Credentials

```
Database: authuser / authpassword123
Database: orderuser / orderpassword123
MongoDB: root / password
JWT Secret: (in .env)
```

## 📁 Important Files

- `.env` - Environment configuration
- `docker-compose.yml` - Service orchestration
- `README.md` - Full documentation
- `TESTING.md` - Testing guide
- `setup.sh` - Automated setup script
- `init-data.sh` - Sample data initialization

## 🔍 Common Commands

### View Logs
```bash
docker-compose logs -f [service]        # Specific service
docker-compose logs -f --tail=50        # Last 50 lines
docker-compose logs api-gateway -f      # API Gateway logs
```

### Database Access
```bash
# PostgreSQL
docker-compose exec auth-db psql -U authuser -d authdb

# MongoDB
docker-compose exec product-db mongosh -u root -p password

# Redis
docker-compose exec redis-broker redis-cli
```

### Stop & Clean
```bash
docker-compose down                     # Stop services
docker-compose down -v                  # Remove volumes too
docker-compose restart [service]        # Restart service
```

## 🧪 Testing

### Manual API Test
```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","username":"user","password":"pass"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass"}'
```

### Load Test
```bash
# Web UI (navigate to http://localhost:8089)
docker-compose up load-tester

# Headless (5000 users)
docker-compose exec load-tester locust \
  -f locustfile.py \
  --host=http://api-gateway:8000 \
  -u 5000 -r 100 --run-time 5m --headless
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `.env` or `docker-compose.yml` |
| Database connection refused | Wait 10s, check `docker-compose ps` |
| Services not starting | Check logs: `docker-compose logs` |
| Load test not connecting | Verify API Gateway: `curl http://localhost:8000/health` |
| High error rate | Restart services: `docker-compose restart` |

## 📊 Monitoring During Load Test

```bash
# Terminal 1: Monitor containers
docker stats

# Terminal 2: Monitor Redis queue
docker-compose exec redis-broker redis-cli LLEN raffle_queue

# Terminal 3: Watch worker logs
docker-compose logs winner-worker -f

# Terminal 4: Check database connections
docker-compose exec order-db psql -U orderuser -d orderdb \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🎯 Architecture Summary

```
Frontend (3000)
    ↓
API Gateway (8000)
    ├→ Auth Service (8001) → PostgreSQL (5432)
    ├→ Product Service (8002) → MongoDB (27017)
    └→ Raffle Service (8003) → Redis (6379)
         ↓
    Winner Worker → PostgreSQL (5433)
```

## 🔐 Authentication Flow

```
1. POST /api/auth/register  → Create user
2. POST /api/auth/login     → Get JWT token
3. Use token in headers:    → Authorization: Bearer <token>
4. Token valid for:        → 24 hours (configurable)
```

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| Raffle throughput | 10,000+ req/s |
| API response time | < 100ms (p50) |
| Worker processing | 1,000+ entries/min |
| Error rate | < 0.1% |
| Availability | 99.9%+ |

## 🛠️ Development Workflow

```bash
# 1. Make changes to service code
# 2. Rebuild and restart
docker-compose build [service]
docker-compose up -d [service]

# 3. View logs to verify
docker-compose logs [service] -f

# 4. Test endpoint
curl http://localhost:8000/api/...
```

## 🚨 Emergency Commands

```bash
# Force restart everything
docker-compose down && docker-compose up -d

# Clean everything (careful!)
docker-compose down -v
rm -rf volumes/
docker-compose up -d

# View resource usage
docker stats

# Kill a stuck container
docker-compose kill [service]

# View environment
docker-compose exec [service] env
```

## 📚 Additional Resources

- `README.md` - Full documentation
- `TESTING.md` - Comprehensive testing guide
- `.env` - Configuration reference
- `setup.sh` - Automated setup
- `init-data.sh` - Sample data

## 🎓 Key Concepts

- **Microservices**: Each service is independent
- **Docker Network**: All services on "sneaker-net" bridge
- **JWT**: Stateless authentication (no sessions)
- **RBAC**: Role-based access (user/admin)
- **Redis Queue**: Async raffle processing
- **Horizontal Scaling**: Services can run multiple instances
- **Health Checks**: Automatic recovery
- **Environment Variables**: No hardcoded configs

## 🔗 API Endpoints Quick Reference

### Auth
```
POST /api/auth/register
POST /api/auth/login
GET /api/auth/profile (protected)
```

### Products
```
GET /api/products (public)
POST /api/products (admin)
PUT /api/products/{id} (admin)
DELETE /api/products/{id} (admin)
```

### Raffle
```
POST /api/raffle/enter-raffle (protected)
GET /api/raffle/raffle-stats (public)
```

---

**Last updated**: 2024-12-20
**Version**: 1.0.0
