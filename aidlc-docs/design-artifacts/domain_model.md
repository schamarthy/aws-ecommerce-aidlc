# Domain Model — Product Catalog System

## Design Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Search | Capability within Product Catalog component; queries same product data store |
| 2 | Images | Dedicated Image Storage component; Product entity holds metadata only (URL, order, primary flag) |
| 3 | Audit | Scoped per domain — product audit in Admin/Product component, stock audit in Admin/Inventory component |
| 4 | Cart data | Snapshot of product name, price, and thumbnail stored at add-to-cart time |

---

## 1. Business Components

Four components form the system. They map directly to the three units plus one shared infrastructure component.

| Component | Unit | Responsibility |
|-----------|------|----------------|
| **Product Catalog** | U1 | Customer-facing browsing, search, product detail, featured & related products |
| **Shopping Cart** | U2 | Cart lifecycle — add, view, update, remove, persist, guest cart |
| **Admin** | U3 | Product CRUD, category management, inventory management, audit logs |
| **Image Storage** | U3 (shared) | Accepts image file uploads; stores files; returns URLs; deletes files |

### Component Descriptions

#### Product Catalog Component
The primary customer interface to the product catalog. Handles all read operations for customers and guests: browsing the catalog, filtering by category, sorting, keyword search, autocomplete, product detail pages, image galleries, featured products, and related products. This component owns no product data directly — it reads all data through APIs exposed by the Admin component. Search is implemented as an internal capability of this component, querying the same product data store.

#### Shopping Cart Component
Manages the full cart lifecycle for authenticated customers and guests. When a customer adds an item, this component fetches a product snapshot (name, price, thumbnail URL) from the Product Catalog API and stores it alongside the cart item. Stock availability is validated against the Product Catalog API before an add or quantity update is accepted. Cart persistence ties to a user identity (authenticated) or browser session (guest). Cart merging on login is supported for the guest-to-customer transition.

#### Admin Component
The foundational component that owns all product and inventory data. It is split into two sub-domains:

- **Product Management sub-domain:** Full lifecycle of products and categories — create, edit, delete, deactivate, publish/unpublish, mark featured, manage images (via Image Storage). Maintains a product audit log recording every field-level change.
- **Inventory Management sub-domain:** Tracks stock quantities per product, supports single and bulk updates, configures low-stock thresholds per product, and maintains a stock change audit log.

The Admin component is the data authority — all other components consume its data through APIs.

#### Image Storage Component
A dedicated file storage component responsible for accepting image file uploads, persisting them, and returning stable URLs. The Admin component calls Image Storage when an admin uploads a product image. The Product entity stores only the returned URL as metadata. Image Storage also handles deletion when an image is removed from a product.

---

## 2. Data Models

### Entity Relationship Overview

```
Category (1) ──────────────── (N) Product
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
               (N) ProductImage  (1) Inventory   (N) ProductAuditLog
                                    │
                               (N) StockAuditLog

Cart (1) ──── (N) CartItem ──── (reference) ──── Product
```

---

### Entity: Category

Represents a logical grouping of products.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| name | String | Required, Unique | Display name |
| description | Text | Optional | |
| created_at | DateTime | Required | |
| updated_at | DateTime | Required | |

**Relationships:**
- One Category has many Products (1:N)

---

### Entity: Product

The core catalog entity. Owned by the Admin component.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| name | String | Required | |
| description | Text | Optional | |
| price | Decimal | Required, ≥ 0 | |
| sku | String | Required, Unique | Stock Keeping Unit |
| status | Enum | Required | `draft` \| `published` \| `deactivated` |
| is_featured | Boolean | Default: false | Controlled by Admin |
| category_id | UUID | FK → Category | Required |
| created_at | DateTime | Required | |
| updated_at | DateTime | Required | |
| created_by | String | Required | Actor identifier (extensibility hook) |
| updated_by | String | Required | Actor identifier (extensibility hook) |

**Relationships:**
- Belongs to one Category (N:1)
- Has many ProductImages (1:N)
- Has one Inventory record (1:1)
- Has many ProductAuditLog entries (1:N)
- Referenced by many CartItems (1:N — reference only, not FK constraint)

**Business rules:**
- Only `published` products are visible to customers
- `deactivated` products are hidden from customers but retained in the system
- SKU must be globally unique
- Price must be non-negative

---

### Entity: ProductImage

Image metadata for a product. The actual file lives in Image Storage.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| product_id | UUID | FK → Product | Required |
| storage_url | String | Required | URL returned by Image Storage |
| is_primary | Boolean | Default: false | Only one primary per product |
| display_order | Integer | Required, ≥ 0 | Controls gallery order |
| created_at | DateTime | Required | |

