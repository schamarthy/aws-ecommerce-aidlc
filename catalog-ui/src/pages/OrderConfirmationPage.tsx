import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ordersApi } from '../api/orders'
import type { Order } from '../types/order'

export default function OrderConfirmationPage() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const [order, setOrder] = useState<Order | null>(location.state?.order ?? null)
  const [loading, setLoading] = useState(!order)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!order && id) {
      ordersApi.getOrder(Number(id))
        .then(setOrder)
        .catch(() => setError('Order not found'))
        .finally(() => setLoading(false))
    }
  }, [id, order])

  if (loading) return <div className="text-center py-20 text-gray-500">Loading…</div>
  if (error || !order) return <div className="text-center py-20 text-red-500">{error ?? 'Order not found'}</div>

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">✅</div>
        <h1 className="text-2xl font-bold text-gray-900">Order confirmed!</h1>
        <p className="text-gray-500 mt-1">Order #{order.id} · {new Date(order.created_at).toLocaleDateString()}</p>
      </div>

      {/* Shipping info */}
      <div className="bg-white border rounded-lg p-5 mb-4">
        <h2 className="font-semibold mb-3 text-gray-700">Shipping to</h2>
        <p className="font-medium">{order.shipping_name}</p>
        <p className="text-sm text-gray-500">{order.shipping_email}</p>
        <p className="text-sm text-gray-500 mt-1 whitespace-pre-line">{order.shipping_address}</p>
      </div>

      {/* Items */}
      <div className="bg-white border rounded-lg divide-y mb-4">
        {order.items.map(item => (
          <div key={item.id} className="flex gap-3 p-4 items-center">
            <div className="w-12 h-12 bg-gray-100 rounded overflow-hidden shrink-0">
              {item.primary_image_url ? (
                <img src={item.primary_image_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-300 text-xl">📦</div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{item.product_name}</p>
              <p className="text-xs text-gray-400">SKU: {item.product_sku} · Qty: {item.quantity}</p>
            </div>
            <p className="text-sm font-semibold">${item.line_total.toFixed(2)}</p>
          </div>
        ))}
        <div className="p-4 flex justify-between font-bold">
          <span>Total</span>
          <span>${order.total_amount.toFixed(2)}</span>
        </div>
      </div>

      <div className="flex gap-3 justify-center">
        <Link
          to="/orders"
          className="px-5 py-2 border rounded-lg text-sm hover:bg-gray-50"
        >
          View all orders
        </Link>
        <Link
          to="/products"
          className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
        >
          Continue shopping
        </Link>
      </div>
    </div>
  )
}
