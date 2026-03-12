import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import SearchBar from './SearchBar'

interface Props {
  cartCount?: number
  onCartClick?: () => void
}

export default function Header({ cartCount = 0, onCartClick }: Props) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-4">
        <Link to="/" className="text-xl font-bold text-indigo-700 shrink-0">
          Shop
        </Link>
        <nav className="hidden sm:flex gap-4 text-sm text-gray-600">
          <Link to="/products" className="hover:text-indigo-700">Products</Link>
          <Link to="/orders" className="hover:text-indigo-700">Orders</Link>
        </nav>
        <div className="flex-1" />
        <SearchBar />

        {/* Auth area */}
        {user ? (
          <div className="flex items-center gap-2 text-sm">
            <Link
              to="/profile"
              className="text-gray-700 hover:text-indigo-700 font-medium hidden sm:block"
            >
              {user.name}
            </Link>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-red-600 text-xs border rounded px-2 py-1"
            >
              Sign out
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm">
            <Link to="/login" className="text-gray-600 hover:text-indigo-700">Sign in</Link>
            <Link
              to="/register"
              className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-700 text-xs font-medium"
            >
              Register
            </Link>
          </div>
        )}

        {onCartClick && (
          <button
            onClick={onCartClick}
            className="relative p-2 text-gray-700 hover:text-indigo-700"
            aria-label="Cart"
          >
            🛒
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-indigo-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </button>
        )}
      </div>
    </header>
  )
}
