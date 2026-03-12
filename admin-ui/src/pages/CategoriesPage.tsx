import { useEffect, useState } from 'react'
import { categoriesApi } from '../api/categories'
import CategoryForm from '../components/categories/CategoryForm'
import CategoryList from '../components/categories/CategoryList'
import type { Category, CategoryCreate } from '../types'

type View = 'list' | 'create' | 'edit'

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [view, setView] = useState<View>('list')
  const [editing, setEditing] = useState<Category | undefined>()

  async function load() {
    setCategories(await categoriesApi.list())
  }

  useEffect(() => { load() }, [])

  async function handleCreate(data: CategoryCreate) {
    await categoriesApi.create(data)
    await load()
    setView('list')
  }

  async function handleUpdate(data: CategoryCreate) {
    if (!editing) return
    await categoriesApi.update(editing.id, data)
    await load()
    setView('list')
    setEditing(undefined)
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this category?')) return
    await categoriesApi.delete(id)
    await load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold">Categories</h1>
        {view === 'list' && (
          <button
            onClick={() => setView('create')}
            className="px-3 py-1.5 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
          >
            + New Category
          </button>
        )}
      </div>

      {view === 'list' && (
        <CategoryList
          categories={categories}
          onEdit={cat => { setEditing(cat); setView('edit') }}
          onDelete={handleDelete}
        />
      )}

      {view === 'create' && (
        <div>
          <h2 className="font-semibold mb-3">Create Category</h2>
          <CategoryForm onSubmit={handleCreate} onCancel={() => setView('list')} />
        </div>
      )}

      {view === 'edit' && editing && (
        <div>
          <h2 className="font-semibold mb-3">Edit Category</h2>
          <CategoryForm
            initial={editing}
            onSubmit={handleUpdate}
            onCancel={() => { setView('list'); setEditing(undefined) }}
          />
        </div>
      )}
    </div>
  )
}
