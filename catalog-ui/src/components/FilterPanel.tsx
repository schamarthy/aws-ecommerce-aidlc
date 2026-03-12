import type { Category, ProductFilters } from '../types'

interface Props {
  categories: Category[]
  filters: ProductFilters
  onChange: (f: Partial<ProductFilters>) => void
  total: number
}

export default function FilterPanel({ categories, filters, onChange, total }: Props) {
  return (
    <aside className="w-52 shrink-0">
      <div className="bg-white border rounded-lg p-4 space-y-5">
        <div>
          <h3 className="font-semibold text-sm mb-2">Category</h3>
          <ul className="space-y-1 text-sm">
            <li>
              <button
                onClick={() => onChange({ category_id: undefined, page: 1 })}
                className={`w-full text-left px-2 py-1 rounded hover:bg-gray-50 ${!filters.category_id ? 'text-indigo-700 font-medium' : ''}`}
              >
                All
              </button>
            </li>
            {categories.map(c => (
              <li key={c.id}>
                <button
                  onClick={() => onChange({ category_id: c.id, page: 1 })}
                  className={`w-full text-left px-2 py-1 rounded hover:bg-gray-50 ${filters.category_id === c.id ? 'text-indigo-700 font-medium' : ''}`}
                >
                  {c.name}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="font-semibold text-sm mb-2">Price</h3>
          <div className="flex gap-2">
            <input
              type="number"
              min="0"
              placeholder="Min"
              value={filters.min_price ?? ''}
              onChange={e => onChange({ min_price: e.target.value ? +e.target.value : undefined, page: 1 })}
              className="w-full border rounded px-2 py-1 text-xs"
            />
            <input
              type="number"
              min="0"
              placeholder="Max"
              value={filters.max_price ?? ''}
              onChange={e => onChange({ max_price: e.target.value ? +e.target.value : undefined, page: 1 })}
              className="w-full border rounded px-2 py-1 text-xs"
            />
          </div>
        </div>

        <div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={!!filters.in_stock}
              onChange={e => onChange({ in_stock: e.target.checked || undefined, page: 1 })}
            />
            In Stock only
          </label>
        </div>

        <div className="text-xs text-gray-500">{total} result{total !== 1 ? 's' : ''}</div>

        <button
          onClick={() => onChange({ category_id: undefined, min_price: undefined, max_price: undefined, in_stock: undefined, page: 1 })}
          className="text-xs text-indigo-600 hover:underline"
        >
          Clear all filters
        </button>
      </div>
    </aside>
  )
}
