import axios from 'axios'
import type {
  AutocompleteResult,
  Category,
  ProductDetail,
  ProductFilters,
  ProductPage,
  ProductSummary,
} from '../types'

const api = axios.create({ baseURL: '/catalog' })

export const catalogApi = {
  categories: () => api.get<Category[]>('/categories').then(r => r.data),

  featured: (limit = 8) =>
    api.get<ProductSummary[]>('/products/featured', { params: { limit } }).then(r => r.data),

  autocomplete: (q: string) =>
    api.get<AutocompleteResult[]>('/products/autocomplete', { params: { q } }).then(r => r.data),

  products: (filters: ProductFilters = {}) =>
    api.get<ProductPage>('/products', { params: filters }).then(r => r.data),

  product: (id: number) => api.get<ProductDetail>(`/products/${id}`).then(r => r.data),

  related: (id: number, limit = 4) =>
    api
      .get<ProductSummary[]>(`/products/${id}/related`, { params: { limit } })
      .then(r => r.data),
}
