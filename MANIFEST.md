# Project Structure & File Manifest

Complete file listing for the Sneaker Store Microservices Platform.

## Root Level Files

- **`.env`** - Environment configuration (ports, DB credentials, URLs)
- **`docker-compose.yml`** - Docker container orchestration (ALL services, networks, volumes)
- **`README.md`** - Comprehensive documentation
- **`TESTING.md`** - Detailed testing guide
- **`QUICKSTART.md`** - Quick reference guide
- **`.gitignore`** - Git ignore patterns
- **`.dockerignore`** - Docker build ignore patterns
- **`setup.sh`** - Automated setup script
- **`init-data.sh`** - Sample data initialization script

## API Gateway Service

Location: `api-gateway/`

- **`main.py`** - FastAPI application
  - Unified API routing
  - JWT validation & token injection
  - CORS configuration
  - Service discovery
  
- **`requirements.txt`** - Python dependencies
  - fastapi, uvicorn, httpx, pydantic, PyJWT, python-jose

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Health check configuration
  - Port 8000

## Auth & User Service

Location: `auth-service/`

- **`main.py`** - FastAPI application
  - User registration endpoint
  - JWT login endpoint
  - Profile retrieval
  - Password hashing (bcrypt)
  - Role-based access (RBAC)
  - SQLAlchemy ORM integration
  
- **`requirements.txt`** - Python dependencies
  - fastapi, uvicorn, sqlalchemy, psycopg2, bcrypt, PyJWT

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Health check configuration
  - Port 8001

## Product & Catalog Service

Location: `product-service/`

- **`main.py`** - FastAPI application
  - Product listing (public)
  - CRUD operations (admin only)
  - MongoDB integration
  - Inventory management
  - Drop timestamp support
  
- **`requirements.txt`** - Python dependencies
  - fastapi, uvicorn, pymongo, pydantic, PyJWT

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Health check configuration
  - Port 8002

## Raffle Ingress Service

Location: `raffle-service/`

- **`main.py`** - FastAPI application
  - High-throughput raffle entry ingestion
  - Redis queue integration
  - 202 Accepted responses
  - Statistics endpoint
  - No database connections (optimized for scale)
  
- **`requirements.txt`** - Python dependencies
  - fastapi, uvicorn, redis, pydantic, PyJWT

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Health check configuration
  - Port 8003

## Winner Processor Worker

Location: `winner-worker/`

- **`worker.py`** - Standalone Python application
  - Continuous Redis BLPOP from raffle queue
  - Synchronous entry processing
  - Stock verification via Product Service API
  - Winner record creation in order-db
  - Error handling & reconnection logic
  
- **`requirements.txt`** - Python dependencies
  - redis, sqlalchemy, psycopg2, httpx

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Background worker

## Frontend (React + Tailwind CSS)

Location: `frontend/`

### Configuration Files

- **`package.json`** - Node.js dependencies
  - react, react-router-dom, axios, jwt-decode
  - tailwindcss, postcss, autoprefixer
  
- **`tailwind.config.js`** - Tailwind CSS configuration
- **`postcss.config.js`** - PostCSS configuration
- **`Dockerfile`** - Multi-stage build
  - Build stage: Node 18 + npm build
  - Production stage: Nginx Alpine

### Source Code

Location: `frontend/src/`

- **`index.jsx`** - React app entry point
- **`App.jsx`** - Main router component
  - Navigation bar
  - Route definitions
  - Auth state management
  
- **`api.js`** - Axios API client
  - Base URL configuration
  - Authorization header injection
  - Service-specific API functions
  
- **`index.css`** - Global styles + Tailwind
  - Component utilities
  - Layout styling
  - Responsive design

- **`CountdownTimer.jsx`** - Countdown component
  - Real-time timer display
  - Days/Hours/Minutes/Seconds
  - "LIVE NOW" indicator
  
- **`ProductCard.jsx`** - Product display component
  - Product details
  - Countdown integration
  - Raffle entry form
  - Size selection

### Pages

Location: `frontend/src/pages/`

- **`Login.jsx`** - User login page
  - Email/password form
  - JWT token storage
  - Navigation to register
  
- **`Register.jsx`** - User registration page
  - Email/username/password form
  - Validation
  - Success redirect to login
  
