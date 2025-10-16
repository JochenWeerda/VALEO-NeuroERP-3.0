const { test, expect } = require('@playwright/test');

test.describe('CRM CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="email"]', 'admin@valero-neuroerp.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3000/dashboard');
  });

  test('should create, read, update and delete a contact', async ({ page }) => {
    // Navigate to contacts
    await page.goto('http://localhost:3000/crm/kontakte');

    // Click "Neuer Kontakt" button
    await page.click('text=Neuer Kontakt');

    // Fill contact form
    await page.fill('input[placeholder*="Name"]', 'Testkunde GmbH');
    await page.fill('input[placeholder*="Unternehmen"]', 'Test Company');
    await page.fill('input[placeholder*="E-Mail"]', 'test@testcompany.de');
    await page.fill('input[placeholder*="Telefon"]', '+49 123 456789');

    // Select type
    await page.click('button:has-text("Kunde")');
    await page.click('text=Kunde');

    // Save contact
    await page.click('button:has-text("Speichern")');

    // Verify contact was created and appears in list
    await page.waitForSelector('text=Testkunde GmbH');
    expect(await page.locator('text=Testkunde GmbH').count()).toBeGreaterThan(0);

    // Click on contact to view details
    await page.click('text=Testkunde GmbH');

    // Verify contact details
    await expect(page.locator('text=Testkunde GmbH')).toBeVisible();
    await expect(page.locator('text=test@testcompany.de')).toBeVisible();

    // Edit contact
    await page.click('button:has-text("Bearbeiten")');
    await page.fill('input[value="Testkunde GmbH"]', 'Testkunde GmbH (aktualisiert)');
    await page.click('button:has-text("Speichern")');

    // Verify update
    await expect(page.locator('text=Testkunde GmbH (aktualisiert)')).toBeVisible();

    // Delete contact
    await page.click('button:has-text("Löschen")');
    await page.click('button:has-text("Bestätigen")');

    // Verify contact was deleted
    await page.waitForSelector('text=Testkunde GmbH (aktualisiert)', { state: 'hidden' });
  });

  test('should create, read, update and delete a lead', async ({ page }) => {
    // Navigate to leads
    await page.goto('http://localhost:3000/crm/leads');

    // Click "Neuer Lead" button
    await page.click('text=Neuer Lead');

    // Fill lead form
    await page.fill('input[placeholder*="Unternehmen"]', 'Neuer Lead GmbH');
    await page.fill('input[placeholder*="Ansprechpartner"]', 'Max Mustermann');
    await page.fill('input[placeholder*="E-Mail"]', 'max@neuerlead.de');
    await page.fill('input[placeholder*="Telefon"]', '+49 987 654321');

    // Select source
    await page.click('button:has-text("Quelle")');
    await page.click('text=Website');

    // Set potential
    await page.fill('input[placeholder*="Potenzial"]', '75000');

    // Select priority
    await page.click('button:has-text("Priorität")');
    await page.click('text=Hoch');

    // Save lead
    await page.click('button:has-text("Speichern")');

    // Verify lead was created
    await page.waitForSelector('text=Neuer Lead GmbH');
    expect(await page.locator('text=Neuer Lead GmbH').count()).toBeGreaterThan(0);

    // Click on lead to view details
    await page.click('text=Neuer Lead GmbH');

    // Verify lead details
    await expect(page.locator('text=Neuer Lead GmbH')).toBeVisible();
    await expect(page.locator('text=75.000')).toBeVisible();

    // Edit lead
    await page.click('button:has-text("Bearbeiten")');
    await page.fill('input[value="Neuer Lead GmbH"]', 'Neuer Lead GmbH (qualifiziert)');
    await page.click('button:has-text("Status")');
    await page.click('text=Qualifiziert');
    await page.click('button:has-text("Speichern")');

    // Verify update
    await expect(page.locator('text=Neuer Lead GmbH (qualifiziert)')).toBeVisible();

    // Delete lead
    await page.click('button:has-text("Löschen")');
    await page.click('button:has-text("Bestätigen")');

    // Verify lead was deleted
    await page.waitForSelector('text=Neuer Lead GmbH (qualifiziert)', { state: 'hidden' });
  });

  test('should create, read, update and delete an activity', async ({ page }) => {
    // Navigate to activities
    await page.goto('http://localhost:3000/crm/aktivitaeten');

    // Click "Neue Aktivität" button
    await page.click('text=Neue Aktivität');

    // Fill activity form
    await page.fill('input[placeholder*="Titel"]', 'Jahresgespräch 2025');
    await page.fill('input[placeholder*="Kunde"]', 'Testkunde GmbH');
    await page.fill('input[placeholder*="Ansprechpartner"]', 'Max Mustermann');

    // Select type
    await page.click('button:has-text("Typ")');
    await page.click('text=Termin');

    // Set date
    await page.fill('input[type="date"]', '2025-12-15');

    // Select status
    await page.click('button:has-text("Status")');
    await page.click('text=Geplant');

    // Save activity
    await page.click('button:has-text("Speichern")');

    // Verify activity was created
    await page.waitForSelector('text=Jahresgespräch 2025');
    expect(await page.locator('text=Jahresgespräch 2025').count()).toBeGreaterThan(0);

    // Click on activity to view details
    await page.click('text=Jahresgespräch 2025');

    // Verify activity details
    await expect(page.locator('text=Jahresgespräch 2025')).toBeVisible();
    await expect(page.locator('text=15.12.2025')).toBeVisible();

    // Edit activity
    await page.click('button:has-text("Bearbeiten")');
    await page.fill('input[value="Jahresgespräch 2025"]', 'Jahresgespräch 2025 (aktualisiert)');
    await page.click('button:has-text("Status")');
    await page.click('text=Abgeschlossen');
    await page.click('button:has-text("Speichern")');

    // Verify update
    await expect(page.locator('text=Jahresgespräch 2025 (aktualisiert)')).toBeVisible();

    // Delete activity
    await page.click('button:has-text("Löschen")');
    await page.click('button:has-text("Bestätigen")');

    // Verify activity was deleted
    await page.waitForSelector('text=Jahresgespräch 2025 (aktualisiert)', { state: 'hidden' });
  });

  test('should create, read, update and delete a farm profile', async ({ page }) => {
    // Navigate to farm profiles
    await page.goto('http://localhost:3000/crm/betriebsprofile');

    // Click "Neues Betriebsprofil" button
    await page.click('text=Neues Betriebsprofil');

    // Fill basic information
    await page.fill('input[id="farmName"]', 'Test Hof GmbH');
    await page.fill('input[id="owner"]', 'Hans Test');
    await page.fill('input[id="totalArea"]', '150.5');

    // Add crops
    await page.click('text=Kultur hinzufügen');
    await page.fill('input[placeholder*="Weizen"]', 'Weizen');
    await page.fill('input[placeholder*="0.00"]', '80');
    await page.click('text=Kultur hinzufügen');
    await page.fill('input[placeholder*="Weizen"]:nth-of-type(2)', 'Gerste');
    await page.fill('input[placeholder*="0.00"]:nth-of-type(2)', '45');

    // Add livestock
    await page.click('text=Tierart hinzufügen');
    await page.click('button:has-text("Tierart auswählen")');
    await page.click('text=Milchkühe');
    await page.fill('input[placeholder*="0"]', '60');

    // Add location
    await page.fill('textarea[id="address"]', 'Teststraße 123, 12345 Teststadt, Deutschland');
    await page.fill('input[id="latitude"]', '52.520008');
    await page.fill('input[id="longitude"]', '13.404954');

    // Add certifications
    await page.click('text=Bio');
    await page.click('text=QS');

    // Save farm profile
    await page.click('button:has-text("Erstellen")');

    // Verify farm profile was created
    await page.waitForSelector('text=Test Hof GmbH');
    expect(await page.locator('text=Test Hof GmbH').count()).toBeGreaterThan(0);

    // Click on farm profile to view details
    await page.click('text=Test Hof GmbH');

    // Verify farm profile details
    await expect(page.locator('text=Test Hof GmbH')).toBeVisible();
    await expect(page.locator('text=Hans Test')).toBeVisible();
    await expect(page.locator('text=150.5 ha')).toBeVisible();

    // Edit farm profile
    await page.click('button:has-text("Bearbeiten")');
    await page.fill('input[id="farmName"]', 'Test Hof GmbH (aktualisiert)');
    await page.fill('input[id="totalArea"]', '160.0');
    await page.click('button:has-text("Speichern")');

    // Verify update
    await expect(page.locator('text=Test Hof GmbH (aktualisiert)')).toBeVisible();

    // Delete farm profile
    await page.click('button:has-text("Löschen")');
    await page.click('button:has-text("Bestätigen")');

    // Verify farm profile was deleted
    await page.waitForSelector('text=Test Hof GmbH (aktualisiert)', { state: 'hidden' });
  });

  test('should handle form validation errors', async ({ page }) => {
    // Navigate to contacts
    await page.goto('http://localhost:3000/crm/kontakte');

    // Click "Neuer Kontakt" button
    await page.click('text=Neuer Kontakt');

    // Try to save without required fields
    await page.click('button:has-text("Speichern")');

    // Verify validation errors are shown
    await expect(page.locator('text=Name ist erforderlich')).toBeVisible();
    await expect(page.locator('text=Unternehmen ist erforderlich')).toBeVisible();
  });

  test('should handle search and filtering', async ({ page }) => {
    // Navigate to contacts
    await page.goto('http://localhost:3000/crm/kontakte');

    // Search for specific contact
    await page.fill('input[placeholder*="Suche"]', 'Testkunde');

    // Verify search results
    await expect(page.locator('text=Testkunde')).toBeVisible();

    // Clear search
    await page.fill('input[placeholder*="Suche"]', '');

    // Filter by type
    await page.click('button:has-text("Alle Typen")');
    await page.click('text=Kunde');

    // Verify filtering works
    const contacts = await page.locator('tbody tr').count();
    expect(contacts).toBeGreaterThan(0);
  });

  test('should handle navigation between CRM modules', async ({ page }) => {
    // Start at dashboard
    await page.goto('http://localhost:3000/dashboard');

    // Navigate to CRM
    await page.click('text=CRM');

    // Navigate between modules
    await page.click('text=Kontakte');
    await expect(page.url()).toContain('/crm/kontakte');

    await page.click('text=Leads');
    await expect(page.url()).toContain('/crm/leads');

    await page.click('text=Aktivitäten');
    await expect(page.url()).toContain('/crm/aktivitaeten');

    await page.click('text=Betriebsprofile');
    await expect(page.url()).toContain('/crm/betriebsprofile');
  });
});