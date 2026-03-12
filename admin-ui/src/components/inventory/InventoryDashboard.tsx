import type { InventoryDashboardItem } from '../../types'

interface Props {
  items: InventoryDashboardItem[]
  onUpdate: (productId: number) => void
  onHistory: (productId: number) => void
}

export default function InventoryDashboard({ items, onUpdate, onHistory }: Props) {
  if (items.length === 0) {
    return <p className="text-gray-500 text-sm">No inventory records yet.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100 text-left">
            <th className="px-3 py-2 border">Product</th>
            <th className="px-3 py-2 border">SKU</th>
            <th className="px-3 py-2 border">Quantity</th>
            <th className="px-3 py-2 border">Threshold</th>
            <th className="px-3 py-2 border">Status</th>
            <th className="px-3 py-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr
              key={item.product_id}
              className={item.is_low_stock ? 'bg-red-50' : 'hover:bg-gray-50'}
            >
              <td className="px-3 py-2 border font-medium">{item.product_name}</td>
              <td className="px-3 py-2 border font-mono text-xs">{item.sku}</td>
              <td className="px-3 py-2 border">{item.quantity}</td>
              <td className="px-3 py-2 border">{item.low_stock_threshold}</td>
              <td className="px-3 py-2 border">
                {item.is_low_stock ? (
                  <span className="text-xs font-medium text-red-600 bg-red-100 px-2 py-0.5 rounded">
                    Low Stock
                  </span>
                ) : (
                  <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-0.5 rounded">
                    OK
                  </span>
                )}
              </td>
              <td className="px-3 py-2 border whitespace-nowrap">
                <button
                  onClick={() => onUpdate(item.product_id)}
                  className="text-indigo-600 hover:underline mr-3"
                >
                  Update
                </button>
                <button
                  onClick={() => onHistory(item.product_id)}
                  className="text-gray-600 hover:underline"
                >
                  History
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
