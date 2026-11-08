import { randomUUID } from 'node:crypto';
import { beforeAll, afterAll, afterEach, beforeEach, describe, expect, it } from 'vitest';

import {
  closeProbeTransaction,
  finishTestCase,
  openProbeTransaction,
  startTestCase,
  type ProbeTestContext,
} from '../setup/probe-database';
import { PostgresTimeEntryRepository } from '../../src/infra/repo/postgres-time-entry-repository';
import { TimeEntry } from '../../src/domain/entities/time-entry';

const formatDate = (iso: Date): string => iso.toISOString().split('T')[0] ?? '';
const addHours = (date: Date, hours: number): Date => new Date(date.getTime() + hours * 60 * 60 * 1000);
// Own test records: the time_entries id, tenant and employee columns are UUIDs
const testTenantId = randomUUID();
const testActorId = randomUUID();

const createTimeEntry = (overrides: Partial<TimeEntry> = {}): TimeEntry => {
  const start = overrides.start ? new Date(overrides.start) : new Date();
  const end = overrides.end ? new Date(overrides.end) : addHours(start, 2);

  const base: TimeEntry = {
    id: randomUUID(),
    tenantId: testTenantId,
    employeeId: randomUUID(),
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
    createdBy: testActorId,
    updatedBy: testActorId,
  };

  return { ...base, ...overrides };
};

describe('PostgresTimeEntryRepository (integration)', () => {
  let context: ProbeTestContext | undefined;
  let repository: PostgresTimeEntryRepository;

  beforeAll(async () => {
    context = await openProbeTransaction();
    repository = new PostgresTimeEntryRepository(context.client);
  });

  afterAll(async () => {
    await closeProbeTransaction(context);
  });

  beforeEach(async () => {
    await startTestCase(context!);
  });

  afterEach(async () => {
    await finishTestCase(context!);
  });

  it('persists and retrieves a time entry', async () => {
    const entry = createTimeEntry();
    await repository.save(entry.tenantId, entry);

    const found = await repository.findById(entry.tenantId, entry.id);

    expect(found).toBeDefined();
    expect(found?.id).toBe(entry.id);
  });
});
