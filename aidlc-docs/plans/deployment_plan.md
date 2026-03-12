# Deployment Plan — AWS eCommerce (us-west-2) — Free Tier

**Role:** Cloud Architect
**Target Region:** us-west-2
**IaC Tool:** AWS CDK (Python)
**Compute:** EC2 t2.micro + Docker Compose (Free Tier)
**Status:** Awaiting final approval (all clarifications resolved)

---

## Deliverables

1. `infra/` — CDK app (Python) defining all AWS resources
2. `Dockerfile` for each of the 5 FastAPI services
3. `docker-compose.prod.yml` — production compose file for EC2
4. `nginx.conf` — reverse proxy routing all 5 services behind port 80
5. S3 bucket for product image uploads (replacing local `uploads/`)
6. S3 bucket + CloudFront distribution for `catalog-ui`
7. S3 bucket + CloudFront distribution for `admin-ui`
8. EC2 t2.micro with Docker Compose running all 5 services (images built on EC2, no ECR)
9. VPC with a single public subnet and security group (no NAT Gateway)
10. Updated `image_service.py` to write uploads to S3 instead of local disk
11. Updated `config.py` files to read env vars (DB paths, S3 bucket, etc.)
12. End-to-end smoke test checklist

---

## Architecture

```
Internet
   │
   ├── CloudFront ──► S3 (catalog-ui)         [FREE TIER]
   │
   ├── CloudFront ──► S3 (admin-ui)           [FREE TIER]
   │
   └── EC2 t2.micro (public subnet)           [FREE TIER]
         └── nginx :80 (reverse proxy)
               ├── /admin/*    → admin-api  :8000
               ├── /catalog/*  → catalog-api :8001
               ├── /cart/*     → cart-api   :8002
               ├── /orders/*   → orders-api :8003
               └── /auth/*     → auth-api   :8004

       Docker named volume: /data/
               ├── admin.db    (admin-api owns)
               ├── cart.db     (cart-api owns)
               ├── orders.db   (orders-api owns)
               └── auth.db     (auth-api owns)
               (catalog-api reads admin.db read-only from same volume)

       S3 bucket: ecommerce-uploads-074412166767  [FREE TIER]
               (product images, served via CloudFront HTTPS)
```

**No ECR** — Docker images are built directly on EC2 via `git clone` + `docker compose build`.
This keeps storage costs at $0.

---

## Free Tier Cost Estimate

| Resource | Free Tier Coverage | Cost |
|----------|-------------------|------|
| EC2 t2.micro | 750 hrs/month, 12 months | $0 |
| EBS 8 GB (EC2 root) | 30 GB/month free, 12 months | $0 |
| S3 (uploads + frontends) | 5 GB / 20K GET / 2K PUT | $0 |
| CloudFront (3 distros) | 1 TB transfer / 10M requests | $0 |
| ECR | **Not used** — images built on EC2 | $0 |
| VPC / Subnet / SG | Always free | $0 |
| Elastic IP (attached) | Free while instance is running | $0 |
| Data transfer in/out | First 100 GB/month free | $0 |
| **Total** | | **$0/month** |

> ⚠️ **t2.micro has 1 GB RAM.** Running 5 containers + nginx is tight. If memory pressure is observed we can tune container memory limits or scale to t3.small (~$15/month).

> ⚠️ **Elastic IP** — free while EC2 is running. If you stop (not terminate) the instance, it charges $0.005/hr. Recommend terminating and redeploying for cost safety.

---

## Why No RDS Needed

With Docker Compose on EC2, all containers share a **named Docker volume** (`/data/`). Each SQLite file lives there and is mounted into every container that needs it — replicating local cross-service DB sharing. This means:
- No database migration (SQLite stays as-is)
- No code changes to the database layer
- No RDS cost
- Only DB path env vars need updating

---

## Clarifications — All Resolved ✅

| # | Question | Decision |
|---|----------|----------|
| Q1 | Image storage | **S3** via `boto3` in `image_service.py` |
| Q2 | IaC tool | **CDK Python** |
| Q3 | Domain | **None** — EC2 HTTP + CloudFront HTTPS for frontends |
| Q4 | AWS CLI | **Configured** — Account `074412166767` (root), us-west-2 |
| Q5 | EC2 Key Pair | **New** — `ecommerce-key`, saved to `~/.ssh/ecommerce-key.pem` |
| Q6 | ECR | **Skip ECR** — build images directly on EC2 to stay $0 |

