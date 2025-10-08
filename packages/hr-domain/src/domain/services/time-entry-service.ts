/**
 * Time Entry Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for time tracking and approval
 */

import pino from 'pino';
import { TimeEntry, TimeEntryEntity } from '../entities/time-entry';
import {
  MonthlySummary,
  PaginatedResult,
  PaginationOptions,
  TimeEntryFilters,
  TimeEntryRepository,
  YearlySummary
} from '../repositories/time-entry-repository';
import { EmployeeRepository } from '../repositories/employee-repository';
import {
  type HREvent,
  createTimeEntryApprovedEvent,
  createTimeEntryCreatedEvent,
  createTimeEntryRejectedEvent
} from '../events';

const timeEntryServiceLogger = pino({ name: 'time-entry-service' });

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

export class TimeEntryService {
  private readonly logger = timeEntryServiceLogger;

  constructor(
    private readonly timeEntryRepository: TimeEntryRepository,
    private readonly employeeRepository: EmployeeRepository,
    private readonly eventPublisher: DomainEventPublisher
  ) {}

  async createTimeEntry(command: CreateTimeEntryCommand): Promise<TimeEntry> {
    const employee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
    if (!employee) {
      throw new Error(`Employee with ID ${command.employeeId} not found`);
    }

    const overlappingEntries = await this.timeEntryRepository.findOverlappingEntries(
      command.tenantId,
      command.employeeId,
      command.start,
      command.end
    );

    if (overlappingEntries.length > 0) {
      throw new Error('Time entry overlaps with existing entries');
    }

    const timeEntryData = {
      tenantId: command.tenantId,
      employeeId: command.employeeId,
      date: command.date,
      start: command.start,
      end: command.end,
      breakMinutes: command.breakMinutes ?? 0,
      projectId: command.projectId,
      costCenter: command.costCenter,
      source: command.source ?? 'Manual',
      status: 'Draft' as const,
      createdBy: command.createdBy,
      updatedBy: command.createdBy
    };

    const timeEntry = TimeEntryEntity.create(timeEntryData);
    const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, timeEntry.toJSON());

    await this.eventPublisher(createTimeEntryCreatedEvent(
      {
        timeEntryId: savedTimeEntry.id,
        employeeId: savedTimeEntry.employeeId,
        date: savedTimeEntry.date,
        start: savedTimeEntry.start,
        end: savedTimeEntry.end,
        workingMinutes: timeEntry.getWorkingMinutes(),
        source: savedTimeEntry.source
      },
      command.tenantId
    ));

