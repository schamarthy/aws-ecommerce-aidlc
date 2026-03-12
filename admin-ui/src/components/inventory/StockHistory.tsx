import { useEffect, useState } from 'react'
import { inventoryApi } from '../../api/inventory'
import type { StockAuditLog } from '../../types'

interface Props {
  productId: number
  onClose: () => void
}

export default function StockHistory({ productId, onClose }: Props) {
  const [logs, setLogs] = useState<StockAuditLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    inventoryApi.history(productId).then(data => {
      setLogs(data)
      setLoading(false)
    })
  }, [productId])

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Stock History — Product #{productId}</h3>
        <button onClick={onClose} className="text-sm text-gray-500 hover:underline">Close</button>
      </div>
      {loading ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : logs.length === 0 ? (
        <p className="text-sm text-gray-500">No history yet.</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-100 text-left">
              <th className="px-3 py-2 border">Date</th>
              <th className="px-3 py-2 border">Previous</th>
              <th className="px-3 py-2 border">New</th>
              <th className="px-3 py-2 border">Adjustment</th>
              <th className="px-3 py-2 border">Actor</th>
              <th className="px-3 py-2 border">Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-3 py-2 border text-xs text-gray-600">
                  {new Date(log.created_at).toLocaleString()}
                </td>
                <td className="px-3 py-2 border">{log.previous_quantity}</td>
                <td className="px-3 py-2 border">{log.new_quantity}</td>
                <td className={`px-3 py-2 border font-medium ${log.adjustment >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {log.adjustment >= 0 ? '+' : ''}{log.adjustment}
                </td>
                <td className="px-3 py-2 border">{log.actor}</td>
                <td className="px-3 py-2 border text-gray-600">{log.reason ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
