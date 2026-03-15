# AWS eCommerce Platform

A full-stack eCommerce application built as an AI-assisted learning project. The system covers the complete shopping experience — product catalog, cart, checkout, user accounts, and admin management — deployed on AWS using infrastructure-as-code.

**Live URLs**
| App | URL |
|---|---|
| Customer Store | https://d3bwott4660u8l.cloudfront.net |
| Admin Dashboard | https://dtjlzqdyq53fa.cloudfront.net |

---

## Architecture Overview

![AWS eCommerce Platform — Design Overview](docs/design-overview.png)

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Architecture Overview](#architecture-overview)
3. [Design Decisions](#design-decisions)
4. [Backend Services](#backend-services)
5. [Frontend Applications](#frontend-applications)
6. [Infrastructure (AWS CDK)](#infrastructure-aws-cdk)
7. [Image Storage Flow](#image-storage-flow)
8. [Authentication](#authentication)
9. [Local Development](#local-development)
10. [Deployment](#deployment)
11. [Cost](#cost)

---

## Project Structure

```
aws-ecommerce-aidlc/
├── admin-api/          # FastAPI — product/category/inventory management
├── catalog-api/        # FastAPI — public read-only product browsing
├── cart-api/           # FastAPI — guest shopping cart
├── orders-api/         # FastAPI — checkout and order history
├── auth-api/           # FastAPI — user registration, login, JWT
├── admin-ui/           # React SPA — admin dashboard
├── catalog-ui/         # React SPA — customer storefront
├── nginx/              # Reverse proxy config
├── infra/              # AWS CDK (Python) — all infrastructure
├── docker-compose.prod.yml
└── docker-compose.yml  # Local development
```

---

## Architecture Overview

```
Browser
  │
  ├─ https://d3bwott4660u8l.cloudfront.net  (Catalog UI)
  │       ├── /* ─────────────────► S3: ecommerce-catalog-ui  (React SPA)
  │       └── /api/* ─────────────► EC2 t3.micro (nginx → API containers)
  │
  ├─ https://dtjlzqdyq53fa.cloudfront.net   (Admin UI)
  │       ├── /* ─────────────────► S3: ecommerce-admin-ui   (React SPA)
  │       └── /api/* ─────────────► EC2 t3.micro (nginx → API containers)
  │
  └─ https://d2uwk625use1bh.cloudfront.net  (Product Images CDN)
          └── /uploads/* ─────────► S3: ecommerce-uploads    (private, OAC)


EC2: t3.micro  (Elastic IP: 100.22.44.133)
  └── nginx :80
        ├── /api/admin   → admin-api  :8000
        ├── /api/catalog → catalog-api :8001
        ├── /api/cart    → cart-api   :8002
        ├── /api/orders  → orders-api :8003
        └── /api/auth    → auth-api   :8004
```

---

## Design Decisions

### 1. `/api/*` URL Prefix for All API Routes

**Problem:** Both React SPAs use client-side routing (React Router), which means URLs like `/products` and `/cart` are handled by the frontend — not the server. CloudFront needs a way to distinguish between requests that should go to the S3 bucket (SPA assets) and requests that should go to the EC2 instance (API calls).

**Decision:** All backend API routes are prefixed with `/api/`. This gives CloudFront a clean, unambiguous rule:
- `/api/*` → EC2 (API, caching disabled, all HTTP methods)
- `/*` → S3 (static assets, caching enabled)

Without this prefix, every API call URL would have to be listed as a separate CloudFront behavior, and any new route would require a CloudFront config change. With `/api/*`, the routing is permanent and zero-maintenance.

**How it works end-to-end:**
- Frontend calls `/api/catalog/products`
- CloudFront matches `/api/*` → forwards to EC2
- Nginx on EC2 strips `/api/` prefix → proxies to `http://catalog-api:8001/catalog/products`
- FastAPI handles the request at `/catalog/products`

The Vite dev proxy replicates the same rewriting locally, so `baseURL: '/api/catalog'` works identically in both development and production.

---

### 2. Single EC2 Instance with Docker Compose

**Decision:** Run all five API containers and nginx on a single `t3.micro` EC2 instance using Docker Compose, rather than separate EC2s or ECS/Fargate.

**Why:**
- Keeps the project within AWS Free Tier limits
- Docker Compose provides service dependencies (`depends_on: condition: service_healthy`), restart policies, and shared volumes with minimal configuration overhead
- A single instance avoids cross-instance networking complexity while still maintaining service isolation via Docker networking
- Easy to SSH in and debug with `docker compose logs`

**Trade-off:** No horizontal scaling, no fault isolation between services. Acceptable for a learning project; a production system would use ECS Fargate or Kubernetes with independent scaling per service.

---

### 3. SQLite on a Shared Docker Volume

**Decision:** Use SQLite files on a Docker named volume (`/data/`) mounted into all containers, rather than a managed database like RDS.

**Why:**
- Zero cost (avoids ~$15–25/month for RDS db.t3.micro)
- SQLite read concurrency is sufficient for a low-traffic learning project
- The shared volume pattern allows `catalog-api` and `orders-api` to read `admin.db` without duplicating data or adding an inter-service API call

**How the databases are split:**

| File | Owner | Shared readers |
|---|---|---|
| `admin.db` | admin-api | catalog-api (products), cart-api (stock check), orders-api (inventory deduction) |
| `cart.db` | cart-api | orders-api (reads + clears cart on checkout) |
| `orders.db` | orders-api | — |
| `auth.db` | auth-api | — |

**Trade-off:** SQLite has write serialization — only one writer at a time. Under concurrent write load, this would become a bottleneck. For a learning project with occasional writes, it's invisible in practice.

---

### 4. CloudFront + S3 for Static Frontends (No EC2 Involvement)

**Decision:** Build the React SPAs into static files and host them on S3, served via CloudFront — not served by the EC2 instance.

**Why:**
- Global edge caching means the HTML/JS/CSS is served from AWS PoPs close to the user, not from a single us-west-2 EC2
- EC2 is relieved of static asset serving entirely — it only handles API traffic
- S3 + CloudFront costs essentially nothing at low traffic (1 TB/month CloudFront free tier)
- SPA deep-linking works by returning `index.html` on 403/404 from S3 (configured as CloudFront error responses), letting React Router handle the route client-side

**Origin Access Control (OAC):** All three S3 buckets block public access entirely. CloudFront authenticates to S3 using OAC (the current AWS-recommended approach, replacing the deprecated Origin Access Identity). This means no S3 object is ever directly accessible — everything goes through CloudFront.

---

### 5. No NAT Gateway

**Decision:** The VPC uses a single public subnet with no NAT Gateway.

**Why:** A NAT Gateway costs ~$32/month in us-west-2 — more than the EC2 instance itself. Since the EC2 has an Elastic IP and lives in a public subnet, it reaches the internet directly (for Docker image pulls, GitHub clone, etc.) without needing NAT.

**Private subnets were skipped** because there are no resources (RDS, Lambda, etc.) that need to be isolated from the internet. Adding private subnets without NAT would prevent those resources from reaching the internet at all.

---

### 6. Elastic IP

**Decision:** Attach an Elastic IP to the EC2 instance rather than using the default AWS-assigned public IP.

**Why:** The default public IP changes every time the instance is stopped and started. The CloudFront distribution has the EC2 DNS hostname hardcoded as its custom origin (`ec2-100-22-44-133.us-west-2.compute.amazonaws.com`). If the IP changed, this hostname would resolve to a different address and all API traffic would break.

The Elastic IP is free while attached to a running instance. It only incurs a charge ($0.005/hr) if the instance is stopped but the EIP remains allocated — a reminder to deallocate or restart the instance.

---

### 7. CloudFront Cannot Use Raw IP Addresses as Origins

**Lesson learned:** When configuring a CloudFront distribution with a custom HTTP origin, CloudFront rejects raw IP addresses (e.g., `100.22.44.133`) as the origin domain. It requires a DNS hostname.

**Solution:** Use the EC2 public DNS hostname (`ec2-{ip-dashes}.{region}.compute.amazonaws.com`) which AWS automatically provides for every instance with a public IP. This resolves to the same Elastic IP but satisfies CloudFront's hostname requirement.

---

### 8. Sequential Docker Builds on t3.micro

**Problem:** Running `docker compose up --build` on a 1 GB RAM t3.micro causes an OOM (out-of-memory) kill mid-build. Each Python service runs `pip install` during build, and five parallel `pip install` processes each consume ~200–300 MB simultaneously, exhausting available RAM.

**Solution (applied in two places):**

1. **At deploy time (user-data script):** Build images sequentially with `docker compose build` one service at a time — not in parallel.

2. **2 GB swap file:** Added to the EC2 instance at boot:
   ```bash
   fallocate -l 2G /swapfile
   chmod 600 /swapfile
   mkswap /swapfile
   swapon /swapfile
   echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
   ```
   This gives the OS overflow memory when RAM is exhausted during builds, preventing the OOM kill. Persisted across reboots via `/etc/fstab`.

---

### 9. EC2 IAM Role Scoped to Uploads Bucket Only

**Decision:** The EC2 instance profile grants `s3:GetObject` / `s3:PutObject` on the uploads bucket only — not the frontend buckets.

**Why:** Principle of least privilege. The API containers only need to read/write product images. The frontend buckets hold static build artifacts that are deployed once from a developer machine (or CI/CD), not written by the running application.

**Consequence during this project:** When deploying the frontend `dist/` builds, we couldn't use `aws s3 sync` from EC2 — we had to download the built files via `scp` and upload from the local machine using root AWS credentials.

---

### 10. Guest Cart via Session Token

**Decision:** The cart does not require a user account. A random UUID is generated client-side on first visit and stored in `localStorage` as `cart_session_token`. It is sent as an `X-Session-Token` header on every cart API request.

**Why:** Forcing login before adding to cart is a known conversion killer in eCommerce. The guest cart pattern lets users browse and add items without friction, then optionally create an account at checkout.

The token has no expiry and persists until localStorage is cleared. Cart data lives in `cart.db` keyed by this token.

---

## Backend Services

All services are Python 3.13 + FastAPI + SQLAlchemy + SQLite. Each has its own Docker image, database file, and `pydantic-settings` configuration with a service-specific env prefix.

| Service | Port | Env Prefix | Database |
|---|---|---|---|
| `admin-api` | 8000 | `ADMIN_` | `admin.db` |
| `catalog-api` | 8001 | `CATALOG_` | `admin.db` (read) |
| `cart-api` | 8002 | `CART_` | `cart.db` |
| `orders-api` | 8003 | `ORDERS_` | `orders.db` |
| `auth-api` | 8004 | `AUTH_` | `auth.db` |

### Admin API
Manages all product data. Key capabilities:
- Full CRUD for products, categories, inventory
- Product image upload — uploads to S3 when `ADMIN_S3_BUCKET_NAME` is set, falls back to local disk in dev
- Product audit log — every field change recorded automatically via `update_product()`
- Stock audit log — every quantity change recorded via `update_stock()`
- 6 ORM models: `Category`, `Product`, `ProductImage`, `ProductAuditLog`, `Inventory`, `StockAuditLog`

### Catalog API
Read-only view of `admin.db`. Exposes products for the customer storefront with filtering, sorting, search, and pagination. Shares the same SQLite file via the Docker volume — no data duplication, no sync needed.

### Cart API
Guest cart identified by `X-Session-Token`. On item add/update, validates requested quantity against current stock in `admin.db` (read-only cross-DB access). Rejects adds that would exceed available stock.

### Orders API
Checkout flow in a single database transaction:
1. Read cart items from `cart.db`
2. Deduct inventory in `admin.db`
3. Create order record in `orders.db`
4. Clear cart in `cart.db`

Atomic across SQLite files via separate sessions — not a true distributed transaction, but sufficient for this scale.

### Auth API
- Passwords: bcrypt hashed via `passlib`
- Tokens: JWT signed with a 64-byte secret (`AUTH_JWT_SECRET`) generated at EC2 boot via `openssl rand -hex 32`
- Email validation: pydantic `EmailStr`
- Routes: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `PATCH /auth/me`

---

## Frontend Applications

Both apps: **React 19 + TypeScript + Vite + Tailwind CSS**.

### Catalog UI — Customer Storefront

| Page | Route |
|---|---|
| Home (featured products) | `/` |
| Product grid + filters | `/products` |
| Product detail + gallery | `/products/:id` |
| Search results | `/search?q=...` |
| Shopping cart | `/cart` |
| Checkout | `/checkout` |
| Order confirmation | `/orders/:id` |
| Order history | `/orders` |
| Login | `/login` |
| Register | `/register` |
| Profile | `/profile` |

State is managed via two React contexts:
- **`CartContext`** — cart items, item count badge, add/update/remove/clear actions, toast notifications
- **`AuthContext`** — current user, JWT token (localStorage), login/register/logout/updateProfile

### Admin UI — Management Dashboard

- Product list with create / edit / delete
- Category management
- Inventory dashboard — stock levels, low-stock alerts, bulk and individual updates
- Product image upload
- Audit log viewer — product change history and stock adjustment history

---

## Infrastructure (AWS CDK)

Three CDK stacks in `infra/infra/`:

### NetworkStack
```
VPC
├── Public subnet (1 AZ, /24)
├── Internet Gateway
├── Security Group: inbound TCP 80, TCP 22
└── Key Pair: ecommerce-key (stored in SSM Parameter Store)
```

### StorageStack
```
S3 Buckets (all block public access)
├── ecommerce-uploads-{account}      — product images, RemovalPolicy.RETAIN
├── ecommerce-catalog-ui-{account}   — catalog SPA, auto-delete on destroy
└── ecommerce-admin-ui-{account}     — admin SPA, auto-delete on destroy

CloudFront Distributions (all use OAC)
├── d2uwk625use1bh.cloudfront.net    — uploads bucket, HTTPS redirect, cache optimized
├── d3bwott4660u8l.cloudfront.net    — catalog UI
│     ├── /* → catalog-ui S3 (cache optimized, index.html fallback)
│     └── /api/* → EC2 (cache disabled, all methods, no Host header forwarding)
└── dtjlzqdyq53fa.cloudfront.net     — admin UI
      ├── /* → admin-ui S3 (cache optimized, index.html fallback)
      └── /api/* → EC2 (cache disabled, all methods, no Host header forwarding)
```

`OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER` is used on the `/api/*` behavior so that request headers (auth tokens, session tokens, content-type) are forwarded to EC2, but the `Host` header is not (which would confuse nginx).

### ComputeStack
```
EC2 t3.micro (Amazon Linux 2023)
├── EBS: 20 GB gp2
├── Elastic IP: 100.22.44.133
├── IAM Role: s3:GetObject, s3:PutObject on uploads bucket
└── User Data:
      ├── Install Docker, Docker Compose plugin, Docker Buildx v0.19.3
      ├── Create 2 GB swapfile (persisted in /etc/fstab)
      ├── git clone → /app
      ├── Write .env (S3 bucket name, CloudFront URL, DB paths, JWT secret)
      ├── docker compose build (sequential, one service at a time)
      └── docker compose up -d
```

---

## Image Storage Flow

```
1. Admin uploads image via Admin UI
   POST /api/admin/products/{id}/images  (multipart/form-data)

2. admin-api → image_service.save_upload()
   If ADMIN_S3_BUCKET_NAME is set:
     boto3.put_object(Bucket=ecommerce-uploads-..., Key=uploads/{id}/{uuid}.jpg)
   Else (local dev):
     Write to ./uploads/{id}/{uuid}.jpg

3. URL stored in ProductImage.storage_url:
   Production: https://d2uwk625use1bh.cloudfront.net/uploads/{id}/{uuid}.jpg
   Local dev:  /uploads/{id}/{uuid}.jpg

4. Browser loads image via CloudFront → CloudFront authenticates to S3 via OAC
   (S3 bucket has no public access; only CloudFront can read it)
```

Images are resized to a maximum of 800 px on the longest side before upload to keep file sizes under ~150 KB.

---

## Authentication

```
Registration:  POST /api/auth/register  { name, email, password }
               → bcrypt hash password → store in auth.db → return JWT

Login:         POST /api/auth/login     { email, password }
               → verify bcrypt → return JWT

JWT stored in browser localStorage.
All protected requests:  Authorization: Bearer <token>

Cart is separate from auth — guest UUID in X-Session-Token header.
Cart is NOT automatically merged into account on login (future enhancement).
```

JWT secret is generated once at EC2 boot:
```bash
openssl rand -hex 32
```
Written to `/app/.env` as `AUTH_JWT_SECRET`. All containers restart on EC2 reboot, but the `.env` file is written fresh each time from user-data — meaning the JWT secret rotates on every EC2 reboot, invalidating all active sessions.

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop

### Run all backends

```bash
# Terminal 1 — Admin API (port 8000)
cd admin-api && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src uvicorn app.main:app --reload

# Terminal 2 — Catalog API (port 8001)
cd catalog-api && source .venv/bin/activate
PYTHONPATH=src uvicorn app.main:app --port 8001 --reload

# Terminal 3 — Cart API (port 8002)
cd cart-api && source .venv/bin/activate
PYTHONPATH=src uvicorn app.main:app --port 8002 --reload

# Terminal 4 — Orders API (port 8003)
cd orders-api && source .venv/bin/activate
PYTHONPATH=src uvicorn app.main:app --port 8003 --reload

# Terminal 5 — Auth API (port 8004)
cd auth-api && source .venv/bin/activate
PYTHONPATH=src uvicorn app.main:app --port 8004 --reload
```

### Run frontends

```bash
# Catalog UI — http://localhost:5174
cd catalog-ui && npm install && npm run dev

# Admin UI — http://localhost:5173
cd admin-ui && npm install && npm run dev
```

Vite proxies strip the `/api/` prefix and forward to local services, mirroring the production nginx behaviour:

```
/api/catalog → localhost:8001/catalog
/api/cart    → localhost:8002/cart
/api/orders  → localhost:8003/orders
/api/auth    → localhost:8004/auth
/api/admin   → localhost:8000/admin
```

### Run tests

```bash
cd admin-api && PYTHONPATH=src pytest    # 22 tests
cd catalog-api && PYTHONPATH=src pytest  # 17 tests
cd cart-api && PYTHONPATH=src pytest     # 13 tests
cd orders-api && PYTHONPATH=src pytest   # 16 tests
cd auth-api && PYTHONPATH=src pytest     # 17 tests
```

---

## Deployment

### Prerequisites
- AWS CLI configured (`aws configure`)
- AWS CDK installed (`npm install -g aws-cdk`)
- Python 3.11+ with CDK dependencies (`pip install -r infra/requirements.txt`)

### First-time bootstrap

```bash
cd infra
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap aws://074412166767/us-west-2
```

### Deploy infrastructure

```bash
cdk deploy --all
# Deploys: NetworkStack → StorageStack → ComputeStack
```

CDK outputs the EC2 Elastic IP and CloudFront URLs after deployment.

### Deploy frontend builds

The EC2 IAM role does not have access to the frontend S3 buckets (intentional — least privilege). Build and sync from your local machine:

```bash
# Build on EC2 (Node.js available there) or locally
cd catalog-ui && npm run build   # or: sudo npx vite build (skips tsc)
cd admin-ui && npm run build

# Sync to S3
aws s3 sync catalog-ui/dist/ s3://ecommerce-catalog-ui-074412166767/ --delete
aws s3 sync admin-ui/dist/   s3://ecommerce-admin-ui-074412166767/  --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <catalog-dist-id> --paths "/*"
aws cloudfront create-invalidation \
  --distribution-id <admin-dist-id>   --paths "/*"
```

### Update EC2 app (without CDK redeploy)

```bash
ssh -i ~/.ssh/ecommerce-key.pem ec2-user@100.22.44.133
cd /app && git pull
docker compose -f docker-compose.prod.yml build <service>
docker compose -f docker-compose.prod.yml up -d
```

---

## Cost

Estimated monthly cost in `us-west-2`:

| Resource | Free Tier (12 months) | After Free Tier |
|---|---|---|
| EC2 t3.micro (730 hrs) | $0 | $7.59 |
| EBS 20 GB gp2 | $0 | $2.00 |
| Elastic IP (attached) | $0 | $0 |
| S3 (~50 MB across 3 buckets) | $0 | ~$0.00 |
| CloudFront (3 distributions, low traffic) | $0 | ~$0.00 |
| Data transfer | $0 | ~$0.00 |
| VPC, IAM, Security Groups | Always free | $0 |
| **Total** | **~$0/month** | **~$9.59/month** |

No NAT Gateway (saves ~$32/month). No RDS (SQLite on EBS). CloudFront free tier covers 1 TB data transfer + 10 M requests per month — more than sufficient for a dev/learning workload.
