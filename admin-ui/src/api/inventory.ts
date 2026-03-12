import api from './client'
import type {
  BulkUpdateItem,
  Inventory,
  InventoryDashboardItem,
  StockAuditLog,
} from '../types'

export const inventoryApi = {
  dashboard: () => api.get<InventoryDashboardItem[]>('/inventory').then(r => r.data),
  get: (productId: number) =>
    api.get<Inventory>(`/inventory/${productId}`).then(r => r.data),
  update: (productId: number, quantity: number, actor = 'admin', reason?: string) =>
    api
      .put<Inventory>(`/inventory/${productId}`, { quantity, actor, reason })
      .then(r => r.data),
  updateThreshold: (productId: number, low_stock_threshold: number) =>
    api
      .patch<Inventory>(`/inventory/${productId}/threshold`, { low_stock_threshold })
      .then(r => r.data),
  history: (productId: number) =>
    api.get<StockAuditLog[]>(`/inventory/${productId}/history`).then(r => r.data),
  bulkUpdate: (updates: BulkUpdateItem[]) =>
    api.post<Inventory[]>('/inventory/bulk-update', { updates }).then(r => r.data),
}