---

## Plan Steps

### Phase 0 — Prerequisites
- [x] **Step 0.1** — Install Node.js (needed for CDK CLI and frontend builds)
- [x] **Step 0.2** — Install CDK CLI: `npm install -g aws-cdk`
- [x] **Step 0.3** — CDK bootstrap: `cdk bootstrap aws://074412166767/us-west-2`

---

### Phase 1 — CDK Infrastructure Scaffold
- [x] **Step 1.1** — Create `infra/` as a CDK Python app (`cdk init app --language python`)
- [x] **Step 1.2** — Define 3 CDK stacks:
  - `NetworkStack` — VPC, public subnet, security group, EC2 key pair
  - `StorageStack` — S3 buckets (uploads, catalog-ui, admin-ui), CloudFront distributions, IAM role for EC2
  - `ComputeStack` — EC2 t2.micro, Elastic IP, user-data bootstrap script

---

### Phase 2 — Networking (NetworkStack)
- [x] **Step 2.1** — VPC with 1 public subnet in us-west-2a (no private subnet, no NAT Gateway)
- [x] **Step 2.2** — Security group for EC2:
  - Inbound: port 80 (HTTP) from `0.0.0.0/0`
  - Inbound: port 22 (SSH) from `0.0.0.0/0` (tighten to your IP post-deploy if needed)
  - Outbound: all traffic
- [x] **Step 2.3** — EC2 Key Pair: create `ecommerce-key`, save private key to `~/.ssh/ecommerce-key.pem`
- [x] **Step 2.4** — Deploy NetworkStack: `cdk deploy NetworkStack`

---

### Phase 3 — Storage (StorageStack)
- [x] **Step 3.1** — S3 bucket: `ecommerce-uploads-074412166767` — private, for product images
- [x] **Step 3.2** — S3 bucket: `ecommerce-catalog-ui-074412166767` — for customer frontend
- [x] **Step 3.3** — S3 bucket: `ecommerce-admin-ui-074412166767` — for admin frontend
- [x] **Step 3.4** — CloudFront OAC distribution → `catalog-ui` bucket (HTTPS)
- [x] **Step 3.5** — CloudFront OAC distribution → `admin-ui` bucket (HTTPS)
- [x] **Step 3.6** — CloudFront OAC distribution → `uploads` bucket (serve images via HTTPS)
- [x] **Step 3.7** — IAM instance role for EC2: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` on uploads bucket only
- [x] **Step 3.8** — Deploy StorageStack: `cdk deploy StorageStack`
- [x] **Step 3.9** — Outputs recorded:
  - Uploads bucket: `ecommerce-uploads-074412166767`
  - Uploads CloudFront: `https://d2uwk625use1bh.cloudfront.net`
  - catalog-ui CloudFront: `https://d3bwott4660u8l.cloudfront.net`
  - admin-ui CloudFront: `https://dtjlzqdyq53fa.cloudfront.net`

---

### Phase 4 — Application Code Changes
- [x] **Step 4.1** — Update all `config.py` files: DB defaults kept as relative paths for local/test; env vars override to `/data/*.db` in Docker
- [x] **Step 4.2** — Update `admin-api` `image_service.py`: S3 via `boto3` when `ADMIN_S3_BUCKET_NAME` is set; falls back to local disk for dev
- [x] **Step 4.3** — Add `boto3` to `admin-api/pyproject.toml` dependencies
- [x] **Step 4.4** — Update CORS origins in all 5 services to accept CloudFront URLs for catalog-ui and admin-ui
- [x] **Step 4.5** — All 85 tests pass (22 + 17 + 13 + 16 + 17)

---

