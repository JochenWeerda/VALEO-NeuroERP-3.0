/**
 * PostgreSQL-backed Time Entry Repository for VALEO NeuroERP 3.0 HR Domain
 */

import type { QueryResultRow } from 'pg';
import { TimeEntry, TimeEntryEntity } from '../../domain/entities/time-entry';
import {
  MonthlySummary,
  PaginatedResult,
  PaginationOptions,
  TimeEntryFilters,
  TimeEntryRepository,
  YearlySummary
} from '../../domain/repositories/time-entry-repository';

const MONTHS_PER_YEAR = 12;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY;
const SECONDS_PER_MINUTE = 60;
const MILLISECONDS_PER_SECOND = 1000;
const MILLISECONDS_PER_MINUTE = SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND;
const MILLISECONDS_PER_DAY = MINUTES_PER_DAY * MILLISECONDS_PER_MINUTE;
const END_OF_DAY_HOUR = HOURS_PER_DAY - 1;
const END_OF_DAY_MINUTE = MINUTES_PER_HOUR - 1;
const END_OF_DAY_SECOND = SECONDS_PER_MINUTE - 1;
const END_OF_DAY_MILLISECOND = MILLISECONDS_PER_SECOND - 1;
const FIRST_MONTH_INDEX = 0;
const MONTH_INDEX_OFFSET = 1;
const DEFAULT_MAX_DAILY_HOURS = 8;
const DEFAULT_SORT_COLUMN = 'updated_at';
const DEFAULT_SORT_DIRECTION = 'desc';

const SORT_COLUMN_MAP: Record<string, string> = {
  start: 'start',
  end: '"end"',
  createdAt: 'created_at',
  updatedAt: 'updated_at'
};

const SORT_DIRECTIONS = new Set(['asc', 'desc']);

interface Queryable {
  query: (statement: string, parameters?: unknown[]) => Promise<{ rows: QueryResultRow[] }>;
}

interface SqlFilter {
  clause: string;
  parameters: unknown[];
}

export class PostgresTimeEntryRepository implements TimeEntryRepository {
  constructor(private readonly db: Queryable) {}

  async save(tenantId: string, timeEntry: TimeEntry): Promise<TimeEntry> {
    const query = `INSERT INTO time_entries (id, tenant_id, employee_id, date, start, "end", break_minutes, project_id, cost_center, source, status, approved_by, created_at, updated_at, version, created_by, updated_by) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17) ON CONFLICT (id) DO UPDATE SET tenant_id = EXCLUDED.tenant_id, employee_id = EXCLUDED.employee_id, date = EXCLUDED.date, start = EXCLUDED.start, "end" = EXCLUDED."end", break_minutes = EXCLUDED.break_minutes, project_id = EXCLUDED.project_id, cost_center = EXCLUDED.cost_center, source = EXCLUDED.source, status = EXCLUDED.status, approved_by = EXCLUDED.approved_by, created_at = EXCLUDED.created_at, updated_at = EXCLUDED.updated_at, version = EXCLUDED.version, created_by = EXCLUDED.created_by, updated_by = EXCLUDED.updated_by RETURNING *`;

    const params = [
      timeEntry.id,
      tenantId,
      timeEntry.employeeId,
      timeEntry.date,
      timeEntry.start,
      timeEntry.end,
      timeEntry.breakMinutes,
      timeEntry.projectId ?? null,
      timeEntry.costCenter ?? null,
      timeEntry.source,
      timeEntry.status,
      timeEntry.approvedBy ?? null,
      timeEntry.createdAt,
      timeEntry.updatedAt,
      timeEntry.version,
      timeEntry.createdBy ?? null,
      timeEntry.updatedBy ?? null
    ];

    const result = await this.db.query(query, params);
    return this.mapRowToTimeEntry(result.rows[0]);
  }

  async findById(tenantId: string, id: string): Promise<TimeEntry | null> {
    const result = await this.db.query(
      'SELECT * FROM time_entries WHERE tenant_id = $1 AND id = $2 LIMIT 1',
      [tenantId, id]
    );

    if (result.rows.length === 0) {
      return null;
    }

    return this.mapRowToTimeEntry(result.rows[0]);
  }

