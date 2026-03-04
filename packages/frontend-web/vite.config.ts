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
  const DEFAULT_KI_USABILITY_PROXY = process.env.VITE_KI_USABILITY_PROXY || env.VITE_KI_USABILITY_PROXY || 'http://localhost:5200'
  const DEV_PORT = Number(process.env.VITE_PORT || env.VITE_PORT || 3000)

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
    entries: ['index.html'],
    include: [
      'react', 'react-dom', 'react/jsx-runtime',
      'react-router-dom',
      '@tanstack/react-query',
      'axios',
      'i18next', 'react-i18next',
      'zustand',
      'react-hook-form', '@hookform/resolvers',
      'zod',
      'recharts',
      'lucide-react',
      'date-fns',
      'clsx', 'tailwind-merge', 'class-variance-authority',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-tabs',
      '@radix-ui/react-toast',
      '@radix-ui/react-tooltip',
      '@radix-ui/react-popover',
    ],
  },
  server: {
    port: DEV_PORT,
    host: '0.0.0.0',
    strictPort: true,
    allowedHosts: 'all',
    warmup: {
      clientFiles: [
        'index.html',
        './src/main.tsx',
        './src/app/routes.tsx',
        './src/layouts/DashboardLayout.tsx',
      ],
    },
    hmr: {
      protocol: env.VITE_HMR_HOST ? 'wss' : 'ws',
      ...(env.VITE_HMR_HOST ? { host: env.VITE_HMR_HOST, port: 443 } : {}),
    },
    watch: {
      usePolling: true,
      interval: 500,
    },
    proxy: {
      '/api/v1': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket-Support
      },
      // MCP Documents laufen im Backend (FastAPI), nicht im BFF
      '/api/mcp/documents': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
        ws: true,
      },
      // MCP Analytics/Inventory/etc. laufen im BFF
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
      '/api/admin': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/contracts': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/agribusiness': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/audit': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/crm-sales': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/crm': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      '/api/finance': {
        target: DEFAULT_BACKEND_PROXY,
        changeOrigin: true,
        secure: false,
      },
      // KI Usability API (Sprachsteuerung, Action Registry)
      '/api/ki-usability': {
        target: DEFAULT_KI_USABILITY_PROXY,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/ki-usability/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    chunkSizeWarningLimit: 500,
    // Performance: Module-Preload nur für kritische Chunks
    modulePreload: { polyfill: false },
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
