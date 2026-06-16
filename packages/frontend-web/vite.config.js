import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    optimizeDeps: {
        entries: ['index.html'],
        esbuildOptions: {
            target: 'es2022',
        },
    },
    server: {
        port: 3000,
        host: true,
        allowedHosts: ['localhost', 'host.docker.internal', '.local', 'all'],
        proxy: {
            '/api/v1': {
                target: process.env.VITE_BACKEND_PROXY || 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
            '/api/mcp/documents': {
                target: process.env.VITE_BACKEND_PROXY || 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
            '/api/mcp': {
                target: process.env.VITE_BFF_PROXY || 'http://127.0.0.1:4001',
                changeOrigin: true,
                ws: true,
            },
            '/api/events': {
                target:
                    process.env.VITE_SSE_PROXY ||
                    process.env.VITE_BACKEND_PROXY ||
                    'http://127.0.0.1:8000',
                changeOrigin: true,
                ws: true,
            },
        },
    },
    preview: {
        port: 4173,
        host: '0.0.0.0',
        strictPort: false,
        allowedHosts: 'all',
    },
    build: {
        outDir: 'dist',
        target: 'es2022',
        sourcemap: true,
    },
    test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./src/test/setup.ts'],
    },
});
