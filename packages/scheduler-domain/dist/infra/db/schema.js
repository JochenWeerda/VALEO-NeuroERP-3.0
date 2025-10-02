"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tenantTimeRangeIdx = exports.jobRunsIdx = exports.scheduleRunsIdx = exports.calendars = exports.workers = exports.runs = exports.jobs = exports.schedules = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
const baseColumns = {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    createdAt: (0, pg_core_1.timestamp)('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at', { withTimezone: true }).defaultNow().notNull(),
};
exports.schedules = (0, pg_core_1.pgTable)('schedules', {
    ...baseColumns,
    tenantId: (0, pg_core_1.text)('tenant_id').notNull(),
    name: (0, pg_core_1.text)('name').notNull(),
    description: (0, pg_core_1.text)('description'),
    tz: (0, pg_core_1.text)('tz').default('Europe/Berlin').notNull(),
    triggerType: (0, pg_core_1.text)('trigger_type', { enum: ['CRON', 'RRULE', 'FIXED_DELAY', 'ONE_SHOT'] }).notNull(),
    triggerConfig: (0, pg_core_1.jsonb)('trigger_config').notNull(),
    targetType: (0, pg_core_1.text)('target_type', { enum: ['EVENT', 'HTTP', 'QUEUE'] }).notNull(),
    targetConfig: (0, pg_core_1.jsonb)('target_config').notNull(),
    payload: (0, pg_core_1.jsonb)('payload'),
    calendarConfig: (0, pg_core_1.jsonb)('calendar_config'),
    enabled: (0, pg_core_1.boolean)('enabled').default(true).notNull(),
    nextFireAt: (0, pg_core_1.timestamp)('next_fire_at', { withTimezone: true }),
    lastFireAt: (0, pg_core_1.timestamp)('last_fire_at', { withTimezone: true }),
    version: (0, pg_core_1.integer)('version').default(1).notNull(),
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('schedules_tenant_idx').on(table.tenantId),
    enabledIdx: (0, pg_core_1.index)('schedules_enabled_idx').on(table.enabled),
    nextFireIdx: (0, pg_core_1.index)('schedules_next_fire_idx').on(table.nextFireAt),
    tenantNameIdx: (0, pg_core_1.uniqueIndex)('schedules_tenant_name_idx').on(table.tenantId, table.name),
}));
exports.jobs = (0, pg_core_1.pgTable)('jobs', {
    ...baseColumns,
    tenantId: (0, pg_core_1.text)('tenant_id').notNull(),
    key: (0, pg_core_1.text)('key').notNull(),
    queue: (0, pg_core_1.text)('queue').default('default').notNull(),
    priority: (0, pg_core_1.integer)('priority').default(5).notNull(),
    maxAttempts: (0, pg_core_1.integer)('max_attempts').default(3).notNull(),
    backoffStrategy: (0, pg_core_1.text)('backoff_strategy', { enum: ['FIXED', 'EXPONENTIAL'] }).default('EXPONENTIAL').notNull(),
    backoffBaseSec: (0, pg_core_1.integer)('backoff_base_sec').default(60).notNull(),
    backoffMaxSec: (0, pg_core_1.integer)('backoff_max_sec'),
    timeoutSec: (0, pg_core_1.integer)('timeout_sec').default(300).notNull(),
    concurrencyLimit: (0, pg_core_1.integer)('concurrency_limit'),
    slaSec: (0, pg_core_1.integer)('sla_sec'),
    enabled: (0, pg_core_1.boolean)('enabled').default(true).notNull(),
    version: (0, pg_core_1.integer)('version').default(1).notNull(),
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('jobs_tenant_idx').on(table.tenantId),
    queueIdx: (0, pg_core_1.index)('jobs_queue_idx').on(table.queue),
    enabledIdx: (0, pg_core_1.index)('jobs_enabled_idx').on(table.enabled),
    tenantKeyIdx: (0, pg_core_1.uniqueIndex)('jobs_tenant_key_idx').on(table.tenantId, table.key),
}));
exports.runs = (0, pg_core_1.pgTable)('runs', {
    ...baseColumns,
    tenantId: (0, pg_core_1.text)('tenant_id').notNull(),
    scheduleId: (0, pg_core_1.uuid)('schedule_id').references(() => exports.schedules.id),
    jobId: (0, pg_core_1.uuid)('job_id').references(() => exports.jobs.id),
    dedupeKey: (0, pg_core_1.text)('dedupe_key'),
    status: (0, pg_core_1.text)('status', {
        enum: ['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']
    }).default('Pending').notNull(),
    startedAt: (0, pg_core_1.timestamp)('started_at', { withTimezone: true }),
    finishedAt: (0, pg_core_1.timestamp)('finished_at', { withTimezone: true }),
    attempt: (0, pg_core_1.integer)('attempt').default(1).notNull(),
    error: (0, pg_core_1.text)('error'),
    latencyMs: (0, pg_core_1.integer)('latency_ms'),
    durationMs: (0, pg_core_1.integer)('duration_ms'),
    workerId: (0, pg_core_1.uuid)('worker_id').references(() => exports.workers.id),
    payload: (0, pg_core_1.jsonb)('payload'),
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('runs_tenant_idx').on(table.tenantId),
    scheduleIdx: (0, pg_core_1.index)('runs_schedule_idx').on(table.scheduleId),
    jobIdx: (0, pg_core_1.index)('runs_job_idx').on(table.jobId),
    statusIdx: (0, pg_core_1.index)('runs_status_idx').on(table.status),
    workerIdx: (0, pg_core_1.index)('runs_worker_idx').on(table.workerId),
    startedIdx: (0, pg_core_1.index)('runs_started_idx').on(table.startedAt),
    dedupeIdx: (0, pg_core_1.uniqueIndex)('runs_dedupe_idx').on(table.dedupeKey),
}));
exports.workers = (0, pg_core_1.pgTable)('workers', {
    ...baseColumns,
    tenantId: (0, pg_core_1.text)('tenant_id'),
    name: (0, pg_core_1.text)('name').notNull(),
    capabilities: (0, pg_core_1.jsonb)('capabilities').notNull(),
    heartbeatAt: (0, pg_core_1.timestamp)('heartbeat_at', { withTimezone: true }).defaultNow().notNull(),
    status: (0, pg_core_1.text)('status', { enum: ['Online', 'Offline', 'Maintenance'] }).default('Online').notNull(),
    maxParallel: (0, pg_core_1.integer)('max_parallel').default(10).notNull(),
    currentJobs: (0, pg_core_1.integer)('current_jobs').default(0).notNull(),
    version: (0, pg_core_1.integer)('version').default(1).notNull(),
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('workers_tenant_idx').on(table.tenantId),
    statusIdx: (0, pg_core_1.index)('workers_status_idx').on(table.status),
    heartbeatIdx: (0, pg_core_1.index)('workers_heartbeat_idx').on(table.heartbeatAt),
    nameIdx: (0, pg_core_1.uniqueIndex)('workers_name_idx').on(table.name),
}));
exports.calendars = (0, pg_core_1.pgTable)('calendars', {
    ...baseColumns,
    tenantId: (0, pg_core_1.text)('tenant_id'),
    key: (0, pg_core_1.text)('key').notNull(),
    name: (0, pg_core_1.text)('name').notNull(),
    holidays: (0, pg_core_1.jsonb)('holidays').default([]).notNull(),
    businessDays: (0, pg_core_1.jsonb)('business_days').default({
        mon: true,
        tue: true,
        wed: true,
        thu: true,
        fri: true,
        sat: false,
        sun: false,
    }).notNull(),
    version: (0, pg_core_1.integer)('version').default(1).notNull(),
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('calendars_tenant_idx').on(table.tenantId),
    keyIdx: (0, pg_core_1.uniqueIndex)('calendars_key_idx').on(table.key),
}));
exports.scheduleRunsIdx = (0, pg_core_1.index)('schedule_runs_idx').on(exports.runs.scheduleId, exports.runs.status);
exports.jobRunsIdx = (0, pg_core_1.index)('job_runs_idx').on(exports.runs.jobId, exports.runs.status);
exports.tenantTimeRangeIdx = (0, pg_core_1.index)('runs_tenant_time_idx').on(exports.runs.tenantId, exports.runs.createdAt);
//# sourceMappingURL=schema.js.map