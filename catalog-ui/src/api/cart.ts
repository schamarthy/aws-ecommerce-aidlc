import axios from 'axios'
import type { Cart } from '../types/cart'

const api = axios.create({ baseURL: '/cart' })

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

export const cartApi = {
  getCart: () => api.get<Cart>('', { headers: headers() }).then(r => r.data),
  addItem: (product_id: number, quantity = 1) =>
    api.post<Cart>('/items', { product_id, quantity }, { headers: headers() }).then(r => r.data),
  updateItem: (item_id: number, quantity: number) =>
    api.patch<Cart>(`/items/${item_id}`, { quantity }, { headers: headers() }).then(r => r.data),
  removeItem: (item_id: number) =>
    api.delete<Cart>(`/items/${item_id}`, { headers: headers() }).then(r => r.data),
  clearCart: () => api.delete<Cart>('', { headers: headers() }).then(r => r.data),
}
