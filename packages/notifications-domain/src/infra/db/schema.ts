import {
  pgTable,
  uuid,
  text,
  timestamp,
  integer,
  jsonb,
  boolean,
  index,
} from 'drizzle-orm/pg-core';

export const notificationTemplates = pgTable(
  'notification_templates',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    key: text('key').notNull(),
    name: text('name').notNull(),
    channel: text('channel').notNull(),
    locale: text('locale').default('de-DE').notNull(),
    subject: text('subject'),
    bodyText: text('body_text').notNull(),
    bodyHtml: text('body_html'),
    placeholders: jsonb('placeholders').default([]).notNull(),
    status: text('status').default('Draft').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('ntpl_tenant_idx').on(table.tenantId),
    keyIdx: index('ntpl_key_idx').on(table.key),
    channelIdx: index('ntpl_channel_idx').on(table.channel),
  })
);

export const notificationMessages = pgTable(
  'notification_messages',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    channel: text('channel').notNull(),
    templateKey: text('template_key'),
    locale: text('locale').default('de-DE').notNull(),
    payload: jsonb('payload').default({}).notNull(),
    recipients: jsonb('recipients').notNull(),
    attachments: jsonb('attachments').default([]).notNull(),
    priority: text('priority').default('Normal').notNull(),
    status: text('status').default('Pending').notNull(),
    attemptCount: integer('attempt_count').default(0).notNull(),
    lastError: text('last_error'),
    sentAt: timestamp('sent_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('nmsg_tenant_idx').on(table.tenantId),
    statusIdx: index('nmsg_status_idx').on(table.status),
    channelIdx: index('nmsg_channel_idx').on(table.channel),
    createdAtIdx: index('nmsg_created_at_idx').on(table.createdAt),
  })
);

export const channelConfigs = pgTable(
  'channel_configs',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    tenantId: text('tenant_id').notNull(),
    channel: text('channel').notNull(),
    provider: text('provider').notNull(),
    credentials: jsonb('credentials').notNull(),
    rateLimit: jsonb('rate_limit'),
    retryPolicy: jsonb('retry_policy'),
    active: boolean('active').default(true).notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    tenantIdx: index('cfg_tenant_idx').on(table.tenantId),
    channelIdx: index('cfg_channel_idx').on(table.channel),
  })
);

export const deliveryReceipts = pgTable(
  'delivery_receipts',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    messageId: uuid('message_id').notNull(),
    channel: text('channel').notNull(),
    provider: text('provider').notNull(),
    status: text('status').notNull(),
    meta: jsonb('meta'),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  table => ({
    messageIdx: index('rcpt_message_idx').on(table.messageId),
    statusIdx: index('rcpt_status_idx').on(table.status),
  })
);
