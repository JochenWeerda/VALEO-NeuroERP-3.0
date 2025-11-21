import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./playwright-tests",
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : 1,
  globalSetup: "./playwright.global-setup.mjs",
  globalTeardown: "./playwright.global-teardown.mjs",
  
  // Reporter-Konfiguration für UAT
  reporter: [
    ['html', { outputFolder: 'playwright-tests/artifacts/html-report' }],
    ['json', { outputFile: 'playwright-tests/artifacts/results.json' }],
    ['list'],
  ],

  // Artefakt-Sammlung
  use: {
    baseURL: process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? "http://localhost:3000",
    actionTimeout: 10000,
    navigationTimeout: 15000,
    
    // Screenshots & Videos
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    
    // HAR-Recording
    recordHar: {
      mode: 'minimal',
      path: 'playwright-tests/artifacts/hars/',
    },
  },

  // Multi-Project-Setup
  projects: [
    // Legacy Auth-API Test
    {
      name: "auth-api",
      testMatch: /auth-api\.spec\.ts/,
    },
    
    // Smoke Tests (schnell, CI-fähig)
    {
      name: "smoke",
      testMatch: /.*smoke\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
      grep: /@smoke/,
    },
    
    // Full UAT Tests
    {
      name: "full",
      testMatch: /.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
      grep: /@full/,
    },
    
    // Fallback-Verifikation
    {
      name: "fallback-verification",
      testMatch: /fallback-verification\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
      grep: /@fallback/,
    },
  ],
});
