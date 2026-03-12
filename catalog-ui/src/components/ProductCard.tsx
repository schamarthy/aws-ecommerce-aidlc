import { Link } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import type { ProductSummary, StockStatus } from '../types'

const stockLabel: Record<StockStatus, { text: string; cls: string }> = {
  in_stock: { text: 'In Stock', cls: 'text-green-600' },
  low_stock: { text: 'Low Stock', cls: 'text-yellow-600' },
  out_of_stock: { text: 'Out of Stock', cls: 'text-red-500' },
}

interface Props {
  product: ProductSummary
}

export default function ProductCard({ product }: Props) {
  const { addToCart, loading } = useCart()
  const stock = stockLabel[product.stock_status]

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow flex flex-col">
      <Link to={`/products/${product.id}`} className="block">
        <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
          {product.primary_image_url ? (
            <img src={product.primary_image_url} alt={product.name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300 text-4xl">📦</div>
          )}
        </div>
      </Link>

      <div className="p-3 flex flex-col flex-1">
        <Link to={`/products/${product.id}`} className="hover:underline">
          <h3 className="font-medium text-sm leading-snug mb-1">{product.name}</h3>
        </Link>
        <p className="text-indigo-700 font-bold text-base mb-1">${Number(product.price).toFixed(2)}</p>
        <p className={`text-xs mb-3 ${stock.cls}`}>{stock.text}</p>

        <button
          disabled={product.stock_status === 'out_of_stock' || loading}
          onClick={() => addToCart(product)}
          className="mt-auto w-full py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Add to Cart
        </button>
      </div>
    </div>
  )
}
