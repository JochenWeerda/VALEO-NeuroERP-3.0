/**
 * API-Helper für Playwright-Tests
 * Auth, CRUD-Wrapper, Seed-Daten
 */

import { Page, APIRequestContext } from '@playwright/test';

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
 * Login-Helper für Page-basierte Tests
 */
export async function loginToPage(
  page: Page,
  credentials: AuthCredentials,
  baseURL: string
): Promise<void> {
  await page.goto(`${baseURL}/auth/login`);
  
  await page.fill('input[name="email"], input[type="email"]', credentials.email);
  await page.fill('input[name="password"], input[type="password"]', credentials.password);
  await page.click('button[type="submit"]');
  
  // Warte auf erfolgreiche Navigation
  await page.waitForURL(/dashboard|home/i, { timeout: 10000 });
}

/**
 * Standard-Test-User
 */
export const TEST_USERS: Record<string, AuthCredentials> = {
  admin: {
    email: process.env.VALEO_USER_ADMIN || 'admin@example.com',
    password: process.env.VALEO_PASS_ADMIN || 'admin123',
    role: 'admin',
  },
  powerUser: {
    email: process.env.VALEO_USER_POWER || 'power@example.com',
    password: process.env.VALEO_PASS_POWER || 'power123',
    role: 'power-user',
  },
  readonly: {
    email: process.env.VALEO_USER_READ || 'readonly@example.com',
    password: process.env.VALEO_PASS_READ || 'readonly123',
    role: 'readonly',
  },
};

