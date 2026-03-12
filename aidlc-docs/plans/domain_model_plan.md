# Plan: Design Domain Model for Product Catalog System

## Deliverables
- `aidlc-docs/design-artifacts/domain_model.md` — Full domain model including:
  - Business components
  - Data models (entities, attributes, relationships)
  - APIs per component
  - Component interaction diagrams (text-based)

---

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| 1 | Search architecture | Option A — Search is a capability within the Product Catalog component; queries the same product data store |
| 2 | Image storage | Option A — Dedicated Image Storage component; Product entity holds only image metadata (URLs, order, primary flag) |
| 3 | Audit trail scope | Option B — Scoped per domain: product audit within Product component, stock audit within Inventory component |
| 4 | Cart data | Option A — Cart stores a snapshot of product data (name, price, thumbnail) at add-to-cart time |

---

## Steps

- [x] **Step 1 — Confirm clarifications**
  Record decisions from the 4 clarification questions above before proceeding.

- [x] **Step 2 — Define business components**
  Identify all components at business level (not code modules), their responsibilities, and team ownership mapping to U1/U2/U3 units.

- [x] **Step 3 — Design core data models**
  Define all entities, their attributes, data types, and relationships (1:1, 1:N, M:N). Cover:
  - Product, Category, ProductImage
  - Inventory, StockAuditLog
  - Cart, CartItem
  - (Audit log entity if Option A chosen in Clarification 3)

- [x] **Step 4 — Define APIs per component**
  For each component, list the API operations it exposes (resource, method, purpose). No implementation details — business-level contracts only.

- [x] **Step 5 — Define component interactions**
  Document how components interact to fulfill each epic:
  - Which component calls which
  - What data is exchanged
  - Direction of dependency

- [x] **Step 6 — Draw component interaction diagram (text-based)**
  Produce an ASCII/text diagram showing all components and their interactions.

- [x] **Step 7 — Review domain model for completeness**
  Verify all 27 user stories are covered by at least one component + data model + API operation.

- [x] **Step 8 — Write output to design-artifacts/domain_model.md**
  Format and save the final domain model document.

---

## Notes
- No code, frameworks, or technology stack decisions at this stage
- Domain model is at the business/logical level
- All decisions are based on the 27 user stories in user_stories.md and the 3 units in units.md
