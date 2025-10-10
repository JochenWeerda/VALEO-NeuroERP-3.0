"use strict";
/**
 * Time Entry Service for VALEO NeuroERP 3.0 HR Domain
 * Business logic for time tracking and approval
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TimeEntryService = void 0;
const pino_1 = __importDefault(require("pino"));
const time_entry_1 = require("../entities/time-entry");
const events_1 = require("../events");
const timeEntryServiceLogger = (0, pino_1.default)({ name: 'time-entry-service' });
class TimeEntryService {
    timeEntryRepository;
    employeeRepository;
    eventPublisher;
    logger = timeEntryServiceLogger;
    constructor(timeEntryRepository, employeeRepository, eventPublisher) {
        this.timeEntryRepository = timeEntryRepository;
        this.employeeRepository = employeeRepository;
        this.eventPublisher = eventPublisher;
    }
    async createTimeEntry(command) {
        const employee = await this.employeeRepository.findById(command.tenantId, command.employeeId);
        if (!employee) {
            throw new Error(`Employee with ID ${command.employeeId} not found`);
        }
        const overlappingEntries = await this.timeEntryRepository.findOverlappingEntries(command.tenantId, command.employeeId, command.start, command.end);
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
            status: 'Draft',
            createdBy: command.createdBy,
            updatedBy: command.createdBy
        };
        const timeEntry = time_entry_1.TimeEntryEntity.create(timeEntryData);
        const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, timeEntry.toJSON());
        await this.eventPublisher((0, events_1.createTimeEntryCreatedEvent)({
            timeEntryId: savedTimeEntry.id,
            employeeId: savedTimeEntry.employeeId,
            date: savedTimeEntry.date,
            start: savedTimeEntry.start,
            end: savedTimeEntry.end,
            workingMinutes: timeEntry.getWorkingMinutes(),
            source: savedTimeEntry.source
        }, command.tenantId));
        return savedTimeEntry;
    }
    async updateTimeEntry(command) {
        const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);
        if (!existingTimeEntry) {
            throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
        }
        const timeEntry = time_entry_1.TimeEntryEntity.fromJSON(existingTimeEntry);
        if (!timeEntry.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        const hasUpdatedStart = command.updates.start !== undefined;
        const hasUpdatedEnd = command.updates.end !== undefined;
        if (hasUpdatedStart || hasUpdatedEnd) {
            const start = command.updates.start ?? timeEntry.start;
            const end = command.updates.end ?? timeEntry.end;
            const overlappingEntries = await this.timeEntryRepository.findOverlappingEntries(command.tenantId, timeEntry.employeeId, start, end, command.timeEntryId);
            if (overlappingEntries.length > 0) {
                throw new Error('Updated time entry would overlap with existing entries');
            }
        }
        let updatedTimeEntry = timeEntry;
        const shouldUpdateTimes = hasUpdatedStart || hasUpdatedEnd || command.updates.breakMinutes !== undefined;
        if (shouldUpdateTimes) {
            updatedTimeEntry = updatedTimeEntry.updateTimes(command.updates.start ?? timeEntry.start, command.updates.end ?? timeEntry.end, command.updates.breakMinutes ?? timeEntry.breakMinutes, command.updatedBy);
        }
        if (command.updates.projectId !== undefined) {
            updatedTimeEntry = updatedTimeEntry.updateProject(command.updates.projectId, command.updatedBy);
        }
        if (command.updates.costCenter !== undefined) {
            updatedTimeEntry = updatedTimeEntry.updateCostCenter(command.updates.costCenter, command.updatedBy);
        }
        return this.timeEntryRepository.save(command.tenantId, updatedTimeEntry.toJSON());
    }
    async approveTimeEntry(command) {
        const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);
        if (!existingTimeEntry) {
            throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
        }
        const timeEntry = time_entry_1.TimeEntryEntity.fromJSON(existingTimeEntry);
        const approvedTimeEntry = timeEntry.approve(command.approvedBy);
        const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, approvedTimeEntry.toJSON());
        const { approvedBy } = savedTimeEntry;
        if (typeof approvedBy !== 'string' || approvedBy.length === 0) {
            this.logger.error({ timeEntryId: savedTimeEntry.id }, 'Approved time entry missing approver');
            throw new Error('Approved time entry missing approver');
        }
        await this.eventPublisher((0, events_1.createTimeEntryApprovedEvent)({
            timeEntryId: savedTimeEntry.id,
            employeeId: savedTimeEntry.employeeId,
            approvedBy,
            date: savedTimeEntry.date,
            workingMinutes: approvedTimeEntry.getWorkingMinutes()
        }, command.tenantId));
        return savedTimeEntry;
    }
    async rejectTimeEntry(command) {
        const existingTimeEntry = await this.timeEntryRepository.findById(command.tenantId, command.timeEntryId);
        if (!existingTimeEntry) {
            throw new Error(`Time entry with ID ${command.timeEntryId} not found`);
        }
        const timeEntry = time_entry_1.TimeEntryEntity.fromJSON(existingTimeEntry);
        const rejectedTimeEntry = timeEntry.reject(command.rejectedBy);
        const savedTimeEntry = await this.timeEntryRepository.save(command.tenantId, rejectedTimeEntry.toJSON());
        const { approvedBy } = savedTimeEntry;
        if (typeof approvedBy !== 'string' || approvedBy.length === 0) {
            this.logger.error({ timeEntryId: savedTimeEntry.id }, 'Rejected time entry missing reviewer');
            throw new Error('Rejected time entry missing reviewer');
        }
        await this.eventPublisher((0, events_1.createTimeEntryRejectedEvent)({
            timeEntryId: savedTimeEntry.id,
            employeeId: savedTimeEntry.employeeId,
            rejectedBy: approvedBy,
            reason: command.reason
        }, command.tenantId));
        return savedTimeEntry;
    }
    async getTimeEntry(tenantId, timeEntryId) {
        const timeEntry = await this.timeEntryRepository.findById(tenantId, timeEntryId);
        if (!timeEntry) {
            throw new Error(`Time entry with ID ${timeEntryId} not found`);
        }
        return timeEntry;
    }
    async listTimeEntries(tenantId, filters, pagination) {
        if (pagination !== undefined) {
            return this.timeEntryRepository.findWithPagination(tenantId, pagination);
        }
        return this.timeEntryRepository.findAll(tenantId, filters);
    }
    async getEmployeeTimeEntries(tenantId, employeeId, fromDate, toDate) {
        if (fromDate !== undefined && toDate !== undefined) {
            return this.timeEntryRepository.findByEmployeeAndDateRange(tenantId, employeeId, fromDate, toDate);
        }
        return this.timeEntryRepository.findByEmployee(tenantId, employeeId);
    }
    async getPendingApprovals(tenantId) {
        return this.timeEntryRepository.findPendingApprovals(tenantId);
    }
    async getEmployeeTimeSummary(tenantId, employeeId, fromDate, toDate) {
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
    async getMonthlySummary(tenantId, employeeId, year, month) {
        return this.timeEntryRepository.getMonthlySummary(tenantId, employeeId, year, month);
    }
    async getYearlySummary(tenantId, employeeId, year) {
        return this.timeEntryRepository.getYearlySummary(tenantId, employeeId, year);
    }
}
exports.TimeEntryService = TimeEntryService;
//# sourceMappingURL=time-entry-service.js.map