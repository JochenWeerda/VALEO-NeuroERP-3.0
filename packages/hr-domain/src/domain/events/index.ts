/**
 * Domain Events for VALEO NeuroERP 3.0 HR Domain
 * Event-driven architecture for HR operations
 */

import { z } from 'zod';

// Base Event Schema
export const BaseEventSchema = z.object({
  eventId: z.string().uuid(),
  eventType: z.string(),
  eventVersion: z.number().int().min(1),
  occurredAt: z.string().datetime(),
  tenantId: z.string().uuid(),
  correlationId: z.string().uuid().optional(),
  causationId: z.string().uuid().optional()
});

export type BaseEvent = z.infer<typeof BaseEventSchema>;

// Employee Events
export const EmployeeCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.employee.created'),
  payload: z.object({
    employeeId: z.string().uuid(),
    employeeNumber: z.string(),
    firstName: z.string(),
    lastName: z.string(),
    hireDate: z.string().datetime(),
    departmentId: z.string().optional(),
    position: z.string().optional()
  })
});

export const EmployeeUpdatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.employee.updated'),
  payload: z.object({
    employeeId: z.string().uuid(),
    changes: z.record(z.any()),
    previousVersion: z.number().int()
  })
});

export const EmployeeDeactivatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.employee.deactivated'),
  payload: z.object({
    employeeId: z.string().uuid(),
    reason: z.string().optional(),
    terminationDate: z.string().datetime().optional()
  })
});

export const EmployeeReactivatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.employee.reactivated'),
  payload: z.object({
    employeeId: z.string().uuid(),
    reactivationDate: z.string().datetime()
  })
});

// Role Events
export const RoleCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.role.created'),
  payload: z.object({
    roleId: z.string().uuid(),
    key: z.string(),
    name: z.string(),
    permissions: z.array(z.string())
  })
});

export const RoleUpdatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.role.updated'),
  payload: z.object({
    roleId: z.string().uuid(),
    changes: z.record(z.any())
  })
});

export const RoleDeletedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.role.deleted'),
  payload: z.object({
    roleId: z.string().uuid(),
    key: z.string()
  })
});

// Time Entry Events
export const TimeEntryCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.time_entry.created'),
  payload: z.object({
    timeEntryId: z.string().uuid(),
    employeeId: z.string().uuid(),
    date: z.string().date(),
    start: z.string().datetime(),
    end: z.string().datetime(),
    workingMinutes: z.number().int(),
    source: z.string()
  })
});

export const TimeEntryApprovedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.time_entry.approved'),
  payload: z.object({
    timeEntryId: z.string().uuid(),
    employeeId: z.string().uuid(),
    approvedBy: z.string().uuid(),
    date: z.string().date(),
    workingMinutes: z.number().int()
  })
});

export const TimeEntryRejectedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.time_entry.rejected'),
  payload: z.object({
    timeEntryId: z.string().uuid(),
    employeeId: z.string().uuid(),
    rejectedBy: z.string().uuid(),
    reason: z.string().optional()
  })
});

// Leave Request Events
export const LeaveRequestedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.leave.requested'),
  payload: z.object({
    leaveRequestId: z.string().uuid(),
    employeeId: z.string().uuid(),
    type: z.string(),
    from: z.string().date(),
    to: z.string().date(),
    days: z.number().positive()
  })
});

export const LeaveApprovedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.leave.approved'),
  payload: z.object({
    leaveRequestId: z.string().uuid(),
    employeeId: z.string().uuid(),
    approvedBy: z.string().uuid(),
    type: z.string(),
    from: z.string().date(),
    to: z.string().date(),
    days: z.number().positive()
  })
});

export const LeaveRejectedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.leave.rejected'),
  payload: z.object({
    leaveRequestId: z.string().uuid(),
    employeeId: z.string().uuid(),
    rejectedBy: z.string().uuid(),
    reason: z.string().optional()
  })
});

// Shift Events
export const ShiftCreatedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.shift.created'),
  payload: z.object({
    shiftId: z.string().uuid(),
    name: z.string(),
    startsAt: z.string().datetime(),
    endsAt: z.string().datetime(),
    requiredHeadcount: z.number().int()
  })
});

export const ShiftAssignedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.shift.assigned'),
  payload: z.object({
    shiftId: z.string().uuid(),
    employeeId: z.string().uuid(),
    assignedBy: z.string().uuid()
  })
});

export const ShiftUnassignedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.shift.unassigned'),
  payload: z.object({
    shiftId: z.string().uuid(),
    employeeId: z.string().uuid(),
    unassignedBy: z.string().uuid()
  })
});

// Payroll Events
export const PayrollPreparedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.payroll.prepared'),
  payload: z.object({
    payrollRunId: z.string().uuid(),
    period: z.object({
      from: z.string().date(),
      to: z.string().date()
    }),
    employeeCount: z.number().int(),
    totalHours: z.number().positive()
  })
});

