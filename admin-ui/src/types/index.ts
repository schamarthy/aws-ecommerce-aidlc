// ─── Categories ──────────────────────────────────────────────────────────────

export interface Category {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  description?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
}

// ─── Products ────────────────────────────────────────────────────────────────

export type ProductStatus = 'active' | 'inactive' | 'archived'

export interface ProductImage {
  id: number
  product_id: number
  storage_url: string
  is_primary: boolean
  display_order: number
  created_at: string
}

export interface Product {
  id: number
  name: string
  description: string | null
  price: number
  sku: string
  status: ProductStatus
  is_featured: boolean
  category_id: number | null
  created_by: string | null
  updated_by: string | null
  images: ProductImage[]
  created_at: string
  updated_at: string
}

export interface ProductCreate {
  name: string
  description?: string
  price: number
  sku: string
  status?: ProductStatus
  is_featured?: boolean
  category_id?: number
  created_by?: string
}

export interface ProductUpdate {
  name?: string
  description?: string
  price?: number
  sku?: string
  status?: ProductStatus
  is_featured?: boolean
  category_id?: number
  updated_by?: string
}

export interface ProductAuditLog {
  id: number
  product_id: number
  field_name: string
  previous_value: string | null
  new_value: string | null
  actor: string
  changed_at: string
}

// ─── Inventory ────────────────────────────────────────────────────────────────

export interface Inventory {
  id: number
  product_id: number
  quantity: number
  low_stock_threshold: number
  updated_at: string
}

export interface InventoryDashboardItem {
  product_id: number
  product_name: string
  sku: string
  quantity: number
  low_stock_threshold: number
  is_low_stock: boolean
}

export interface StockAuditLog {
  id: number
  product_id: number
  inventory_id: number
  previous_quantity: number
  new_quantity: number
  adjustment: number
  actor: string
  reason: string | null
  created_at: string
}

export interface BulkUpdateItem {
  product_id: number
  quantity: number
  actor?: string
  reason?: string
}