**Relationships:**
- Belongs to one Product (N:1)

**Business rules:**
- Each product must have at most one `is_primary = true` image
- Supports up to 10 images per product
- Accepted formats: JPG, PNG, WebP (enforced at upload time by Image Storage)
- Maximum file size: 5MB per image (enforced at upload time)

---

### Entity: ProductAuditLog

Records field-level changes to a product. Scoped to the Admin/Product sub-domain.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| product_id | UUID | FK → Product | Required |
| field_name | String | Required | Name of the changed field |
| previous_value | Text | Optional | Null on creation |
| new_value | Text | Required | |
| actor | String | Required | Actor identifier (extensibility hook for future roles) |
| changed_at | DateTime | Required | |

**Relationships:**
- Belongs to one Product (N:1)

**Business rules:**
- Entries are immutable (read-only after creation)
- Created automatically on every product edit or status change

---

### Entity: Inventory

Tracks current stock level for a product. Owned by the Admin/Inventory sub-domain.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| product_id | UUID | FK → Product, Unique | 1:1 with Product |
| quantity | Integer | Required, ≥ 0 | Current stock level |
| low_stock_threshold | Integer | Required, ≥ 0 | Default from system config |
| updated_at | DateTime | Required | |

**Relationships:**
- Belongs to one Product (1:1)
- Has many StockAuditLog entries (1:N)

**Business rules:**
- Quantity cannot go negative
- Products with `quantity = 0` are considered Out of Stock
- Products with `quantity > 0 AND quantity ≤ low_stock_threshold` are considered Low Stock
- Inventory record is created automatically when a product is created

---

### Entity: StockAuditLog

Immutable log of every stock quantity change. Scoped to the Admin/Inventory sub-domain.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| product_id | UUID | FK → Product | Required |
| previous_quantity | Integer | Required | Stock before change |
| new_quantity | Integer | Required | Stock after change |
| adjustment | Integer | Computed | `new_quantity - previous_quantity` |
| actor | String | Required | Actor identifier (extensibility hook) |
| reason | String | Optional | Free-text reason for the change |
| created_at | DateTime | Required | |

**Relationships:**
- Belongs to one Product (N:1) via product_id

**Business rules:**
- Entries are immutable (read-only after creation)
- Created automatically on every stock quantity update (single or bulk)

---

### Entity: Cart

Represents a customer's or guest's shopping cart.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| user_id | UUID | Optional | Null for guest carts |
| session_id | String | Optional | For guest cart identification |
| created_at | DateTime | Required | |
| updated_at | DateTime | Required | |

**Relationships:**
- Has many CartItems (1:N)

**Business rules:**
- Either `user_id` or `session_id` must be present (not both null)
- One active cart per user (authenticated)
- One active cart per session (guest)
- On guest-to-customer login, guest cart items are merged into the user's cart

---

### Entity: CartItem

An individual line item within a cart, storing a snapshot of product data.

| Attribute | Type | Constraints | Notes |
|-----------|------|-------------|-------|
| id | UUID | PK | System-generated |
| cart_id | UUID | FK → Cart | Required |
| product_id | UUID | Reference to Product | Required (soft reference — no FK constraint) |
| quantity | Integer | Required, ≥ 1 | |
| unit_price_snapshot | Decimal | Required | Price at time of add-to-cart |
| product_name_snapshot | String | Required | Name at time of add-to-cart |
| product_thumbnail_snapshot | String | Required | Primary image URL at add time |
| created_at | DateTime | Required | |
| updated_at | DateTime | Required | |

**Relationships:**
- Belongs to one Cart (N:1)
- Soft reference to Product (no enforced FK — snapshot model)

**Business rules:**
- Quantity cannot be less than 1
- Quantity cannot exceed current stock (validated at add and update time via Product Catalog API)
- Price and name are frozen at add time; they do not change if admin updates the product
- If the referenced product is deleted or deactivated, the cart item is removed
- One CartItem per product per cart (adding the same product again increases quantity)

---

## 3. APIs

### 3.1 Product Catalog API (Customer-facing, read-only)

Exposed by the Product Catalog component. Consumed by customers, guests, and the Shopping Cart component.

