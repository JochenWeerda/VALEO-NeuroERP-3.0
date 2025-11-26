import { test, expect } from '@playwright/test';

/**
 * E2E Tests für SALES-CRM-02: Kundenstamm Sales-Felder
 *
 * Testet die neuen Sales-spezifischen Felder:
 * - preisgruppe (price_group) im "konditionen" Tab
 * - steuerkategorie (tax_category) im "steuern" Tab
 *
 * Hinweis: Die UI verwendet Radix Select. Die Felder sind daher als Buttons
 * mit role="combobox" und Options mit role="option" gerendert.
 */

const openOrCreateCustomer = async (page) => {
  const createButton = page.getByRole('button', { name: /neu|erstellen|create/i });
  if (await createButton.isVisible()) {
    await createButton.click();
  }
};

test.describe('SALES-CRM-02: Customer Master Sales Fields', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/crm/kunden-stamm');
    await page.waitForLoadState('networkidle');
    await openOrCreateCustomer(page);
  });

  test('sollte Preisgruppe im Konditionen-Tab anzeigen', async ({ page }) => {
    await page.getByRole('tab', { name: /konditionen|terms/i }).click();

    const priceGroupField = page.getByRole('combobox', { name: /preisgruppe|price.*group/i });
    await expect(priceGroupField).toBeVisible();

    await priceGroupField.click();
    await expect(page.getByRole('option', { name: /standard/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /premium/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /(großhandel|grosshandel|wholesale)/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /einzelhandel|retail/i })).toBeVisible();
  });

  test('sollte Preisgruppe speichern können', async ({ page }) => {
    await page.getByRole('tab', { name: /konditionen|terms/i }).click();

    const priceGroupField = page.getByRole('combobox', { name: /preisgruppe|price.*group/i });
    await priceGroupField.click();
    await page.getByRole('option', { name: /premium/i }).click();

    await page.getByRole('button', { name: /speichern|save/i }).first().click();
    await expect(priceGroupField).toContainText(/premium/i);
  });

  test('sollte Steuerkategorie im Steuern-Tab anzeigen', async ({ page }) => {
    await page.getByRole('tab', { name: /steuern|tax/i }).click();

    const taxCategoryField = page.getByRole('combobox', { name: /steuerkategorie|tax.*category/i });
    await expect(taxCategoryField).toBeVisible();

    await taxCategoryField.click();
    await expect(page.getByRole('option', { name: /standard.*19/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /(erm|reduced).*7/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /(nullsatz|zero).*0/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /reverse.*charge/i })).toBeVisible();
    await expect(page.getByRole('option', { name: /befreit|exempt/i })).toBeVisible();
  });

  test('sollte Steuerkategorie speichern können', async ({ page }) => {
    await page.getByRole('tab', { name: /steuern|tax/i }).click();

    const taxCategoryField = page.getByRole('combobox', { name: /steuerkategorie|tax.*category/i });
    await taxCategoryField.click();
    await page.getByRole('option', { name: /(erm|reduced)/i }).click();

    await page.getByRole('button', { name: /speichern|save/i }).first().click();
    await expect(taxCategoryField).toContainText(/erm/i);
  });

  test('sollte beide Felder zusammen speichern können', async ({ page }) => {
    await page.getByRole('tab', { name: /konditionen|terms/i }).click();
    const priceGroupField = page.getByRole('combobox', { name: /preisgruppe|price.*group/i });
    await priceGroupField.click();
    await page.getByRole('option', { name: /(wholesale|großhandel|grosshandel)/i }).click();

    await page.getByRole('tab', { name: /steuern|tax/i }).click();
    const taxCategoryField = page.getByRole('combobox', { name: /steuerkategorie|tax.*category/i });
    await taxCategoryField.click();
    await page.getByRole('option', { name: /zero|nullsatz/i }).click();

    await page.getByRole('button', { name: /speichern|save/i }).first().click();
    await page.getByRole('button', { name: /speichern|save/i }).first().click();

    await page.getByRole('tab', { name: /konditionen|terms/i }).click();
    await expect(priceGroupField).toContainText(/wholesale|großhandel|grosshandel/i);

    await page.getByRole('tab', { name: /steuern|tax/i }).click();
    await expect(taxCategoryField).toContainText(/zero|nullsatz/i);
  });
});
