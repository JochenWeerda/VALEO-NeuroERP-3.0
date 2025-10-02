"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.interactionsRelations = exports.opportunitiesRelations = exports.contactsRelations = exports.customersRelations = exports.interactions = exports.opportunities = exports.contacts = exports.customers = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
// Customer Table
exports.customers = (0, pg_core_1.pgTable)('customers', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    number: (0, pg_core_1.text)('number').notNull().unique(),
    name: (0, pg_core_1.text)('name').notNull(),
    vatId: (0, pg_core_1.text)('vat_id'),
    billingAddress: (0, pg_core_1.jsonb)('billing_address').notNull(),
    shippingAddresses: (0, pg_core_1.jsonb)('shipping_addresses').$type().default([]).notNull(),
    email: (0, pg_core_1.text)('email'),
    phone: (0, pg_core_1.text)('phone'),
    tags: (0, pg_core_1.text)('tags').array().default([]).notNull(),
    status: (0, pg_core_1.text)('status', { enum: ['Active', 'Prospect', 'Blocked'] }).notNull().default('Prospect'),
    ownerUserId: (0, pg_core_1.uuid)('owner_user_id'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('customers_tenant_idx').on(table.tenantId),
    statusIdx: (0, pg_core_1.index)('customers_status_idx').on(table.status),
    ownerIdx: (0, pg_core_1.index)('customers_owner_idx').on(table.ownerUserId)
}));
// Contact Table
exports.contacts = (0, pg_core_1.pgTable)('contacts', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull().references(() => exports.customers.id, { onDelete: 'cascade' }),
    firstName: (0, pg_core_1.text)('first_name').notNull(),
    lastName: (0, pg_core_1.text)('last_name').notNull(),
    role: (0, pg_core_1.text)('role'),
    email: (0, pg_core_1.text)('email').notNull(),
    phone: (0, pg_core_1.text)('phone'),
    isPrimary: (0, pg_core_1.boolean)('is_primary').notNull().default(false),
    notes: (0, pg_core_1.text)('notes'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('contacts_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('contacts_customer_idx').on(table.customerId),
    emailIdx: (0, pg_core_1.index)('contacts_email_idx').on(table.email),
    primaryIdx: (0, pg_core_1.index)('contacts_primary_idx').on(table.customerId, table.isPrimary)
}));
// Opportunity Table
exports.opportunities = (0, pg_core_1.pgTable)('opportunities', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull().references(() => exports.customers.id, { onDelete: 'cascade' }),
    title: (0, pg_core_1.text)('title').notNull(),
    stage: (0, pg_core_1.text)('stage', { enum: ['Lead', 'Qualified', 'Proposal', 'Won', 'Lost'] }).notNull().default('Lead'),
    expectedCloseDate: (0, pg_core_1.timestamp)('expected_close_date'),
    amountNet: (0, pg_core_1.numeric)('amount_net', { precision: 15, scale: 2 }),
    currency: (0, pg_core_1.text)('currency', { length: 3 }),
    probability: (0, pg_core_1.numeric)('probability', { precision: 3, scale: 2 }).notNull().default('0.10'),
    ownerUserId: (0, pg_core_1.uuid)('owner_user_id'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('opportunities_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('opportunities_customer_idx').on(table.customerId),
    stageIdx: (0, pg_core_1.index)('opportunities_stage_idx').on(table.stage),
    ownerIdx: (0, pg_core_1.index)('opportunities_owner_idx').on(table.ownerUserId),
    amountIdx: (0, pg_core_1.index)('opportunities_amount_idx').on(table.amountNet)
}));
// Interaction Table
exports.interactions = (0, pg_core_1.pgTable)('interactions', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull().references(() => exports.customers.id, { onDelete: 'cascade' }),
    contactId: (0, pg_core_1.uuid)('contact_id').references(() => exports.contacts.id, { onDelete: 'set null' }),
    type: (0, pg_core_1.text)('type', { enum: ['Call', 'Email', 'Visit', 'Note'] }).notNull(),
    subject: (0, pg_core_1.text)('subject').notNull(),
    content: (0, pg_core_1.text)('content').notNull(),
    occurredAt: (0, pg_core_1.timestamp)('occurred_at').notNull(),
    createdBy: (0, pg_core_1.uuid)('created_by').notNull(),
    attachments: (0, pg_core_1.jsonb)('attachments').$type().default([]).notNull(),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('interactions_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('interactions_customer_idx').on(table.customerId),
    contactIdx: (0, pg_core_1.index)('interactions_contact_idx').on(table.contactId),
    typeIdx: (0, pg_core_1.index)('interactions_type_idx').on(table.type),
    occurredAtIdx: (0, pg_core_1.index)('interactions_occurred_at_idx').on(table.occurredAt),
    createdByIdx: (0, pg_core_1.index)('interactions_created_by_idx').on(table.createdBy)
}));
// Export table references for foreign keys
exports.customersRelations = {
    contacts: exports.contacts,
    opportunities: exports.opportunities,
    interactions: exports.interactions
};
exports.contactsRelations = {
    customer: exports.customers,
    interactions: exports.interactions
};
exports.opportunitiesRelations = {
    customer: exports.customers
};
exports.interactionsRelations = {
    customer: exports.customers,
    contact: exports.contacts
};
//# sourceMappingURL=schema.js.map