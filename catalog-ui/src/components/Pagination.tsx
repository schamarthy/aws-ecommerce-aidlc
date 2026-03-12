interface Props {
  page: number
  pages: number
  onPage: (p: number) => void
}

export default function Pagination({ page, pages, onPage }: Props) {
  if (pages <= 1) return null

  return (
    <div className="flex items-center gap-1 justify-center mt-6">
      <button
        disabled={page === 1}
        onClick={() => onPage(page - 1)}
        className="px-3 py-1.5 text-sm border rounded disabled:opacity-40 hover:bg-gray-50"
      >
        ‹ Prev
      </button>
      {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
        <button
          key={p}
          onClick={() => onPage(p)}
          className={`px-3 py-1.5 text-sm border rounded ${p === page ? 'bg-indigo-600 text-white border-indigo-600' : 'hover:bg-gray-50'}`}
        >
          {p}
        </button>
      ))}
      <button
        disabled={page === pages}
        onClick={() => onPage(page + 1)}
        className="px-3 py-1.5 text-sm border rounded disabled:opacity-40 hover:bg-gray-50"
      >
        Next ›
      </button>
    </div>
  )
}
