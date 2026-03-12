# Plan: Group User Stories into Buildable Units

## Deliverables
- `aidlc-docs/story-artifacts/units.md` — Units with grouped user stories and acceptance criteria

---

## Grouping Rationale

Units are designed around these principles:
- **High cohesion**: stories within a unit share the same domain, data model, and team skill set
- **Loose coupling**: units expose clean interfaces (APIs/contracts) to each other
- **Independent deliverability**: each unit can be built, tested, and deployed without waiting for another unit (except noted dependencies)

---

## Finalized Units

| Unit | Name | Stories | Depends On |
|------|------|---------|------------|
| U1 | Product Catalog & Discovery | US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010 | U3 (for featured/category admin controls) |
| U2 | Shopping Cart | US-011, US-012, US-013, US-014, US-015, US-016 | U1 (product data + stock status) |
| U3 | Admin (Product Management + Inventory) | US-017, US-018, US-019, US-020, US-021, US-022, US-023, US-024, US-025, US-026, US-027 | — (foundational unit) |

> **Decision — Admin:** Merged into one Admin unit (U3). Single team owns product management and inventory management.
> **Decision — Search:** Bundled with Product Catalog into U1. Same team handles all product discovery.

---

## Steps

- [x] **Step 1 — Confirm unit boundaries based on clarification responses**
  Finalize unit definitions based on your answers to the two clarification questions above.

- [x] **Step 2 — Map each user story to its unit**
  Assign all 27 stories to units; document any cross-unit dependencies.

- [x] **Step 3 — Write Unit 1: Product Catalog**
  Include stories, acceptance criteria, and dependency notes.

- [x] **Step 4 — Write Unit 2: Shopping Cart**
  Include stories, acceptance criteria, and dependency notes.

- [x] **Step 5 — Write Unit 3: Admin (Product Management + Inventory)**
  Include stories, acceptance criteria, and dependency notes.

- [x] **Step 8 — Write summary table and dependency graph**
  Summarize all units, story counts, MoSCoW breakdown, and inter-unit dependencies.

- [x] **Step 9 — Write output to story-artifacts/units.md**
  Format and save the final units document.

---

## Notes
- No technology or implementation decisions will be made at this stage
- Units define functional boundaries only
- Cross-unit dependencies are noted but not designed
