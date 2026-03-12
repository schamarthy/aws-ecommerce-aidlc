export type OrderStatus = 'pending' | 'confirmed' | 'cancelled'

export interface OrderItem {
  id: number
  product_id: number
  product_name: string
  product_sku: string
  primary_image_url: string | null
  unit_price: number
  quantity: number
  line_total: number
}

export interface Order {
  id: number
  session_token: string
  status: OrderStatus
  shipping_name: string
  shipping_email: string
  shipping_address: string
  total_amount: number
  created_at: string
  items: OrderItem[]
}
