import { useEffect, useState } from 'react'
import { categoriesApi } from '../api/categories'
import { productsApi } from '../api/products'
import ProductForm from '../components/products/ProductForm'
import ProductList from '../components/products/ProductList'
import type { Category, Product, ProductCreate, ProductStatus } from '../types'

type View = 'list' | 'create' | 'edit'

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [view, setView] = useState<View>('list')
  const [editing, setEditing] = useState<Product | undefined>()

  async function load() {
    const [prods, cats] = await Promise.all([productsApi.list(), categoriesApi.list()])
    setProducts(prods)
    setCategories(cats)
  }

  useEffect(() => { load() }, [])

  async function handleCreate(data: ProductCreate) {
    await productsApi.create(data)
    await load()
    setView('list')
  }

  async function handleUpdate(data: ProductCreate) {
    if (!editing) return
    await productsApi.update(editing.id, { ...data, updated_by: 'admin' })
    await load()
    setView('list')
    setEditing(undefined)
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this product?')) return
    await productsApi.delete(id)
    await load()
  }

  async function handleStatusChange(id: number, status: ProductStatus) {
    await productsApi.updateStatus(id, status)
    await load()
  }

  async function handleToggleFeatured(id: number, featured: boolean) {
    await productsApi.updateFeatured(id, featured)
    await load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Products</h1>
        {view === 'list' && (
          <button
            onClick={() => setView('create')}
            className="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
          >
            + New Product
          </button>
        )}
      </div>

      {view === 'list' && (
        <ProductList
          products={products}
          onEdit={p => { setEditing(p); setView('edit') }}
          onDelete={handleDelete}
          onStatusChange={handleStatusChange}
          onToggleFeatured={handleToggleFeatured}
        />
      )}

      {view === 'create' && (
        <div>
          <h2 className="font-semibold mb-3">Create Product</h2>
          <ProductForm
            categories={categories}
            onSubmit={handleCreate}
            onCancel={() => setView('list')}
          />
        </div>
      )}

      {view === 'edit' && editing && (
        <div>
          <h2 className="font-semibold mb-3">Edit Product</h2>
          <ProductForm
            initial={editing}
            categories={categories}
            onSubmit={handleUpdate}
            onCancel={() => { setView('list'); setEditing(undefined) }}
          />
        </div>
      )}
    </div>
  )
}
