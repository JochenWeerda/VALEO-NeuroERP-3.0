import { test, expect } from "@playwright/test";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://localhost:3000";

test.describe("Smoke tests for Docker workflow", () => {
  test.skip("frontend loads successfully", async ({ page }) => {
    await page.goto(FRONTEND_URL, { waitUntil: "domcontentloaded" });

    // Check that the page loads without errors
    await expect(page).toHaveTitle(/VALEO NeuroERP/);

    // Check for main content
    await expect(page.locator("body")).toBeVisible();
  });

  test("BFF health endpoint responds", async ({ page }) => {
    // Test BFF health via frontend proxy
    const response = await page.request.get(`${FRONTEND_URL}/api/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.ok).toBe(true);
    expect(data.data.service).toBe("bff-web");
  });

  test("MCP analytics KPIs endpoint works", async ({ page }) => {
    const response = await page.request.get(`${FRONTEND_URL}/api/mcp/analytics/kpis`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.ok).toBe(true);
    expect(data.data).toHaveProperty("data");
    expect(Array.isArray(data.data.data)).toBe(true);
  });

  test("MCP analytics trends endpoint works", async ({ page }) => {
    const response = await page.request.get(`${FRONTEND_URL}/api/mcp/analytics/trends`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.ok).toBe(true);
    expect(data.data).toHaveProperty("data");
    expect(Array.isArray(data.data.data)).toBe(true);
  });

  test("MCP inventory list endpoint works", async ({ page }) => {
    const response = await page.request.get(`${FRONTEND_URL}/api/mcp/inventory/list`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.ok).toBe(true);
    expect(data.data).toHaveProperty("data");
    expect(Array.isArray(data.data.data)).toBe(true);
  });

  test("SSE events endpoint is accessible", async ({ page }) => {
    // Test SSE endpoint accessibility
    const response = await page.request.get("http://localhost:5174/api/events?stream=mcp");
    expect(response.ok()).toBeTruthy();
  });
});