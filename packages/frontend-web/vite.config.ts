import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'
import path from 'path'
import fs from 'fs'

function getPackageName(id: string): string | null {
  const normalizedId = id.replace(/\\/g, '/')
  const parts = normalizedId.split('node_modules/')
  const dependencyPath = parts.at(-1)
  if (!dependencyPath) return null

  const segments = dependencyPath.split('/')
  if (segments[0]?.startsWith('@') && segments[1]) {
    return `${segments[0]}/${segments[1]}`
  }

  return segments[0] ?? null
}

function getVendorChunk(id: string): string | undefined {
  if (!id.includes('node_modules')) return undefined

  const pkg = getPackageName(id)
  if (!pkg) return 'vendor-misc'

  if (['react', 'react-dom', 'react-router-dom'].includes(pkg)) return 'vendor-react'
  if (pkg.startsWith('@radix-ui/')) return 'vendor-radix'
  if (['lucide-react', '@radix-ui/react-icons'].includes(pkg)) return 'vendor-icons'
  if (['@tanstack/react-query', 'axios'].includes(pkg)) return 'vendor-data'
  if (['react-hook-form', '@hookform/resolvers', 'zod'].includes(pkg)) return 'vendor-forms'
  if (['i18next', 'react-i18next', 'i18next-browser-languagedetector', 'i18next-http-backend'].includes(pkg)) return 'vendor-i18n'
  if (['recharts', 'victory-vendor'].includes(pkg) || pkg.startsWith('d3-')) return 'vendor-charts'
  if (['date-fns', 'react-day-picker'].includes(pkg)) return 'vendor-dates'
  if (['framer-motion'].includes(pkg)) return 'vendor-motion'
  if (['oidc-client-ts', 'jwt-decode'].includes(pkg)) return 'vendor-auth'
  if (['openai'].includes(pkg)) return 'vendor-openai'
  if (['zustand', 'cmdk', 'qrcode.react', 'sonner', 'clsx', 'tailwind-merge', 'class-variance-authority'].includes(pkg)) return 'vendor-utils'

  return `vendor-${pkg.replace('@', '').replace(/[\/.]/g, '-')}`
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Lade Umgebungsvariablen - zuerst aus loadEnv, dann process.env als Fallback
  const env = loadEnv(mode, process.cwd(), '')
  
  // Verwende process.env direkt, da loadEnv im Container möglicherweise nicht funktioniert
  const DEFAULT_BFF_PROXY = process.env.VITE_BFF_PROXY || env.VITE_BFF_PROXY || 'http://localhost:4001'
  const DEFAULT_SSE_PROXY = process.env.VITE_SSE_PROXY || env.VITE_SSE_PROXY || 'http://localhost:5174'
  // Im Container: backend (Docker-Service-Name), lokal: localhost
  const DEFAULT_BACKEND_PROXY = process.env.VITE_BACKEND_PROXY || env.VITE_BACKEND_PROXY || 'http://localhost:8000'
  // Standard: Haupt-Backend (ki-usability integriert); separater Service: VITE_KI_USABILITY_PROXY=http://localhost:5200
  const DEFAULT_KI_USABILITY_PROXY = process.env.VITE_KI_USABILITY_PROXY || env.VITE_KI_USABILITY_PROXY || 'http://localhost:8000'
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
    ...(mode === 'production' ? [
      compression({ algorithm: 'gzip', ext: '.gz' }),
      compression({ algorithm: 'brotliCompress', ext: '.br' }),
    ] : []),
    {
      name: 'sw-version',
      closeBundle() {
        if (mode !== 'production') return
        const swPath = path.resolve(__dirname, 'dist/sw.js')
        if (!fs.existsSync(swPath)) return
        const version = String(Date.now())
        let content = fs.readFileSync(swPath, 'utf-8')
        content = content.replace(/__SW_VERSION__/g, version)
        fs.writeFileSync(swPath, content)
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
    sourcemap: mode === 'production' ? 'hidden' : true,
    chunkSizeWarningLimit: 500,
    modulePreload: { polyfill: false },
    minify: mode === 'production' ? 'terser' : 'esbuild',
    ...(mode === 'production' ? {
      terserOptions: {
        compress: { drop_console: true, drop_debugger: true },
      },
    } : {}),
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
        manualChunks(id) {
          return getVendorChunk(id)
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    exclude: ['tests/e2e/**', '**/node_modules/**', '**/dist/**'],
  },
  }
})
