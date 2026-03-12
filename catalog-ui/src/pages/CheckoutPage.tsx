import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { ordersApi } from '../api/orders'

export default function CheckoutPage() {
  const { cart, clearCart } = useCart()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    shipping_name: '',
    shipping_email: '',
    shipping_address: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!cart || cart.items.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600 text-lg mb-4">Your cart is empty.</p>
        <button
          onClick={() => navigate('/products')}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          Browse Products
        </button>
      </div>
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const order = await ordersApi.checkout(form)
      await clearCart()
      navigate(`/orders/${order.id}`, { state: { order } })
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        'Checkout failed. Please try again.'
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Shipping form */}
      <div>
        <h1 className="text-2xl font-bold mb-6">Checkout</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
            <input
              type="text"
              required
              value={form.shipping_name}
              onChange={e => setForm(f => ({ ...f, shipping_name: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Jane Doe"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              required
              value={form.shipping_email}
              onChange={e => setForm(f => ({ ...f, shipping_email: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="jane@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Shipping address</label>
            <textarea
              required
              rows={3}
              value={form.shipping_address}
              onChange={e => setForm(f => ({ ...f, shipping_address: e.target.value }))}
              className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
              placeholder="123 Main St, City, State 12345"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Placing order…' : `Place order · $${cart.subtotal.toFixed(2)}`}
          </button>
        </form>
      </div>

      {/* Order summary */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Order summary</h2>
        <div className="bg-white border rounded-lg divide-y">
          {cart.items.map(item => (
            <div key={item.id} className="flex gap-3 p-4 items-center">
              <div className="w-12 h-12 bg-gray-100 rounded overflow-hidden shrink-0">
                {item.primary_image_url ? (
                  <img src={item.primary_image_url} alt="" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-300 text-xl">📦</div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate text-sm">{item.product_name}</p>
                <p className="text-xs text-gray-400">Qty: {item.quantity}</p>
              </div>
              <p className="text-sm font-semibold shrink-0">${item.line_total.toFixed(2)}</p>
            </div>
          ))}
          <div className="p-4 flex justify-between font-bold">
            <span>Total</span>
            <span>${cart.subtotal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
