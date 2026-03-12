import type { Product, ProductStatus } from '../../types'

const statusColor: Record<ProductStatus, string> = {
  active: 'bg-green-100 text-green-700',
  inactive: 'bg-yellow-100 text-yellow-700',
  archived: 'bg-gray-100 text-gray-600',
}

interface Props {
  products: Product[]
  onEdit: (p: Product) => void
  onDelete: (id: number) => void
  onStatusChange: (id: number, status: ProductStatus) => void
  onToggleFeatured: (id: number, featured: boolean) => void
}

export default function ProductList({
  products,
  onEdit,
  onDelete,
  onStatusChange,
  onToggleFeatured,
}: Props) {
  if (products.length === 0) {
    return <p className="text-gray-500 text-sm">No products yet.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100 text-left">
            <th className="px-3 py-2 border">ID</th>
            <th className="px-3 py-2 border">Name</th>
            <th className="px-3 py-2 border">SKU</th>
            <th className="px-3 py-2 border">Price</th>
            <th className="px-3 py-2 border">Status</th>
            <th className="px-3 py-2 border">Featured</th>
            <th className="px-3 py-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 border">{p.id}</td>
              <td className="px-3 py-2 border font-medium">{p.name}</td>
              <td className="px-3 py-2 border font-mono text-xs">{p.sku}</td>
              <td className="px-3 py-2 border">${Number(p.price).toFixed(2)}</td>
              <td className="px-3 py-2 border">
                <select
                  value={p.status}
                  onChange={e => onStatusChange(p.id, e.target.value as ProductStatus)}
                  className={`rounded px-2 py-0.5 text-xs border-0 font-medium ${statusColor[p.status]}`}
                >
                  <option value="active">active</option>
                  <option value="inactive">inactive</option>
                  <option value="archived">archived</option>
                </select>
              </td>
              <td className="px-3 py-2 border text-center">
                <input
                  type="checkbox"
                  checked={p.is_featured}
                  onChange={e => onToggleFeatured(p.id, e.target.checked)}
                />
              </td>
              <td className="px-3 py-2 border whitespace-nowrap">
                <button
                  onClick={() => onEdit(p)}
                  className="text-indigo-600 hover:underline mr-3"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(p.id)}
                  className="text-red-600 hover:underline"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
