import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { catalogApi } from '../api/catalog'
import FilterPanel from '../components/FilterPanel'
import Pagination from '../components/Pagination'
import ProductCard from '../components/ProductCard'
import type { Category, ProductFilters, ProductPage } from '../types'

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest' },
  { value: 'price_asc', label: 'Price: Low → High' },
  { value: 'price_desc', label: 'Price: High → Low' },
  { value: 'name_asc', label: 'Name A–Z' },
] as const

export default function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [categories, setCategories] = useState<Category[]>([])
  const [result, setResult] = useState<ProductPage | null>(null)
  const [loading, setLoading] = useState(false)

  const filters: ProductFilters = {
    q: searchParams.get('q') || undefined,
    category_id: searchParams.get('category_id') ? +searchParams.get('category_id')! : undefined,
    min_price: searchParams.get('min_price') ? +searchParams.get('min_price')! : undefined,
    max_price: searchParams.get('max_price') ? +searchParams.get('max_price')! : undefined,
    in_stock: searchParams.get('in_stock') === 'true' || undefined,
    sort: (searchParams.get('sort') as ProductFilters['sort']) || 'newest',
    page: searchParams.get('page') ? +searchParams.get('page')! : 1,
    page_size: 20,
  }

  useEffect(() => {
    catalogApi.categories().then(setCategories)
  }, [])

  useEffect(() => {
    setLoading(true)
    catalogApi.products(filters).then(data => {
      setResult(data)
      setLoading(false)
    })
  }, [searchParams.toString()])

  function updateFilters(updates: Partial<ProductFilters>) {
    const next = new URLSearchParams(searchParams)
    Object.entries(updates).forEach(([k, v]) => {
      if (v === undefined || v === null) next.delete(k)
      else next.set(k, String(v))
    })
    setSearchParams(next)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">
          {filters.q ? `Results for "${filters.q}"` : 'Products'}
        </h1>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-gray-600">Sort:</label>
          <select
            value={filters.sort}
            onChange={e => updateFilters({ sort: e.target.value as ProductFilters['sort'], page: 1 })}
            className="border rounded px-2 py-1 text-sm"
          >
            {SORT_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex gap-6">
        <FilterPanel
          categories={categories}
          filters={filters}
          onChange={updateFilters}
          total={result?.total ?? 0}
        />

        <div className="flex-1">
          {loading ? (
            <p className="text-gray-400 text-sm">Loading…</p>
          ) : result && result.items.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <p className="text-4xl mb-3">🔍</p>
              <p>No products found. Try adjusting your filters.</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {result?.items.map(p => <ProductCard key={p.id} product={p} />)}
              </div>
              {result && (
                <Pagination
                  page={result.page}
                  pages={result.pages}
                  onPage={p => updateFilters({ page: p })}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
