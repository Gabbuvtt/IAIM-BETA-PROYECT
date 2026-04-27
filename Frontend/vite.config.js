import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    allowedHosts: true,
    proxy: {
      '/auth': { target: BACKEND_URL, changeOrigin: true },
      '/users': { target: BACKEND_URL, changeOrigin: true },
      '/tickets': { target: BACKEND_URL, changeOrigin: true },
      '/docs': { target: BACKEND_URL, changeOrigin: true },
      '/openapi.json': { target: BACKEND_URL, changeOrigin: true },
    },
  },
})
