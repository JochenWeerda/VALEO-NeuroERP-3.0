/**
 * Time Entry Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for time tracking and approval
 */
import { TimeEntry } from '../entities/time-entry';
import { MonthlySummary, PaginatedResult, PaginationOptions, TimeEntryFilters, TimeEntryRepository, YearlySummary } from '../repositories/time-entry-repository';
import { EmployeeRepository } from '../repositories/employee-repository';
import { type HREvent } from '../events';
type DomainEventPublisher = (event: HREvent) => Promise<void>;
export interface CreateTimeEntryCommand {
    tenantId: string;
    employeeId: string;
    date: string;
    start: string;
    end: string;
    breakMinutes?: number;
    projectId?: string;
    costCenter?: string;
    source?: 'Manual' | 'Terminal' | 'Mobile';
    createdBy?: string;
}
export interface UpdateTimeEntryCommand {
    tenantId: string;
    timeEntryId: string;
    updates: {
        start?: string;
        end?: string;
        breakMinutes?: number;
        projectId?: string;
        costCenter?: string;
    };
    updatedBy?: string;
}
export interface ApproveTimeEntryCommand {
    tenantId: string;
    timeEntryId: string;
    approvedBy: string;
}
export interface RejectTimeEntryCommand {
    tenantId: string;
    timeEntryId: string;
    rejectedBy: string;
    reason?: string;
}
export interface TimeEntrySummary {
    totalHours: number;
    regularHours: number;
    overtimeHours: number;
    totalEntries: number;
    approvedEntries: number;
    pendingEntries: number;
}
export declare class TimeEntryService {
    private readonly timeEntryRepository;
    private readonly employeeRepository;
    private readonly eventPublisher;
    private readonly logger;
    constructor(timeEntryRepository: TimeEntryRepository, employeeRepository: EmployeeRepository, eventPublisher: DomainEventPublisher);
    createTimeEntry(command: CreateTimeEntryCommand): Promise<TimeEntry>;
    updateTimeEntry(command: UpdateTimeEntryCommand): Promise<TimeEntry>;
    approveTimeEntry(command: ApproveTimeEntryCommand): Promise<TimeEntry>;
    rejectTimeEntry(command: RejectTimeEntryCommand): Promise<TimeEntry>;
    getTimeEntry(tenantId: string, timeEntryId: string): Promise<TimeEntry>;
    listTimeEntries(tenantId: string, filters?: TimeEntryFilters, pagination?: PaginationOptions): Promise<TimeEntry[] | PaginatedResult<TimeEntry>>;
    getEmployeeTimeEntries(tenantId: string, employeeId: string, fromDate?: string, toDate?: string): Promise<TimeEntry[]>;
    getPendingApprovals(tenantId: string): Promise<TimeEntry[]>;
    getEmployeeTimeSummary(tenantId: string, employeeId: string, fromDate: string, toDate: string): Promise<TimeEntrySummary>;
    getMonthlySummary(tenantId: string, employeeId: string, year: number, month: number): Promise<MonthlySummary>;
    getYearlySummary(tenantId: string, employeeId: string, year: number): Promise<YearlySummary>;
}
export {};
//# sourceMappingURL=time-entry-service.d.ts.map