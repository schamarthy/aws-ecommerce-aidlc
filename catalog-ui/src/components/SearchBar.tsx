import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { catalogApi } from '../api/catalog'
import type { AutocompleteResult } from '../types'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([])
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([])
      return
    }
    clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(async () => {
      const results = await catalogApi.autocomplete(query)
      setSuggestions(results)
      setOpen(results.length > 0)
    }, 250)
    return () => clearTimeout(timeoutRef.current)
  }, [query])

  function submit(e: React.FormEvent) {
    e.preventDefault()
    setOpen(false)
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`)
  }

  function selectSuggestion(id: number) {
    setOpen(false)
    setQuery('')
    navigate(`/products/${id}`)
  }

  return (
    <div className="relative">
      <form onSubmit={submit} className="flex">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search products…"
          className="w-64 px-3 py-1.5 text-sm rounded-l border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white text-gray-900"
        />
        <button
          type="submit"
          className="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-r hover:bg-indigo-700"
        >
          Search
        </button>
      </form>

      {open && (
        <ul className="absolute z-50 w-full bg-white border border-gray-200 rounded shadow-lg mt-1 text-sm">
          {suggestions.map(s => (
            <li
              key={s.id}
              onMouseDown={() => selectSuggestion(s.id)}
              className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer"
            >
              {s.primary_image_url && (
                <img src={s.primary_image_url} alt="" className="w-8 h-8 object-cover rounded" />
              )}
              <span>{s.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