### Phase 5 — Containerization (local, no ECR)
- [x] **Step 5.1** — Write `Dockerfile` for `admin-api`
- [x] **Step 5.2** — Write `Dockerfile` for `catalog-api`
- [x] **Step 5.3** — Write `Dockerfile` for `cart-api`
- [x] **Step 5.4** — Write `Dockerfile` for `orders-api`
- [x] **Step 5.5** — Write `Dockerfile` for `auth-api`
- [x] **Step 5.6** — Write `nginx/nginx.conf` — path-based reverse proxy for all 5 services
- [x] **Step 5.7** — Write `nginx/Dockerfile` — nginx container with custom config
- [x] **Step 5.8** — Write `docker-compose.prod.yml` — all 5 services + nginx + shared `/data/` volume + `.env` file support
- [x] **Step 5.9** — Docker not installed locally; build verified structurally. Full runtime test will execute on EC2 in Phase 6.

---

### Phase 6 — EC2 Compute (ComputeStack)
- [ ] **Step 6.1** — EC2 t2.micro (Amazon Linux 2023, public subnet, IAM role + key pair attached)
- [ ] **Step 6.2** — EC2 user-data script installs on first boot:
  - Git, Docker, Docker Compose plugin
  - Clones this repo to `/app/`
  - Writes `/app/.env` with: `S3_BUCKET`, `S3_IMAGES_CLOUDFRONT_URL`, DB paths, `AUTH_JWT_SECRET`
  - Runs `docker compose -f docker-compose.prod.yml up --build -d`
- [ ] **Step 6.3** — Elastic IP allocated and associated with EC2
- [ ] **Step 6.4** — Deploy ComputeStack: `cdk deploy ComputeStack`
- [ ] **Step 6.5** — Wait for EC2 user-data to complete (~3–5 min), then SSH in: `ssh -i ~/.ssh/ecommerce-key.pem ec2-user@EC2_IP`
- [ ] **Step 6.6** — Verify all 6 containers running: `docker ps` (5 APIs + nginx)
- [ ] **Step 6.7** — Verify nginx routes: `curl http://EC2_IP/catalog/products`

---

### Phase 7 — Frontend Deployment
- [ ] **Step 7.1** — Install Node.js locally (for frontend builds)
- [ ] **Step 7.2** — Create `catalog-ui/.env.production` with `VITE_API_BASE_URL=http://EC2_ELASTIC_IP`
- [ ] **Step 7.3** — `cd catalog-ui && npm install && npm run build`
- [ ] **Step 7.4** — Upload `catalog-ui/dist/` to `ecommerce-catalog-ui-074412166767` S3 bucket
- [ ] **Step 7.5** — Create `admin-ui/.env.production` with `VITE_API_BASE_URL=http://EC2_ELASTIC_IP`
- [ ] **Step 7.6** — `cd admin-ui && npm install && npm run build`
- [ ] **Step 7.7** — Upload `admin-ui/dist/` to `ecommerce-admin-ui-074412166767` S3 bucket
- [ ] **Step 7.8** — Invalidate CloudFront caches for both frontend distributions
- [ ] **Step 7.9** — Verify both CloudFront URLs load in browser

---

### Phase 8 — Validation & Smoke Tests
- [ ] **Step 8.1** — EC2: all 6 containers running, nginx healthy on port 80
- [ ] **Step 8.2** — Admin API: `POST /admin/categories` → `POST /admin/products` → `POST /admin/products/{id}/images` → verify image URL is a CloudFront URL pointing to S3
- [ ] **Step 8.3** — Catalog API: `GET /catalog/products`, `GET /catalog/search?q=...`, `GET /catalog/products/{id}`
- [ ] **Step 8.4** — Cart API: add item, view cart, update qty, remove item
- [ ] **Step 8.5** — Auth API: register, login, get profile, update profile
- [ ] **Step 8.6** — Orders API: checkout, list orders, view order
- [ ] **Step 8.7** — End-to-end: open `catalog-ui` CloudFront URL → browse → add to cart → register → checkout
- [ ] **Step 8.8** — End-to-end: open `admin-ui` CloudFront URL → add product with image → verify visible in catalog-ui
- [ ] **Step 8.9** — Mark all steps complete in this plan

---

## CDK Stack Deploy Order

```
cdk deploy NetworkStack   (VPC, SG, Key Pair)
cdk deploy StorageStack   (S3, CloudFront, IAM role)
cdk deploy ComputeStack   (EC2, Elastic IP — needs outputs from above two)
```

---

*Plan finalised: 2026-03-12 — Free Tier, no ECR, ~$0/month | Awaiting your approval to begin Phase 0*