    return savedTimeEntry;
  }

  async updateTimeEntry(command: UpdateTimeEntryCommand): Promise<TimeEntry> {
    const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);

    if (!existingTimeEntry) {
      throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
    }

    const timeEntry = TimeEntryEntity.fromJSON(existingTimeEntry);

    if (!timeEntry.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    const hasUpdatedStart = command.updates.start !== undefined;
    const hasUpdatedEnd = command.updates.end !== undefined;

    if (hasUpdatedStart || hasUpdatedEnd) {
      const start = command.updates.start ?? timeEntry.start;
      const end = command.updates.end ?? timeEntry.end;

      const overlappingEntries = await this.timeEntryRepository.findOverlappingEntries(
        command.tenantId,
        timeEntry.employeeId,
        start,
        end,
        command.timeEntryId
      );

      if (overlappingEntries.length > 0) {
        throw new Error('Updated time entry would overlap with existing entries');
      }
    }

    let updatedTimeEntry = timeEntry;

    const shouldUpdateTimes =
      hasUpdatedStart || hasUpdatedEnd || command.updates.breakMinutes !== undefined;

    if (shouldUpdateTimes) {
      updatedTimeEntry = updatedTimeEntry.updateTimes(
        command.updates.start ?? timeEntry.start,
        command.updates.end ?? timeEntry.end,
        command.updates.breakMinutes ?? timeEntry.breakMinutes,
        command.updatedBy
      );
    }

    if (command.updates.projectId !== undefined) {
      updatedTimeEntry = updatedTimeEntry.updateProject(command.updates.projectId, command.updatedBy);
    }

    if (command.updates.costCenter !== undefined) {
      updatedTimeEntry = updatedTimeEntry.updateCostCenter(command.updates.costCenter, command.updatedBy);
    }

    return this.timeEntryRepository.save(command.tenantId, updatedTimeEntry.toJSON());
  }

  async approveTimeEntry(command: ApproveTimeEntryCommand): Promise<TimeEntry> {
    const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);

    if (!existingTimeEntry) {
      throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
    }

    const timeEntry = TimeEntryEntity.fromJSON(existingTimeEntry);
    const approvedTimeEntry = timeEntry.approve(command.approvedBy);
    const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, approvedTimeEntry.toJSON());

    const { approvedBy } = savedTimeEntry;
    if (typeof approvedBy !== 'string' || approvedBy.length === 0) {
      this.logger.error({ timeEntryId: savedTimeEntry.id }, 'Approved time entry missing approver');
      throw new Error('Approved time entry missing approver');
    }

    await this.eventPublisher(createTimeEntryApprovedEvent(
      {
        timeEntryId: savedTimeEntry.id,
        employeeId: savedTimeEntry.employeeId,
        approvedBy,
        date: savedTimeEntry.date,
        workingMinutes: approvedTimeEntry.getWorkingMinutes()
      },
      command.tenantId
    ));

    return savedTimeEntry;
  }

  async rejectTimeEntry(command: RejectTimeEntryCommand): Promise<TimeEntry> {
    const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);

    if (!existingTimeEntry) {
      throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
    }

    const timeEntry = TimeEntryEntity.fromJSON(existingTimeEntry);
    const rejectedTimeEntry = timeEntry.reject(command.rejectedBy);
    const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, rejectedTimeEntry.toJSON());

    const { approvedBy } = savedTimeEntry;
    if (typeof approvedBy !== 'string' || approvedBy.length === 0) {
      this.logger.error({ timeEntryId: savedTimeEntry.id }, 'Rejected time entry missing reviewer');
      throw new Error('Rejected time entry missing reviewer');
    }

    await this.eventPublisher(createTimeEntryRejectedEvent(
      {
        timeEntryId: savedTimeEntry.id,
        employeeId: savedTimeEntry.employeeId,
        rejectedBy: approvedBy,
        reason: command.reason
      },
      command.tenantId
    ));

    return savedTimeEntry;
  }

  async getTimeEntry(tenantId: string, timeEntryId: string): Promise<TimeEntry> {
    const timeEntry = await this.timeEntryRepository.findById(tenantId, timeEntryId);

    if (!timeEntry) {
      throw new Error(`Time entry with ID ${timeEntryId} not found`);
    }

    return timeEntry;
  }

  async listTimeEntries(
    tenantId: string,
    filters?: TimeEntryFilters,
    pagination?: PaginationOptions
  ): Promise<TimeEntry[] | PaginatedResult<TimeEntry>> {
    if (pagination !== undefined) {
      return this.timeEntryRepository.findWithPagination(tenantId, pagination);
    }

    return this.timeEntryRepository.findAll(tenantId, filters);
  }

  async getEmployeeTimeEntries(
    tenantId: string,
    employeeId: string,
    fromDate?: string,
    toDate?: string
  ): Promise<TimeEntry[]> {
    if (fromDate !== undefined && toDate !== undefined) {
      return this.timeEntryRepository.findByEmployeeAndDateRange(tenantId, employeeId, fromDate, toDate);
    }

    return this.timeEntryRepository.findByEmployee(tenantId, employeeId);
  }

  async getPendingApprovals(tenantId: string): Promise<TimeEntry[]> {
    return this.timeEntryRepository.findPendingApprovals(tenantId);
  }

  async getEmployeeTimeSummary(
    tenantId: string,
    employeeId: string,
    fromDate: string,
    toDate: string
  ): Promise<TimeEntrySummary> {
    const totalHours = await this.timeEntryRepository.getEmployeeTotalHours(tenantId, employeeId, fromDate, toDate);
    const overtimeHours = await this.timeEntryRepository.getOvertimeHours(tenantId, employeeId, fromDate, toDate);
    const entries = await this.timeEntryRepository.findByEmployeeAndDateRange(tenantId, employeeId, fromDate, toDate);

    return {
      totalHours,
      regularHours: totalHours - overtimeHours,
      overtimeHours,
      totalEntries: entries.length,
      approvedEntries: entries.filter(entry => entry.status === 'Approved').length,
      pendingEntries: entries.filter(entry => entry.status === 'Draft').length
    };
  }

  async getMonthlySummary(
    tenantId: string,
    employeeId: string,
    year: number,
    month: number
  ): Promise<MonthlySummary> {
    return this.timeEntryRepository.getMonthlySummary(tenantId, employeeId, year, month);
  }

  async getYearlySummary(tenantId: string, employeeId: string, year: number): Promise<YearlySummary> {
    return this.timeEntryRepository.getYearlySummary(tenantId, employeeId, year);
  }
}
