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
  tenant: async (_deps, use) => {
    const tenant =
      process.env.VALEO_TENANT ||
      process.env.X_TENANT_ID ||
      '00000000-0000-0000-0000-000000000001';
    await use(tenant);
  },

  // API-Helper
  apiHelper: async ({ request }, use) => {
    const baseURL = process.env.VALEO_BASE_URL || 'http://localhost:3000';
    const helper = new ApiHelper(request, baseURL);
    await use(helper);
  },

  // Admin Page (automatisch eingeloggt)
  adminPage: async ({ browser, tenant }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();
    
    const baseURL = process.env.VALEO_BASE_URL || 'http://localhost:3000';
    
    try {
      await loginToPage(page, TEST_USERS.admin, baseURL);
    } catch (error) {
      console.warn('Admin login failed, continuing without auth:', error);
    }
    
    await use(page);
    await context.close();
  },

  // Power-User Page (automatisch eingeloggt)
  powerUserPage: async ({ browser, tenant }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();
    
    const baseURL = process.env.VALEO_BASE_URL || 'http://localhost:3000';
    
    try {
      await loginToPage(page, TEST_USERS.powerUser, baseURL);
    } catch (error) {
      console.warn('Power-User login failed, continuing without auth:', error);
    }
    
    await use(page);
    await context.close();
  },

  // Readonly Page (automatisch eingeloggt)
  readonlyPage: async ({ browser, tenant }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Tenant-ID': tenant,
      },
    });
    const page = await context.newPage();
    
    const baseURL = process.env.VALEO_BASE_URL || 'http://localhost:3000';
    
    try {
      await loginToPage(page, TEST_USERS.readonly, baseURL);
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

