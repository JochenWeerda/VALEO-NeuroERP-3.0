import { pgTable, uuid, text, timestamp, boolean, integer, numeric, jsonb, index } from 'drizzle-orm/pg-core';

// Customer Table
export const customers = pgTable('customers', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  number: text('number').notNull().unique(),
  name: text('name').notNull(),
  vatId: text('vat_id'),
  billingAddress: jsonb('billing_address').notNull(),
  shippingAddresses: jsonb('shipping_addresses').$type<Address[]>().default([]).notNull(),
  email: text('email'),
  phone: text('phone'),
  tags: text('tags').array().default([]).notNull(),
  status: text('status', { enum: ['Active', 'Prospect', 'Blocked'] }).notNull().default('Prospect'),
  ownerUserId: uuid('owner_user_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('customers_tenant_idx').on(table.tenantId),
  statusIdx: index('customers_status_idx').on(table.status),
  ownerIdx: index('customers_owner_idx').on(table.ownerUserId)
}));

// Contact Table
export const contacts = pgTable('contacts', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull().references(() => customers.id, { onDelete: 'cascade' }),
  firstName: text('first_name').notNull(),
  lastName: text('last_name').notNull(),
  role: text('role'),
  email: text('email').notNull(),
  phone: text('phone'),
  isPrimary: boolean('is_primary').notNull().default(false),
  notes: text('notes'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('contacts_tenant_idx').on(table.tenantId),
  customerIdx: index('contacts_customer_idx').on(table.customerId),
  emailIdx: index('contacts_email_idx').on(table.email),
  primaryIdx: index('contacts_primary_idx').on(table.customerId, table.isPrimary)
}));

// Opportunity Table
export const opportunities = pgTable('opportunities', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull().references(() => customers.id, { onDelete: 'cascade' }),
  title: text('title').notNull(),
  stage: text('stage', { enum: ['Lead', 'Qualified', 'Proposal', 'Won', 'Lost'] }).notNull().default('Lead'),
  expectedCloseDate: timestamp('expected_close_date'),
  amountNet: numeric('amount_net', { precision: 15, scale: 2 }),
  currency: text('currency'),
  probability: numeric('probability', { precision: 3, scale: 2 }).notNull().default('0.10'),
  ownerUserId: uuid('owner_user_id'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('opportunities_tenant_idx').on(table.tenantId),
  customerIdx: index('opportunities_customer_idx').on(table.customerId),
  stageIdx: index('opportunities_stage_idx').on(table.stage),
  ownerIdx: index('opportunities_owner_idx').on(table.ownerUserId),
  amountIdx: index('opportunities_amount_idx').on(table.amountNet)
}));

// Interaction Table
export const interactions = pgTable('interactions', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull().references(() => customers.id, { onDelete: 'cascade' }),
  contactId: uuid('contact_id').references(() => contacts.id, { onDelete: 'set null' }),
  type: text('type', { enum: ['Call', 'Email', 'Visit', 'Note'] }).notNull(),
  subject: text('subject').notNull(),
  content: text('content').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  createdBy: uuid('created_by').notNull(),
  attachments: jsonb('attachments').$type<Attachment[]>().default([]).notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('interactions_tenant_idx').on(table.tenantId),
  customerIdx: index('interactions_customer_idx').on(table.customerId),
  contactIdx: index('interactions_contact_idx').on(table.contactId),
  typeIdx: index('interactions_type_idx').on(table.type),
  occurredAtIdx: index('interactions_occurred_at_idx').on(table.occurredAt),
  createdByIdx: index('interactions_created_by_idx').on(table.createdBy)
}));

// Type definitions for JSONB columns
export interface Address {
  street: string;
  city: string;
  postalCode: string;
  country: string;
  state?: string;
}

export interface Attachment {
  id: string;
  filename: string;
  url: string;
  size: number;
  mimeType: string;
}

// Export table references for foreign keys
export const customersRelations = {
  contacts: contacts,
  opportunities: opportunities,
  interactions: interactions
};

export const contactsRelations = {
  customer: customers,
  interactions: interactions
};

export const opportunitiesRelations = {
  customer: customers
};

export const interactionsRelations = {
  customer: customers,
  contact: contacts
};