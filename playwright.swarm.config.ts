/**
 * Playwright Config für Swarm-Tests
 * Nutzt waitForApp für Health-Checks
 */

import { defineConfig } from "@playwright/test";
import { waitForApp } from "./tests/seed/waitForApp";

const baseURL = process.env.NEUROERP_URL || "http://localhost:3000";

export default defineConfig({
  testDir: "./tests/e2e",
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : 1,
  
  // Global Setup: Warte auf App-Ready
  globalSetup: "./tests/seed/waitForApp.ts",
  
  reporter: [
    ['html', { outputFolder: 'evidence/traces/html-report' }],
    ['json', { outputFile: 'evidence/traces/results.json' }],
    ['list'],
  ],

  use: {
    baseURL,
    trace: "on-first-retry",
    video: "retain-on-failure",
    screenshot: "only-on-failure",
  },

  // Projekte für verschiedene Test-Typen
  projects: [
    {
      name: "seed",
      testMatch: /seed\.spec\.ts/,
    },
    {
      name: "e2e",
      testMatch: /.*\.spec\.ts/,
      dependencies: ["seed"],
    },
  ],
});

