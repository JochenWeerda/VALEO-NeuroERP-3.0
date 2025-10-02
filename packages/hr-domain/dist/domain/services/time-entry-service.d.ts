/**
 * Time Entry Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for time tracking and approval
 */
import { TimeEntry } from '../entities/time-entry';
import { TimeEntryRepository } from '../repositories/time-entry-repository';
import { EmployeeRepository } from '../repositories/employee-repository';
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
export declare class TimeEntryService {
    private timeEntryRepository;
    private employeeRepository;
    private eventPublisher;
    constructor(timeEntryRepository: TimeEntryRepository, employeeRepository: EmployeeRepository, eventPublisher: (event: any) => Promise<void>);
    createTimeEntry(command: CreateTimeEntryCommand): Promise<TimeEntry>;
    updateTimeEntry(command: UpdateTimeEntryCommand): Promise<TimeEntry>;
    approveTimeEntry(command: ApproveTimeEntryCommand): Promise<TimeEntry>;
    rejectTimeEntry(command: RejectTimeEntryCommand): Promise<TimeEntry>;
    getTimeEntry(tenantId: string, timeEntryId: string): Promise<TimeEntry>;
    listTimeEntries(tenantId: string, filters?: any, pagination?: any): Promise<any>;
    getEmployeeTimeEntries(tenantId: string, employeeId: string, fromDate?: string, toDate?: string): Promise<TimeEntry[]>;
    getPendingApprovals(tenantId: string): Promise<TimeEntry[]>;
    getEmployeeTimeSummary(tenantId: string, employeeId: string, fromDate: string, toDate: string): Promise<any>;
    getMonthlySummary(tenantId: string, employeeId: string, year: number, month: number): Promise<any>;
    getYearlySummary(tenantId: string, employeeId: string, year: number): Promise<any>;
}
//# sourceMappingURL=time-entry-service.d.ts.map