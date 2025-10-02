"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.hedgeRefs = exports.amendments = exports.fulfilments = exports.callOffs = exports.contracts = exports.amendmentStatusEnum = exports.amendmentTypeEnum = exports.callOffStatusEnum = exports.titleTransferTypeEnum = exports.shipmentTypeEnum = exports.pricingModeEnum = exports.contractStatusEnum = exports.commodityTypeEnum = exports.contractTypeEnum = void 0;
const pg_core_1 = require("drizzle-orm/pg-core");
const drizzle_orm_1 = require("drizzle-orm");
exports.contractTypeEnum = (0, drizzle_orm_1.sql) `enum('Buy','Sell')`;
exports.commodityTypeEnum = (0, drizzle_orm_1.sql) `enum('WHEAT','BARLEY','RAPESEED','SOYMEAL','COMPOUND_FEED','FERTILIZER')`;
exports.contractStatusEnum = (0, drizzle_orm_1.sql) `enum('Draft','Active','PartiallyFulfilled','Fulfilled','Cancelled','Defaulted')`;
exports.pricingModeEnum = (0, drizzle_orm_1.sql) `enum('FORWARD_CASH','BASIS','HTA','DEFERRED','MIN_PRICE','FIXED','INDEXED')`;
exports.shipmentTypeEnum = (0, drizzle_orm_1.sql) `enum('Spot','Window','CallOff')`;
exports.titleTransferTypeEnum = (0, drizzle_orm_1.sql) `enum('AtDelivery','AtStorage','AtPricing')`;
exports.callOffStatusEnum = (0, drizzle_orm_1.sql) `enum('Planned','Scheduled','Delivered','Invoiced','Cancelled')`;
exports.amendmentTypeEnum = (0, drizzle_orm_1.sql) `enum('QtyChange','WindowChange','PriceRuleChange','CounterpartyChange','DeliveryTermsChange','Other')`;
exports.amendmentStatusEnum = (0, drizzle_orm_1.sql) `enum('Pending','Approved','Rejected','Cancelled')`;
exports.contracts = (0, pg_core_1.pgTable)('contracts', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    contractNo: (0, pg_core_1.text)('contract_no').notNull(),
    type: (0, pg_core_1.text)('type', { enum: ['Buy', 'Sell'] }).notNull(),
    commodity: (0, pg_core_1.text)('commodity', { enum: ['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER'] }).notNull(),
    counterpartyId: (0, pg_core_1.uuid)('counterparty_id').notNull(),
    incoterm: (0, pg_core_1.text)('incoterm'),
    deliveryWindowFrom: (0, pg_core_1.timestamp)('delivery_window_from', { withTimezone: true }).notNull(),
    deliveryWindowTo: (0, pg_core_1.timestamp)('delivery_window_to', { withTimezone: true }).notNull(),
    qtyUnit: (0, pg_core_1.text)('qty_unit', { enum: ['t', 'mt'] }).notNull(),
    qtyContracted: (0, pg_core_1.decimal)('qty_contracted', { precision: 15, scale: 3 }).notNull(),
    qtyTolerance: (0, pg_core_1.decimal)('qty_tolerance', { precision: 5, scale: 2 }),
    pricingMode: (0, pg_core_1.text)('pricing_mode', { enum: ['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED'] }).notNull(),
    pricingReferenceMarket: (0, pg_core_1.text)('pricing_reference_market', { enum: ['CME', 'EURONEXT', 'CASH_INDEX'] }),
    pricingFuturesMonth: (0, pg_core_1.text)('pricing_futures_month'),
    pricingBasis: (0, pg_core_1.decimal)('pricing_basis', { precision: 10, scale: 2 }),
    pricingFees: (0, pg_core_1.jsonb)('pricing_fees'),
    pricingFx: (0, pg_core_1.jsonb)('pricing_fx'),
    pricingLastFixingAt: (0, pg_core_1.timestamp)('pricing_last_fixing_at', { withTimezone: true }),
    deliveryShipmentType: (0, pg_core_1.text)('delivery_shipment_type', { enum: ['Spot', 'Window', 'CallOff'] }).notNull(),
    deliveryParity: (0, pg_core_1.text)('delivery_parity'),
    deliveryStorage: (0, pg_core_1.jsonb)('delivery_storage'),
    deliveryQualitySpecs: (0, pg_core_1.jsonb)('delivery_quality_specs'),
    status: (0, pg_core_1.text)('status', { enum: ['Draft', 'Active', 'PartiallyFulfilled', 'Fulfilled', 'Cancelled', 'Defaulted'] }).notNull().default('Draft'),
    createdAt: (0, pg_core_1.timestamp)('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at', { withTimezone: true }).notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
}, (table) => ({
    tenantIdIdx: (0, pg_core_1.index)('contracts_tenant_id_idx').on(table.tenantId),
    counterpartyIdIdx: (0, pg_core_1.index)('contracts_counterparty_id_idx').on(table.counterpartyId),
    statusIdx: (0, pg_core_1.index)('contracts_status_idx').on(table.status),
    commodityIdx: (0, pg_core_1.index)('contracts_commodity_idx').on(table.commodity),
    typeIdx: (0, pg_core_1.index)('contracts_type_idx').on(table.type),
    deliveryWindowIdx: (0, pg_core_1.index)('contracts_delivery_window_idx').on(table.deliveryWindowFrom, table.deliveryWindowTo),
}));
exports.callOffs = (0, pg_core_1.pgTable)('call_offs', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    contractId: (0, pg_core_1.uuid)('contract_id').notNull().references(() => exports.contracts.id, { onDelete: 'cascade' }),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    qty: (0, pg_core_1.decimal)('qty', { precision: 15, scale: 3 }).notNull(),
    windowFrom: (0, pg_core_1.timestamp)('window_from', { withTimezone: true }).notNull(),
    windowTo: (0, pg_core_1.timestamp)('window_to', { withTimezone: true }).notNull(),
    site: (0, pg_core_1.text)('site'),
    silo: (0, pg_core_1.text)('silo'),
    customerYard: (0, pg_core_1.text)('customer_yard'),
    status: (0, pg_core_1.text)('status', { enum: ['Planned', 'Scheduled', 'Delivered', 'Invoiced', 'Cancelled'] }).notNull().default('Planned'),
    notes: (0, pg_core_1.text)('notes'),
    createdAt: (0, pg_core_1.timestamp)('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at', { withTimezone: true }).notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
}, (table) => ({
    contractIdIdx: (0, pg_core_1.index)('call_offs_contract_id_idx').on(table.contractId),
    tenantIdIdx: (0, pg_core_1.index)('call_offs_tenant_id_idx').on(table.tenantId),
    statusIdx: (0, pg_core_1.index)('call_offs_status_idx').on(table.status),
    windowIdx: (0, pg_core_1.index)('call_offs_window_idx').on(table.windowFrom, table.windowTo),
}));
exports.fulfilments = (0, pg_core_1.pgTable)('fulfilments', {
    contractId: (0, pg_core_1.uuid)('contract_id').primaryKey().references(() => exports.contracts.id, { onDelete: 'cascade' }),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    deliveredQty: (0, pg_core_1.decimal)('delivered_qty', { precision: 15, scale: 3 }).notNull().default('0'),
    pricedQty: (0, pg_core_1.decimal)('priced_qty', { precision: 15, scale: 3 }).notNull().default('0'),
    invoicedQty: (0, pg_core_1.decimal)('invoiced_qty', { precision: 15, scale: 3 }).notNull().default('0'),
    openQty: (0, pg_core_1.decimal)('open_qty', { precision: 15, scale: 3 }).notNull(),
    avgPrice: (0, pg_core_1.decimal)('avg_price', { precision: 10, scale: 2 }),
    timeline: (0, pg_core_1.jsonb)('timeline').notNull().default([]),
    lastUpdated: (0, pg_core_1.timestamp)('last_updated', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
    tenantIdIdx: (0, pg_core_1.index)('fulfilments_tenant_id_idx').on(table.tenantId),
}));
exports.amendments = (0, pg_core_1.pgTable)('amendments', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    contractId: (0, pg_core_1.uuid)('contract_id').notNull().references(() => exports.contracts.id, { onDelete: 'cascade' }),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    type: (0, pg_core_1.text)('type', { enum: ['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other'] }).notNull(),
    reason: (0, pg_core_1.text)('reason').notNull(),
    changes: (0, pg_core_1.jsonb)('changes').notNull(),
    approvedBy: (0, pg_core_1.uuid)('approved_by'),
    approvedAt: (0, pg_core_1.timestamp)('approved_at', { withTimezone: true }),
    status: (0, pg_core_1.text)('status', { enum: ['Pending', 'Approved', 'Rejected', 'Cancelled'] }).notNull().default('Pending'),
    effectiveAt: (0, pg_core_1.timestamp)('effective_at', { withTimezone: true }),
    notes: (0, pg_core_1.text)('notes'),
    createdAt: (0, pg_core_1.timestamp)('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: (0, pg_core_1.timestamp)('updated_at', { withTimezone: true }).notNull().defaultNow(),
    version: (0, pg_core_1.integer)('version').notNull().default(1),
}, (table) => ({
    contractIdIdx: (0, pg_core_1.index)('amendments_contract_id_idx').on(table.contractId),
    tenantIdIdx: (0, pg_core_1.index)('amendments_tenant_id_idx').on(table.tenantId),
    statusIdx: (0, pg_core_1.index)('amendments_status_idx').on(table.status),
}));
exports.hedgeRefs = (0, pg_core_1.pgTable)('hedge_refs', {
    id: (0, pg_core_1.uuid)('id').primaryKey().defaultRandom(),
    contractId: (0, pg_core_1.uuid)('contract_id').notNull().references(() => exports.contracts.id, { onDelete: 'cascade' }),
    tenantId: (0, pg_core_1.uuid)('tenant_id').notNull(),
    instrument: (0, pg_core_1.text)('instrument', { enum: ['FUTURES', 'OPTIONS'] }).notNull(),
    market: (0, pg_core_1.text)('market').notNull(),
    symbol: (0, pg_core_1.text)('symbol').notNull(),
    month: (0, pg_core_1.text)('month').notNull(),
    qty: (0, pg_core_1.decimal)('qty', { precision: 15, scale: 3 }).notNull(),
    side: (0, pg_core_1.text)('side', { enum: ['BUY', 'SELL'] }).notNull(),
    linkId: (0, pg_core_1.text)('link_id'),
    createdAt: (0, pg_core_1.timestamp)('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => ({
    contractIdIdx: (0, pg_core_1.index)('hedge_refs_contract_id_idx').on(table.contractId),
    tenantIdIdx: (0, pg_core_1.index)('hedge_refs_tenant_id_idx').on(table.tenantId),
    linkIdIdx: (0, pg_core_1.index)('hedge_refs_link_id_idx').on(table.linkId),
}));
//# sourceMappingURL=schema.js.map