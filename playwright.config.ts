import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./playwright-tests",
  retries: 0,
  workers: 1,
  globalSetup: "./playwright.global-setup.mjs",
  globalTeardown: "./playwright.global-teardown.mjs",
  use: {
    baseURL: process.env.FRONTEND_URL ?? "http://localhost:3000",
    actionTimeout: 10000,
    navigationTimeout: 15000,
    trace: "on-first-retry",
  },
});
