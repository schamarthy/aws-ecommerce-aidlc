import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { cartApi } from '../api/cart'
import type { Cart } from '../types/cart'
import type { ProductSummary } from '../types'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error'
}

interface CartContextValue {
  cart: Cart | null
  loading: boolean
  addToCart: (product: ProductSummary) => Promise<void>
  updateItem: (itemId: number, qty: number) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
  clearCart: () => Promise<void>
  toasts: Toast[]
}

const CartContext = createContext<CartContextValue | null>(null)

let toastId = 0

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null)
  const [loading, setLoading] = useState(false)
  const [toasts, setToasts] = useState<Toast[]>([])

  function showToast(message: string, type: Toast['type'] = 'success') {
    const id = ++toastId
    setToasts(t => [...t, { id, message, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3000)
  }

  useEffect(() => {
    cartApi.getCart().then(setCart).catch(() => {})
  }, [])

  const addToCart = useCallback(async (product: ProductSummary) => {
    if (product.stock_status === 'out_of_stock') {
      showToast('This product is out of stock', 'error')
      return
    }
    try {
      setLoading(true)
      const updated = await cartApi.addItem(product.id)
      setCart(updated)
      showToast(`${product.name} added to cart`)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        'Could not add to cart'
      showToast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }, [])

  const updateItem = useCallback(async (itemId: number, qty: number) => {
    try {
      const updated = await cartApi.updateItem(itemId, qty)
      setCart(updated)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ??
        'Could not update item'
      showToast(msg, 'error')
    }
  }, [])

  const removeItem = useCallback(async (itemId: number) => {
    const updated = await cartApi.removeItem(itemId)
    setCart(updated)
  }, [])

  const clearCart = useCallback(async () => {
    const updated = await cartApi.clearCart()
    setCart(updated)
  }, [])

  return (
    <CartContext.Provider value={{ cart, loading, addToCart, updateItem, removeItem, clearCart, toasts }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
