export interface CartItem {
  id: number
  product_id: number
  product_name: string
  product_sku: string
  primary_image_url: string | null
  unit_price: number
  quantity: number
  line_total: number
  added_at: string
}

export interface Cart {
  id: number
  session_token: string
  items: CartItem[]
  subtotal: number
  item_count: number
}
