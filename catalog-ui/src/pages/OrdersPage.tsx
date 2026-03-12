import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ordersApi } from '../api/orders'
import type { Order } from '../types/order'

const STATUS_COLORS: Record<string, string> = {
  confirmed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  cancelled: 'bg-red-100 text-red-700',
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ordersApi.getOrders()
      .then(setOrders)
      .catch(() => setError('Could not load orders'))
  }, [])

  if (error) return <div className="text-center py-20 text-red-500">{error}</div>
  if (!orders) return <div className="text-center py-20 text-gray-400">Loading…</div>

  if (orders.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-4xl mb-4">📋</p>
        <p className="text-gray-600 text-lg mb-4">No orders yet.</p>
        <Link
          to="/products"
          className="inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          Browse Products
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Your Orders</h1>
      <div className="space-y-4">
        {orders.map(order => (
          <Link
            key={order.id}
            to={`/orders/${order.id}`}
            className="block bg-white border rounded-lg p-5 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-semibold">Order #{order.id}</p>
                <p className="text-sm text-gray-500 mt-0.5">
                  {new Date(order.created_at).toLocaleDateString()} · {order.items.length} item(s)
                </p>
                <p className="text-sm text-gray-500">{order.shipping_name}</p>
              </div>
              <div className="text-right shrink-0">
                <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[order.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {order.status}
                </span>
                <p className="font-bold mt-1">${order.total_amount.toFixed(2)}</p>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {order.items.map(item => (
                <span key={item.id} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {item.product_name} ×{item.quantity}
                </span>
              ))}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
