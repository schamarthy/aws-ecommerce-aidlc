import type { Category } from '../../types'

interface Props {
  categories: Category[]
  onEdit: (cat: Category) => void
  onDelete: (id: number) => void
}

export default function CategoryList({ categories, onEdit, onDelete }: Props) {
  if (categories.length === 0) {
    return <p className="text-gray-500 text-sm">No categories yet.</p>
  }

  return (
    <table className="w-full text-sm border-collapse">
      <thead>
        <tr className="bg-gray-100 text-left">
          <th className="px-4 py-2 border">ID</th>
          <th className="px-4 py-2 border">Name</th>
          <th className="px-4 py-2 border">Description</th>
          <th className="px-4 py-2 border">Actions</th>
        </tr>
      </thead>
      <tbody>
        {categories.map(cat => (
          <tr key={cat.id} className="hover:bg-gray-50">
            <td className="px-4 py-2 border">{cat.id}</td>
            <td className="px-4 py-2 border font-medium">{cat.name}</td>
            <td className="px-4 py-2 border text-gray-600">{cat.description ?? '—'}</td>
            <td className="px-4 py-2 border">
              <button
                onClick={() => onEdit(cat)}
                className="text-indigo-600 hover:underline mr-3"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(cat.id)}
                className="text-red-600 hover:underline"
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