export const PayrollLockedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.payroll.locked'),
  payload: z.object({
    payrollRunId: z.string().uuid(),
    period: z.object({
      from: z.string().date(),
      to: z.string().date()
    }),
    lockedBy: z.string().uuid(),
    employeeCount: z.number().int(),
    totalHours: z.number().positive()
  })
});

export const PayrollExportedEventSchema = BaseEventSchema.extend({
  eventType: z.literal('hr.payroll.exported'),
  payload: z.object({
    payrollRunId: z.string().uuid(),
    period: z.object({
      from: z.string().date(),
      to: z.string().date()
    }),
    exportedBy: z.string().uuid(),
    exportFormat: z.string(),
    exportLocation: z.string(),
    employeeCount: z.number().int(),
    totalHours: z.number().positive(),
    totalGrossAmount: z.number().min(0),
    items: z.array(z.object({
      employeeId: z.string().uuid(),
      hours: z.number().positive(),
      grossAmount: z.number().min(0).optional()
    }))
  })
});

// Type exports
export type EmployeeCreatedEvent = z.infer<typeof EmployeeCreatedEventSchema>;
export type EmployeeUpdatedEvent = z.infer<typeof EmployeeUpdatedEventSchema>;
export type EmployeeDeactivatedEvent = z.infer<typeof EmployeeDeactivatedEventSchema>;
export type EmployeeReactivatedEvent = z.infer<typeof EmployeeReactivatedEventSchema>;

export type RoleCreatedEvent = z.infer<typeof RoleCreatedEventSchema>;
export type RoleUpdatedEvent = z.infer<typeof RoleUpdatedEventSchema>;
export type RoleDeletedEvent = z.infer<typeof RoleDeletedEventSchema>;

export type TimeEntryCreatedEvent = z.infer<typeof TimeEntryCreatedEventSchema>;
export type TimeEntryApprovedEvent = z.infer<typeof TimeEntryApprovedEventSchema>;
export type TimeEntryRejectedEvent = z.infer<typeof TimeEntryRejectedEventSchema>;

export type LeaveRequestedEvent = z.infer<typeof LeaveRequestedEventSchema>;
export type LeaveApprovedEvent = z.infer<typeof LeaveApprovedEventSchema>;
export type LeaveRejectedEvent = z.infer<typeof LeaveRejectedEventSchema>;

export type ShiftCreatedEvent = z.infer<typeof ShiftCreatedEventSchema>;
export type ShiftAssignedEvent = z.infer<typeof ShiftAssignedEventSchema>;
export type ShiftUnassignedEvent = z.infer<typeof ShiftUnassignedEventSchema>;

export type PayrollPreparedEvent = z.infer<typeof PayrollPreparedEventSchema>;
export type PayrollLockedEvent = z.infer<typeof PayrollLockedEventSchema>;
export type PayrollExportedEvent = z.infer<typeof PayrollExportedEventSchema>;

// Union type for all HR events
export type HREvent = 
  | EmployeeCreatedEvent
  | EmployeeUpdatedEvent
  | EmployeeDeactivatedEvent
  | EmployeeReactivatedEvent
  | RoleCreatedEvent
  | RoleUpdatedEvent
  | RoleDeletedEvent
  | TimeEntryCreatedEvent
  | TimeEntryApprovedEvent
  | TimeEntryRejectedEvent
  | LeaveRequestedEvent
  | LeaveApprovedEvent
  | LeaveRejectedEvent
  | ShiftCreatedEvent
  | ShiftAssignedEvent
  | ShiftUnassignedEvent
  | PayrollPreparedEvent
  | PayrollLockedEvent
  | PayrollExportedEvent;

// Event factory functions
export function createEmployeeCreatedEvent(data: EmployeeCreatedEvent['payload'], tenantId: string): EmployeeCreatedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.employee.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createEmployeeUpdatedEvent(data: EmployeeUpdatedEvent['payload'], tenantId: string): EmployeeUpdatedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.employee.updated',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createEmployeeDeactivatedEvent(data: EmployeeDeactivatedEvent['payload'], tenantId: string): EmployeeDeactivatedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.employee.deactivated',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createTimeEntryCreatedEvent(data: TimeEntryCreatedEvent['payload'], tenantId: string): TimeEntryCreatedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.time_entry.created',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createTimeEntryApprovedEvent(data: TimeEntryApprovedEvent['payload'], tenantId: string): TimeEntryApprovedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.time_entry.approved',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createTimeEntryRejectedEvent(data: TimeEntryRejectedEvent['payload'], tenantId: string): TimeEntryRejectedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.time_entry.rejected',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}

export function createPayrollExportedEvent(data: PayrollExportedEvent['payload'], tenantId: string): PayrollExportedEvent {
  return {
    eventId: require('uuid').v4(),
    eventType: 'hr.payroll.exported',
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: data
  };
}
