import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom'
import CategoriesPage from './pages/CategoriesPage'
import InventoryPage from './pages/InventoryPage'
import ProductsPage from './pages/ProductsPage'

const navClass = ({ isActive }: { isActive: boolean }) =>
  `block px-4 py-2 rounded hover:bg-indigo-700 transition-colors ${isActive ? 'bg-indigo-700 font-semibold' : ''}`

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="w-56 bg-indigo-800 text-white flex flex-col">
          <div className="px-4 py-5 text-xl font-bold border-b border-indigo-700">
            <Link to="/">Admin</Link>
          </div>
          <nav className="flex-1 px-2 py-4 space-y-1 text-sm">
            <NavLink to="/products" className={navClass}>Products</NavLink>
            <NavLink to="/categories" className={navClass}>Categories</NavLink>
            <NavLink to="/inventory" className={navClass}>Inventory</NavLink>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6 overflow-auto">
          <Routes>
            <Route path="/" element={<div className="text-gray-500">Select a section from the sidebar.</div>} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/inventory" element={<InventoryPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