| Method | Path | Purpose | Stories |
|--------|------|---------|---------|
| GET | `/products` | List published products with pagination, sorting, and category filter | US-001, US-002, US-003 |
| GET | `/products/featured` | List featured published products | US-004 |
| GET | `/products/search` | Keyword search with filters (category, price range, availability) | US-005, US-007 |
| GET | `/products/search/suggestions` | Autocomplete suggestions for a partial query | US-006 |
| GET | `/products/{id}` | Full product detail (name, description, price, images, category, SKU, stock status) | US-008, US-009 |
| GET | `/products/{id}/related` | Related products from the same category | US-010 |
| GET | `/categories` | List all categories | US-002 |

**Query parameters for `/products`:**
- `category_id` — filter by category
- `sort` — `price_asc`, `price_desc`, `name_asc`, `newest`
- `page`, `page_size` — pagination
- `in_stock` — boolean filter

**Query parameters for `/products/search`:**
- `q` — keyword query
- `category_id`, `price_min`, `price_max`, `in_stock` — filters
- `page`, `page_size`, `sort`

---

### 3.2 Admin Product Management API

Exposed by the Admin component (Product Management sub-domain). Consumed by the Admin UI.

| Method | Path | Purpose | Stories |
|--------|------|---------|---------|
| GET | `/admin/products` | List all products (all statuses, paginated) | US-017, US-018, US-019 |
| POST | `/admin/products` | Create a new product (draft or published) | US-017 |
| GET | `/admin/products/{id}` | Get full product detail for editing | US-018 |
| PUT | `/admin/products/{id}` | Update product fields | US-018 |
| DELETE | `/admin/products/{id}` | Permanently delete a product | US-019 |
| PATCH | `/admin/products/{id}/status` | Change product status (publish/unpublish/deactivate) | US-019, US-022 |
| PATCH | `/admin/products/{id}/featured` | Toggle featured flag | US-004 |
| POST | `/admin/products/{id}/images` | Upload image (delegates to Image Storage; saves metadata) | US-021 |
| PUT | `/admin/products/{id}/images/{imageId}` | Update image metadata (order, primary flag) | US-021 |
| DELETE | `/admin/products/{id}/images/{imageId}` | Delete image (removes from Image Storage and metadata) | US-021 |
| GET | `/admin/products/{id}/audit` | View product change audit log | US-018 |
| GET | `/admin/categories` | List all categories | US-020 |
| POST | `/admin/categories` | Create a new category | US-020 |
| PUT | `/admin/categories/{id}` | Rename or update category description | US-020 |
| DELETE | `/admin/categories/{id}` | Delete category (with product reassignment) | US-020 |

---

### 3.3 Admin Inventory Management API

Exposed by the Admin component (Inventory Management sub-domain). Consumed by the Admin UI.

| Method | Path | Purpose | Stories |
|--------|------|---------|---------|
| GET | `/admin/inventory` | Inventory dashboard — all products with stock levels, low-stock flags | US-023, US-025 |
| GET | `/admin/inventory/{productId}` | Stock detail for a single product | US-024 |
| PUT | `/admin/inventory/{productId}` | Update stock quantity (absolute set or +/- adjustment) | US-024 |
| PATCH | `/admin/inventory/{productId}/threshold` | Set low-stock threshold for a product | US-025 |
| GET | `/admin/inventory/{productId}/history` | Stock change audit log for a product | US-026 |
| POST | `/admin/inventory/bulk-update` | Upload CSV for bulk stock quantity update | US-027 |

---

### 3.4 Image Storage API (Internal)

Exposed by the Image Storage component. Consumed by the Admin component only.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/images` | Accept image file upload; validate format and size; return storage URL |
| DELETE | `/images/{imageId}` | Delete an image file by its identifier |

---

### 3.5 Shopping Cart API

Exposed by the Shopping Cart component. Consumed by the customer-facing frontend.

| Method | Path | Purpose | Stories |
|--------|------|---------|---------|
| GET | `/cart` | View current cart (by user_id or session_id) | US-012 |
| POST | `/cart/items` | Add item — fetches product snapshot, validates stock | US-011 |
| PUT | `/cart/items/{itemId}` | Update item quantity — validates against current stock | US-013 |
| DELETE | `/cart/items/{itemId}` | Remove a specific item from cart | US-014 |
| DELETE | `/cart` | Clear entire cart | US-012 |
| POST | `/cart/merge` | Merge guest cart into authenticated user cart on login | US-016 |

---

## 4. Component Interactions

### 4.1 Interaction Map

| Caller | Callee | Data Exchanged | Trigger |
|--------|--------|----------------|---------|
| Product Catalog | Admin (Product Mgmt API) | Product list, product detail, categories, featured flag | Customer browses or searches |
| Product Catalog | Admin (Inventory API) | Stock quantity per product (for availability display) | Product detail / listing render |
| Shopping Cart | Product Catalog API | Product snapshot (name, price, thumbnail, stock status) | Customer adds item to cart |
| Shopping Cart | Product Catalog API | Current stock quantity | Customer updates cart item quantity |
| Admin (Product Mgmt) | Image Storage | Image file upload → storage URL | Admin uploads product image |
| Admin (Product Mgmt) | Image Storage | Delete image file | Admin removes product image |
| Admin (Product Mgmt) | Shopping Cart | Notification: product deleted/deactivated | Admin deletes or deactivates a product |

### 4.2 Key Interaction Flows

#### Flow 1: Customer Browses and Views a Product
```
Customer
  │
  ├─► Product Catalog Component
  │     ├─► Admin Product Mgmt API: GET /products (published, paginated)
  │     ├─► Admin Product Mgmt API: GET /categories (for filter menu)
  │     └─► Admin Inventory API: GET /inventory/{productId} (stock status)
  │
  └─► Product Catalog renders listing to customer
