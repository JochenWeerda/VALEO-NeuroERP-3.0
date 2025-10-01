import { pgTable, uuid, text, timestamp, jsonb, integer, index } from 'drizzle-orm/pg-core';

export const auditEvents = pgTable(
  'audit_events',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    timestamp: timestamp('timestamp', { withTimezone: true }).notNull(),
    actor: jsonb('actor').notNull(),
    action: text('action').notNull(),
    target: jsonb('target').notNull(),
    payload: jsonb('payload'),
    ip: text('ip'),
    userAgent: text('user_agent'),
    prevHash: text('prev_hash').notNull(),
    hash: text('hash').notNull(),
    integrity: jsonb('integrity'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('ae_tenant_idx').on(table.tenantId),
    timestampIdx: index('ae_timestamp_idx').on(table.timestamp),
    actionIdx: index('ae_action_idx').on(table.action),
    hashIdx: index('ae_hash_idx').on(table.hash),
  })
);

export const exportJobs = pgTable(
  'export_jobs',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    requestedBy: text('requested_by').notNull(),
    filters: jsonb('filters').notNull(),
    format: text('format').notNull(),
    status: text('status').default('Pending').notNull(),
    fileUri: text('file_uri'),
    recordCount: integer('record_count'),
    error: text('error'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    finishedAt: timestamp('finished_at', { withTimezone: true }),
  },
  table => ({
    tenantIdx: index('ej_tenant_idx').on(table.tenantId),
    statusIdx: index('ej_status_idx').on(table.status),
  })
);
