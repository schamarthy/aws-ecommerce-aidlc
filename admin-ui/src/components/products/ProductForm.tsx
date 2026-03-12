import { useEffect, useRef, useState } from 'react'
import { productsApi } from '../../api/products'
import type { Category, Product, ProductCreate, ProductStatus } from '../../types'

interface Props {
  initial?: Product
  categories: Category[]
  onSubmit: (data: ProductCreate) => Promise<void>
  onCancel: () => void
}

const STATUSES: ProductStatus[] = ['active', 'inactive', 'archived']

export default function ProductForm({ initial, categories, onSubmit, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? '')
  const [description, setDescription] = useState(initial?.description ?? '')
  const [price, setPrice] = useState(String(initial?.price ?? ''))
  const [sku, setSku] = useState(initial?.sku ?? '')
  const [status, setStatus] = useState<ProductStatus>(initial?.status ?? 'active')
  const [isFeatured, setIsFeatured] = useState(initial?.is_featured ?? false)
  const [categoryId, setCategoryId] = useState<string>(String(initial?.category_id ?? ''))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await onSubmit({
        name,
        description: description || undefined,
        price: parseFloat(price),
        sku,
        status,
        is_featured: isFeatured,
        category_id: categoryId ? parseInt(categoryId) : undefined,
      })

      // Upload pending images if editing (new product handled after creation in page)
      if (initial && fileRef.current?.files?.length) {
        for (const file of Array.from(fileRef.current.files)) {
          await productsApi.uploadImage(initial.id, file)
        }
      }
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      setError(msg ?? 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
      {error && <p className="text-red-600 text-sm">{error}</p>}

      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Name *</label>
          <input
            required
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">SKU *</label>
          <input
            required
            value={sku}
            onChange={e => setSku(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Price *</label>
          <input
            required
            type="number"
            min="0"
            step="0.01"
            value={price}
            onChange={e => setPrice(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Status</label>
          <select
            value={status}
            onChange={e => setStatus(e.target.value as ProductStatus)}
            className="w-full border rounded px-3 py-2 text-sm"
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Category</label>
          <select
            value={categoryId}
            onChange={e => setCategoryId(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm"
          >
            <option value="">— none —</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div className="col-span-2 flex items-center gap-2">
          <input
            id="featured"
            type="checkbox"
            checked={isFeatured}
            onChange={e => setIsFeatured(e.target.checked)}
          />
          <label htmlFor="featured" className="text-sm">Featured product</label>
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Images</label>
          <input ref={fileRef} type="file" accept="image/*" multiple className="text-sm" />
          {initial && initial.images.length > 0 && (
            <div className="flex gap-2 mt-2 flex-wrap">
              {initial.images.map(img => (
                <img
                  key={img.id}
                  src={img.storage_url}
                  alt=""
                  className="w-16 h-16 object-cover rounded border"
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Saving…' : initial ? 'Update' : 'Create'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border rounded text-sm hover:bg-gray-100"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
