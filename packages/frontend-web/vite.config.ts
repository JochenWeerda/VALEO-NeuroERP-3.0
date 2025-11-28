import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Lade Umgebungsvariablen - zuerst aus loadEnv, dann process.env als Fallback
  const env = loadEnv(mode, process.cwd(), '')
  
  // Verwende process.env direkt, da loadEnv im Container möglicherweise nicht funktioniert
  const DEFAULT_BFF_PROXY = process.env.VITE_BFF_PROXY || env.VITE_BFF_PROXY || 'http://localhost:4001'
  const DEFAULT_SSE_PROXY = process.env.VITE_SSE_PROXY || env.VITE_SSE_PROXY || 'http://localhost:5174'
  // Im Container: backend (Docker-Service-Name), lokal: localhost
  const DEFAULT_BACKEND_PROXY = process.env.VITE_BACKEND_PROXY || env.VITE_BACKEND_PROXY || 'http://localhost:8000'

  return {
  plugins: [
    react({
      jsxRuntime: 'automatic',
    }),
    // Health endpoint plugin for Docker health checks
    {
      name: 'health-endpoint',
      configureServer(server) {
        server.middlewares.use('/health', (_req, res, _next) => {
          res.statusCode = 200;
          res.end('ok');
        });
      },
    },
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    dedupe: ['react', 'react-dom'],
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react/jsx-runtime'],
    exclude: [],
    esbuildOptions: {
      dedupe: ['react', 'react-dom'],
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0', // Explizit für Docker
    strictPort: true,
    hmr: {
      // HMR im Browser: localhost, im Container: 0.0.0.0
      // clientPort wird automatisch vom Browser verwendet
      port: 3000,
      clientPort: 3000,
      protocol: 'ws',
      host: 'localhost', // Browser verwendet localhost
    },
    watch: {
      usePolling: true, // Für Docker-Kompatibilität
      interval: 1000,
    },
    proxy: {
      '/api/v1': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket-Support
      },
      '/api/mcp': {
        target: DEFAULT_BFF_PROXY,
        changeOrigin: true,
        ws: true,
      },
      '/api/events': {
        target: DEFAULT_SSE_PROXY,
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor-Chunk: React Core
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI-Chunk: Radix UI Komponenten
          ui: [
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-select',
            '@radix-ui/react-tabs',
            '@radix-ui/react-toast',
            '@radix-ui/react-tooltip',
            '@radix-ui/react-popover',
            'lucide-react',
          ],
          // Charts-Chunk: Recharts (schwer)
          charts: ['recharts'],
          // Forms-Chunk: Formular-Bibliotheken
          forms: ['react-hook-form', 'zod', '@hookform/resolvers'],
          // Query-Chunk: Data-Fetching
          query: ['@tanstack/react-query', 'axios'],
          // Utils-Chunk: Hilfsfunktionen
          utils: ['date-fns', 'clsx', 'tailwind-merge', 'class-variance-authority'],
          // i18n-Chunk: Internationalisierung
          i18n: ['i18next', 'react-i18next', 'i18next-browser-languagedetector'],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  },
  }
})
