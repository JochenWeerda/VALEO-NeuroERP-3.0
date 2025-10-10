import { test, expect } from "@playwright/test";

const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://localhost:3000";
const SSE_BASE = process.env.SSE_BASE ?? "http://localhost:5174";

async function triggerSequence(page) {
  await page.evaluate(async (endpoint) => {
    await fetch(`${endpoint}/trigger-sequence`);
  }, SSE_BASE);
}

test.describe.serial("MCP realtime integration", () => {
  test("dashboard shows connection and events", async ({ page }) => {
    await page.goto(FRONTEND_URL, { waitUntil: "domcontentloaded" });

    // Wait until connection indicator switches to Connected
    await expect(page.locator("text=Realtime: Connected")).toBeVisible({ timeout: 10000 });

    // initial event emitted by SSE server on startup
    await expect(page.locator("text=Last event: inventory:inventory.created")).toBeVisible({ timeout: 10000 });

    // Trigger additional events
    await triggerSequence(page);

    await expect(page.locator("text=Last event: inventory:inventory.adjusted")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("text=Last event: weighing:weighing.updated")).toBeVisible({ timeout: 10000 });
  });

  test("inventory toast appears on event", async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/inventory`, { waitUntil: "domcontentloaded" });

    // Trigger a specific inventory event
    await page.evaluate(async (endpoint) => {
      await fetch(`${endpoint}/emit?type=inventory.created&service=inventory`);
    }, SSE_BASE);

    await expect(page.locator("text=Notification")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("text=Inventory created")).toBeVisible({ timeout: 10000 });
  });

  test("weighing toast appears on event", async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/weighing`, { waitUntil: "domcontentloaded" });

    await page.evaluate(async (endpoint) => {
      await fetch(`${endpoint}/emit?type=weighing.updated&service=weighing`);
    }, SSE_BASE);

    await expect(page.locator("text=Notification")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("text=Weighing updated")).toBeVisible({ timeout: 10000 });
  });
});

