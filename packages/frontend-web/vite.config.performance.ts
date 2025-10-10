import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'

/**
 * Performance-optimierte Vite-Konfiguration
 * 
 * Features:
 * - Code-Splitting
 * - Bundle-Analyze
 * - Compression (gzip + brotli)
 * - Asset-Optimization
 */
export default defineConfig({
  plugins: [
    react(),
    
    // Bundle-Analyzer (nur im Build)
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
    
    // Gzip-Compression
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    
    // Brotli-Compression (bessere Kompression als gzip)
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],
  
  build: {
    // Code-Splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor-Chunks
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select'],
          'vendor-state': ['zustand'],
          'vendor-forms': ['react-hook-form', 'zod'],
          
          // Feature-Chunks
          'feature-workflow': ['./src/hooks/useWorkflow.ts', './src/hooks/useWorkflowEvents.ts'],
          'feature-documents': ['./src/pages/sales.tsx', './src/pages/contracts.tsx'],
        },
        
        // Asset-Namen mit Hash für Caching
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    
    // Bundle-Size-Limits
    chunkSizeWarningLimit: 500,  // 500 KB
    
    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.log in production
        drop_debugger: true,
      },
    },
    
    // Source Maps (nur für Errors)
    sourcemap: 'hidden',
  },
  
  // Performance-Hints
  server: {
    headers: {
      'Cache-Control': 'public, max-age=31536000',
    },
  },
})

