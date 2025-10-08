/**
 * Database Schema for VALEO NeuroERP 3.0 HR Domain
 * PostgreSQL schema using Drizzle ORM
 */

import {
  boolean,
  date,
  index,
  integer,
  jsonb,
  numeric,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar
} from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import type { PayrollItem } from '../../domain/entities/payroll-run';

// Employees table
export const employees = pgTable('employees', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  employeeNumber: varchar('employee_number', { length: 50 }).notNull(),
  
  // Person data
  firstName: varchar('first_name', { length: 100 }).notNull(),
  lastName: varchar('last_name', { length: 100 }).notNull(),
  birthDate: timestamp('birth_date'),
  
  // Contact data
  email: varchar('email', { length: 255 }),
  phone: varchar('phone', { length: 50 }),
  
  // Employment data
  hireDate: timestamp('hire_date').notNull(),
  terminationDate: timestamp('termination_date'),
  employmentType: varchar('employment_type', { length: 20 }).notNull(), // Full, Part, Temp
  
  // Organization data
  departmentId: uuid('department_id'),
  position: varchar('position', { length: 200 }),
  managerId: uuid('manager_id'),
  
  // Payroll data (sensitive - encrypted in production)
  taxClass: varchar('tax_class', { length: 10 }),
  socialSecurityId: varchar('social_security_id', { length: 50 }),
  iban: varchar('iban', { length: 50 }),
  
  // Status and roles
  status: varchar('status', { length: 20 }).notNull().default('Active'),
  roles: jsonb('roles').$type<string[]>().default([]),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantEmployeeNumberIdx: index('tenant_employee_number_idx').on(table.tenantId, table.employeeNumber),
  tenantStatusIdx: index('tenant_status_idx').on(table.tenantId, table.status),
  tenantDepartmentIdx: index('tenant_department_idx').on(table.tenantId, table.departmentId),
  tenantManagerIdx: index('tenant_manager_idx').on(table.tenantId, table.managerId)
}));

// Roles table
export const roles = pgTable('roles', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  key: varchar('key', { length: 100 }).notNull(),
  name: varchar('name', { length: 200 }).notNull(),
  permissions: jsonb('permissions').$type<string[]>().notNull().default([]),
  editable: boolean('editable').notNull().default(true),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantKeyIdx: index('tenant_key_idx').on(table.tenantId, table.key)
}));

// Time entries table
export const timeEntries = pgTable('time_entries', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  employeeId: uuid('employee_id').notNull(),
  date: date('date').notNull(),
  start: timestamp('start', { withTimezone: true, mode: 'string' }).notNull(),
  end: timestamp('end', { withTimezone: true, mode: 'string' }).notNull(),
  breakMinutes: integer('break_minutes').notNull().default(0),

  // Optional project/cost center
  projectId: uuid('project_id'),
  costCenter: varchar('cost_center', { length: 100 }),
  
  // Metadata
  source: varchar('source', { length: 20 }).notNull().default('Manual'),
  status: varchar('status', { length: 20 }).notNull().default('Draft'),
  approvedBy: uuid('approved_by'),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantEmployeeIdx: index('tenant_employee_idx').on(table.tenantId, table.employeeId),
  tenantDateIdx: index('tenant_date_idx').on(table.tenantId, table.date),
  tenantStatusIdx: index('tenant_status_idx').on(table.tenantId, table.status),
  tenantProjectIdx: index('tenant_project_idx').on(table.tenantId, table.projectId),
  tenantStartIdx: index('tenant_start_idx').on(table.tenantId, table.start),
  employeeDateRangeIdx: index('employee_date_range_idx').on(table.employeeId, table.start, table.end),
  tenantEmployeeStartUk: uniqueIndex('tenant_employee_start_uk').on(table.tenantId, table.employeeId, table.start)
}));

// Shifts table
export const shifts = pgTable('shifts', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  name: varchar('name', { length: 200 }).notNull(),
  location: varchar('location', { length: 200 }),
  startsAt: timestamp('starts_at').notNull(),
  endsAt: timestamp('ends_at').notNull(),
  requiredHeadcount: integer('required_headcount').notNull(),
  assigned: jsonb('assigned').$type<string[]>().default([]),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantStartsAtIdx: index('tenant_starts_at_idx').on(table.tenantId, table.startsAt),
  tenantLocationIdx: index('tenant_location_idx').on(table.tenantId, table.location)
}));

