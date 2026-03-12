export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock'

export interface Category {
  id: number
  name: string
  description: string | null
}

export interface ImageOut {
  id: number
  storage_url: string
  is_primary: boolean
  display_order: number
}

export interface ProductSummary {
  id: number
  name: string
  price: number
  sku: string
  is_featured: boolean
  category_id: number | null
  primary_image_url: string | null
  stock_status: StockStatus
}

export interface ProductDetail {
  id: number
  name: string
  description: string | null
  price: number
  sku: string
  is_featured: boolean
  category_id: number | null
  category: Category | null
  images: ImageOut[]
  stock_status: StockStatus
  quantity: number
}

export interface ProductPage {
  items: ProductSummary[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface AutocompleteResult {
  id: number
  name: string
  primary_image_url: string | null
}

export interface ProductFilters {
  q?: string
  category_id?: number
  min_price?: number
  max_price?: number
  in_stock?: boolean
  sort?: 'price_asc' | 'price_desc' | 'name_asc' | 'newest'
  page?: number
  page_size?: number
}
