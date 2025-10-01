import { pgTable, uuid, text, timestamp, integer, jsonb, index } from 'drizzle-orm/pg-core';

export const templates = pgTable(
  'templates',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    key: text('key').notNull(),
    name: text('name').notNull(),
    engine: text('engine').default('handlebars').notNull(),
    version: integer('version').default(1).notNull(),
    status: text('status').default('Draft').notNull(),
    locale: jsonb('locale').default(['de-DE']).notNull(),
    paper: text('paper').default('A4').notNull(),
    margins: jsonb('margins'),
    sourceHtml: text('source_html').notNull(),
    css: text('css'),
    assets: jsonb('assets'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('tpl_tenant_idx').on(table.tenantId),
    keyIdx: index('tpl_key_idx').on(table.key),
  })
);

export const numberSeries = pgTable(
  'number_series',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    scope: text('scope').notNull(),
    pattern: text('pattern').notNull(),
    nextSeq: integer('next_seq').default(1).notNull(),
    resetPolicy: text('reset_policy').default('Yearly').notNull(),
    lastResetAt: timestamp('last_reset_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('ns_tenant_idx').on(table.tenantId),
    scopeIdx: index('ns_scope_idx').on(table.scope),
  })
);

export const documents = pgTable(
  'documents',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    docType: text('doc_type').notNull(),
    number: text('number'),
    templateKey: text('template_key').notNull(),
    templateVersion: integer('template_version').notNull(),
    payloadHash: text('payload_hash').notNull(),
    locale: text('locale').default('de-DE').notNull(),
    status: text('status').default('Draft').notNull(),
    files: jsonb('files').default([]).notNull(),
    signatures: jsonb('signatures').default([]).notNull(),
    metadata: jsonb('metadata'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('doc_tenant_idx').on(table.tenantId),
    typeIdx: index('doc_type_idx').on(table.docType),
    numberIdx: index('doc_number_idx').on(table.number),
  })
);
