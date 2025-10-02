/**
 * Time Entry Repository Interface for VALEO NeuroERP 3.0 HR Domain
 * Time tracking data access with tenant isolation
 */
import { TimeEntry } from '../entities/time-entry';
export interface TimeEntryRepository {
    save(tenantId: string, timeEntry: TimeEntry): Promise<TimeEntry>;
    findById(tenantId: string, id: string): Promise<TimeEntry | null>;
    findAll(tenantId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]>;
    delete(tenantId: string, id: string): Promise<void>;
    findByEmployee(tenantId: string, employeeId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]>;
    findByEmployeeAndDate(tenantId: string, employeeId: string, date: string): Promise<TimeEntry[]>;
    findByEmployeeAndDateRange(tenantId: string, employeeId: string, fromDate: string, toDate: string): Promise<TimeEntry[]>;
    findByDate(tenantId: string, date: string): Promise<TimeEntry[]>;
    findByDateRange(tenantId: string, fromDate: string, toDate: string): Promise<TimeEntry[]>;
    findByStatus(tenantId: string, status: string): Promise<TimeEntry[]>;
    findPendingApprovals(tenantId: string): Promise<TimeEntry[]>;
    findByProject(tenantId: string, projectId: string, filters?: TimeEntryFilters): Promise<TimeEntry[]>;
    findByCostCenter(tenantId: string, costCenter: string, filters?: TimeEntryFilters): Promise<TimeEntry[]>;
    findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<TimeEntry>>;
    bulkSave(tenantId: string, timeEntries: TimeEntry[]): Promise<TimeEntry[]>;
    bulkDelete(tenantId: string, ids: string[]): Promise<void>;
    getTotalHours(tenantId: string, filters?: TimeEntryFilters): Promise<number>;
    getEmployeeTotalHours(tenantId: string, employeeId: string, fromDate: string, toDate: string): Promise<number>;
    getOvertimeHours(tenantId: string, employeeId: string, fromDate: string, toDate: string, maxDailyHours?: number): Promise<number>;
    findOverlappingEntries(tenantId: string, employeeId: string, start: string, end: string, excludeId?: string): Promise<TimeEntry[]>;
    getMonthlySummary(tenantId: string, employeeId: string, year: number, month: number): Promise<MonthlySummary>;
    getYearlySummary(tenantId: string, employeeId: string, year: number): Promise<YearlySummary>;
}
export interface TimeEntryFilters {
    employeeId?: string;
    projectId?: string;
    costCenter?: string;
    status?: string;
    source?: string;
    dateFrom?: string;
    dateTo?: string;
    approvedBy?: string;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
    filters?: TimeEntryFilters;
}
export interface PaginatedResult<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export interface MonthlySummary {
    year: number;
    month: number;
    employeeId: string;
    totalHours: number;
    regularHours: number;
    overtimeHours: number;
    totalDays: number;
    workingDays: number;
    entries: number;
    averageHoursPerDay: number;
}
export interface YearlySummary {
    year: number;
    employeeId: string;
    totalHours: number;
    regularHours: number;
    overtimeHours: number;
    totalDays: number;
    workingDays: number;
    entries: number;
    averageHoursPerDay: number;
    monthlyBreakdown: MonthlySummary[];
}
//# sourceMappingURL=time-entry-repository.d.ts.map