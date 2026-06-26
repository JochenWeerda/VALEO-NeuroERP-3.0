import { defineConfig } from '@playwright/test'

/**
 * SEMANTIC-E2E-STRICT-001 — schlanke Playwright-Config fuer @critical API-Health-Tests.
 * Kein globalSetup (kein Frontend-Build/Preview), nur Backend-API via request-Context.
 */
export default defineConfig({
  testDir: './playwright-tests/specs/e2e-matrix',
  grep: /@critical/,
  timeout: 60_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : 1,
  reporter: [['list']],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000',
  },
  projects: [
    {
      name: 'api-critical',
      use: {},
    },
  ],
})
