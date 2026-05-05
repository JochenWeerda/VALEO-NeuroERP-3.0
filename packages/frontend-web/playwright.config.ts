import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig, devices } from '@playwright/test'

/**
 * Umgebungsvariablen (E2E / CI):
 * - FRONTEND_BASE_URL — Basis-URL der App (Default: http://127.0.0.1:<PLAYWRIGHT_FRONTEND_PORT>)
 * - PLAYWRIGHT_FRONTEND_PORT — Port für den automatisch gestarteten Vite (Default: 5177)
 * - PLAYWRIGHT_SKIP_WEBSERVER — auf "1" setzen, wenn der Dev-Server extern läuft (kein webServer-Start)
 * - E2E_BACKEND_URL — FastAPI für Upload/Health (Default: http://127.0.0.1:8000)
 * - E2E_API_DEV_TOKEN — Bearer für geschützte Agrar-Routes (Default: dev-token)
 */
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PLAYWRIGHT_FRONTEND_PORT = Number(process.env.PLAYWRIGHT_FRONTEND_PORT ?? 5177)
const baseURL =
  process.env.FRONTEND_BASE_URL ?? `http://127.0.0.1:${PLAYWRIGHT_FRONTEND_PORT}`

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: ['**/*.spec.ts', '**/*.e2e.ts'],
  /** Vite dev: viele parallele Lazy-Chunks — längere Budgets für stabile Smokes */
  timeout: 90_000,
  expect: {
    timeout: 45_000,
  },
  fullyParallel: !!process.env.CI,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  /** Lokal: ein Worker entlastet den Vite-Dev-Server (weniger flaky dynamic imports) */
  workers: process.env.CI ? 2 : 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  ...(process.env.PLAYWRIGHT_SKIP_WEBSERVER === '1'
    ? {}
    : {
        webServer: {
          command: `pnpm exec vite --host 127.0.0.1 --port ${PLAYWRIGHT_FRONTEND_PORT} --strictPort`,
          url: baseURL,
          cwd: __dirname,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
        },
      }),
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
