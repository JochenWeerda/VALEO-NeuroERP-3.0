import { pgTable, uuid, text, varchar, timestamp, boolean, integer, numeric, jsonb, index } from 'drizzle-orm/pg-core';

// Sales Offer Table
export const salesOffers = pgTable('sales_offers', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerInquiryId: uuid('customer_inquiry_id'),
  customerId: uuid('customer_id').notNull(),
  offerNumber: text('offer_number').notNull().unique(),
  subject: text('subject').notNull(),
  description: text('description').notNull(),
  totalAmount: numeric('total_amount', { precision: 15, scale: 2 }).notNull(),
  currency: varchar('currency', { length: 3 }).notNull().default('EUR'),
  validUntil: timestamp('valid_until').notNull(),
  status: text('status', { enum: ['ENTWURF', 'VERSENDET', 'ANGENOMMEN', 'ABGELEHNT', 'ABGELAUFEN'] }).notNull().default('ENTWURF'),
  contactPerson: text('contact_person'),
  deliveryDate: timestamp('delivery_date'),
  paymentTerms: text('payment_terms'),
  notes: text('notes'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  deletedAt: timestamp('deleted_at'),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('sales_offers_tenant_idx').on(table.tenantId),
  customerIdx: index('sales_offers_customer_idx').on(table.customerId),
  customerInquiryIdx: index('sales_offers_customer_inquiry_idx').on(table.customerInquiryId),
  statusIdx: index('sales_offers_status_idx').on(table.status),
  validUntilIdx: index('sales_offers_valid_until_idx').on(table.validUntil)
}));

// Quote Table
export const quotes = pgTable('quotes', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull(),
  quoteNumber: text('quote_number').notNull().unique(),
  lines: jsonb('lines').$type<QuoteLine[]>().notNull(),
  subtotalNet: numeric('subtotal_net', { precision: 15, scale: 2 }).notNull(),
  totalDiscount: numeric('total_discount', { precision: 15, scale: 2 }).notNull(),
  totalNet: numeric('total_net', { precision: 15, scale: 2 }).notNull(),
  totalGross: numeric('total_gross', { precision: 15, scale: 2 }).notNull(),
  taxRate: numeric('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
  currency: varchar('currency', { length: 3 }).notNull().default('EUR'),
  validUntil: timestamp('valid_until').notNull(),
  notes: text('notes'),
  status: text('status', { enum: ['Draft', 'Sent', 'Accepted', 'Rejected', 'Expired'] }).notNull().default('Draft'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('quotes_tenant_idx').on(table.tenantId),
  customerIdx: index('quotes_customer_idx').on(table.customerId),
  statusIdx: index('quotes_status_idx').on(table.status),
  validUntilIdx: index('quotes_valid_until_idx').on(table.validUntil)
}));

// Order Table
export const orders = pgTable('orders', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull(),
  orderNumber: text('order_number').notNull().unique(),
  lines: jsonb('lines').$type<OrderLine[]>().notNull(),
  subtotalNet: numeric('subtotal_net', { precision: 15, scale: 2 }).notNull(),
  totalDiscount: numeric('total_discount', { precision: 15, scale: 2 }).notNull(),
  totalNet: numeric('total_net', { precision: 15, scale: 2 }).notNull(),
  totalGross: numeric('total_gross', { precision: 15, scale: 2 }).notNull(),
  taxRate: numeric('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
  currency: varchar('currency', { length: 3 }).notNull().default('EUR'),
  expectedDeliveryDate: timestamp('expected_delivery_date'),
  notes: text('notes'),
  status: text('status', { enum: ['Draft', 'Confirmed', 'Invoiced', 'Cancelled'] }).notNull().default('Draft'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('orders_tenant_idx').on(table.tenantId),
  customerIdx: index('orders_customer_idx').on(table.customerId),
  statusIdx: index('orders_status_idx').on(table.status),
  deliveryDateIdx: index('orders_delivery_date_idx').on(table.expectedDeliveryDate)
}));

// Invoice Table
export const invoices = pgTable('invoices', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull(),
  orderId: uuid('order_id').references(() => orders.id, { onDelete: 'set null' }),
  invoiceNumber: text('invoice_number').notNull().unique(),
  lines: jsonb('lines').$type<InvoiceLine[]>().notNull(),
  subtotalNet: numeric('subtotal_net', { precision: 15, scale: 2 }).notNull(),
  totalDiscount: numeric('total_discount', { precision: 15, scale: 2 }).notNull(),
  totalNet: numeric('total_net', { precision: 15, scale: 2 }).notNull(),
  totalGross: numeric('total_gross', { precision: 15, scale: 2 }).notNull(),
  taxRate: numeric('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
  currency: varchar('currency', { length: 3 }).notNull().default('EUR'),
  dueDate: timestamp('due_date').notNull(),
  paidAt: timestamp('paid_at'),
  notes: text('notes'),
  status: text('status', { enum: ['Issued', 'Paid', 'Overdue', 'Cancelled'] }).notNull().default('Issued'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('invoices_tenant_idx').on(table.tenantId),
  customerIdx: index('invoices_customer_idx').on(table.customerId),
  orderIdx: index('invoices_order_idx').on(table.orderId),
  statusIdx: index('invoices_status_idx').on(table.status),
  dueDateIdx: index('invoices_due_date_idx').on(table.dueDate)
}));

// Credit Note Table
export const creditNotes = pgTable('credit_notes', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  customerId: uuid('customer_id').notNull(),
  invoiceId: uuid('invoice_id').notNull().references(() => invoices.id, { onDelete: 'cascade' }),
  creditNumber: text('credit_number').notNull().unique(),
  lines: jsonb('lines').$type<CreditNoteLine[]>().notNull(),
  subtotalNet: numeric('subtotal_net', { precision: 15, scale: 2 }).notNull(),
  totalDiscount: numeric('total_discount', { precision: 15, scale: 2 }).notNull(),
  totalNet: numeric('total_net', { precision: 15, scale: 2 }).notNull(),
  totalGross: numeric('total_gross', { precision: 15, scale: 2 }).notNull(),
  taxRate: numeric('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
  currency: varchar('currency', { length: 3 }).notNull().default('EUR'),
  reason: text('reason').notNull(),
  notes: text('notes'),
  status: text('status', { enum: ['Issued', 'Settled'] }).notNull().default('Issued'),
  settledAt: timestamp('settled_at'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  version: integer('version').notNull().default(1)
}, (table) => ({
  tenantIdx: index('credit_notes_tenant_idx').on(table.tenantId),
  customerIdx: index('credit_notes_customer_idx').on(table.customerId),
  invoiceIdx: index('credit_notes_invoice_idx').on(table.invoiceId),
  statusIdx: index('credit_notes_status_idx').on(table.status)
}));

// Type definitions for JSONB columns
export interface QuoteLine {
  id: string;
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  totalNet: number;
  totalGross: number;
}

export interface OrderLine {
  id: string;
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  totalNet: number;
  totalGross: number;
}

export interface InvoiceLine {
  id: string;
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  totalNet: number;
  totalGross: number;
}

export interface CreditNoteLine {
  id: string;
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  totalNet: number;
  totalGross: number;
}

// Export table references for foreign keys
export const quotesRelations = {
  orders: orders
};

export const ordersRelations = {
  quote: quotes,
  invoices: invoices
};

export const invoicesRelations = {
  order: orders,
  creditNotes: creditNotes
};

export const creditNotesRelations = {
  invoice: invoices
};