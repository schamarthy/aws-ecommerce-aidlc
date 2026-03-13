import axios from 'axios'
import type { Order } from '../types/order'

const api = axios.create({ baseURL: '/api/orders' })

function getToken(): string {
  let token = localStorage.getItem('cart_session_token')
  if (!token) {
    token = crypto.randomUUID()
    localStorage.setItem('cart_session_token', token)
  }
  return token
}

function headers() {
  return { 'X-Session-Token': getToken() }
}

export interface CheckoutPayload {
  shipping_name: string
  shipping_email: string
  shipping_address: string
}

export const ordersApi = {
  checkout: (payload: CheckoutPayload) =>
    api.post<Order>('/checkout', payload, { headers: headers() }).then(r => r.data),
  getOrders: () =>
    api.get<Order[]>('', { headers: headers() }).then(r => r.data),
  getOrder: (id: number) =>
    api.get<Order>(`/${id}`, { headers: headers() }).then(r => r.data),
}
