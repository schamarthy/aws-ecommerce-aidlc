import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { catalogApi } from '../api/catalog'
import ProductCard from '../components/ProductCard'
import { useCart } from '../context/CartContext'
import type { ImageOut, ProductDetail, ProductSummary, StockStatus } from '../types'

const stockBadge: Record<StockStatus, { text: string; cls: string }> = {
  in_stock: { text: 'In Stock', cls: 'bg-green-100 text-green-700' },
  low_stock: { text: 'Limited Stock', cls: 'bg-yellow-100 text-yellow-700' },
  out_of_stock: { text: 'Out of Stock', cls: 'bg-red-100 text-red-600' },
}

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { addToCart, loading: cartLoading } = useCart()
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [related, setRelated] = useState<ProductSummary[]>([])
  const [activeImage, setActiveImage] = useState<ImageOut | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    setNotFound(false)
    catalogApi.product(+id)
      .then(p => {
        setProduct(p)
        const primary = p.images.find(i => i.is_primary) ?? p.images[0] ?? null
        setActiveImage(primary)
        return catalogApi.related(+id)
      })
      .then(setRelated)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="text-gray-400 text-sm">Loading…</p>
  if (notFound || !product)
    return (
      <div className="text-center py-16">
        <p className="text-5xl mb-4">😕</p>
        <p className="text-gray-600 mb-4">Product not found.</p>
        <Link to="/products" className="text-indigo-600 hover:underline">Browse Products</Link>
      </div>
    )

  const badge = stockBadge[product.stock_status]

  const asSummary: ProductSummary = {
    id: product.id,
    name: product.name,
    price: product.price,
    sku: product.sku,
    is_featured: product.is_featured,
    category_id: product.category_id,
    primary_image_url: activeImage?.storage_url ?? null,
    stock_status: product.stock_status,
  }

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="text-xs text-gray-500 mb-4 flex gap-1 flex-wrap">
        <Link to="/" className="hover:underline">Home</Link>
        <span>/</span>
        <Link to="/products" className="hover:underline">Products</Link>
        {product.category && (
          <>
            <span>/</span>
            <Link to={`/products?category_id=${product.category_id}`} className="hover:underline">
              {product.category.name}
            </Link>
          </>
        )}
        <span>/</span>
        <span className="text-gray-800">{product.name}</span>
      </nav>

      {/* Main layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Image gallery */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden mb-3">
            {activeImage ? (
              <img src={activeImage.storage_url} alt={product.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-300 text-6xl">📦</div>
            )}
          </div>
          {product.images.length > 1 && (
            <div className="flex gap-2 flex-wrap">
              {product.images.map(img => (
                <button
                  key={img.id}
                  onClick={() => setActiveImage(img)}
                  className={`w-16 h-16 rounded border-2 overflow-hidden transition-colors ${activeImage?.id === img.id ? 'border-indigo-500' : 'border-transparent hover:border-gray-300'}`}
                >
                  <img src={img.storage_url} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product info */}
        <div>
          <h1 className="text-2xl font-bold mb-1">{product.name}</h1>
          <p className="text-xs text-gray-400 mb-3">SKU: {product.sku}</p>
          <p className="text-3xl font-bold text-indigo-700 mb-3">
            ${Number(product.price).toFixed(2)}
          </p>
          <span className={`inline-block text-xs font-medium px-3 py-1 rounded-full mb-4 ${badge.cls}`}>
            {badge.text}
          </span>
          {product.description && (
            <p className="text-gray-600 text-sm leading-relaxed mb-5">{product.description}</p>
          )}
          {product.category && (
            <p className="text-sm text-gray-500 mb-5">
              Category:{' '}
              <Link to={`/products?category_id=${product.category_id}`} className="text-indigo-600 hover:underline">
                {product.category.name}
              </Link>
            </p>
          )}
          <button
            disabled={product.stock_status === 'out_of_stock' || cartLoading}
            onClick={() => addToCart(asSummary)}
            className="w-full py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {product.stock_status === 'out_of_stock' ? 'Out of Stock' : 'Add to Cart'}
          </button>
        </div>
      </div>

      {/* Related products */}
      {related.length > 0 && (
        <section>
          <h2 className="text-lg font-bold mb-4">Related Products</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {related.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}
    </div>
  )
}
