import { useEffect, useState } from 'react'
import { inventoryApi } from '../api/inventory'
import InventoryDashboard from '../components/inventory/InventoryDashboard'
import StockHistory from '../components/inventory/StockHistory'
import StockUpdateForm from '../components/inventory/StockUpdateForm'
import type { InventoryDashboardItem } from '../types'

type View = 'dashboard' | 'update' | 'history'

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryDashboardItem[]>([])
  const [view, setView] = useState<View>('dashboard')
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null)

  async function load() {
    setItems(await inventoryApi.dashboard())
  }

  useEffect(() => { load() }, [])

  function handleUpdate(productId: number) {
    setSelectedProductId(productId)
    setView('update')
  }

  function handleHistory(productId: number) {
    setSelectedProductId(productId)
    setView('history')
  }

  async function afterUpdate() {
    await load()
    setView('dashboard')
    setSelectedProductId(null)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Inventory</h1>
        {view !== 'dashboard' && (
          <button
            onClick={() => { setView('dashboard'); setSelectedProductId(null) }}
            className="px-3 py-1.5 border rounded text-sm hover:bg-gray-100"
          >
            ← Back
          </button>
        )}
      </div>

      {view === 'dashboard' && (
        <InventoryDashboard
          items={items}
          onUpdate={handleUpdate}
          onHistory={handleHistory}
        />
      )}

      {view === 'update' && selectedProductId !== null && (
        <div>
          <h2 className="font-semibold mb-3">Update Stock — Product #{selectedProductId}</h2>
          <StockUpdateForm productId={selectedProductId} onDone={afterUpdate} />
        </div>
      )}

      {view === 'history' && selectedProductId !== null && (
        <StockHistory
          productId={selectedProductId}
          onClose={() => { setView('dashboard'); setSelectedProductId(null) }}
        />
      )}
    </div>
  )
}