```

#### Flow 2: Customer Searches for a Product
```
Customer types query
  │
  ├─► Product Catalog Component (Search capability)
  │     ├─► Internal: query product data store by name/description
  │     └─► Apply filters: category, price range, in_stock
  │
  └─► Product Catalog renders search results
```

#### Flow 3: Customer Adds Item to Cart
```
Customer clicks "Add to Cart"
  │
  ├─► Shopping Cart Component
  │     ├─► Product Catalog API: GET /products/{id} (fetch snapshot: name, price, thumbnail)
  │     ├─► Product Catalog API: check stock status (must be In Stock)
  │     ├─► Create/update CartItem with product snapshot + quantity = 1
  │     └─► Return updated cart item count to frontend
  │
  └─► Customer sees cart count update + confirmation toast
```

#### Flow 4: Admin Creates a Product with Images
```
Admin submits new product form
  │
  ├─► Admin Component (Product Mgmt)
  │     ├─► Validate fields (SKU uniqueness, required fields)
  │     ├─► Create Product record (status: draft or published)
  │     ├─► For each image file:
  │     │     ├─► Image Storage API: POST /images (upload file)
  │     │     └─► Save ProductImage metadata (url, order, is_primary)
  │     ├─► Create Inventory record (quantity from form, default threshold)
  │     └─► Write ProductAuditLog entry (created_by actor)
  │
  └─► Admin sees confirmation; product visible in catalog if published
```

#### Flow 5: Admin Updates Stock Quantity
```
Admin submits stock update
  │
  ├─► Admin Component (Inventory Mgmt)
  │     ├─► Validate: new quantity ≥ 0
  │     ├─► Update Inventory.quantity
  │     ├─► Write StockAuditLog entry (previous qty, new qty, actor, reason)
  │     └─► Updated stock immediately readable via Product Catalog API
  │
  └─► Product Catalog reflects new availability status to customers
  └─► Cart validates against new stock on next quantity update attempt
```

#### Flow 6: Admin Deletes a Product
```
Admin confirms product deletion
  │
  ├─► Admin Component (Product Mgmt)
  │     ├─► Soft-deactivate or hard-delete Product record
  │     ├─► If hard-delete: delete ProductImages + notify Image Storage
  │     ├─► Notify Shopping Cart Component: product {id} removed
  │     └─► Write ProductAuditLog entry
  │
  ├─► Shopping Cart Component
  │     └─► Remove all CartItems referencing the deleted product_id
  │
  └─► Product no longer visible in catalog or carts
