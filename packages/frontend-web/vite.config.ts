import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

const DEFAULT_BFF_PROXY = process.env.VITE_BFF_PROXY ?? 'http://localhost:4001'
const DEFAULT_SSE_PROXY = process.env.VITE_SSE_PROXY ?? 'http://localhost:5174'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api/mcp': {
        target: DEFAULT_BFF_PROXY,
        changeOrigin: true,
      },
      '/api/events': {
        target: DEFAULT_SSE_PROXY,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  },
})
