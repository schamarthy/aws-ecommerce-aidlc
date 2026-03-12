import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'

export default function CartPage() {
  const { cart, updateItem, removeItem, clearCart } = useCart()
  const navigate = useNavigate()

  if (!cart || cart.items.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-5xl mb-4">🛒</p>
        <p className="text-gray-600 mb-4 text-lg">Your cart is empty.</p>
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Shopping Cart</h1>
        <button
          onClick={clearCart}
          className="text-sm text-red-500 hover:underline"
        >
          Clear cart
        </button>
      </div>

      <div className="space-y-3 mb-8">
        {cart.items.map(item => (
          <div key={item.id} className="flex gap-4 bg-white border rounded-lg p-4 items-center">
            {/* Thumbnail */}
            <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden shrink-0">
              {item.primary_image_url ? (
                <img src={item.primary_image_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-300 text-2xl">📦</div>
              )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <Link
                to={`/products/${item.product_id}`}
                className="font-medium hover:underline truncate block"
              >
                {item.product_name}
              </Link>
              <p className="text-xs text-gray-400">SKU: {item.product_sku}</p>
              <p className="text-sm text-gray-600 mt-0.5">${item.unit_price.toFixed(2)} each</p>
            </div>

            {/* Qty controls */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => item.quantity > 1 ? updateItem(item.id, item.quantity - 1) : removeItem(item.id)}
                className="w-7 h-7 rounded border text-lg flex items-center justify-center hover:bg-gray-100"
              >
                −
              </button>
              <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
              <button
                onClick={() => updateItem(item.id, item.quantity + 1)}
                className="w-7 h-7 rounded border text-lg flex items-center justify-center hover:bg-gray-100"
              >
                +
              </button>
            </div>

            {/* Line total */}
            <div className="w-20 text-right shrink-0">
              <p className="font-semibold">${item.line_total.toFixed(2)}</p>
            </div>

            {/* Remove */}
            <button
              onClick={() => removeItem(item.id)}
              className="text-gray-400 hover:text-red-500 ml-2 shrink-0"
              aria-label="Remove"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="bg-white border rounded-lg p-6 max-w-sm ml-auto">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Items ({cart.item_count})</span>
          <span>${cart.subtotal.toFixed(2)}</span>
        </div>
        <div className="border-t pt-3 flex justify-between font-bold text-lg">
          <span>Subtotal</span>
          <span>${cart.subtotal.toFixed(2)}</span>
        </div>
        <button
          onClick={() => navigate('/checkout')}
          className="mt-4 w-full py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700"
        >
          Proceed to checkout
        </button>
      </div>
    </div>
  )
}
