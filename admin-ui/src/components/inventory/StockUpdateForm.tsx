import { useEffect, useState } from 'react'
import { inventoryApi } from '../../api/inventory'
import type { Inventory } from '../../types'

interface Props {
  productId: number
  onDone: () => void
}

export default function StockUpdateForm({ productId, onDone }: Props) {
  const [inventory, setInventory] = useState<Inventory | null>(null)
  const [quantity, setQuantity] = useState('')
  const [threshold, setThreshold] = useState('')
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    inventoryApi.get(productId).then(inv => {
      setInventory(inv)
      setQuantity(String(inv.quantity))
      setThreshold(String(inv.low_stock_threshold))
    })
  }, [productId])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await inventoryApi.update(productId, parseInt(quantity), 'admin', reason || undefined)
      if (threshold !== String(inventory?.low_stock_threshold)) {
        await inventoryApi.updateThreshold(productId, parseInt(threshold))
      }
      onDone()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      setError(msg ?? 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  if (!inventory) return <p className="text-sm text-gray-500">Loading…</p>

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-xs">
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <div>
        <label className="block text-sm font-medium mb-1">Quantity *</label>
        <input
          required
          type="number"
          min="0"
          value={quantity}
          onChange={e => setQuantity(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Low-stock threshold</label>
        <input
          type="number"
          min="0"
          value={threshold}
          onChange={e => setThreshold(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Reason</label>
        <input
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="e.g. restock, manual correction"
          className="w-full border rounded px-3 py-2 text-sm"
        />
      </div>
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Saving…' : 'Update Stock'}
        </button>
        <button
          type="button"
          onClick={onDone}
          className="px-4 py-2 border rounded text-sm hover:bg-gray-100"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
