/**
 * Domain Events for VALEO NeuroERP 3.0 HR Domain
 * Event-driven architecture for HR operations
 */
import { z } from 'zod';
export declare const BaseEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventType: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: string;
    eventVersion: number;
    occurredAt: string;
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: string;
    eventVersion: number;
    occurredAt: string;
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export type BaseEvent = z.infer<typeof BaseEventSchema>;
export declare const EmployeeCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.employee.created">;
    payload: z.ZodObject<{
        employeeId: z.ZodString;
        employeeNumber: z.ZodString;
        firstName: z.ZodString;
        lastName: z.ZodString;
        hireDate: z.ZodString;
        departmentId: z.ZodOptional<z.ZodString>;
        position: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        firstName: string;
        lastName: string;
        hireDate: string;
        employeeNumber: string;
        employeeId: string;
        departmentId?: string | undefined;
        position?: string | undefined;
    }, {
        firstName: string;
        lastName: string;
        hireDate: string;
        employeeNumber: string;
        employeeId: string;
        departmentId?: string | undefined;
        position?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        firstName: string;
        lastName: string;
        hireDate: string;
        employeeNumber: string;
        employeeId: string;
        departmentId?: string | undefined;
        position?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        firstName: string;
        lastName: string;
        hireDate: string;
        employeeNumber: string;
        employeeId: string;
        departmentId?: string | undefined;
        position?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const EmployeeUpdatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.employee.updated">;
    payload: z.ZodObject<{
        employeeId: z.ZodString;
        changes: z.ZodRecord<z.ZodString, z.ZodAny>;
        previousVersion: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        changes: Record<string, any>;
        previousVersion: number;
    }, {
        employeeId: string;
        changes: Record<string, any>;
        previousVersion: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        changes: Record<string, any>;
        previousVersion: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        changes: Record<string, any>;
        previousVersion: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const EmployeeDeactivatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.employee.deactivated">;
    payload: z.ZodObject<{
        employeeId: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
        terminationDate: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        terminationDate?: string | undefined;
        reason?: string | undefined;
    }, {
        employeeId: string;
        terminationDate?: string | undefined;
        reason?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.deactivated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        terminationDate?: string | undefined;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.deactivated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        terminationDate?: string | undefined;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const EmployeeReactivatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.employee.reactivated">;
    payload: z.ZodObject<{
        employeeId: z.ZodString;
        reactivationDate: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        reactivationDate: string;
    }, {
        employeeId: string;
        reactivationDate: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.reactivated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        reactivationDate: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.employee.reactivated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        reactivationDate: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RoleCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.role.created">;
    payload: z.ZodObject<{
        roleId: z.ZodString;
        key: z.ZodString;
        name: z.ZodString;
        permissions: z.ZodArray<z.ZodString, "many">;
    }, "strip", z.ZodTypeAny, {
        roleId: string;
        key: string;
        name: string;
        permissions: string[];
    }, {
        roleId: string;
        key: string;
        name: string;
        permissions: string[];
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        roleId: string;
        key: string;
        name: string;
        permissions: string[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        roleId: string;
        key: string;
        name: string;
        permissions: string[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RoleUpdatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.role.updated">;
    payload: z.ZodObject<{
        roleId: z.ZodString;
        changes: z.ZodRecord<z.ZodString, z.ZodAny>;
    }, "strip", z.ZodTypeAny, {
        changes: Record<string, any>;
        roleId: string;
    }, {
        changes: Record<string, any>;
        roleId: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        changes: Record<string, any>;
        roleId: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.updated";
    eventVersion: number;
    occurredAt: string;
    payload: {
        changes: Record<string, any>;
        roleId: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const RoleDeletedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.role.deleted">;
    payload: z.ZodObject<{
        roleId: z.ZodString;
        key: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        roleId: string;
        key: string;
    }, {
        roleId: string;
        key: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.deleted";
    eventVersion: number;
    occurredAt: string;
    payload: {
        roleId: string;
        key: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.role.deleted";
    eventVersion: number;
    occurredAt: string;
    payload: {
        roleId: string;
        key: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const TimeEntryCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.time_entry.created">;
    payload: z.ZodObject<{
        timeEntryId: z.ZodString;
        employeeId: z.ZodString;
        date: z.ZodString;
        start: z.ZodString;
        end: z.ZodString;
        workingMinutes: z.ZodNumber;
        source: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        date: string;
        employeeId: string;
        timeEntryId: string;
        start: string;
        end: string;
        workingMinutes: number;
        source: string;
    }, {
        date: string;
        employeeId: string;
        timeEntryId: string;
        start: string;
        end: string;
        workingMinutes: number;
        source: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        date: string;
        employeeId: string;
        timeEntryId: string;
        start: string;
        end: string;
        workingMinutes: number;
        source: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        date: string;
        employeeId: string;
        timeEntryId: string;
        start: string;
        end: string;
        workingMinutes: number;
        source: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const TimeEntryApprovedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.time_entry.approved">;
    payload: z.ZodObject<{
        timeEntryId: z.ZodString;
        employeeId: z.ZodString;
        approvedBy: z.ZodString;
        date: z.ZodString;
        workingMinutes: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        date: string;
        employeeId: string;
        timeEntryId: string;
        workingMinutes: number;
        approvedBy: string;
    }, {
        date: string;
        employeeId: string;
        timeEntryId: string;
        workingMinutes: number;
        approvedBy: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.approved";
    eventVersion: number;
    occurredAt: string;
    payload: {
        date: string;
        employeeId: string;
        timeEntryId: string;
        workingMinutes: number;
        approvedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.approved";
    eventVersion: number;
    occurredAt: string;
    payload: {
        date: string;
        employeeId: string;
        timeEntryId: string;
        workingMinutes: number;
        approvedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const TimeEntryRejectedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.time_entry.rejected">;
    payload: z.ZodObject<{
        timeEntryId: z.ZodString;
        employeeId: z.ZodString;
        rejectedBy: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        timeEntryId: string;
        rejectedBy: string;
        reason?: string | undefined;
    }, {
        employeeId: string;
        timeEntryId: string;
        rejectedBy: string;
        reason?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        timeEntryId: string;
        rejectedBy: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.time_entry.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        timeEntryId: string;
        rejectedBy: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const LeaveRequestedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.leave.requested">;
    payload: z.ZodObject<{
        leaveRequestId: z.ZodString;
        employeeId: z.ZodString;
        type: z.ZodString;
        from: z.ZodString;
        to: z.ZodString;
        days: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        type: string;
        employeeId: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    }, {
        type: string;
        employeeId: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.requested";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: string;
        employeeId: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.requested";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: string;
        employeeId: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const LeaveApprovedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.leave.approved">;
    payload: z.ZodObject<{
        leaveRequestId: z.ZodString;
        employeeId: z.ZodString;
        approvedBy: z.ZodString;
        type: z.ZodString;
        from: z.ZodString;
        to: z.ZodString;
        days: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        type: string;
        employeeId: string;
        approvedBy: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    }, {
        type: string;
        employeeId: string;
        approvedBy: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.approved";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: string;
        employeeId: string;
        approvedBy: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.approved";
    eventVersion: number;
    occurredAt: string;
    payload: {
        type: string;
        employeeId: string;
        approvedBy: string;
        leaveRequestId: string;
        from: string;
        to: string;
        days: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const LeaveRejectedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.leave.rejected">;
    payload: z.ZodObject<{
        leaveRequestId: z.ZodString;
        employeeId: z.ZodString;
        rejectedBy: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        rejectedBy: string;
        leaveRequestId: string;
        reason?: string | undefined;
    }, {
        employeeId: string;
        rejectedBy: string;
        leaveRequestId: string;
        reason?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        rejectedBy: string;
        leaveRequestId: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.leave.rejected";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        rejectedBy: string;
        leaveRequestId: string;
        reason?: string | undefined;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const ShiftCreatedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.shift.created">;
    payload: z.ZodObject<{
        shiftId: z.ZodString;
        name: z.ZodString;
        startsAt: z.ZodString;
        endsAt: z.ZodString;
        requiredHeadcount: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        name: string;
        shiftId: string;
        startsAt: string;
        endsAt: string;
        requiredHeadcount: number;
    }, {
        name: string;
        shiftId: string;
        startsAt: string;
        endsAt: string;
        requiredHeadcount: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        name: string;
        shiftId: string;
        startsAt: string;
        endsAt: string;
        requiredHeadcount: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.created";
    eventVersion: number;
    occurredAt: string;
    payload: {
        name: string;
        shiftId: string;
        startsAt: string;
        endsAt: string;
        requiredHeadcount: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const ShiftAssignedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.shift.assigned">;
    payload: z.ZodObject<{
        shiftId: z.ZodString;
        employeeId: z.ZodString;
        assignedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        shiftId: string;
        assignedBy: string;
    }, {
        employeeId: string;
        shiftId: string;
        assignedBy: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.assigned";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        shiftId: string;
        assignedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.assigned";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        shiftId: string;
        assignedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const ShiftUnassignedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.shift.unassigned">;
    payload: z.ZodObject<{
        shiftId: z.ZodString;
        employeeId: z.ZodString;
        unassignedBy: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        shiftId: string;
        unassignedBy: string;
    }, {
        employeeId: string;
        shiftId: string;
        unassignedBy: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.unassigned";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        shiftId: string;
        unassignedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.shift.unassigned";
    eventVersion: number;
    occurredAt: string;
    payload: {
        employeeId: string;
        shiftId: string;
        unassignedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const PayrollPreparedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.payroll.prepared">;
    payload: z.ZodObject<{
        payrollRunId: z.ZodString;
        period: z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>;
        employeeCount: z.ZodNumber;
        totalHours: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
    }, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.prepared";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.prepared";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const PayrollLockedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.payroll.locked">;
    payload: z.ZodObject<{
        payrollRunId: z.ZodString;
        period: z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>;
        lockedBy: z.ZodString;
        employeeCount: z.ZodNumber;
        totalHours: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        lockedBy: string;
    }, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        lockedBy: string;
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.locked";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        lockedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.locked";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        lockedBy: string;
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
export declare const PayrollExportedEventSchema: z.ZodObject<{
    eventId: z.ZodString;
    eventVersion: z.ZodNumber;
    occurredAt: z.ZodString;
    tenantId: z.ZodString;
    correlationId: z.ZodOptional<z.ZodString>;
    causationId: z.ZodOptional<z.ZodString>;
} & {
    eventType: z.ZodLiteral<"hr.payroll.exported">;
    payload: z.ZodObject<{
        payrollRunId: z.ZodString;
        period: z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>;
        exportedBy: z.ZodString;
        exportFormat: z.ZodString;
        exportLocation: z.ZodString;
        employeeCount: z.ZodNumber;
        totalHours: z.ZodNumber;
        totalGrossAmount: z.ZodNumber;
        items: z.ZodArray<z.ZodObject<{
            employeeId: z.ZodString;
            hours: z.ZodNumber;
            grossAmount: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }, {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }>, "many">;
    }, "strip", z.ZodTypeAny, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        exportedBy: string;
        exportFormat: string;
        exportLocation: string;
        totalGrossAmount: number;
        items: {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }[];
    }, {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        exportedBy: string;
        exportFormat: string;
        exportLocation: string;
        totalGrossAmount: number;
        items: {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }[];
    }>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.exported";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        exportedBy: string;
        exportFormat: string;
        exportLocation: string;
        totalGrossAmount: number;
        items: {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}, {
    tenantId: string;
    eventId: string;
    eventType: "hr.payroll.exported";
    eventVersion: number;
    occurredAt: string;
    payload: {
        payrollRunId: string;
        period: {
            from: string;
            to: string;
        };
        employeeCount: number;
        totalHours: number;
        exportedBy: string;
        exportFormat: string;
        exportLocation: string;
        totalGrossAmount: number;
        items: {
            employeeId: string;
            hours: number;
            grossAmount?: number | undefined;
        }[];
    };
    correlationId?: string | undefined;
    causationId?: string | undefined;
}>;
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
export type HREvent = EmployeeCreatedEvent | EmployeeUpdatedEvent | EmployeeDeactivatedEvent | EmployeeReactivatedEvent | RoleCreatedEvent | RoleUpdatedEvent | RoleDeletedEvent | TimeEntryCreatedEvent | TimeEntryApprovedEvent | TimeEntryRejectedEvent | LeaveRequestedEvent | LeaveApprovedEvent | LeaveRejectedEvent | ShiftCreatedEvent | ShiftAssignedEvent | ShiftUnassignedEvent | PayrollPreparedEvent | PayrollLockedEvent | PayrollExportedEvent;
export declare function createEmployeeCreatedEvent(data: EmployeeCreatedEvent['payload'], tenantId: string): EmployeeCreatedEvent;
export declare function createEmployeeUpdatedEvent(data: EmployeeUpdatedEvent['payload'], tenantId: string): EmployeeUpdatedEvent;
export declare function createEmployeeDeactivatedEvent(data: EmployeeDeactivatedEvent['payload'], tenantId: string): EmployeeDeactivatedEvent;
export declare function createTimeEntryCreatedEvent(data: TimeEntryCreatedEvent['payload'], tenantId: string): TimeEntryCreatedEvent;
export declare function createTimeEntryApprovedEvent(data: TimeEntryApprovedEvent['payload'], tenantId: string): TimeEntryApprovedEvent;
export declare function createTimeEntryRejectedEvent(data: TimeEntryRejectedEvent['payload'], tenantId: string): TimeEntryRejectedEvent;
export declare function createPayrollExportedEvent(data: PayrollExportedEvent['payload'], tenantId: string): PayrollExportedEvent;
//# sourceMappingURL=index.d.ts.map