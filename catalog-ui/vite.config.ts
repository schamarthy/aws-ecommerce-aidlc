import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/api/catalog': { target: 'http://localhost:8001', rewrite: (p) => p.replace('/api/catalog', '/catalog') },
      '/api/cart': { target: 'http://localhost:8002', rewrite: (p) => p.replace('/api/cart', '/cart') },
      '/api/orders': { target: 'http://localhost:8003', rewrite: (p) => p.replace('/api/orders', '/orders') },
      '/api/auth': { target: 'http://localhost:8004', rewrite: (p) => p.replace('/api/auth', '/auth') },
    },
  },
})
