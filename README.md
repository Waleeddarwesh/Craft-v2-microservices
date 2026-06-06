# 🧶 Craft Application — v2.0 Microservices Architecture

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![Django REST Framework](https://img.shields.io/badge/DRF-REST%20APIs-red)
![FastAPI](https://img.shields.io/badge/FastAPI-Realtime%20%26%20ML-teal)
![Docker](https://img.shields.io/badge/Docker-Microservices-blue)
![Traefik](https://img.shields.io/badge/Traefik-API%20Gateway-cyan)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Service%20Databases-336791)
![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Events-dc382d)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange)
![Grafana](https://img.shields.io/badge/Grafana-Observability-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Overview

**Craft v2.0** is a production-oriented microservices evolution of the original Craft platform: a multi-vendor handcraft marketplace combined with e-learning, real-time communication, delivery workflows, analytics, support operations, and intelligent recommendations.

This version moves the platform from a modular monolithic backend into a distributed microservices ecosystem where each business domain is isolated, independently deployable, and designed for scalability.

Craft v2.0 focuses on:

- 🧩 Domain-driven microservice separation
- 🚪 Centralized API Gateway routing with Traefik
- 🔐 Dedicated authentication and RBAC service
- 🛒 Independent catalog, order, payment, platform, and reporting services
- ⚡ FastAPI-based real-time notification service
- 🤖 FastAPI-based recommendation and ML service
- 🐳 Full Docker Compose orchestration
- 📊 Prometheus and Grafana observability
- ♻️ Shared internal Python package for common logic

---

## 🧠 From Monolith to Microservices

Previous Craft versions focused on building a large production-ready Django backend with e-commerce, e-learning, chat, delivery, analytics, security, support tickets, disputes, recommendations, audit logs, and GDPR-oriented privacy features.

**Craft v2.0** restructures these capabilities into independent services to improve:

| Area | Improvement |
|---|---|
| Scalability | Scale heavy services independently, such as orders, real-time notifications, or ML recommendations |
| Maintainability | Smaller codebases per domain with clearer ownership |
| Deployment | Deploy, rebuild, or restart one service without affecting the full platform |
| Reliability | Failure in one service is isolated from the rest of the system |
| Team Workflow | Multiple developers can work on different services in parallel |
| Security | Sensitive domains such as authentication and payments are isolated |
| Observability | Metrics and logs can be tracked per service |

---

## 🏗️ Architecture Overview

Craft v2.0 is composed of multiple backend services communicating through HTTP APIs and internal service clients. External traffic enters through **Traefik**, which acts as the API Gateway and routes requests based on path prefixes.

```text
Client Apps
    |
    v
Traefik API Gateway
    |
    |-- /api/auth/        -> Auth Service
    |-- /api/catalog/     -> Catalog Service
    |-- /api/orders/      -> Order Service
    |-- /api/payments/    -> Payment Service
    |-- /api/platform/    -> Platform Service
    |-- /api/reports/     -> Reporting Service
    |-- /ws/              -> Realtime Service
    |-- /api/ml/          -> ML Service
    |
    v
Independent Databases, Redis, Monitoring, and Internal Services
```

---

## 🧩 Microservices

| Service | Technology | Main Responsibility | Port |
|---|---|---|---|
| **Auth Service** | Django + DRF | Users, JWT authentication, profiles, RBAC, permissions | `8001` |
| **Catalog Service** | Django + DRF | Products, categories, materials, inventory, search, filtering | `8002` |
| **Order Service** | Django + DRF | Cart, checkout, orders, shipping workflow, returns | `8003` |
| **Payment Service** | Django + DRF | Stripe integration, payment intents, webhooks, wallets, refunds | `8004` |
| **Platform Service** | Django + DRF | Reviews, support tickets, disputes, moderation, notification preferences | `8005` |
| **Reporting Service** | Django + DRF | Analytics, reports, supplier insights, admin metrics | `8006` |
| **Realtime Service** | FastAPI | WebSockets, real-time notifications, live updates | `8007` |
| **ML Service** | FastAPI | Recommendation engine, personalization, scoring APIs | `8008` |

---

## 🚪 API Gateway Routing

Craft uses **Traefik** as a reverse proxy and API Gateway.

| Public Path | Routed Service |
|---|---|
| `/api/auth/` | Auth Service |
| `/api/catalog/` | Catalog Service |
| `/api/orders/` | Order Service |
| `/api/payments/` | Payment Service |
| `/api/platform/` | Platform Service |
| `/api/reports/` | Reporting Service |
| `/ws/` | Realtime Service |
| `/api/ml/` | ML Service |
| `/dashboard/` | Traefik Dashboard |

Example:

```text
http://localhost/api/auth/
http://localhost/api/catalog/
http://localhost/api/orders/
http://localhost/api/payments/
```

---

## 📦 Repository Structure

```text
craft-v2-microservices/
│
├── services/
│   ├── auth-service/
│   ├── catalog-service/
│   ├── order-service/
│   ├── payment-service/
│   ├── platform-service/
│   ├── reporting-service/
│   ├── realtime-service/
│   └── ml-service/
│
├── shared/
│   └── craft-common/
│       └── craft_common/
│           ├── auth/
│           ├── api_clients/
│           ├── logging/
│           ├── middleware/
│           ├── models/
│           └── utils/
│
├── infrastructure/
│   ├── traefik/
│   ├── prometheus/
│   └── grafana/
│
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── verify_services.sh
└── README.md
```

---

## ♻️ Shared Library: `craft_common`

`craft_common` is an internal shared Python package mounted into multiple services.

It contains reusable logic such as:

- JWT authentication helpers
- Service-to-service API clients
- Common response formatters
- Shared exception handling
- Logging configuration
- Request correlation ID utilities
- Permission and role helpers
- Common constants and service URLs

This reduces duplication while keeping every microservice independent.

---

## 🔐 Authentication & Authorization

Authentication is centralized in the **Auth Service**.

The Auth Service handles:

- User registration and login
- JWT access and refresh tokens
- Role-Based Access Control
- Profile management
- Supplier, customer, delivery, and admin identities
- Permission validation for protected services

Other services validate incoming tokens using shared utilities from `craft_common`.

---

## 🛒 Main Platform Capabilities

### E-Commerce

- Multi-vendor product catalog
- Category and material management
- Inventory tracking
- Cart and checkout
- Order lifecycle management
- Delivery and shipping workflow
- Returns and refund requests

### E-Learning

- Supplier course publishing
- Course enrollment
- Video learning content
- Progress tracking
- Course reviews and engagement

### Payments

- Stripe payment intents
- Stripe webhook handling
- Wallet transactions
- Refund tracking
- Payment reconciliation-ready structure

### Platform Operations

- Product and course reviews
- Review moderation
- Support tickets
- Ticket replies
- Dispute resolution
- Notification preferences

### Real-Time System

- WebSocket notifications
- Live user updates
- Event-driven notification delivery
- Redis-backed real-time communication support

### Analytics & Reporting

- Supplier analytics
- Sales metrics
- Return rates
- Top products
- Admin reporting endpoints
- Service health metrics

### Machine Learning

- Personalized recommendations
- Product scoring
- User interaction tracking
- Recommendation fallback strategies

---

## 🐳 Running with Docker Compose

The full microservices ecosystem can be started using Docker Compose.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Waleeddarwesh/Micoservices_Craft.git
cd craft-v2-microservices
```

### 2️⃣ Create Environment File

```bash
cp .env.example .env
```

Update the required values inside `.env`, especially:

```ini
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
POSTGRES_USER=craft
POSTGRES_PASSWORD=craft_password
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
REDIS_URL=redis://redis:6379/0
```

### 3️⃣ Build and Start All Services

```bash
docker compose up --build -d
```

### 4️⃣ Check Running Containers

```bash
docker compose ps
```

### 5️⃣ View Logs

```bash
docker compose logs -f
```

For a specific service:

```bash
docker compose logs -f auth_service
docker compose logs -f catalog_service
docker compose logs -f realtime_service
```

---

## 🗄️ Database Migrations

Each Django microservice owns its database schema and migrations.

Run migrations per service:

```bash
docker compose exec auth_service python manage.py migrate
docker compose exec catalog_service python manage.py migrate
docker compose exec order_service python manage.py migrate
docker compose exec payment_service python manage.py migrate
docker compose exec platform_service python manage.py migrate
docker compose exec reporting_service python manage.py migrate
```

Create an admin user in the Auth Service:

```bash
docker compose exec auth_service python manage.py createsuperuser
```

---

## 🌱 Seed Demo Data

If demo seed commands are available, run them service by service:

```bash
docker compose exec auth_service python manage.py seed_demo_data
docker compose exec catalog_service python manage.py seed_demo_data
docker compose exec order_service python manage.py seed_demo_data
```

---

## ✅ Service Verification

Run the global verification script:

```bash
bash verify_services.sh
```

The script can be used to check:

- Django configuration validity
- Missing migrations
- Service health
- Environment variable availability
- Import errors
- Basic endpoint readiness

You can also check services manually:

```bash
curl http://localhost/api/auth/health/
curl http://localhost/api/catalog/health/
curl http://localhost/api/orders/health/
curl http://localhost/api/payments/health/
```

---

## 📊 Monitoring & Observability

Craft v2.0 includes monitoring infrastructure using **Prometheus** and **Grafana**.

| Tool | Purpose | URL |
|---|---|---|
| Traefik Dashboard | Gateway routes and service status | `http://localhost:8080` |
| Prometheus | Metrics collection | `http://localhost:9090` |
| Grafana | Dashboards and visualization | `http://localhost:3000` |

Recommended service metrics:

- Request count
- Response time
- Error rate
- Database availability
- Redis availability
- WebSocket connections
- Payment webhook failures
- Order creation rate
- Recommendation API latency

---

## 🔁 Service Communication

Craft v2.0 supports two communication styles:

### 1. Synchronous HTTP Communication

Used when a service needs immediate data from another service.

Examples:

- Order Service validates product data from Catalog Service
- Payment Service verifies order payment status
- Reporting Service collects aggregated metrics

### 2. Event-Driven Communication

Used for asynchronous workflows and decoupled processing.

Examples:

- Order created → notify user
- Payment succeeded → update order status
- Review approved → update product rating
- Refund processed → notify customer
- Product viewed → update recommendation signals

---

## 🧪 API Documentation

Each service can expose independent API documentation.

Suggested documentation URLs:

```text
http://localhost/api/auth/docs/
http://localhost/api/catalog/docs/
http://localhost/api/orders/docs/
http://localhost/api/payments/docs/
http://localhost/api/platform/docs/
http://localhost/api/reports/docs/
http://localhost/api/ml/docs/
```

---

## 🔐 Environment Variables

Example `.env` structure:

```ini
# Global
ENVIRONMENT=development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Security
SECRET_KEY=change_me
JWT_SECRET_KEY=change_me
CORS_ALLOWED_ORIGINS=http://localhost

# PostgreSQL
POSTGRES_USER=craft
POSTGRES_PASSWORD=craft_password

# Service Databases
AUTH_DB_NAME=craft_auth
CATALOG_DB_NAME=craft_catalog
ORDER_DB_NAME=craft_orders
PAYMENT_DB_NAME=craft_payments
PLATFORM_DB_NAME=craft_platform
REPORTING_DB_NAME=craft_reporting

# Redis
REDIS_URL=redis://redis:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Internal Service URLs
AUTH_SERVICE_URL=http://auth-service:8001
CATALOG_SERVICE_URL=http://catalog-service:8002
ORDER_SERVICE_URL=http://order-service:8003
PAYMENT_SERVICE_URL=http://payment-service:8004
PLATFORM_SERVICE_URL=http://platform-service:8005
REPORTING_SERVICE_URL=http://reporting-service:8006
REALTIME_SERVICE_URL=http://realtime-service:8007
ML_SERVICE_URL=http://ml-service:8008
```

---

## 🧰 Development Commands

### Rebuild One Service

```bash
docker compose build auth-service
docker compose up -d auth-service
```

### Restart One Service

```bash
docker compose restart catalog-service
```

### Open Shell Inside a Service

```bash
docker compose exec order_service bash
```

### Run Django Checks

```bash
docker compose exec auth_service python manage.py check
docker compose exec catalog_service python manage.py check
```

### Run Tests

```bash
docker compose exec auth_service python manage.py test
docker compose exec catalog_service python manage.py test
docker compose exec order_service python manage.py test
```

## 🤝 Contributing

### 1️⃣ Fork the Repository

```bash
git fork https://github.com/Waleeddarwesh/Micoservices_Craft
```

### 2️⃣ Create a Feature Branch

```bash
git checkout -b feature/service-enhancement
```

### 3️⃣ Commit Your Changes

```bash
git commit -m "Add service enhancement"
```

### 4️⃣ Push to GitHub

```bash
git push origin feature/service-enhancement
```

### 5️⃣ Open a Pull Request

Open a pull request and describe the service, feature, or infrastructure change clearly.

---

## 📞 Contact

### Waleed Darwesh

**Django Backend Developer | Junior Cloud DevOps Engineer**

📧 Email: [Waleeddarwesh2002@gmail.com](mailto:Waleeddarwesh2002@gmail.com)

🔗 LinkedIn: [Waleed Darwesh](https://www.linkedin.com/in/waleeddarwesh1/)

🐙 GitHub: [Waleeddarwesh](https://github.com/Waleeddarwesh)

🐳 Docker Hub: [waleeddarwesh](https://hub.docker.com/u/waleeddarwesh)

---