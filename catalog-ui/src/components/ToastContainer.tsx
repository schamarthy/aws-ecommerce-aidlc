import { useCart } from '../context/CartContext'

export default function ToastContainer() {
  const { toasts } = useCart()
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`px-4 py-3 rounded-lg shadow-lg text-sm text-white transition-all ${
            t.type === 'error' ? 'bg-red-600' : 'bg-green-600'
          }`}
        >
          {t.message}
        </div>
      ))}
    </div>
  )
}