  async findAll(tenantId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, filters);
  }

  async delete(tenantId: string, id: string): Promise<void> {
    await this.db.query('DELETE FROM time_entries WHERE tenant_id = $1 AND id = $2', [tenantId, id]);
  }

  async findByEmployee(tenantId: string, employeeId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { ...filters, employeeId });
  }

  async findByEmployeeAndDate(tenantId: string, employeeId: string, date: string): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { employeeId, dateFrom: date, dateTo: date });
  }

  async findByEmployeeAndDateRange(
    tenantId: string,
    employeeId: string,
    fromDate: string,
    toDate: string
  ): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { employeeId, dateFrom: fromDate, dateTo: toDate });
  }

  async findByDate(tenantId: string, date: string): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { dateFrom: date, dateTo: date });
  }

  async findByDateRange(tenantId: string, fromDate: string, toDate: string): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { dateFrom: fromDate, dateTo: toDate });
  }

  async findByStatus(tenantId: string, status: string): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { status });
  }

  async findPendingApprovals(tenantId: string): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { status: 'Draft' });
  }

  async findByProject(tenantId: string, projectId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { ...filters, projectId });
  }

  async findByCostCenter(tenantId: string, costCenter: string, filters?: TimeEntryFilters): Promise<TimeEntry[]> {
    return this.fetchEntries(tenantId, { ...filters, costCenter });
  }

  async findWithPagination(
    tenantId: string,
    options: PaginationOptions
  ): Promise<PaginatedResult<TimeEntry>> {
    const { page, pageSize, sortBy, sortOrder, filters } = options;
    const offset = (page - 1) * pageSize;

    const entries = await this.fetchEntries(tenantId, filters, {
      sortBy,
      sortOrder,
      limit: pageSize,
      offset
    });

    const totalResult = await this.fetchEntries(tenantId, filters, { countOnly: true });
    const total = Array.isArray(totalResult) ? totalResult.length : Number(totalResult);

    return {
      data: entries,
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize) || 1
      }
    };
  }

  async bulkSave(tenantId: string, timeEntries: TimeEntry[]): Promise<TimeEntry[]> {
    const saved: TimeEntry[] = [];
    for (const entry of timeEntries) {
      const result = await this.save(tenantId, entry);
      saved.push(result);
    }
    return saved;
  }

  async bulkDelete(tenantId: string, ids: string[]): Promise<void> {
    if (ids.length === 0) {
      return;
    }
    await this.db.query(
      'DELETE FROM time_entries WHERE tenant_id = $1 AND id = ANY($2)',
      [tenantId, ids]
    );
  }

  async getTotalHours(tenantId: string, filters?: TimeEntryFilters): Promise<number> {
    const entries = await this.fetchEntries(tenantId, filters);
    return this.calculateHours(entries);
  }

  async getEmployeeTotalHours(
    tenantId: string,
    employeeId: string,
    fromDate: string,
    toDate: string
  ): Promise<number> {
    const entries = await this.findByEmployeeAndDateRange(tenantId, employeeId, fromDate, toDate);
    return this.calculateHours(entries);
  }

  async getOvertimeHours(
    tenantId: string,
    employeeId: string,
    fromDate: string,
    toDate: string,
    maxDailyHours = DEFAULT_MAX_DAILY_HOURS
  ): Promise<number> {
    const entries = await this.findByEmployeeAndDateRange(tenantId, employeeId, fromDate, toDate);
    return entries.reduce((sum, entry) => {
      const entity = TimeEntryEntity.fromJSON(entry);
      return sum + entity.getOvertimeMinutes(maxDailyHours) / MINUTES_PER_HOUR;
    }, 0);
  }

  async findOverlappingEntries(
    tenantId: string,
    employeeId: string,
    start: string,
    end: string,
    excludeId?: string
  ): Promise<TimeEntry[]> {
    const startMs = new Date(start).getTime();
    const endMs = new Date(end).getTime();

    const entries = await this.fetchEntries(tenantId, { employeeId });
    return entries.filter(entry => {
      if (excludeId !== undefined && entry.id === excludeId) {
        return false;
      }
      const entryStart = new Date(entry.start).getTime();
      const entryEnd = new Date(entry.end).getTime();
      return startMs < entryEnd && endMs > entryStart;
    });
  }

  async getMonthlySummary(
    tenantId: string,
    employeeId: string,
    year: number,
    month: number
  ): Promise<MonthlySummary> {
    const monthIndex = month - MONTH_INDEX_OFFSET;
    const monthStart = new Date(Date.UTC(year, monthIndex, 1)).toISOString();
    const monthEnd = new Date(
      Date.UTC(
        year,
        monthIndex + 1,
        0,
        END_OF_DAY_HOUR,
        END_OF_DAY_MINUTE,
        END_OF_DAY_SECOND,
        END_OF_DAY_MILLISECOND
      )
    ).toISOString();
    const entries = await this.findByEmployeeAndDateRange(tenantId, employeeId, monthStart, monthEnd);
    return this.buildMonthlySummary(year, month, employeeId, entries);
  }

  async getYearlySummary(tenantId: string, employeeId: string, year: number): Promise<YearlySummary> {
    const yearStart = new Date(Date.UTC(year, FIRST_MONTH_INDEX, 1)).toISOString();
    const yearEnd = new Date(
      Date.UTC(
        year + MONTH_INDEX_OFFSET,
        FIRST_MONTH_INDEX,
        0,
        END_OF_DAY_HOUR,
        END_OF_DAY_MINUTE,
        END_OF_DAY_SECOND,
        END_OF_DAY_MILLISECOND
      )
    ).toISOString();
    const entries = await this.findByEmployeeAndDateRange(tenantId, employeeId, yearStart, yearEnd);

    const monthlyBreakdown: MonthlySummary[] = Array.from({ length: MONTHS_PER_YEAR }, (_, index) =>
      this.buildMonthlySummary(year, index + MONTH_INDEX_OFFSET, employeeId, entries)
    );

    const totalHours = monthlyBreakdown.reduce((sum, summary) => sum + summary.totalHours, 0);
    const regularHours = monthlyBreakdown.reduce((sum, summary) => sum + summary.regularHours, 0);
    const overtimeHours = monthlyBreakdown.reduce((sum, summary) => sum + summary.overtimeHours, 0);
    const totalEntries = monthlyBreakdown.reduce((sum, summary) => sum + summary.entries, 0);
    const totalDays = monthlyBreakdown.reduce((sum, summary) => sum + summary.totalDays, 0);
    const workingDays = monthlyBreakdown.reduce((sum, summary) => sum + summary.workingDays, 0);

    return {
      year,
      employeeId,
      totalHours,
      regularHours,
      overtimeHours,
      totalDays,
      workingDays,
      entries: totalEntries,
      averageHoursPerDay: workingDays > 0 ? totalHours / workingDays : 0,
      monthlyBreakdown
    };
  }

  private async fetchEntries(
    tenantId: string,
    filters?: TimeEntryFilters,
    options?: { sortBy?: string; sortOrder?: 'asc' | 'desc'; limit?: number; offset?: number; countOnly?: boolean }
  ): Promise<TimeEntry[] | number> {
    const { clause, parameters } = this.buildFilterClause(tenantId, filters);

    const sortColumn = SORT_COLUMN_MAP[options?.sortBy ?? DEFAULT_SORT_COLUMN] ?? SORT_COLUMN_MAP[DEFAULT_SORT_COLUMN];
    const sortDirection = options?.sortOrder && SORT_DIRECTIONS.has(options.sortOrder)
      ? options.sortOrder
      : DEFAULT_SORT_DIRECTION;

    if (options?.countOnly === true) {
      const { rows } = await this.db.query(
        `SELECT COUNT(*)::int AS total FROM time_entries WHERE ${clause}`,
        parameters
      );
      return Number(rows[0]?.total ?? 0);
    }

    let sql = `SELECT * FROM time_entries WHERE ${clause} ORDER BY ${sortColumn} ${sortDirection}`;
    const queryParams = [...parameters];
    let index = parameters.length + 1;

    if (typeof options?.limit === 'number') {
      sql += ` LIMIT $${index}`;
      queryParams.push(options.limit);
      index += 1;
    }

    if (typeof options?.offset === 'number') {
      sql += ` OFFSET $${index}`;
      queryParams.push(options.offset);
      index += 1;
    }

    const { rows } = await this.db.query(sql, queryParams);
    return rows.map(row => this.mapRowToTimeEntry(row));
  }

  private buildFilterClause(tenantId: string, filters?: TimeEntryFilters): SqlFilter {
    const clauses: string[] = ['tenant_id = $1'];
    const parameters: unknown[] = [tenantId];
    const INITIAL_INDEX = 2;
    let index = INITIAL_INDEX;

    const addEqualityClause = (column: string, value: unknown): void => {
      clauses.push(`${column} = $${index}`);
      parameters.push(value);
      index += 1;
    };

    if (filters?.employeeId !== undefined) {
      addEqualityClause('employee_id', filters.employeeId);
    }
    if (filters?.projectId !== undefined) {
      addEqualityClause('project_id', filters.projectId);
    }
    if (filters?.costCenter !== undefined) {
      addEqualityClause('cost_center', filters.costCenter);
    }
    if (filters?.status !== undefined) {
      addEqualityClause('status', filters.status);
    }
    if (filters?.source !== undefined) {
      addEqualityClause('source', filters.source);
    }
    if (filters?.approvedBy !== undefined) {
      addEqualityClause('approved_by', filters.approvedBy);
    }
    if (filters?.dateFrom !== undefined) {
      const from = new Date(filters.dateFrom).toISOString();
      clauses.push(`start >= $${index}`);
      parameters.push(from);
      index += 1;
    }
    if (filters?.dateTo !== undefined) {
      const parsed = new Date(filters.dateTo).getTime();
      if (Number.isFinite(parsed)) {
        const inclusiveTo = new Date(parsed + MILLISECONDS_PER_DAY - 1).toISOString();
        clauses.push(`start <= $${index}`);
        parameters.push(inclusiveTo);
        index += 1;
      }
    }

    return {
      clause: clauses.join(' AND '),
      parameters
    };
  }

  private calculateHours(entries: TimeEntry[]): number {
    return entries.reduce((sum, entry) => {
      const entity = TimeEntryEntity.fromJSON(entry);
      return sum + entity.getWorkingHours();
    }, 0);
  }

  private buildMonthlySummary(
    year: number,
    month: number,
    employeeId: string,
    entries: TimeEntry[]
  ): MonthlySummary {
    const monthEntries = entries.filter(entry => {
      const date = new Date(entry.date);
      return date.getUTCFullYear() === year && date.getUTCMonth() + MONTH_INDEX_OFFSET === month;
    });

    const totalHours = this.calculateHours(monthEntries);
    const overtimeHours = monthEntries.reduce((sum, entry) => {
      const entity = TimeEntryEntity.fromJSON(entry);
      return sum + entity.getOvertimeMinutes(DEFAULT_MAX_DAILY_HOURS) / MINUTES_PER_HOUR;
    }, 0);
    const regularHours = totalHours - overtimeHours;
    const workingDays = new Set(monthEntries.map(entry => entry.date)).size;
    const totalDays = new Date(Date.UTC(year, month, 0)).getUTCDate();

    return {
      year,
      month,
      employeeId,
      totalHours,
      regularHours,
      overtimeHours,
      totalDays,
      workingDays,
      entries: monthEntries.length,
      averageHoursPerDay: workingDays > 0 ? totalHours / workingDays : 0
    };
  }

  private mapRowToTimeEntry(row: QueryResultRow): TimeEntry {
    return {
      id: String(row.id),
      tenantId: String(row.tenant_id),
      employeeId: String(row.employee_id),
      date: String(row.date),
      start: new Date(row.start as string | Date).toISOString(),
      end: new Date(row.end as string | Date).toISOString(),
      breakMinutes: Number(row.break_minutes),
      projectId: row.project_id != null ? String(row.project_id) : undefined,
      costCenter: row.cost_center != null ? String(row.cost_center) : undefined,
      source: String(row.source) as TimeEntry['source'],
      status: String(row.status) as TimeEntry['status'],
      approvedBy: row.approved_by != null ? String(row.approved_by) : undefined,
      createdAt: new Date(row.created_at as string | Date).toISOString(),
      updatedAt: new Date(row.updated_at as string | Date).toISOString(),
      version: Number(row.version),
      createdBy: row.created_by != null ? String(row.created_by) : undefined,
      updatedBy: row.updated_by != null ? String(row.updated_by) : undefined
    } satisfies TimeEntry;
  }
}
