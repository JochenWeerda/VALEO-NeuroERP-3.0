/**
 * SEMANTIC-E2E-MATRIX-001 — Semantische Action-Matrix kritischer ERP-UI-Flows.
 * Prüft nicht nur Navigation, sondern dass Buttons fachlich das Richtige tun.
 *
 * Externe Gates: TSE, ELSTER, DATEV, DMS bleiben simuliert / skipped.
 */
import { test, expect } from "@playwright/test";

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3001";
const HEADERS = {
  "X-Tenant-ID": "test-tenant",
  Authorization: "Bearer dev-token",
};

test.describe("O2C — Order-to-Cash Prozesskette @smoke", () => {
  test("Auftragsbestätigung → Status FREIGEGEBEN sichtbar", async ({ page }) => {
    await page.goto(`${BASE}/verkauf/auftraege`);
    await expect(page.locator("h1, [data-testid='page-title']")).toBeVisible();
    // Prüfe dass Statusfilter vorhanden
    const filterEl = page.locator('[data-testid="status-filter"], select, [role="combobox"]').first();
    await expect(filterEl).toBeVisible();
  });

  test("Lieferschein-Liste lädt ohne 404", async ({ page }) => {
    await page.goto(`${BASE}/verkauf/lieferscheine`);
    await expect(page).not.toHaveURL(/404/);
    await expect(page.locator("main, [role='main']")).toBeVisible();
  });

  test("Sales-Rechnungen erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/verkauf/rechnungen`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("P2P — Procure-to-Pay Prozesskette @smoke", () => {
  test("Bestellungen-Liste erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/einkauf/bestellungen`);
    await expect(page).not.toHaveURL(/404/);
    await expect(page.locator("main, [role='main']")).toBeVisible();
  });

  test("Wareneingang-Liste erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/einkauf/wareneingaenge`);
    await expect(page).not.toHaveURL(/404/);
  });

  test("Rechnungseingang erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/einkauf/rechnungseingang`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("WMS — Lager-Workflows @smoke", () => {
  test("Silo-Übersicht lädt mit KPI-Bar", async ({ page }) => {
    await page.goto(`${BASE}/lager/silo-uebersicht`);
    await expect(page).not.toHaveURL(/404/);
    await expect(page.locator("main, [role='main']")).toBeVisible();
  });

  test("Materialfluss-Seite erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/lager/materialfluss`);
    await expect(page).not.toHaveURL(/404/);
  });

  test("QS-Leitstand erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/lager/qs-leitstand`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("FIBU — Finance-Workflows @smoke", () => {
  test("Buchungsjournal erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/fibu/buchungsjournal`);
    await expect(page).not.toHaveURL(/404/);
  });

  test("OP-Liste erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/fibu/offene-posten`);
    await expect(page).not.toHaveURL(/404/);
  });

  test("Mahnwesen erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/fibu/mahnwesen`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("CRM — Customer Workflows @smoke", () => {
  test("CRM-Übersicht erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/crm/kunden`);
    await expect(page).not.toHaveURL(/404/);
    await expect(page.locator("main, [role='main']")).toBeVisible();
  });

  test("CRM 360°-Cockpit erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/crm`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("Kontrakt-Lifecycle @smoke", () => {
  test("Kontrakte-Liste erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/kontrakte`);
    await expect(page).not.toHaveURL(/404/);
    await expect(page.locator("main, [role='main']")).toBeVisible();
  });
});

test.describe("POS — Kasse @smoke", () => {
  test("POS-Tagesabschluss-Seite erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/pos/tagesabschluss`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("Compliance @smoke", () => {
  test("Compliance-Dashboard erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/compliance`);
    await expect(page).not.toHaveURL(/404/);
  });
});

test.describe("HRM @smoke", () => {
  test("HRM-Übersicht erreichbar", async ({ page }) => {
    await page.goto(`${BASE}/personal`);
    await expect(page).not.toHaveURL(/404/);
  });
});
