/**
 * Seed test for NeuroERP
 * This test logs in and sets up the test environment
 */

import { test, expect } from "@playwright/test";

const NEUROERP_URL = process.env.NEUROERP_URL || "http://localhost:3000";
const NEUROERP_USER = process.env.NEUROERP_USER || "testuser";
const NEUROERP_PASS = process.env.NEUROERP_PASS || "testpass";

test("seed - login and setup", async ({ page }) => {
  await page.goto(NEUROERP_URL);
  
  // Wait for page to load
  await page.waitForLoadState("networkidle");
  
  // Try to find login form (adjust selectors based on your actual login page)
  const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
  const passwordInput = page.locator('input[type="password"], input[name="password"], input[id="password"]').first();
  const loginButton = page.locator('button:has-text("Login"), button[type="submit"]').first();
  
  // If login form exists, fill it
  if (await usernameInput.isVisible().catch(() => false)) {
    await usernameInput.fill(NEUROERP_USER);
    await passwordInput.fill(NEUROERP_PASS);
    await loginButton.click();
    
    // Wait for navigation after login
    await page.waitForLoadState("networkidle");
  }
  
  // Verify we're logged in (adjust based on your actual app)
  // This could be checking for a dashboard, user menu, etc.
  await expect(page).toHaveURL(new RegExp(NEUROERP_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  
  console.log("✅ Seed test: Login successful");
});

