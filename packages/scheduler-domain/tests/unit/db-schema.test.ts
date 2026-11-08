import { describe, it, expect } from 'vitest';
import { getTableConfig } from 'drizzle-orm/pg-core';

// drizzle-orm 0.45 throws while importing a schema that builds indexes outside a table callback
describe('scheduler db schema', () => {
  it('loads and keeps the composite run indexes on the runs table', async () => {
    const { runs } = await import('../../src/infra/db/schema');
    const indexes = getTableConfig(runs).indexes.map((index) => [
      index.config.name,
      index.config.columns.map((column) => ('name' in column ? column.name : '')).join(','),
    ]);

    expect(indexes).toEqual(expect.arrayContaining([
      ['schedule_runs_idx', 'schedule_id,status'],
      ['job_runs_idx', 'job_id,status'],
      ['runs_tenant_time_idx', 'tenant_id,created_at'],
    ]));
  });
});
