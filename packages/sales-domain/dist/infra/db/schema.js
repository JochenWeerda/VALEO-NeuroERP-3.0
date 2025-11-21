"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.creditNotesRelations = exports.invoicesRelations = exports.ordersRelations = exports.quotesRelations = exports.creditNotes = exports.invoices = exports.orders = exports.quotes = exports.salesOffers = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
// Sales Offer Table
exports.salesOffers = (0, pg_core_1.pgTable)('sales_offers', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerInquiryId: (0, pg_core_1.uuid)('customer_inquiry_id'),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull(),
    offerNumber: (0, pg_core_1.text)('offer_number').notNull().unique(),
    subject: (0, pg_core_1.text)('subject').notNull(),
    description: (0, pg_core_1.text)('description').notNull(),
    totalAmount: (0, pg_core_1.numeric)('total_amount', { precision: 15, scale: 2 }).notNull(),
    currency: (0, pg_core_1.varchar)('currency', { length: 3 }).notNull().default('EUR'),
    validUntil: (0, pg_core_1.timestamp)('valid_until').notNull(),
    status: (0, pg_core_1.text)('status', { enum: ['ENTWURF', 'VERSENDET', 'ANGENOMMEN', 'ABGELEHNT', 'ABGELAUFEN'] }).notNull().default('ENTWURF'),
    contactPerson: (0, pg_core_1.text)('contact_person'),
    deliveryDate: (0, pg_core_1.timestamp)('delivery_date'),
    paymentTerms: (0, pg_core_1.text)('payment_terms'),
    notes: (0, pg_core_1.text)('notes'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    deletedAt: (0, pg_core_1.timestamp)('deleted_at'),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('sales_offers_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('sales_offers_customer_idx').on(table.customerId),
    customerInquiryIdx: (0, pg_core_1.index)('sales_offers_customer_inquiry_idx').on(table.customerInquiryId),
    statusIdx: (0, pg_core_1.index)('sales_offers_status_idx').on(table.status),
    validUntilIdx: (0, pg_core_1.index)('sales_offers_valid_until_idx').on(table.validUntil)
}));
// Quote Table
exports.quotes = (0, pg_core_1.pgTable)('quotes', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull(),
    quoteNumber: (0, pg_core_1.text)('quote_number').notNull().unique(),
    lines: (0, pg_core_1.jsonb)('lines').$type().notNull(),
    subtotalNet: (0, pg_core_1.numeric)('subtotal_net', { precision: 15, scale: 2 }).notNull(),
    totalDiscount: (0, pg_core_1.numeric)('total_discount', { precision: 15, scale: 2 }).notNull(),
    totalNet: (0, pg_core_1.numeric)('total_net', { precision: 15, scale: 2 }).notNull(),
    totalGross: (0, pg_core_1.numeric)('total_gross', { precision: 15, scale: 2 }).notNull(),
    taxRate: (0, pg_core_1.numeric)('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
    currency: (0, pg_core_1.varchar)('currency', { length: 3 }).notNull().default('EUR'),
    validUntil: (0, pg_core_1.timestamp)('valid_until').notNull(),
    notes: (0, pg_core_1.text)('notes'),
    status: (0, pg_core_1.text)('status', { enum: ['Draft', 'Sent', 'Accepted', 'Rejected', 'Expired'] }).notNull().default('Draft'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('quotes_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('quotes_customer_idx').on(table.customerId),
    statusIdx: (0, pg_core_1.index)('quotes_status_idx').on(table.status),
    validUntilIdx: (0, pg_core_1.index)('quotes_valid_until_idx').on(table.validUntil)
}));
// Order Table
exports.orders = (0, pg_core_1.pgTable)('orders', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull(),
    orderNumber: (0, pg_core_1.text)('order_number').notNull().unique(),
    lines: (0, pg_core_1.jsonb)('lines').$type().notNull(),
    subtotalNet: (0, pg_core_1.numeric)('subtotal_net', { precision: 15, scale: 2 }).notNull(),
    totalDiscount: (0, pg_core_1.numeric)('total_discount', { precision: 15, scale: 2 }).notNull(),
    totalNet: (0, pg_core_1.numeric)('total_net', { precision: 15, scale: 2 }).notNull(),
    totalGross: (0, pg_core_1.numeric)('total_gross', { precision: 15, scale: 2 }).notNull(),
    taxRate: (0, pg_core_1.numeric)('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
    currency: (0, pg_core_1.varchar)('currency', { length: 3 }).notNull().default('EUR'),
    expectedDeliveryDate: (0, pg_core_1.timestamp)('expected_delivery_date'),
    notes: (0, pg_core_1.text)('notes'),
    status: (0, pg_core_1.text)('status', { enum: ['Draft', 'Confirmed', 'Invoiced', 'Cancelled'] }).notNull().default('Draft'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('orders_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('orders_customer_idx').on(table.customerId),
    statusIdx: (0, pg_core_1.index)('orders_status_idx').on(table.status),
    deliveryDateIdx: (0, pg_core_1.index)('orders_delivery_date_idx').on(table.expectedDeliveryDate)
}));
// Invoice Table
exports.invoices = (0, pg_core_1.pgTable)('invoices', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull(),
    orderId: (0, pg_core_1.uuid)('order_id').references(() => exports.orders.id, { onDelete: 'set null' }),
    invoiceNumber: (0, pg_core_1.text)('invoice_number').notNull().unique(),
    lines: (0, pg_core_1.jsonb)('lines').$type().notNull(),
    subtotalNet: (0, pg_core_1.numeric)('subtotal_net', { precision: 15, scale: 2 }).notNull(),
    totalDiscount: (0, pg_core_1.numeric)('total_discount', { precision: 15, scale: 2 }).notNull(),
    totalNet: (0, pg_core_1.numeric)('total_net', { precision: 15, scale: 2 }).notNull(),
    totalGross: (0, pg_core_1.numeric)('total_gross', { precision: 15, scale: 2 }).notNull(),
    taxRate: (0, pg_core_1.numeric)('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
    currency: (0, pg_core_1.varchar)('currency', { length: 3 }).notNull().default('EUR'),
    dueDate: (0, pg_core_1.timestamp)('due_date').notNull(),
    paidAt: (0, pg_core_1.timestamp)('paid_at'),
    notes: (0, pg_core_1.text)('notes'),
    status: (0, pg_core_1.text)('status', { enum: ['Issued', 'Paid', 'Overdue', 'Cancelled'] }).notNull().default('Issued'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('invoices_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('invoices_customer_idx').on(table.customerId),
    orderIdx: (0, pg_core_1.index)('invoices_order_idx').on(table.orderId),
    statusIdx: (0, pg_core_1.index)('invoices_status_idx').on(table.status),
    dueDateIdx: (0, pg_core_1.index)('invoices_due_date_idx').on(table.dueDate)
}));
// Credit Note Table
exports.creditNotes = (0, pg_core_1.pgTable)('credit_notes', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    customerId: (0, pg_core_1.uuid)('customer_id').notNull(),
    invoiceId: (0, pg_core_1.uuid)('invoice_id').notNull().references(() => exports.invoices.id, { onDelete: 'cascade' }),
    creditNumber: (0, pg_core_1.text)('credit_number').notNull().unique(),
    lines: (0, pg_core_1.jsonb)('lines').$type().notNull(),
    subtotalNet: (0, pg_core_1.numeric)('subtotal_net', { precision: 15, scale: 2 }).notNull(),
    totalDiscount: (0, pg_core_1.numeric)('total_discount', { precision: 15, scale: 2 }).notNull(),
    totalNet: (0, pg_core_1.numeric)('total_net', { precision: 15, scale: 2 }).notNull(),
    totalGross: (0, pg_core_1.numeric)('total_gross', { precision: 15, scale: 2 }).notNull(),
    taxRate: (0, pg_core_1.numeric)('tax_rate', { precision: 5, scale: 2 }).notNull().default('19.00'),
    currency: (0, pg_core_1.varchar)('currency', { length: 3 }).notNull().default('EUR'),
    reason: (0, pg_core_1.text)('reason').notNull(),
    notes: (0, pg_core_1.text)('notes'),
    status: (0, pg_core_1.text)('status', { enum: ['Issued', 'Settled'] }).notNull().default('Issued'),
    settledAt: (0, pg_core_1.timestamp)('settled_at'),
    createdAt: (0, pg_core_1.timestamp)('created_at').notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at').notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1)
}, (table) => ({
    tenantIdx: (0, pg_core_1.index)('credit_notes_tenant_idx').on(table.tenantId),
    customerIdx: (0, pg_core_1.index)('credit_notes_customer_idx').on(table.customerId),
    invoiceIdx: (0, pg_core_1.index)('credit_notes_invoice_idx').on(table.invoiceId),
    statusIdx: (0, pg_core_1.index)('credit_notes_status_idx').on(table.status)
}));
// Export table references for foreign keys
exports.quotesRelations = {
    orders: exports.orders
};
exports.ordersRelations = {
    quote: exports.quotes,
    invoices: exports.invoices
};
exports.invoicesRelations = {
    order: exports.orders,
    creditNotes: exports.creditNotes
};
exports.creditNotesRelations = {
    invoice: exports.invoices
};
//# sourceMappingURL=schema.js.map