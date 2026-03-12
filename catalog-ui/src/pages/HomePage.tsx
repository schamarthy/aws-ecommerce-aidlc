import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { catalogApi } from '../api/catalog'
import ProductCard from '../components/ProductCard'
import type { ProductSummary } from '../types'

export default function HomePage() {
  const [featured, setFeatured] = useState<ProductSummary[]>([])

  useEffect(() => {
    catalogApi.featured().then(setFeatured)
  }, [])

  return (
    <div>
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-16 px-6 text-center rounded-xl mb-10">
        <h1 className="text-4xl font-bold mb-3">Welcome to Shop</h1>
        <p className="text-indigo-100 mb-6">Discover amazing products at great prices.</p>
        <Link
          to="/products"
          className="inline-block bg-white text-indigo-700 font-semibold px-6 py-2 rounded-full hover:bg-indigo-50 transition-colors"
        >
          Browse All Products
        </Link>
      </div>

      {featured.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4">Featured Products</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {featured.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}
    </div>
  )
}