- **`Storefront.jsx`** - Main product listing
  - Product grid layout
  - Public product catalog
  - Fresh drops display
  - Countdown timers
  
- **`Dashboard.jsx`** - Admin dashboard
  - Create new products
  - Manage inventory
  - Schedule drops
  - Admin-only access control

### Public Assets

Location: `frontend/public/`

- **`index.html`** - HTML template
  - React mount point
  - Metadata tags

## Load Testing

Location: `load-tester/`

- **`locustfile.py`** - Locust test scenarios
  - RaffleUser class (high-frequency raffle entries)
  - WebsiteUser class (light browsing)
  - Automatic user registration
  - JWT token acquisition
  - Performance metrics
  
- **`requirements.txt`** - Python dependencies
  - locust, requests

- **`Dockerfile`** - Container image definition
  - Python 3.11 base
  - Locust setup

## Infrastructure (Defined in docker-compose.yml)

### Databases

1. **auth-db** (PostgreSQL)
   - User credentials storage
   - Role information
   - Connection: postgresql://authuser:authpassword123@auth-db:5432/authdb
   - Port: 5432

2. **order-db** (PostgreSQL)
   - Winner records
   - Order tracking
   - Connection: postgresql://orderuser:orderpassword123@order-db:5432/orderdb
   - Port: 5433

3. **product-db** (MongoDB)
   - Product inventory
   - Drop information
   - Connection: mongodb://product-db:27017/productdb
   - Port: 27017

4. **redis-broker** (Redis)
   - Raffle queue (FIFO)
   - Real-time counters
   - Port: 6379

### Networks

- **sneaker-net** - Custom Docker bridge network
  - All services connected
  - Service discovery by name
  - Isolated from host

### Volumes

- **auth_db_data** - PostgreSQL auth database storage
- **order_db_data** - PostgreSQL order database storage
- **product_db_data** - MongoDB storage
- **redis_data** - Redis persistence

## File Statistics

```
Total Python Files:       6 (gateway, auth, product, raffle, worker + tests)
Total Node/React Files:   8 (components + pages)
Configuration Files:      7 (.env, compose, Dockerfiles, configs)
Documentation Files:      4 (README, TESTING, QUICKSTART, MANIFEST)
Database Files:           0 (generated at runtime)
Total Services:           6 (5 backend + 1 frontend)
Total Databases:          4 (2 PostgreSQL + 1 MongoDB + 1 Redis)
```

## Key Design Decisions

### API Gateway Pattern
- Unified entry point for all frontend requests
- JWT validation before routing
- No direct service-to-service communication from frontend
- CORS handled in one place

### Raffle Service Design
- No database connections (avoids connection pool exhaustion)
- Redis for async queue (supports 10,000+ req/sec)
- 202 Accepted for fire-and-forget raffle entries
- Worker pulls and processes asynchronously

### Stateless Services
- JWT instead of sessions
- All state in databases
- Horizontal scaling ready
- No sticky sessions required

### Docker Networking
- Custom bridge network "sneaker-net"
- Service discovery by hostname
- Internal communication only (no host exposure needed)
- Clean separation from host network

### Multi-Database Strategy
- PostgreSQL for transactional data (auth, winners)
- MongoDB for flexible product catalog
- Redis for high-speed queue
- Each database is right tool for its job

## Database Schemas (Auto-created)

### PostgreSQL Users Table (auth-db)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE,
    username VARCHAR UNIQUE,
    hashed_password VARCHAR,
    role VARCHAR DEFAULT 'user',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### PostgreSQL Winners Table (order-db)
```sql
CREATE TABLE winners (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id VARCHAR,
    shoe_size VARCHAR,
    entry_timestamp TIMESTAMP,
    processed_timestamp TIMESTAMP,
    status VARCHAR DEFAULT 'pending'
);
```

### MongoDB Products Collection
```json
{
    "_id": ObjectId(),
    "name": String,
    "brand": String,
    "size": String,
    "price": Float,
    "stock": Integer,
    "drop_timestamp": DateTime,
    "description": String,
    "created_at": DateTime,
    "updated_at": DateTime
}
```

---

**Total Lines of Code**: ~3,000+
**Total Configuration**: ~500 lines
**Documentation**: ~2,000 lines
**Docker Images**: 7 (6 custom + postgres/mongo/redis base)
**External Dependencies**: ~30 npm packages + ~30 pip packages