```

---

## 5. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CUSTOMER / GUEST                             │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ browse / search / view / add to cart
                            ▼
┌───────────────────────────────────────────────────────┐
│            Product Catalog Component  (U1)            │
│                                                       │
│  Capabilities:                                        │
│  • Browse & paginate products                         │
│  • Filter by category, sort by price/name/date        │
│  • Keyword search + autocomplete (same data store)    │
│  • Filter search results                              │
│  • Product detail page + image gallery                │
│  • Featured products section                         │
│  • Related products                                   │
│                                                       │
│  Reads from: Admin Product Mgmt API                   │
│             Admin Inventory API (stock status)        │
└───────────────────────┬───────────────────────────────┘
                        │ product snapshot + stock status
                        ▼
┌───────────────────────────────────────────────────────┐
│              Shopping Cart Component  (U2)            │
│                                                       │
│  Capabilities:                                        │
│  • Add / remove / update cart items                   │
│  • View cart with line totals and subtotal            │
│  • Persist cart per user (authenticated)              │
│  • Session cart for guests                            │
│  • Merge guest cart on login                          │
│  • Stores product snapshot at add time                │
│                                                       │
│  Reads: Product snapshot from Product Catalog API     │
│  Validates: Stock availability from Product Catalog   │
│  Listens: Product deletion events from Admin          │
└───────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                             ADMIN                                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ manage products, categories, inventory
                            ▼
┌────────────────────────────────────────────┐   ┌────────────────────┐
│           Admin Component  (U3)            │   │  Image Storage     │
│                                            │◄─►│  Component  (U3)   │
│  Product Management sub-domain:            │   │                    │
│  • Create / edit / delete products         │   │ • Accept uploads   │
│  • Manage categories                       │   │ • Store image files│
│  • Publish / unpublish / deactivate        │   │ • Return URLs      │
│  • Mark products as featured               │   │ • Delete files     │
│  • Manage product images (via Image Store) │   └────────────────────┘
│  • Product audit log (per field change)    │
│                                            │
│  Inventory Management sub-domain:          │
│  • Inventory dashboard (all stock levels)  │
│  • Update stock (single + bulk CSV)        │
│  • Set low-stock thresholds                │
│  • Stock audit log (per quantity change)   │
└─────────────┬──────────────────────────────┘
              │ exposes APIs (product, category, inventory)
              │ sends deletion events
              ▼
   ┌──────────────────────┐    ┌──────────────────────────┐
   │ Product Catalog (U1) │    │  Shopping Cart (U2)      │
   │ consumes read APIs   │    │  consumes product data   │
   └──────────────────────┘    │  receives deletion events│
                               └──────────────────────────┘
```

---

## 6. User Story Coverage Matrix

| Story | Component | Data Model(s) | API Operation(s) |
|-------|-----------|---------------|-----------------|
| US-001 Browse catalog | Product Catalog | Product, Category, Inventory | GET /products |
| US-002 Browse by category | Product Catalog | Product, Category | GET /products?category_id=, GET /categories |
| US-003 Sort listing | Product Catalog | Product | GET /products?sort= |
| US-004 Featured products | Product Catalog | Product (is_featured) | GET /products/featured |
| US-005 Keyword search | Product Catalog | Product | GET /products/search?q= |
| US-006 Search autocomplete | Product Catalog | Product | GET /products/search/suggestions?q= |
| US-007 Filter search results | Product Catalog | Product, Category, Inventory | GET /products/search (with filters) |
| US-008 Product detail page | Product Catalog | Product, ProductImage, Inventory | GET /products/{id} |
| US-009 Image gallery | Product Catalog | ProductImage | GET /products/{id} |
| US-010 Related products | Product Catalog | Product, Category | GET /products/{id}/related |
| US-011 Add to cart | Shopping Cart | Cart, CartItem, Product (snapshot) | POST /cart/items |
| US-012 View cart | Shopping Cart | Cart, CartItem | GET /cart |
| US-013 Update quantity | Shopping Cart | CartItem, Inventory (validation) | PUT /cart/items/{itemId} |
| US-014 Remove from cart | Shopping Cart | CartItem | DELETE /cart/items/{itemId} |
| US-015 Persistent cart | Shopping Cart | Cart (user_id) | GET /cart, (auth dependency) |
| US-016 Guest cart + merge | Shopping Cart | Cart (session_id), CartItem | GET /cart, POST /cart/merge |
| US-017 Add product | Admin | Product, Inventory, ProductAuditLog | POST /admin/products |
| US-018 Edit product | Admin | Product, ProductAuditLog | PUT /admin/products/{id}, GET /admin/products/{id}/audit |
| US-019 Delete/deactivate | Admin | Product, ProductAuditLog | DELETE /admin/products/{id}, PATCH /admin/products/{id}/status |
| US-020 Manage categories | Admin | Category | POST/PUT/DELETE /admin/categories |
| US-021 Upload images | Admin, Image Storage | ProductImage | POST /admin/products/{id}/images, POST /images |
| US-022 Publish/unpublish | Admin | Product (status) | PATCH /admin/products/{id}/status |
| US-023 Inventory dashboard | Admin | Inventory, Product | GET /admin/inventory |
| US-024 Update stock | Admin | Inventory, StockAuditLog | PUT /admin/inventory/{productId} |
| US-025 Low-stock threshold | Admin | Inventory | PATCH /admin/inventory/{productId}/threshold |
| US-026 Stock audit log | Admin | StockAuditLog | GET /admin/inventory/{productId}/history |
| US-027 Bulk stock update | Admin | Inventory, StockAuditLog | POST /admin/inventory/bulk-update |
