import { beforeAll, afterAll, beforeEach, describe, expect, it } from 'vitest';
import { Client } from 'pg';

import { startPostgresContainer, stopPostgresContainer, type PostgresTestContext } from '../setup/testcontainers';
import { runMigrations } from '../setup/migrations';
import { PostgresTimeEntryRepository } from '../../src/infra/repo/postgres-time-entry-repository';
import { TimeEntry } from '../../src/domain/entities/time-entry';

const formatDate = (iso: Date): string => iso.toISOString().split('T')[0] ?? '';
const addHours = (date: Date, hours: number): Date => new Date(date.getTime() + hours * 60 * 60 * 1000);
const randomId = () => 'id-' + Math.random().toString(16).slice(2, 10);

const createTimeEntry = (overrides: Partial<TimeEntry> = {}): TimeEntry => {
  const start = overrides.start ? new Date(overrides.start) : new Date();
  const end = overrides.end ? new Date(overrides.end) : addHours(start, 2);

  const base: TimeEntry = {
    id: randomId(),
    tenantId: 'tenant-default',
    employeeId: randomId(),
    date: formatDate(start),
    start: start.toISOString(),
    end: end.toISOString(),
    breakMinutes: 0,
    projectId: undefined,
    costCenter: undefined,
    source: 'Manual',
    status: 'Draft',
    approvedBy: undefined,
    createdAt: start.toISOString(),
    updatedAt: start.toISOString(),
    version: 1,
    createdBy: 'system',
    updatedBy: 'system',
  };

  return { ...base, ...overrides };
};

describe('PostgresTimeEntryRepository (integration)', () => {
  let context: PostgresTestContext;
  let client: Client;
  let repository: PostgresTimeEntryRepository;

  beforeAll(async () => {
    context = await startPostgresContainer();
    client = new Client({ connectionString: context.connectionString });
    await client.connect();
    await runMigrations(client);
    repository = new PostgresTimeEntryRepository(client);
  });

  afterAll(async () => {
    await client.end();
    await stopPostgresContainer(context);
  });

  beforeEach(async () => {
    await client.query('TRUNCATE TABLE time_entries RESTART IDENTITY CASCADE;');
  });

  it('persists and retrieves a time entry', async () => {
    const entry = createTimeEntry();
    await repository.save(entry.tenantId, entry);

    const found = await repository.findById(entry.tenantId, entry.id);

    expect(found).toBeDefined();
    expect(found?.id).toBe(entry.id);
  });
});
