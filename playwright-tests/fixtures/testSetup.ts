/**
 * Test-Fixtures für UAT
 * - Auto-Login für verschiedene Rollen
 * - Tenant-Isolation
 * - Seed-Daten
 */

import { Page, test as base } from '@playwright/test';
import { ApiHelper, TEST_USERS, loginToPage } from '../helpers/api';
import { FallbackDetector } from '../helpers/fallbackDetector';

export interface UATFixtures {
  adminPage: Page;
  powerUserPage: Page;
  readonlyPage: Page;
  apiHelper: ApiHelper;
  fallbackDetector: FallbackDetector;
  tenant: string;
}

export const test = base.extend<UATFixtures>({
  // Tenant-Isolation (Backend erwartet üblicherweise UUID; QA-UAT-01 bricht API-Calls)
  tenant: async ({ request: _request }, use) => {
    const tenant =
      process.env.VALEO_TENANT ||
      process.env.X_TENANT_ID ||
      '00000000-0000-0000-0000-000000000001';
    await use(tenant);
  },

  // API-Helper
  // baseURL kommt aus der eingebauten Playwright-Fixture und damit aus einer einzigen
  // Quelle (playwright.config.ts: VALEO_BASE_URL ?? FRONTEND_URL ?? 127.0.0.1:4173) —
  // vorher drifteten Fixture-Default (localhost:3000) und Config-Default (4173) auseinander
  // (E2E-SMOKE-REPAIR-001).
  apiHelper: async ({ request, baseURL }, use) => {
    const helper = new ApiHelper(request, baseURL ?? 'http://127.0.0.1:4173');
    await use(helper);
  },

  // Admin Page (automatisch eingeloggt)
  adminPage: async ({ browser, tenant, baseURL }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();

    try {
      await loginToPage(page, TEST_USERS.admin, baseURL ?? 'http://127.0.0.1:4173');
    } catch (error) {
      console.warn('Admin login failed, continuing without auth:', error);
    }
    
    await use(page);
    await context.close();
  },

  // Power-User Page (automatisch eingeloggt)
  powerUserPage: async ({ browser, tenant, baseURL }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();

    try {
      await loginToPage(page, TEST_USERS.powerUser, baseURL ?? 'http://127.0.0.1:4173');
    } catch (error) {
      console.warn('Power-User login failed, continuing without auth:', error);
    }
    
    await use(page);
    await context.close();
  },

  // Readonly Page (automatisch eingeloggt)
  readonlyPage: async ({ browser, tenant, baseURL }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();

    try {
      await loginToPage(page, TEST_USERS.readonly, baseURL ?? 'http://127.0.0.1:4173');
    } catch (error) {
      console.warn('Readonly login failed, continuing without auth:', error);
    }
    
    await use(page);
    await context.close();
  },

  // Fallback-Detector
  fallbackDetector: async ({ page }, use) => {
    const detector = new FallbackDetector(page);
    await use(detector);
  },
});

export { expect } from '@playwright/test';

