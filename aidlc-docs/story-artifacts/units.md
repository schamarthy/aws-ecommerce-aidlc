# Units — Product Catalog System

## Overview

User stories are grouped into 3 independently buildable units. Each unit is highly cohesive and loosely coupled from the others via well-defined API contracts.

| Unit | Name | Stories | Total | Depends On |
|------|------|---------|-------|------------|
| U1 | Product Catalog & Discovery | US-001 – US-010 | 10 | U3 (featured/category data) |
| U2 | Shopping Cart | US-011 – US-016 | 6 | U1 (product data, stock status) |
| U3 | Admin — Product & Inventory Management | US-017 – US-027 | 11 | — (foundational) |

**Build order recommendation:** U3 → U1 → U2

---

## U1 — Product Catalog & Discovery

**Description:** Covers all customer-facing product browsing, search, and product detail experiences. This unit is the primary interface through which customers discover and explore products.

**Team scope:** Customer-facing frontend + catalog/search backend

**Depends on:** U3 must expose product, category, and inventory data via API

**Exposes to U2:** Product data (id, name, price, stock status, images) via API

---

### US-001 — Browse Product Catalog

**As a** Guest or Customer,
**I want to** view a list of available products,
**so that** I can discover items I may want to purchase.

**Acceptance Criteria:**
- Products are displayed in a grid or list layout
- Each product card shows: name, thumbnail image, price, and availability status
- Products are paginated (default 20 per page)
- Page loads within acceptable time even with large catalog

**MoSCoW:** Must Have | **Complexity:** M

---

### US-002 — Browse Products by Category

**As a** Guest or Customer,
**I want to** filter products by category,
**so that** I can narrow down items relevant to my interest.

**Acceptance Criteria:**
- Categories are visible as a navigable list or menu
- Selecting a category filters the product listing to that category only
- Active category filter is clearly indicated
- "All" option resets the filter

**MoSCoW:** Must Have | **Complexity:** M

---

### US-003 — Sort Product Listing

**As a** Guest or Customer,
**I want to** sort products by price, name, or newest first,
**so that** I can find the most relevant products quickly.

**Acceptance Criteria:**
- Sort options include: Price Low–High, Price High–Low, Name A–Z, Newest First
- Selected sort order persists during the browsing session
- Sort applies within the current category/search filter

**MoSCoW:** Should Have | **Complexity:** S

---

### US-004 — View Featured / Promoted Products

**As a** Guest or Customer,
**I want to** see featured or promoted products on the homepage,
**so that** I am aware of highlighted deals or new arrivals.

**Acceptance Criteria:**
- A dedicated section highlights featured products
- Featured products are controlled by the Admin (via U3)
- At least 4 featured products can be displayed

**MoSCoW:** Could Have | **Complexity:** S
**Cross-unit note:** Featured flag is set by Admin in U3; U1 reads and renders it.

---

### US-005 — Search Products by Keyword

**As a** Guest or Customer,
**I want to** search for products using a keyword,
**so that** I can quickly find a specific item without browsing all categories.

**Acceptance Criteria:**
- A search bar is accessible from all pages
- Search matches against product name and description
- Results are displayed on a search results page
- If no results found, a clear "no results" message is shown

**MoSCoW:** Must Have | **Complexity:** M

---

### US-006 — Search Autocomplete / Suggestions

**As a** Guest or Customer,
**I want to** see search suggestions as I type,
**so that** I can find products faster without typing the full query.

**Acceptance Criteria:**
- Suggestions appear after 2+ characters are typed
- Suggestions show up to 5 matching product names
- Clicking a suggestion navigates directly to that product

**MoSCoW:** Should Have | **Complexity:** M

---

### US-007 — Filter Search Results

**As a** Guest or Customer,
**I want to** filter search results by category, price range, and availability,
**so that** I can refine results to match my needs.

**Acceptance Criteria:**
- Filter panel is available on the search results page
- Filters include: Category, Price Range (min/max), In Stock only
- Multiple filters can be applied simultaneously
- Filters can be individually cleared or all cleared at once
- Result count updates as filters are applied

**MoSCoW:** Should Have | **Complexity:** L

---

### US-008 — View Product Detail Page

**As a** Guest or Customer,
**I want to** view a dedicated product detail page,
**so that** I can get full information about a product before purchasing.

**Acceptance Criteria:**
- Page displays: product name, full description, price, images, category, SKU, and stock status
- Multiple product images are viewable (gallery or carousel)
- Stock availability is clearly shown (In Stock / Out of Stock / Limited Stock)
- Page has a unique, shareable URL

**MoSCoW:** Must Have | **Complexity:** M

---

### US-009 — View Product Image Gallery

**As a** Guest or Customer,
**I want to** view multiple images of a product,
**so that** I can see the product from different angles before deciding.

**Acceptance Criteria:**
- Thumbnail images are clickable to expand to full size
- At least 1 image is always shown; supports up to 10 images
- Images are optimized for fast loading

**MoSCoW:** Should Have | **Complexity:** M

---

### US-010 — View Related Products