// Leave requests table
export const leaveRequests = pgTable('leave_requests', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  employeeId: uuid('employee_id').notNull(),
  type: varchar('type', { length: 20 }).notNull(), // Vacation, Sick, Unpaid, Other
  from: date('from').notNull(),
  to: date('to').notNull(),
  days: numeric('days', { precision: 5, scale: 2 }).notNull(),
  status: varchar('status', { length: 20 }).notNull().default('Pending'),
  approvedBy: uuid('approved_by'),
  note: text('note'),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantEmployeeIdx: index('tenant_employee_idx').on(table.tenantId, table.employeeId),
  tenantStatusIdx: index('tenant_status_idx').on(table.tenantId, table.status),
  tenantDateRangeIdx: index('tenant_date_range_idx').on(table.tenantId, table.from, table.to),
  employeeDateRangeIdx: index('employee_date_range_idx').on(table.employeeId, table.from, table.to)
}));

// Payroll runs table
export const payrollRuns = pgTable('payroll_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  periodFrom: date('period_from').notNull(),
  periodTo: date('period_to').notNull(),
  status: varchar('status', { length: 20 }).notNull().default('Draft'),
  items: jsonb('items').$type<PayrollItem[]>().default([]),
  exportedAt: timestamp('exported_at'),
  exportedBy: uuid('exported_by'),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdBy: uuid('created_by'),
  updatedBy: uuid('updated_by')
}, (table) => ({
  tenantPeriodIdx: index('tenant_period_idx').on(table.tenantId, table.periodFrom, table.periodTo),
  tenantStatusIdx: index('tenant_status_idx').on(table.tenantId, table.status)
}));

// Domain events table (for event sourcing and audit trail)
export const domainEvents = pgTable('domain_events', {
  id: uuid('id').primaryKey().defaultRandom(),
  eventId: uuid('event_id').notNull(),
  eventType: varchar('event_type', { length: 100 }).notNull(),
  eventVersion: integer('event_version').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  tenantId: uuid('tenant_id').notNull(),
  aggregateId: uuid('aggregate_id'),
  aggregateType: varchar('aggregate_type', { length: 50 }),
  payload: jsonb('payload').notNull(),
  correlationId: uuid('correlation_id'),
  causationId: uuid('causation_id'),
  
  // Audit fields
  createdAt: timestamp('created_at').notNull().defaultNow()
}, (table) => ({
  tenantEventTypeIdx: index('tenant_event_type_idx').on(table.tenantId, table.eventType),
  tenantOccurredAtIdx: index('tenant_occurred_at_idx').on(table.tenantId, table.occurredAt),
  aggregateIdx: index('aggregate_idx').on(table.tenantId, table.aggregateType, table.aggregateId),
  correlationIdx: index('correlation_idx').on(table.correlationId)
}));

// Relations
export const employeesRelations = relations(employees, ({ one, many }) => ({
  manager: one(employees, {
    fields: [employees.managerId],
    references: [employees.id]
  }),
  subordinates: many(employees),
  timeEntries: many(timeEntries),
  leaveRequests: many(leaveRequests)
}));

export const timeEntriesRelations = relations(timeEntries, ({ one }) => ({
  employee: one(employees, {
    fields: [timeEntries.employeeId],
    references: [employees.id]
  })
}));

export const leaveRequestsRelations = relations(leaveRequests, ({ one }) => ({
  employee: one(employees, {
    fields: [leaveRequests.employeeId],
    references: [employees.id]
  })
}));

// Export types
export type EmployeeRecord = typeof employees.$inferSelect;
export type NewEmployeeRecord = typeof employees.$inferInsert;

export type RoleRecord = typeof roles.$inferSelect;
export type NewRoleRecord = typeof roles.$inferInsert;

export type TimeEntryRecord = typeof timeEntries.$inferSelect;
export type NewTimeEntryRecord = typeof timeEntries.$inferInsert;

export type ShiftRecord = typeof shifts.$inferSelect;
export type NewShiftRecord = typeof shifts.$inferInsert;

export type LeaveRequestRecord = typeof leaveRequests.$inferSelect;
export type NewLeaveRequestRecord = typeof leaveRequests.$inferInsert;

export type PayrollRunRecord = typeof payrollRuns.$inferSelect;
export type NewPayrollRunRecord = typeof payrollRuns.$inferInsert;

export type DomainEventRecord = typeof domainEvents.$inferSelect;
export type NewDomainEventRecord = typeof domainEvents.$inferInsert;

