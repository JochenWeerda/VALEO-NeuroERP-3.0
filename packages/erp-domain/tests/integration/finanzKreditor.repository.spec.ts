/**
 * Integration test scaffold for FinanzKreditorPostgresRepository.
 * Connects to a live Postgres instance; skips automatically if env var is missing.
 */

import { Pool } from 'pg';
import { FinanzKreditorPostgresRepository } from '../../src/infrastructure/repositories/finanzKreditor-postgres.repository';

describe('FinanzKreditorPostgresRepository', () => {
  const connectionString = process.env.ERP_DATABASE_URL;

  if (!connectionString) {
    it('is skipped because ERP_DATABASE_URL is not defined', () => {
      expect(true).toBe(true);
    });
    return;
  }

  const pool = new Pool({ connectionString });
  const repository = new FinanzKreditorPostgresRepository(pool);

  afterAll(async () => {
    await pool.end();
  });

  it('list returns an array', async () => {
    const items = await repository.list();
    expect(Array.isArray(items)).toBe(true);
  });
});