**As a** Guest or Customer,
**I want to** see related or similar products on a product detail page,
**so that** I can discover alternatives or complementary items.

**Acceptance Criteria:**
- A "Related Products" section shows up to 4 items
- Related products are from the same category
- Clicking a related product navigates to its detail page

**MoSCoW:** Could Have | **Complexity:** M

---

## U2 — Shopping Cart

**Description:** Covers all cart operations for authenticated customers and guests. Manages item selection, quantity control, and cart persistence.

**Team scope:** Cart frontend + cart backend service

**Depends on:** U1 must expose product detail API (name, price, image, stock status) for cart item rendering and stock validation

**Exposes to:** Nothing downstream in this system (checkout is out of scope)

---

### US-011 — Add Product to Cart

**As a** Customer,
**I want to** add a product to my shopping cart,
**so that** I can collect items I intend to purchase.

**Acceptance Criteria:**
- "Add to Cart" button is present on both product listing and detail pages
- Item is added with quantity defaulting to 1
- Cart item count in the header updates immediately
- User receives visual confirmation (toast/notification) that item was added
- Out-of-stock products cannot be added to the cart

**MoSCoW:** Must Have | **Complexity:** M
**Cross-unit note:** Stock status is read from U1's product API before allowing add-to-cart.

---

### US-012 — View Shopping Cart

**As a** Customer,
**I want to** view the contents of my shopping cart,
**so that** I can review my selected items before proceeding.

**Acceptance Criteria:**
- Cart page lists all added items with: name, image thumbnail, unit price, quantity, and line total
- Cart shows subtotal of all items
- Empty cart state displays a clear message and a link to browse products

**MoSCoW:** Must Have | **Complexity:** M

---

### US-013 — Update Item Quantity in Cart

**As a** Customer,
**I want to** change the quantity of an item in my cart,
**so that** I can buy more or fewer units without removing and re-adding the item.

**Acceptance Criteria:**
- Quantity can be increased or decreased via +/- controls or a direct input field
- Quantity cannot be set below 1
- Quantity cannot exceed available stock
- Line total updates immediately upon quantity change

**MoSCoW:** Must Have | **Complexity:** S

---

### US-014 — Remove Item from Cart

**As a** Customer,
**I want to** remove an item from my cart,
**so that** I can discard items I no longer wish to purchase.

**Acceptance Criteria:**
- Each cart item has a "Remove" action
- Item is removed immediately upon confirmation
- Cart totals recalculate after removal
- If cart becomes empty, the empty cart state is shown

**MoSCoW:** Must Have | **Complexity:** S

---

### US-015 — Persistent Cart

**As a** Customer,
**I want to** have my cart saved across sessions,
**so that** I don't lose my selections if I leave and return to the site.

**Acceptance Criteria:**
- Cart contents are preserved when the user logs out and logs back in
- Cart is associated with the authenticated user account, not the browser session

**MoSCoW:** Should Have | **Complexity:** M
**Cross-unit note:** Depends on the deferred Authentication epic for user identity.

---

### US-016 — Guest Cart

**As a** Guest,
**I want to** add items to a cart without logging in,
**so that** I can explore purchasing without creating an account first.

**Acceptance Criteria:**
- Guest cart is stored in the browser session/local storage
- Guest is prompted to log in or create an account at checkout
- Cart items from guest session are merged into the account cart upon login

**MoSCoW:** Could Have | **Complexity:** L
**Cross-unit note:** Cart merge on login depends on the deferred Authentication epic.

---

## U3 — Admin: Product & Inventory Management

**Description:** Covers all admin-facing capabilities for managing the product catalog and inventory. This is the foundational unit — it creates and manages the product and category data that U1 and U2 consume.

**Team scope:** Admin frontend + product/inventory backend services

**Depends on:** Nothing — this is the foundational unit

**Exposes to U1:** Product list, product detail, category list, featured flags, stock status via API
**Exposes to U2:** Stock availability per product via API

---

### US-017 — Add New Product

**As an** Admin,
**I want to** add a new product to the catalog,
**so that** customers can discover and purchase it.

**Acceptance Criteria:**
- Form fields: name, description, price, category, SKU, images (upload), stock quantity
- All required fields are validated before submission
- SKU must be unique; duplicate SKU shows a clear error
- Product is saved in draft or published state
- Admin receives confirmation upon successful creation

**MoSCoW:** Must Have | **Complexity:** M

---

### US-018 — Edit Existing Product

**As an** Admin,
**I want to** edit an existing product's details,
**so that** I can keep the catalog accurate and up to date.

**Acceptance Criteria:**
- All product fields are editable
- Changes are saved and immediately reflected in the catalog
- Audit trail records who made the change and when (extensibility hook for future roles)

**MoSCoW:** Must Have | **Complexity:** M

---

### US-019 — Delete / Deactivate Product

**As an** Admin,
**I want to** remove or deactivate a product,
**so that** unavailable or discontinued items are not shown to customers.

**Acceptance Criteria:**
- Admin can choose to permanently delete or soft-deactivate a product
- Deactivated products are hidden from customers but remain in the system
- Confirmation dialog is shown before permanent deletion
- Deleted products are removed from all customer carts

