import { boolean, index, integer, jsonb, pgTable, text, timestamp, uniqueIndex, uuid } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// Base columns for all tables
const baseColumns = {
  id: uuid('id').primaryKey().defaultRandom(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
};

// Schedules table
export const schedules = pgTable('schedules', {
  ...baseColumns,
  tenantId: text('tenant_id').notNull(),
  name: text('name').notNull(),
  description: text('description'),
  tz: text('tz').default('Europe/Berlin').notNull(),
  triggerType: text('trigger_type', { enum: ['CRON', 'RRULE', 'FIXED_DELAY', 'ONE_SHOT'] }).notNull(),
  triggerConfig: jsonb('trigger_config').notNull(), // Stores trigger-specific configuration
  targetType: text('target_type', { enum: ['EVENT', 'HTTP', 'QUEUE'] }).notNull(),
  targetConfig: jsonb('target_config').notNull(), // Stores target-specific configuration
  payload: jsonb('payload'), // Optional payload to send with triggers
  calendarConfig: jsonb('calendar_config'), // Optional calendar configuration
  enabled: boolean('enabled').default(true).notNull(),
  nextFireAt: timestamp('next_fire_at', { withTimezone: true }),
  lastFireAt: timestamp('last_fire_at', { withTimezone: true }),
  version: integer('version').default(1).notNull(),
}, (table) => ({
  tenantIdx: index('schedules_tenant_idx').on(table.tenantId),
  enabledIdx: index('schedules_enabled_idx').on(table.enabled),
  nextFireIdx: index('schedules_next_fire_idx').on(table.nextFireAt),
  tenantNameIdx: uniqueIndex('schedules_tenant_name_idx').on(table.tenantId, table.name),
}));

// Jobs table (configuration for job types)
export const jobs = pgTable('jobs', {
  ...baseColumns,
  tenantId: text('tenant_id').notNull(),
  key: text('key').notNull(), // Unique identifier within tenant
  queue: text('queue').default('default').notNull(),
  priority: integer('priority').default(5).notNull(), // 1-9, higher = more priority
  maxAttempts: integer('max_attempts').default(3).notNull(),
  backoffStrategy: text('backoff_strategy', { enum: ['FIXED', 'EXPONENTIAL'] }).default('EXPONENTIAL').notNull(),
  backoffBaseSec: integer('backoff_base_sec').default(60).notNull(),
  backoffMaxSec: integer('backoff_max_sec'),
  timeoutSec: integer('timeout_sec').default(300).notNull(), // 5 minutes default
  concurrencyLimit: integer('concurrency_limit'), // Max concurrent runs
  slaSec: integer('sla_sec'), // SLA in seconds
  enabled: boolean('enabled').default(true).notNull(),
  version: integer('version').default(1).notNull(),
}, (table) => ({
  tenantIdx: index('jobs_tenant_idx').on(table.tenantId),
  queueIdx: index('jobs_queue_idx').on(table.queue),
  enabledIdx: index('jobs_enabled_idx').on(table.enabled),
  tenantKeyIdx: uniqueIndex('jobs_tenant_key_idx').on(table.tenantId, table.key),
}));

// Runs table (individual executions)
export const runs = pgTable('runs', {
  ...baseColumns,
  tenantId: text('tenant_id').notNull(),
  scheduleId: uuid('schedule_id').references(() => schedules.id),
  jobId: uuid('job_id').references(() => jobs.id),
  dedupeKey: text('dedupe_key'), // For deduplication
  status: text('status', {
    enum: ['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']
  }).default('Pending').notNull(),
  startedAt: timestamp('started_at', { withTimezone: true }),
  finishedAt: timestamp('finished_at', { withTimezone: true }),
  attempt: integer('attempt').default(1).notNull(),
  error: text('error'),
  latencyMs: integer('latency_ms'), // Time from scheduled to started
  durationMs: integer('duration_ms'), // Time from started to finished
  workerId: uuid('worker_id').references(() => workers.id),
  payload: jsonb('payload'), // Payload for this specific run
}, (table) => ({
  tenantIdx: index('runs_tenant_idx').on(table.tenantId),
  scheduleIdx: index('runs_schedule_idx').on(table.scheduleId),
  jobIdx: index('runs_job_idx').on(table.jobId),
  statusIdx: index('runs_status_idx').on(table.status),
  workerIdx: index('runs_worker_idx').on(table.workerId),
  startedIdx: index('runs_started_idx').on(table.startedAt),
  dedupeIdx: uniqueIndex('runs_dedupe_idx').on(table.dedupeKey),
}));

// Workers table
export const workers = pgTable('workers', {
  ...baseColumns,
  tenantId: text('tenant_id'), // null for shared workers
  name: text('name').notNull(),
  capabilities: jsonb('capabilities').notNull(), // { queues: string[], jobKeys: string[] }
  heartbeatAt: timestamp('heartbeat_at', { withTimezone: true }).defaultNow().notNull(),
  status: text('status', { enum: ['Online', 'Offline', 'Maintenance'] }).default('Online').notNull(),
  maxParallel: integer('max_parallel').default(10).notNull(),
  currentJobs: integer('current_jobs').default(0).notNull(),
  version: integer('version').default(1).notNull(),
}, (table) => ({
  tenantIdx: index('workers_tenant_idx').on(table.tenantId),
  statusIdx: index('workers_status_idx').on(table.status),
  heartbeatIdx: index('workers_heartbeat_idx').on(table.heartbeatAt),
  nameIdx: uniqueIndex('workers_name_idx').on(table.name),
}));

// Calendars table
export const calendars = pgTable('calendars', {
  ...baseColumns,
  tenantId: text('tenant_id'), // null for global calendars
  key: text('key').notNull(), // e.g., "DE-BY-AGRI"
  name: text('name').notNull(),
  holidays: jsonb('holidays').default([]).notNull(), // Array of ISO date strings
  businessDays: jsonb('business_days').default({
    mon: true,
    tue: true,
    wed: true,
    thu: true,
    fri: true,
    sat: false,
    sun: false,
  }).notNull(),
  version: integer('version').default(1).notNull(),
}, (table) => ({
  tenantIdx: index('calendars_tenant_idx').on(table.tenantId),
  keyIdx: uniqueIndex('calendars_key_idx').on(table.key),
}));

// Indexes for performance
export const scheduleRunsIdx = index('schedule_runs_idx').on(runs.scheduleId, runs.status);
export const jobRunsIdx = index('job_runs_idx').on(runs.jobId, runs.status);
export const tenantTimeRangeIdx = index('runs_tenant_time_idx').on(runs.tenantId, runs.createdAt);

// Types for TypeScript
export type Schedule = typeof schedules.$inferSelect;
export type NewSchedule = typeof schedules.$inferInsert;

export type Job = typeof jobs.$inferSelect;
export type NewJob = typeof jobs.$inferInsert;

export type Run = typeof runs.$inferSelect;
export type NewRun = typeof runs.$inferInsert;

export type Worker = typeof workers.$inferSelect;
export type NewWorker = typeof workers.$inferInsert;

export type Calendar = typeof calendars.$inferSelect;
export type NewCalendar = typeof calendars.$inferInsert;