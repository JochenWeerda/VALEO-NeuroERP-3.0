import { Client } from 'pg';
import { TimeEntry } from '../../src/domain/entities/time-entry';
import { PostgresTimeEntryRepository } from '../../src/infra/repo/postgres-time-entry-repository';

const formatDate = (date: Date): string => date.toISOString().split('T')[0] ?? '';
const toIso = (date: Date): string => date.toISOString();
const addMinutes = (date: Date, minutes: number): Date => new Date(date.getTime() + minutes * 60 * 1000);

const randomId = (prefix: string) => prefix + '-' + Math.random().toString(16).slice(2, 10);

export async function seedTimeEntries(
  client: Client,
  repository: PostgresTimeEntryRepository,
  options: { tenantId: string; employees: number; entriesPerEmployee: number }
): Promise<TimeEntry[]> {
  const { tenantId, employees, entriesPerEmployee } = options;
  const entries: TimeEntry[] = [];

  for (let employeeIndex = 0; employeeIndex < employees; employeeIndex += 1) {
    const employeeId = randomId('emp');

    for (let entryIndex = 0; entryIndex < entriesPerEmployee; entryIndex += 1) {
      const baseDate = new Date(Date.UTC(2024, 2, 1 + entryIndex));
      const start = addMinutes(baseDate, 8 * 60);
      const end = addMinutes(start, 8 * 60);

      const timeEntry: TimeEntry = {
        id: randomId('entry'),
        tenantId,
        employeeId,
        date: formatDate(baseDate),
        start: toIso(start),
        end: toIso(end),
        breakMinutes: 30,
        projectId: undefined,
        costCenter: undefined,
        source: 'Manual',
        status: 'Approved',
        approvedBy: 'manager-1',
        createdAt: toIso(baseDate),
        updatedAt: toIso(baseDate),
        version: 1,
        createdBy: 'seed-script',
        updatedBy: 'seed-script'
      };

      entries.push(timeEntry);
      await repository.save(tenantId, timeEntry);
    }
  }

  return entries;
}