**MoSCoW:** Must Have | **Complexity:** M
**Cross-unit note:** Deletion must trigger cart cleanup in U2 via an event or API call.

---

### US-020 — Manage Product Categories

**As an** Admin,
**I want to** create, edit, and delete product categories,
**so that** the catalog is logically organized for customers.

**Acceptance Criteria:**
- Admin can add a new category with a name and optional description
- Admin can rename or delete a category
- Deleting a category prompts reassignment of products in that category
- Categories are reflected immediately in the customer-facing navigation

**MoSCoW:** Must Have | **Complexity:** M

---

### US-021 — Upload Product Images

**As an** Admin,
**I want to** upload one or more images for a product,
**so that** customers can visually evaluate the product.

**Acceptance Criteria:**
- Supports upload of JPG, PNG, and WebP formats
- Maximum file size per image: 5MB
- Up to 10 images per product
- Admin can set the primary/display image
- Images can be reordered or deleted

**MoSCoW:** Must Have | **Complexity:** M

---

### US-022 — Publish / Unpublish Product

**As an** Admin,
**I want to** control whether a product is visible to customers,
**so that** I can prepare products in advance and control their release.

**Acceptance Criteria:**
- Products have Published / Draft status
- Only published products appear in customer-facing pages
- Status can be toggled from the product list or detail view

**MoSCoW:** Should Have | **Complexity:** S

---

### US-023 — View Inventory Dashboard

**As an** Admin,
**I want to** see an overview of current inventory levels,
**so that** I can quickly identify low-stock or out-of-stock items.

**Acceptance Criteria:**
- Dashboard lists all products with current stock quantity
- Products below a configurable low-stock threshold are highlighted
- Out-of-stock products are clearly flagged
- Dashboard is sortable by stock level

**MoSCoW:** Must Have | **Complexity:** M

---

### US-024 — Update Stock Quantity

**As an** Admin,
**I want to** manually update the stock quantity for a product,
**so that** inventory reflects actual availability.

**Acceptance Criteria:**
- Admin can set an absolute quantity or apply an adjustment (+/-)
- Change is logged with timestamp and actor (extensibility hook)
- Updated quantity is immediately reflected in the customer-facing catalog

**MoSCoW:** Must Have | **Complexity:** S
**Cross-unit note:** Stock update must be immediately visible in U1 product listings and U2 cart validation.

---

### US-025 — Set Low-Stock Threshold

**As an** Admin,
**I want to** set a low-stock threshold per product,
**so that** I am alerted when stock falls below a safe level.

**Acceptance Criteria:**
- Threshold is configurable per product
- Products at or below threshold are flagged in the inventory dashboard
- Default threshold is configurable at the system level

**MoSCoW:** Should Have | **Complexity:** S

---

### US-026 — View Stock History / Audit Log

**As an** Admin,
**I want to** view a history of stock changes for a product,
**so that** I can audit inventory movements and identify discrepancies.

**Acceptance Criteria:**
- Log shows each stock change with: date, previous quantity, new quantity, actor, and reason
- Log is viewable per product
- Log entries are read-only

**MoSCoW:** Could Have | **Complexity:** M

---

### US-027 — Bulk Update Inventory

**As an** Admin,
**I want to** update stock quantities for multiple products at once,
**so that** I can efficiently process large inventory updates (e.g., after a stock delivery).

**Acceptance Criteria:**
- Admin can upload a CSV file with SKU and new quantity columns
- System validates the file and shows a preview before applying
- Errors in the file (unknown SKU, invalid quantity) are reported per row
- Successful updates are applied atomically

**MoSCoW:** Could Have | **Complexity:** L

---

## Summary

### Story Distribution

| Unit | Stories | Must Have | Should Have | Could Have |
|------|---------|-----------|-------------|------------|
| U1 — Product Catalog & Discovery | 10 | 3 | 4 | 3 |
| U2 — Shopping Cart | 6 | 4 | 1 | 1 |
| U3 — Admin: Product & Inventory | 11 | 8 | 2 | 2 |
| **Total** | **27** | **15** | **7** | **5** |

### Inter-Unit Dependencies

```
U3 (Admin: Product & Inventory)
 └──► U1 (Product Catalog & Discovery)
       └──► U2 (Shopping Cart)
```

| Dependency | What is shared |
|------------|----------------|
| U3 → U1 | Product list, product detail, categories, featured flags, stock status |
| U3 → U2 | Stock availability per product (for cart validation) |
| U1 → U2 | Product data (name, price, image) for cart item rendering |
| U3 ← U2 | Cart cleanup on product deletion (event/callback) |

### Recommended Build Order

1. **U3** — Build first; creates all product, category, and inventory data
2. **U1** — Build second; consumes U3 data to power customer-facing catalog
3. **U2** — Build last; consumes U1 product data to power cart operations

> Auth / Login epic is deferred. US-015 (Persistent Cart) and US-016 (Guest Cart merge) have a noted dependency on it.
