import { pgTable, uuid, text, integer, decimal, boolean, jsonb, timestamp, index } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// Enums
export const contractTypeEnum = sql`enum('Buy','Sell')`;
export const commodityTypeEnum = sql`enum('WHEAT','BARLEY','RAPESEED','SOYMEAL','COMPOUND_FEED','FERTILIZER')`;
export const contractStatusEnum = sql`enum('Draft','Active','PartiallyFulfilled','Fulfilled','Cancelled','Defaulted')`;
export const pricingModeEnum = sql`enum('FORWARD_CASH','BASIS','HTA','DEFERRED','MIN_PRICE','FIXED','INDEXED')`;
export const shipmentTypeEnum = sql`enum('Spot','Window','CallOff')`;
export const titleTransferTypeEnum = sql`enum('AtDelivery','AtStorage','AtPricing')`;
export const callOffStatusEnum = sql`enum('Planned','Scheduled','Delivered','Invoiced','Cancelled')`;
export const amendmentTypeEnum = sql`enum('QtyChange','WindowChange','PriceRuleChange','CounterpartyChange','DeliveryTermsChange','Other')`;
export const amendmentStatusEnum = sql`enum('Pending','Approved','Rejected','Cancelled')`;

// Contracts table
export const contracts = pgTable('contracts', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: uuid('tenant_id').notNull(),
  contractNo: text('contract_no').notNull(),
  type: text('type', { enum: ['Buy', 'Sell'] }).notNull(),
  commodity: text('commodity', { enum: ['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER'] }).notNull(),
  counterpartyId: uuid('counterparty_id').notNull(),
  incoterm: text('incoterm'),
  deliveryWindowFrom: timestamp('delivery_window_from', { withTimezone: true }).notNull(),
  deliveryWindowTo: timestamp('delivery_window_to', { withTimezone: true }).notNull(),
  qtyUnit: text('qty_unit', { enum: ['t', 'mt'] }).notNull(),
  qtyContracted: decimal('qty_contracted', { precision: 15, scale: 3 }).notNull(),
  qtyTolerance: decimal('qty_tolerance', { precision: 5, scale: 2 }),
  pricingMode: text('pricing_mode', { enum: ['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED'] }).notNull(),
  pricingReferenceMarket: text('pricing_reference_market', { enum: ['CME', 'EURONEXT', 'CASH_INDEX'] }),
  pricingFuturesMonth: text('pricing_futures_month'),
  pricingBasis: decimal('pricing_basis', { precision: 10, scale: 2 }),
  pricingFees: jsonb('pricing_fees'),
  pricingFx: jsonb('pricing_fx'),
  pricingLastFixingAt: timestamp('pricing_last_fixing_at', { withTimezone: true }),
  deliveryShipmentType: text('delivery_shipment_type', { enum: ['Spot', 'Window', 'CallOff'] }).notNull(),
  deliveryParity: text('delivery_parity'),
  deliveryStorage: jsonb('delivery_storage'),
  deliveryQualitySpecs: jsonb('delivery_quality_specs'),
  status: text('status', { enum: ['Draft', 'Active', 'PartiallyFulfilled', 'Fulfilled', 'Cancelled', 'Defaulted'] }).notNull().default('Draft'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => [
  index('contracts_tenant_id_idx').on(table.tenantId),
  index('contracts_counterparty_id_idx').on(table.counterpartyId),
  index('contracts_status_idx').on(table.status),
  index('contracts_commodity_idx').on(table.commodity),
  index('contracts_type_idx').on(table.type),
  index('contracts_delivery_window_idx').on(table.deliveryWindowFrom, table.deliveryWindowTo),
]);

// Call-offs table
export const callOffs = pgTable('call_offs', {
  id: uuid('id').primaryKey().defaultRandom(),
  contractId: uuid('contract_id').notNull().references(() => contracts.id, { onDelete: 'cascade' }),
  tenantId: uuid('tenant_id').notNull(),
  qty: decimal('qty', { precision: 15, scale: 3 }).notNull(),
  windowFrom: timestamp('window_from', { withTimezone: true }).notNull(),
  windowTo: timestamp('window_to', { withTimezone: true }).notNull(),
  site: text('site'),
  silo: text('silo'),
  customerYard: text('customer_yard'),
  status: text('status', { enum: ['Planned', 'Scheduled', 'Delivered', 'Invoiced', 'Cancelled'] }).notNull().default('Planned'),
  notes: text('notes'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => [
  index('call_offs_contract_id_idx').on(table.contractId),
  index('call_offs_tenant_id_idx').on(table.tenantId),
  index('call_offs_status_idx').on(table.status),
  index('call_offs_window_idx').on(table.windowFrom, table.windowTo),
]);

// Fulfilment tracking table
export const fulfilments = pgTable('fulfilments', {
  contractId: uuid('contract_id').primaryKey().references(() => contracts.id, { onDelete: 'cascade' }),
  tenantId: uuid('tenant_id').notNull(),
  deliveredQty: decimal('delivered_qty', { precision: 15, scale: 3 }).notNull().default('0'),
  pricedQty: decimal('priced_qty', { precision: 15, scale: 3 }).notNull().default('0'),
  invoicedQty: decimal('invoiced_qty', { precision: 15, scale: 3 }).notNull().default('0'),
  openQty: decimal('open_qty', { precision: 15, scale: 3 }).notNull(),
  avgPrice: decimal('avg_price', { precision: 10, scale: 2 }),
  timeline: jsonb('timeline').notNull().default([]),
  lastUpdated: timestamp('last_updated', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('fulfilments_tenant_id_idx').on(table.tenantId),
]);

// Amendments table
export const amendments = pgTable('amendments', {
  id: uuid('id').primaryKey().defaultRandom(),
  contractId: uuid('contract_id').notNull().references(() => contracts.id, { onDelete: 'cascade' }),
  tenantId: uuid('tenant_id').notNull(),
  type: text('type', { enum: ['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other'] }).notNull(),
  reason: text('reason').notNull(),
  changes: jsonb('changes').notNull(),
  approvedBy: uuid('approved_by'),
  approvedAt: timestamp('approved_at', { withTimezone: true }),
  status: text('status', { enum: ['Pending', 'Approved', 'Rejected', 'Cancelled'] }).notNull().default('Pending'),
  effectiveAt: timestamp('effective_at', { withTimezone: true }),
  notes: text('notes'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  version: integer('version').notNull().default(1),
}, (table) => [
  index('amendments_contract_id_idx').on(table.contractId),
  index('amendments_tenant_id_idx').on(table.tenantId),
  index('amendments_status_idx').on(table.status),
]);

// Hedge references table
export const hedgeRefs = pgTable('hedge_refs', {
  id: uuid('id').primaryKey().defaultRandom(),
  contractId: uuid('contract_id').notNull().references(() => contracts.id, { onDelete: 'cascade' }),
  tenantId: uuid('tenant_id').notNull(),
  instrument: text('instrument', { enum: ['FUTURES', 'OPTIONS'] }).notNull(),
  market: text('market').notNull(),
  symbol: text('symbol').notNull(),
  month: text('month').notNull(),
  qty: decimal('qty', { precision: 15, scale: 3 }).notNull(),
  side: text('side', { enum: ['BUY', 'SELL'] }).notNull(),
  linkId: text('link_id'), // External reference ID
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('hedge_refs_contract_id_idx').on(table.contractId),
  index('hedge_refs_tenant_id_idx').on(table.tenantId),
  index('hedge_refs_link_id_idx').on(table.linkId),
]);

// Type exports
export type Contract = typeof contracts.$inferSelect;
export type NewContract = typeof contracts.$inferInsert;
export type CallOff = typeof callOffs.$inferSelect;
export type NewCallOff = typeof callOffs.$inferInsert;
export type Fulfilment = typeof fulfilments.$inferSelect;
export type NewFulfilment = typeof fulfilments.$inferInsert;
export type Amendment = typeof amendments.$inferSelect;
export type NewAmendment = typeof amendments.$inferInsert;
export type HedgeRef = typeof hedgeRefs.$inferSelect;
export type NewHedgeRef = typeof hedgeRefs.$inferInsert;