import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/catalog': 'http://localhost:8001',
      '/cart': 'http://localhost:8002',
      '/orders': 'http://localhost:8003',
      '/auth': 'http://localhost:8004',
    },
  },
})
