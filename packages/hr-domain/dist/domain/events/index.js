"use strict";
/**
 * Domain Events for VALEO NeuroERP 3.0 HR Domain
 * Event-driven architecture for HR operations
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PayrollExportedEventSchema = exports.PayrollLockedEventSchema = exports.PayrollPreparedEventSchema = exports.ShiftUnassignedEventSchema = exports.ShiftAssignedEventSchema = exports.ShiftCreatedEventSchema = exports.LeaveRejectedEventSchema = exports.LeaveApprovedEventSchema = exports.LeaveRequestedEventSchema = exports.TimeEntryRejectedEventSchema = exports.TimeEntryApprovedEventSchema = exports.TimeEntryCreatedEventSchema = exports.RoleDeletedEventSchema = exports.RoleUpdatedEventSchema = exports.RoleCreatedEventSchema = exports.EmployeeReactivatedEventSchema = exports.EmployeeDeactivatedEventSchema = exports.EmployeeUpdatedEventSchema = exports.EmployeeCreatedEventSchema = exports.BaseEventSchema = void 0;
exports.createEmployeeCreatedEvent = createEmployeeCreatedEvent;
exports.createEmployeeUpdatedEvent = createEmployeeUpdatedEvent;
exports.createEmployeeDeactivatedEvent = createEmployeeDeactivatedEvent;
exports.createTimeEntryCreatedEvent = createTimeEntryCreatedEvent;
exports.createTimeEntryApprovedEvent = createTimeEntryApprovedEvent;
exports.createTimeEntryRejectedEvent = createTimeEntryRejectedEvent;
exports.createPayrollExportedEvent = createPayrollExportedEvent;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
// Base Event Schema
exports.BaseEventSchema = zod_1.z.object({
    eventId: zod_1.z.string().uuid(),
    eventType: zod_1.z.string(),
    eventVersion: zod_1.z.number().int().min(1),
    occurredAt: zod_1.z.string().datetime(),
    tenantId: zod_1.z.string().uuid(),
    correlationId: zod_1.z.string().uuid().optional(),
    causationId: zod_1.z.string().uuid().optional()
});
// Employee Events
exports.EmployeeCreatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.employee.created'),
    payload: zod_1.z.object({
        employeeId: zod_1.z.string().uuid(),
        employeeNumber: zod_1.z.string(),
        firstName: zod_1.z.string(),
        lastName: zod_1.z.string(),
        hireDate: zod_1.z.string().datetime(),
        departmentId: zod_1.z.string().optional(),
        position: zod_1.z.string().optional()
    })
});
exports.EmployeeUpdatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.employee.updated'),
    payload: zod_1.z.object({
        employeeId: zod_1.z.string().uuid(),
        changes: zod_1.z.record(zod_1.z.any()),
        previousVersion: zod_1.z.number().int()
    })
});
exports.EmployeeDeactivatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.employee.deactivated'),
    payload: zod_1.z.object({
        employeeId: zod_1.z.string().uuid(),
        reason: zod_1.z.string().optional(),
        terminationDate: zod_1.z.string().datetime().optional()
    })
});
exports.EmployeeReactivatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.employee.reactivated'),
    payload: zod_1.z.object({
        employeeId: zod_1.z.string().uuid(),
        reactivationDate: zod_1.z.string().datetime()
    })
});
// Role Events
exports.RoleCreatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.role.created'),
    payload: zod_1.z.object({
        roleId: zod_1.z.string().uuid(),
        key: zod_1.z.string(),
        name: zod_1.z.string(),
        permissions: zod_1.z.array(zod_1.z.string())
    })
});
exports.RoleUpdatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.role.updated'),
    payload: zod_1.z.object({
        roleId: zod_1.z.string().uuid(),
        changes: zod_1.z.record(zod_1.z.any())
    })
});
exports.RoleDeletedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.role.deleted'),
    payload: zod_1.z.object({
        roleId: zod_1.z.string().uuid(),
        key: zod_1.z.string()
    })
});
// Time Entry Events
exports.TimeEntryCreatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.time_entry.created'),
    payload: zod_1.z.object({
        timeEntryId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        date: zod_1.z.string().date(),
        start: zod_1.z.string().datetime(),
        end: zod_1.z.string().datetime(),
        workingMinutes: zod_1.z.number().int(),
        source: zod_1.z.string()
    })
});
exports.TimeEntryApprovedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.time_entry.approved'),
    payload: zod_1.z.object({
        timeEntryId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        approvedBy: zod_1.z.string().uuid(),
        date: zod_1.z.string().date(),
        workingMinutes: zod_1.z.number().int()
    })
});
exports.TimeEntryRejectedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.time_entry.rejected'),
    payload: zod_1.z.object({
        timeEntryId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        rejectedBy: zod_1.z.string().uuid(),
        reason: zod_1.z.string().optional()
    })
});
// Leave Request Events
exports.LeaveRequestedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.leave.requested'),
    payload: zod_1.z.object({
        leaveRequestId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        type: zod_1.z.string(),
        from: zod_1.z.string().date(),
        to: zod_1.z.string().date(),
        days: zod_1.z.number().positive()
    })
});
exports.LeaveApprovedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.leave.approved'),
    payload: zod_1.z.object({
        leaveRequestId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        approvedBy: zod_1.z.string().uuid(),
        type: zod_1.z.string(),
        from: zod_1.z.string().date(),
        to: zod_1.z.string().date(),
        days: zod_1.z.number().positive()
    })
});
exports.LeaveRejectedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.leave.rejected'),
    payload: zod_1.z.object({
        leaveRequestId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        rejectedBy: zod_1.z.string().uuid(),
        reason: zod_1.z.string().optional()
    })
});
// Shift Events
exports.ShiftCreatedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.shift.created'),
    payload: zod_1.z.object({
        shiftId: zod_1.z.string().uuid(),
        name: zod_1.z.string(),
        startsAt: zod_1.z.string().datetime(),
        endsAt: zod_1.z.string().datetime(),
        requiredHeadcount: zod_1.z.number().int()
    })
});
exports.ShiftAssignedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.shift.assigned'),
    payload: zod_1.z.object({
        shiftId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        assignedBy: zod_1.z.string().uuid()
    })
});
exports.ShiftUnassignedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.shift.unassigned'),
    payload: zod_1.z.object({
        shiftId: zod_1.z.string().uuid(),
        employeeId: zod_1.z.string().uuid(),
        unassignedBy: zod_1.z.string().uuid()
    })
});
// Payroll Events
exports.PayrollPreparedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.payroll.prepared'),
    payload: zod_1.z.object({
        payrollRunId: zod_1.z.string().uuid(),
        period: zod_1.z.object({
            from: zod_1.z.string().date(),
            to: zod_1.z.string().date()
        }),
        employeeCount: zod_1.z.number().int(),
        totalHours: zod_1.z.number().positive()
    })
});
exports.PayrollLockedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.payroll.locked'),
    payload: zod_1.z.object({
        payrollRunId: zod_1.z.string().uuid(),
        period: zod_1.z.object({
            from: zod_1.z.string().date(),
            to: zod_1.z.string().date()
        }),
        lockedBy: zod_1.z.string().uuid(),
        employeeCount: zod_1.z.number().int(),
        totalHours: zod_1.z.number().positive()
    })
});
exports.PayrollExportedEventSchema = exports.BaseEventSchema.extend({
    eventType: zod_1.z.literal('hr.payroll.exported'),
    payload: zod_1.z.object({
        payrollRunId: zod_1.z.string().uuid(),
        period: zod_1.z.object({
            from: zod_1.z.string().date(),
            to: zod_1.z.string().date()
        }),
        exportedBy: zod_1.z.string().uuid(),
        exportFormat: zod_1.z.string(),
        exportLocation: zod_1.z.string(),
        employeeCount: zod_1.z.number().int(),
        totalHours: zod_1.z.number().positive(),
        totalGrossAmount: zod_1.z.number().min(0),
        items: zod_1.z.array(zod_1.z.object({
            employeeId: zod_1.z.string().uuid(),
            hours: zod_1.z.number().positive(),
            grossAmount: zod_1.z.number().min(0).optional()
        }))
    })
});
// Event factory functions
function createEmployeeCreatedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.employee.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createEmployeeUpdatedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.employee.updated',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createEmployeeDeactivatedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.employee.deactivated',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createTimeEntryCreatedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.time_entry.created',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createTimeEntryApprovedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.time_entry.approved',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createTimeEntryRejectedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.time_entry.rejected',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
function createPayrollExportedEvent(data, tenantId) {
    return {
        eventId: (0, uuid_1.v4)(),
        eventType: 'hr.payroll.exported',
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId,
        payload: data
    };
}
//# sourceMappingURL=index.js.map