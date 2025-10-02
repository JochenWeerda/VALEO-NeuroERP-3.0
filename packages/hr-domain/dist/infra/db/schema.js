"use strict";
/**
 * Database Schema for VALEO NeuroERP 3.0 HR Domain
 * PostgreSQL schema using Drizzle ORM
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.leaveRequestsRelations = exports.timeEntriesRelations = exports.employeesRelations = exports.domainEvents = exports.payrollRuns = exports.leaveRequests = exports.shifts = exports.timeEntries = exports.roles = exports.employees = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
const drizzle_orm_1 = require("drizzle-orm");
// Employees table
exports.employees = (0, pg_core_1.pgTable)('employees', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    employeeNumber: (0, pg_core_1.varchar)('employee_number', { length: 50 }).notNull(),
    // Person data
    firstName: (0, pg_core_1.varchar)('first_name', { length: 100 }).notNull(),
    lastName: (0, pg_core_1.varchar)('last_name', { length: 100 }).notNull(),
    birthDate: (0, pg_core_1.timestamp)('birth_date'),
    // Contact data
    email: (0, pg_core_1.varchar)('email', { length: 255 }),
    phone: (0, pg_core_1.varchar)('phone', { length: 50 }),
    // Employment data
    hireDate: (0, pg_core_1.timestamp)('hire_date').notNull(),
    terminationDate: (0, pg_core_1.timestamp)('termination_date'),
    employmentType: (0, pg_core_1.varchar)('employment_type', { length: 20 }).notNull(), // Full, Part, Temp
    // Organization data
    departmentId: (0, pg_core_1.uuid)('department_id'),
    position: (0, pg_core_1.varchar)('position', { length: 200 }),
    managerId: (0, pg_core_1.uuid)('manager_id'),
    // Payroll data (sensitive - encrypted in production)
    taxClass: (0, pg_core_1.varchar)('tax_class', { length: 10 }),
    socialSecurityId: (0, pg_core_1.varchar)('social_security_id', { length: 50 }),
    iban: (0, pg_core_1.varchar)('iban', { length: 50 }),
    // Status and roles
    status: (0, pg_core_1.varchar)('status', { length: 20 }).notNull().default('Active'),
    roles: (0, pg_core_1.jsonb)('roles').$type().default([]),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantEmployeeNumberIdx: (0, pg_core_1.index)('tenant_employee_number_idx').on(table.tenantId, table.employeeNumber),
    tenantStatusIdx: (0, pg_core_1.index)('tenant_status_idx').on(table.tenantId, table.status),
    tenantDepartmentIdx: (0, pg_core_1.index)('tenant_department_idx').on(table.tenantId, table.departmentId),
    tenantManagerIdx: (0, pg_core_1.index)('tenant_manager_idx').on(table.tenantId, table.managerId)
}));
// Roles table
exports.roles = (0, pg_core_1.pgTable)('roles', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    key: (0, pg_core_1.varchar)('key', { length: 100 }).notNull(),
    name: (0, pg_core_1.varchar)('name', { length: 200 }).notNull(),
    permissions: (0, pg_core_1.jsonb)('permissions').$type().notNull().default([]),
    editable: (0, pg_core_1.boolean)('editable').notNull().default(true),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantKeyIdx: (0, pg_core_1.index)('tenant_key_idx').on(table.tenantId, table.key)
}));
// Time entries table
exports.timeEntries = (0, pg_core_1.pgTable)('time_entries', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    employeeId: (0, pg_core_1.uuid)('employee_id').notNull(),
    date: (0, pg_core_1.date)('date').notNull(),
    start: (0, pg_core_1.timestamp)('start').notNull(),
    end: (0, pg_core_1.timestamp)('end').notNull(),
    breakMinutes: (0, pg_core_1.integer)('break_minutes').notNull().default(0),
    // Optional project/cost center
    projectId: (0, pg_core_1.uuid)('project_id'),
    costCenter: (0, pg_core_1.varchar)('cost_center', { length: 100 }),
    // Metadata
    source: (0, pg_core_1.varchar)('source', { length: 20 }).notNull().default('Manual'),
    status: (0, pg_core_1.varchar)('status', { length: 20 }).notNull().default('Draft'),
    approvedBy: (0, pg_core_1.uuid)('approved_by'),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantEmployeeIdx: (0, pg_core_1.index)('tenant_employee_idx').on(table.tenantId, table.employeeId),
    tenantDateIdx: (0, pg_core_1.index)('tenant_date_idx').on(table.tenantId, table.date),
    tenantStatusIdx: (0, pg_core_1.index)('tenant_status_idx').on(table.tenantId, table.status),
    tenantProjectIdx: (0, pg_core_1.index)('tenant_project_idx').on(table.tenantId, table.projectId),
    employeeDateRangeIdx: (0, pg_core_1.index)('employee_date_range_idx').on(table.employeeId, table.start, table.end)
}));
// Shifts table
exports.shifts = (0, pg_core_1.pgTable)('shifts', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    name: (0, pg_core_1.varchar)('name', { length: 200 }).notNull(),
    location: (0, pg_core_1.varchar)('location', { length: 200 }),
    startsAt: (0, pg_core_1.timestamp)('starts_at').notNull(),
    endsAt: (0, pg_core_1.timestamp)('ends_at').notNull(),
    requiredHeadcount: (0, pg_core_1.integer)('required_headcount').notNull(),
    assigned: (0, pg_core_1.jsonb)('assigned').$type().default([]),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantStartsAtIdx: (0, pg_core_1.index)('tenant_starts_at_idx').on(table.tenantId, table.startsAt),
    tenantLocationIdx: (0, pg_core_1.index)('tenant_location_idx').on(table.tenantId, table.location)
}));
// Leave requests table
exports.leaveRequests = (0, pg_core_1.pgTable)('leave_requests', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    employeeId: (0, pg_core_1.uuid)('employee_id').notNull(),
    type: (0, pg_core_1.varchar)('type', { length: 20 }).notNull(), // Vacation, Sick, Unpaid, Other
    from: (0, pg_core_1.date)('from').notNull(),
    to: (0, pg_core_1.date)('to').notNull(),
    days: (0, pg_core_1.numeric)('days', { precision: 5, scale: 2 }).notNull(),
    status: (0, pg_core_1.varchar)('status', { length: 20 }).notNull().default('Pending'),
    approvedBy: (0, pg_core_1.uuid)('approved_by'),
    note: (0, pg_core_1.text)('note'),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantEmployeeIdx: (0, pg_core_1.index)('tenant_employee_idx').on(table.tenantId, table.employeeId),
    tenantStatusIdx: (0, pg_core_1.index)('tenant_status_idx').on(table.tenantId, table.status),
    tenantDateRangeIdx: (0, pg_core_1.index)('tenant_date_range_idx').on(table.tenantId, table.from, table.to),
    employeeDateRangeIdx: (0, pg_core_1.index)('employee_date_range_idx').on(table.employeeId, table.from, table.to)
}));
// Payroll runs table
exports.payrollRuns = (0, pg_core_1.pgTable)('payroll_runs', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    periodFrom: (0, pg_core_1.date)('period_from').notNull(),
    periodTo: (0, pg_core_1.date)('period_to').notNull(),
    status: (0, pg_core_1.varchar)('status', { length: 20 }).notNull().default('Draft'),
    items: (0, pg_core_1.jsonb)('items').$type().default([]),
    exportedAt: (0, pg_core_1.timestamp)('exported_at'),
    exportedBy: (0, pg_core_1.uuid)('exported_by'),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    createdBy: (0, pg_core_1.uuid)('created_by'),
    updatedBy: (0, pg_core_1.uuid)('updated_by')
}, (table) => ({
    tenantPeriodIdx: (0, pg_core_1.index)('tenant_period_idx').on(table.tenantId, table.periodFrom, table.periodTo),
    tenantStatusIdx: (0, pg_core_1.index)('tenant_status_idx').on(table.tenantId, table.status)
}));
// Domain events table (for event sourcing and audit trail)
exports.domainEvents = (0, pg_core_1.pgTable)('domain_events', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    eventId: (0, pg_core_1.uuid)('event_id').notNull(),
    eventType: (0, pg_core_1.varchar)('event_type', { length: 100 }).notNull(),
    eventVersion: (0, pg_core_1.integer)('event_version').notNull(),
    occurredAt: (0, pg_core_1.timestamp)('occurred_at').notNull(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    aggregateId: (0, pg_core_1.uuid)('aggregate_id'),
    aggregateType: (0, pg_core_1.varchar)('aggregate_type', { length: 50 }),
    payload: (0, pg_core_1.jsonb)('payload').notNull(),
    correlationId: (0, pg_core_1.uuid)('correlation_id'),
    causationId: (0, pg_core_1.uuid)('causation_id'),
    // Audit fields
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow()
}, (table) => ({
    tenantEventTypeIdx: (0, pg_core_1.index)('tenant_event_type_idx').on(table.tenantId, table.eventType),
    tenantOccurredAtIdx: (0, pg_core_1.index)('tenant_occurred_at_idx').on(table.tenantId, table.occurredAt),
    aggregateIdx: (0, pg_core_1.index)('aggregate_idx').on(table.tenantId, table.aggregateType, table.aggregateId),
    correlationIdx: (0, pg_core_1.index)('correlation_idx').on(table.correlationId)
}));
// Relations
exports.employeesRelations = (0, drizzle_orm_1.relations)(exports.employees, ({ one, many }) => ({
    manager: one(exports.employees, {
        fields: [exports.employees.managerId],
        references: [exports.employees.id]
    }),
    subordinates: many(exports.employees),
    timeEntries: many(exports.timeEntries),
    leaveRequests: many(exports.leaveRequests)
}));
exports.timeEntriesRelations = (0, drizzle_orm_1.relations)(exports.timeEntries, ({ one }) => ({
    employee: one(exports.employees, {
        fields: [exports.timeEntries.employeeId],
        references: [exports.employees.id]
    })
}));
exports.leaveRequestsRelations = (0, drizzle_orm_1.relations)(exports.leaveRequests, ({ one }) => ({
    employee: one(exports.employees, {
        fields: [exports.leaveRequests.employeeId],
        references: [exports.employees.id]
    })
}));
//# sourceMappingURL=schema.js.map