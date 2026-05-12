/**
 * Tenant-Isolation Tests (Phase 3 — ERP-Finanz Roadmap)
 *
 * Verifies:
 *  1. FinanzDebitorPostgresRepository.list() isolates by tenant_id
 *  2. FinanzKreditorPostgresRepository.list() isolates by tenant_id
 *  3. registerErpDomain() controller-Token ist NICHT registriert
 *     (Orders-REST = Python-Backend, kein duplizierender Node-Endpunkt)
 *
 * DB-Tests werden übersprungen wenn ERP_DATABASE_URL nicht gesetzt ist.
 */

import { ServiceLocator } from '@valero-neuroerp/utilities';
import { ERP_DOMAIN_SERVICE_TOKENS, registerErpDomain } from '../../src/bootstrap';
import { InMemoryOrderRepository } from '../../src/infrastructure/repositories/in-memory-order-repository';

// ── 1. Bootstrap-Invariante ───────────────────────────────────────────────────

describe('registerErpDomain — controller-Token (Architektur-Invariante)', () => {
  it('registriert KEINEN ERPApiController-Token (Orders-REST = Python-Backend)', () => {
    const locator = new ServiceLocator();
    registerErpDomain({ locator, repository: new InMemoryOrderRepository() });
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.controller)).toBe(false);
  });

  it('registriert alle notwendigen Commands und Queries', () => {
    const locator = new ServiceLocator();
    registerErpDomain({ locator, repository: new InMemoryOrderRepository() });
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.repository)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.service)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.listOrders)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.getOrder)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.createOrder)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.updateOrderStatus)).toBe(true);
    expect(locator.has(ERP_DOMAIN_SERVICE_TOKENS.deleteOrder)).toBe(true);
  });
});

// ── 2. DB-basierte Tenant-Isolation ──────────────────────────────────────────

const DB_URL = process.env.ERP_DATABASE_URL;

const describeWithDb = DB_URL ? describe : describe.skip;

describeWithDb('FinanzDebitorPostgresRepository — Tenant-Isolation', () => {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { Pool } = require('pg') as typeof import('pg');
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { FinanzDebitorPostgresRepository } = require('../../src/infrastructure/repositories/finanzDebitor-postgres.repository');

  const pool = new Pool({ connectionString: DB_URL });

  afterAll(async () => { await pool.end(); });

  it('list() für Tenant A enthält keine Einträge von Tenant B', async () => {
    const repo = new FinanzDebitorPostgresRepository(pool);
    const tenantA = await repo.list('tenant-a');
    const tenantB = await repo.list('tenant-b');

    // Wenn beide Tenants Daten haben dürfen sie sich nicht überschneiden
    const idsA = new Set((tenantA as { id: string }[]).map(d => d.id));
    const idsB = new Set((tenantB as { id: string }[]).map(d => d.id));
    const overlap = [...idsA].filter(id => idsB.has(id));
    expect(overlap).toHaveLength(0);
  });

  it('list() gibt leeres Array zurück für unbekannten Tenant', async () => {
    const repo = new FinanzDebitorPostgresRepository(pool);
    const result = await repo.list('__unknown-tenant-xyz__');
    expect(Array.isArray(result)).toBe(true);
    expect(result).toHaveLength(0);
  });
});

describeWithDb('FinanzKreditorPostgresRepository — Tenant-Isolation', () => {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { Pool } = require('pg') as typeof import('pg');
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { FinanzKreditorPostgresRepository } = require('../../src/infrastructure/repositories/finanzKreditor-postgres.repository');

  const pool = new Pool({ connectionString: DB_URL });

  afterAll(async () => { await pool.end(); });

  it('list() für Tenant A enthält keine Einträge von Tenant B', async () => {
    const repo = new FinanzKreditorPostgresRepository(pool);
    const tenantA = await repo.list('tenant-a');
    const tenantB = await repo.list('tenant-b');

    const idsA = new Set((tenantA as { id: string }[]).map(k => k.id));
    const idsB = new Set((tenantB as { id: string }[]).map(k => k.id));
    const overlap = [...idsA].filter(id => idsB.has(id));
    expect(overlap).toHaveLength(0);
  });

  it('list() gibt leeres Array zurück für unbekannten Tenant', async () => {
    const repo = new FinanzKreditorPostgresRepository(pool);
    const result = await repo.list('__unknown-tenant-xyz__');
    expect(Array.isArray(result)).toBe(true);
    expect(result).toHaveLength(0);
  });
});
