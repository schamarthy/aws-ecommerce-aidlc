import api from './client'
import type { Product, ProductAuditLog, ProductCreate, ProductStatus, ProductUpdate } from '../types'

export const productsApi = {
  list: (params?: { status?: ProductStatus; category_id?: number }) =>
    api.get<Product[]>('/products', { params }).then(r => r.data),
  get: (id: number) => api.get<Product>(`/products/${id}`).then(r => r.data),
  create: (data: ProductCreate) => api.post<Product>('/products', data).then(r => r.data),
  update: (id: number, data: ProductUpdate) =>
    api.put<Product>(`/products/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/products/${id}`),
  updateStatus: (id: number, status: ProductStatus) =>
    api.patch<Product>(`/products/${id}/status`, { status }).then(r => r.data),
  updateFeatured: (id: number, is_featured: boolean) =>
    api.patch<Product>(`/products/${id}/featured`, { is_featured }).then(r => r.data),
  getAuditLog: (id: number) =>
    api.get<ProductAuditLog[]>(`/products/${id}/audit`).then(r => r.data),
  uploadImage: (
    id: number,
    file: File,
    opts?: { is_primary?: boolean; display_order?: number }
  ) => {
    const form = new FormData()
    form.append('file', file)
    const params = new URLSearchParams()
    if (opts?.is_primary !== undefined) params.set('is_primary', String(opts.is_primary))
    if (opts?.display_order !== undefined) params.set('display_order', String(opts.display_order))
    return api
      .post(`/products/${id}/images?${params}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then(r => r.data)
  },
  deleteImage: (productId: number, imageId: number) =>
    api.delete(`/products/${productId}/images/${imageId}`),
}
