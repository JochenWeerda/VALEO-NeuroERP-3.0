/**
 * Integration test scaffold for FinanzDebitorPostgresRepository.
 * Connects to a live Postgres instance; skips automatically if env var is missing.
 */

import { Pool } from 'pg';
import { FinanzDebitorPostgresRepository } from '../../src/infrastructure/repositories/finanzDebitor-postgres.repository';

describe('FinanzDebitorPostgresRepository', () => {
  const connectionString = process.env.ERP_DATABASE_URL;

  if (!connectionString) {
    it('is skipped because ERP_DATABASE_URL is not defined', () => {
      expect(true).toBe(true);
    });
    return;
  }

  const pool = new Pool({ connectionString });
  const repository = new FinanzDebitorPostgresRepository(pool);

  afterAll(async () => {
    await pool.end();
  });

  it('list returns an array', async () => {
    const items = await repository.list();
    expect(Array.isArray(items)).toBe(true);
  });
});
