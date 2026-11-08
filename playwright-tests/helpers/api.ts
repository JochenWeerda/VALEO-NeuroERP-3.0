/**
 * API-Helper für Playwright-Tests
 * Auth, CRUD-Wrapper, Seed-Daten
 */

import { APIRequestContext, Page } from '@playwright/test';
import { holeTokens } from './anmeldung';

export interface AuthCredentials {
  email: string;
  password: string;
  role: 'admin' | 'power-user' | 'readonly';
}

export interface TestUser {
  credentials: AuthCredentials;
  token?: string;
}

export class ApiHelper {
  private baseURL: string;
  private request: APIRequestContext;

  constructor(request: APIRequestContext, baseURL: string) {
    this.request = request;
    this.baseURL = baseURL;
  }

  /**
   * Login und Token-Generierung
   */
  async login(credentials: AuthCredentials): Promise<string> {
    const response = await this.request.post(`${this.baseURL}/api/auth/login`, {
      data: {
        email: credentials.email,
        password: credentials.password,
      },
    });

    if (!response.ok()) {
      throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
    }

    const data = await response.json();
    return data.token || data.access_token;
  }

  /**
   * CRUD-Wrapper: Create
   */
  async create<T>(endpoint: string, data: T, token?: string): Promise<any> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await this.request.post(`${this.baseURL}${endpoint}`, {
      data,
      headers,
    });

    if (!response.ok()) {
      throw new Error(`Create failed: ${response.status()} ${await response.text()}`);
    }

    return await response.json();
  }

  /**
   * CRUD-Wrapper: Read (List)
   */
  async list(endpoint: string, token?: string): Promise<any[]> {
    const headers: Record<string, string> = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await this.request.get(`${this.baseURL}${endpoint}`, {
      headers,
    });

    if (!response.ok()) {
      throw new Error(`List failed: ${response.status()} ${await response.text()}`);
    }

    return await response.json();
  }

  /**
   * CRUD-Wrapper: Update
   */
  async update<T>(endpoint: string, id: string, data: T, token?: string): Promise<any> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await this.request.put(`${this.baseURL}${endpoint}/${id}`, {
      data,
      headers,
    });

    if (!response.ok()) {
      throw new Error(`Update failed: ${response.status()} ${await response.text()}`);
    }

    return await response.json();
  }

  /**
   * CRUD-Wrapper: Delete
   */
  async delete(endpoint: string, id: string, token?: string): Promise<void> {
    const headers: Record<string, string> = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await this.request.delete(`${this.baseURL}${endpoint}/${id}`, {
      headers,
    });

    if (!response.ok()) {
      throw new Error(`Delete failed: ${response.status()} ${await response.text()}`);
    }
  }

  /**
   * Seed-Daten für Test-Mandant
   */
  async seedTestData(domain: string, token: string): Promise<void> {
    const seedEndpoints: Record<string, string> = {
      sales: '/api/test/seed/sales',
      agrar: '/api/test/seed/agrar',
      crm: '/api/test/seed/crm',
      finance: '/api/test/seed/finance',
      inventory: '/api/test/seed/inventory',
    };

    const endpoint = seedEndpoints[domain];
    if (!endpoint) {
      console.warn(`No seed endpoint for domain: ${domain}`);
      return;
    }

    try {
      await this.request.post(`${this.baseURL}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant': 'QA-UAT-01',
        },
      });
    } catch (error) {
      console.warn(`Seeding ${domain} failed (may not be implemented):`, error);
    }
  }
}

/**
 * Session für Page-basierte Tests.
 *
 * Seit 12.10.2026 gibt es keinen Dev-Token mehr. Standard: Tokens per Password Grant vom Test-Keycloak holen
 * (`helpers/anmeldung.ts`) und so in `localStorage` legen, wie die SPA sie nach dem PKCE-Rueckruf ablegt.
 * `VALEO_PLAYWRIGHT_USE_SSO=1` meldet stattdessen ueber die Anmeldeseite des Anbieters an.
 */
export async function loginToPage(
  page: Page,
  credentials: AuthCredentials,
  baseURL: string
): Promise<void> {
  const root = baseURL.replace(/\/$/, '');

  if (process.env.VALEO_PLAYWRIGHT_USE_SSO === '1') {
    await page.goto(`${root}/login`);
    await page.getByRole('button', { name: /SSO/i }).click();
    await page.fill('input[name="username"], input[type="email"]', credentials.email);
    await page.fill('input[name="password"], input[type="password"]', credentials.password);
    await page.press('input[name="password"], input[type="password"]', 'Enter');
    await page.waitForURL((url) => url.origin === new URL(root).origin && !url.pathname.startsWith('/login'), { timeout: 15000 });
    return;
  }

  const tokens = await holeTokens(credentials.email, credentials.password);
  await page.addInitScript((t: { access: string; refresh?: string }) => {
    localStorage.setItem('access_token', t.access);
    if (t.refresh) localStorage.setItem('refresh_token', t.refresh);
  }, tokens);

  await page.goto(`${root}/`, { waitUntil: 'domcontentloaded' });
  // networkidle tritt bei offenen SSE-/Polling-Verbindungen der Universal-Masken nie
  // ein (E2E-SMOKE-REPAIR-001). Best-effort auf die App-Shell warten — nicht kritisch,
  // da die Specs ihre Zielelemente anschliessend deterministisch selbst abwarten.
  await page
    .locator('h1, h2, main, [role="main"]')
    .first()
    .waitFor({ state: 'visible', timeout: 15000 })
    .catch(() => undefined);
}

/**
 * Standard-Test-User — nur aus der Umgebung; feste Beispielkennwoerter gibt es nicht mehr.
 */
export const TEST_USERS: Record<string, AuthCredentials> = {
  admin: {
    email: process.env.VALEO_USER_ADMIN ?? '',
    password: process.env.VALEO_PASS_ADMIN ?? '',
    role: 'admin',
  },
  powerUser: {
    email: process.env.VALEO_USER_POWER ?? '',
    password: process.env.VALEO_PASS_POWER ?? '',
    role: 'power-user',
  },
  readonly: {
    email: process.env.VALEO_USER_READ ?? '',
    password: process.env.VALEO_PASS_READ ?? '',
    role: 'readonly',
  },
};

