import { pgTable, text, integer, decimal, timestamp, uuid, jsonb, boolean, index } from 'drizzle-orm/pg-core';

// Base columns for all tables
const baseColumns = {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  version: integer('version').default(1).notNull(),
};

// KPI Table
export const kpis = pgTable('kpis', {
  ...baseColumns,
  name: text('name').notNull(),
  description: text('description').notNull(),
  value: text('value').notNull(), // Store as text to handle numbers, strings, booleans
  unit: text('unit').notNull(),
  context: jsonb('context'), // Commodity, contract, batch, site, customer, supplier, period
  calculatedAt: timestamp('calculated_at').defaultNow().notNull(),
  metadata: jsonb('metadata'), // Calculation method, data source, confidence, etc.
}, (table) => ({
  tenantNameIdx: index('kpis_tenant_name_idx').on(table.tenantId, table.name),
  tenantCalculatedIdx: index('kpis_tenant_calculated_idx').on(table.tenantId, table.calculatedAt),
}));

// Reports Table
export const reports = pgTable('reports', {
  ...baseColumns,
  type: text('type').notNull(), // Contracts, Inventory, Weighing, Finance, Quality, etc.
  parameters: jsonb('parameters').notNull(),
  generatedAt: timestamp('generated_at').defaultNow().notNull(),
  uri: text('uri'), // S3 URI or file path for report content
  format: text('format').default('json').notNull(), // json, csv, excel, pdf
  metadata: jsonb('metadata'), // Total records, execution time, checksum, etc.
}, (table) => ({
  tenantTypeIdx: index('reports_tenant_type_idx').on(table.tenantId, table.type),
  tenantGeneratedIdx: index('reports_tenant_generated_idx').on(table.tenantId, table.generatedAt),
}));

// Forecasts Table
export const forecasts = pgTable('forecasts', {
  ...baseColumns,
  metricName: text('metric_name').notNull(),
  horizon: integer('horizon').notNull(), // Number of time units
  horizonUnit: text('horizon_unit').notNull(), // days, weeks, months, quarters, years
  model: text('model').notNull(), // ARIMA, ExponentialSmoothing, etc.
  forecastValues: jsonb('forecast_values').notNull(), // Array of forecast data points
  confidenceInterval: decimal('confidence_interval', { precision: 3, scale: 2 }), // 0.95 for 95%
  metadata: jsonb('metadata'), // Training data points, accuracy metrics, etc.
}, (table) => ({
  tenantMetricIdx: index('forecasts_tenant_metric_idx').on(table.tenantId, table.metricName),
  tenantCreatedIdx: index('forecasts_tenant_created_idx').on(table.tenantId, table.createdAt),
}));

// Fact Tables for Event Ingestion

// Contract Events Fact Table
export const factContracts = pgTable('fact_contracts', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  contractId: text('contract_id').notNull(),
  customerId: text('customer_id'),
  supplierId: text('supplier_id'),
  commodity: text('commodity').notNull(),
  quantity: decimal('quantity', { precision: 15, scale: 3 }),
  unit: text('unit'),
  price: decimal('price', { precision: 10, scale: 4 }),
  currency: text('currency').default('EUR'),
  status: text('status'), // Draft, Confirmed, Active, Completed, Cancelled
  deliveryStart: timestamp('delivery_start'),
  deliveryEnd: timestamp('delivery_end'),
  contractType: text('contract_type'), // Purchase, Sales
  hedgingRequired: boolean('hedging_required').default(false),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_contracts_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantCommodityIdx: index('fact_contracts_tenant_commodity_idx').on(table.tenantId, table.commodity),
  tenantStatusIdx: index('fact_contracts_tenant_status_idx').on(table.tenantId, table.status),
  tenantOccurredIdx: index('fact_contracts_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Production Events Fact Table
export const factProduction = pgTable('fact_production', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  batchId: text('batch_id').notNull(),
  contractId: text('contract_id'),
  commodity: text('commodity').notNull(),
  quantity: decimal('quantity', { precision: 15, scale: 3 }),
  unit: text('unit'),
  qualityGrade: text('quality_grade'),
  moisture: decimal('moisture', { precision: 5, scale: 2 }),
  protein: decimal('protein', { precision: 5, scale: 2 }),
  status: text('status'), // Started, InProgress, Completed, Rejected
  siteId: text('site_id'),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_production_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantBatchIdx: index('fact_production_tenant_batch_idx').on(table.tenantId, table.batchId),
  tenantCommodityIdx: index('fact_production_tenant_commodity_idx').on(table.tenantId, table.commodity),
  tenantOccurredIdx: index('fact_production_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Weighing Events Fact Table
export const factWeighing = pgTable('fact_weighing', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  ticketId: text('ticket_id').notNull(),
  contractId: text('contract_id'),
  orderId: text('order_id'),
  customerId: text('customer_id'),
  commodity: text('commodity').notNull(),
  grossWeight: decimal('gross_weight', { precision: 10, scale: 3 }),
  tareWeight: decimal('tare_weight', { precision: 10, scale: 3 }),
  netWeight: decimal('net_weight', { precision: 10, scale: 3 }),
  unit: text('unit').default('kg'),
  tolerancePercent: decimal('tolerance_percent', { precision: 5, scale: 2 }),
  isWithinTolerance: boolean('is_within_tolerance'),
  status: text('status'), // Draft, InProgress, Completed, Cancelled
  siteId: text('site_id'),
  gateId: text('gate_id'),
  licensePlate: text('license_plate'),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_weighing_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantTicketIdx: index('fact_weighing_tenant_ticket_idx').on(table.tenantId, table.ticketId),
  tenantCommodityIdx: index('fact_weighing_tenant_commodity_idx').on(table.tenantId, table.commodity),
  tenantStatusIdx: index('fact_weighing_tenant_status_idx').on(table.tenantId, table.status),
  tenantOccurredIdx: index('fact_weighing_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Quality Events Fact Table
export const factQuality = pgTable('fact_quality', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  sampleId: text('sample_id').notNull(),
  batchId: text('batch_id'),
  contractId: text('contract_id'),
  commodity: text('commodity').notNull(),
  testType: text('test_type'), // Moisture, Protein, Foreign Matter, etc.
  testResult: text('test_result'),
  numericResult: decimal('numeric_result', { precision: 10, scale: 4 }),
  unit: text('unit'),
  isPassed: boolean('is_passed'),
  testedBy: text('tested_by'),
  siteId: text('site_id'),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_quality_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantSampleIdx: index('fact_quality_tenant_sample_idx').on(table.tenantId, table.sampleId),
  tenantCommodityIdx: index('fact_quality_tenant_commodity_idx').on(table.tenantId, table.commodity),
  tenantPassedIdx: index('fact_quality_tenant_passed_idx').on(table.tenantId, table.isPassed),
  tenantOccurredIdx: index('fact_quality_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Regulatory Events Fact Table
export const factRegulatory = pgTable('fact_regulatory', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  batchId: text('batch_id'),
  contractId: text('contract_id'),
  commodity: text('commodity').notNull(),
  labelType: text('label_type'), // Organic, Non-GMO, etc.
  isEligible: boolean('is_eligible'),
  certificationNumber: text('certification_number'),
  expiryDate: timestamp('expiry_date'),
  issuedBy: text('issued_by'),
  siteId: text('site_id'),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_regulatory_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantBatchIdx: index('fact_regulatory_tenant_batch_idx').on(table.tenantId, table.batchId),
  tenantCommodityIdx: index('fact_regulatory_tenant_commodity_idx').on(table.tenantId, table.commodity),
  tenantEligibleIdx: index('fact_regulatory_tenant_eligible_idx').on(table.tenantId, table.isEligible),
  tenantOccurredIdx: index('fact_regulatory_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Finance Events Fact Table
export const factFinance = pgTable('fact_finance', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  eventId: text('event_id').notNull(),
  eventType: text('event_type').notNull(),
  occurredAt: timestamp('occurred_at').notNull(),
  invoiceId: text('invoice_id'),
  contractId: text('contract_id'),
  customerId: text('customer_id'),
  supplierId: text('supplier_id'),
  commodity: text('commodity'),
  amount: decimal('amount', { precision: 15, scale: 2 }),
  currency: text('currency').default('EUR'),
  type: text('type'), // Revenue, Cost, Payment, etc.
  status: text('status'), // Pending, Paid, Overdue, Cancelled
  dueDate: timestamp('due_date'),
  paidDate: timestamp('paid_date'),
  metadata: jsonb('metadata'),
}, (table) => ({
  tenantEventIdx: index('fact_finance_tenant_event_idx').on(table.tenantId, table.eventId),
  tenantInvoiceIdx: index('fact_finance_tenant_invoice_idx').on(table.tenantId, table.invoiceId),
  tenantCustomerIdx: index('fact_finance_tenant_customer_idx').on(table.tenantId, table.customerId),
  tenantStatusIdx: index('fact_finance_tenant_status_idx').on(table.tenantId, table.status),
  tenantOccurredIdx: index('fact_finance_tenant_occurred_idx').on(table.tenantId, table.occurredAt),
}));

// Materialized Views (defined as regular tables for simplicity)
// These would be refreshed periodically or on-demand

export const mvContractPositions = pgTable('mv_contract_positions', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity').notNull(),
  month: text('month').notNull(), // YYYY-MM format
  shortPosition: decimal('short_position', { precision: 15, scale: 3 }).default('0'),
  longPosition: decimal('long_position', { precision: 15, scale: 3 }).default('0'),
  netPosition: decimal('net_position', { precision: 15, scale: 3 }).default('0'),
  hedgingRatio: decimal('hedging_ratio', { precision: 5, scale: 4 }),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityMonthIdx: index('mv_contract_positions_tenant_commodity_month_idx').on(table.tenantId, table.commodity, table.month),
}));

export const mvInventoryBalances = pgTable('mv_inventory_balances', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity').notNull(),
  siteId: text('site_id'),
  currentBalance: decimal('current_balance', { precision: 15, scale: 3 }).default('0'),
  reservedBalance: decimal('reserved_balance', { precision: 15, scale: 3 }).default('0'),
  availableBalance: decimal('available_balance', { precision: 15, scale: 3 }).default('0'),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityIdx: index('mv_inventory_balances_tenant_commodity_idx').on(table.tenantId, table.commodity),
}));

export const mvQualityStats = pgTable('mv_quality_stats', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity').notNull(),
  period: text('period').notNull(), // YYYY-MM format
  totalSamples: integer('total_samples').default(0),
  passedSamples: integer('passed_samples').default(0),
  failedSamples: integer('failed_samples').default(0),
  passRate: decimal('pass_rate', { precision: 5, scale: 4 }),
  failureRate: decimal('failure_rate', { precision: 5, scale: 4 }),
  avgMoisture: decimal('avg_moisture', { precision: 5, scale: 2 }),
  avgProtein: decimal('avg_protein', { precision: 5, scale: 2 }),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityPeriodIdx: index('mv_quality_stats_tenant_commodity_period_idx').on(table.tenantId, table.commodity, table.period),
}));

export const mvRegulatoryStats = pgTable('mv_regulatory_stats', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity').notNull(),
  labelType: text('label_type').notNull(),
  period: text('period').notNull(), // YYYY-MM format
  totalEligible: integer('total_eligible').default(0),
  totalIneligible: integer('total_ineligible').default(0),
  eligibilityRate: decimal('eligibility_rate', { precision: 5, scale: 4 }),
  ineligibilityRate: decimal('ineligibility_rate', { precision: 5, scale: 4 }),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityLabelPeriodIdx: index('mv_regulatory_stats_tenant_commodity_label_period_idx').on(table.tenantId, table.commodity, table.labelType, table.period),
}));

export const mvFinanceKpis = pgTable('mv_finance_kpis', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity'),
  customerId: text('customer_id'),
  period: text('period').notNull(), // YYYY-MM format
  totalRevenue: decimal('total_revenue', { precision: 15, scale: 2 }).default('0'),
  totalCost: decimal('total_cost', { precision: 15, scale: 2 }).default('0'),
  grossMargin: decimal('gross_margin', { precision: 15, scale: 2 }).default('0'),
  marginPercentage: decimal('margin_percentage', { precision: 5, scale: 4 }),
  outstandingInvoices: decimal('outstanding_invoices', { precision: 15, scale: 2 }).default('0'),
  overdueInvoices: decimal('overdue_invoices', { precision: 15, scale: 2 }).default('0'),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityPeriodIdx: index('mv_finance_kpis_tenant_commodity_period_idx').on(table.tenantId, table.commodity, table.period),
}));

export const mvWeighingVolumes = pgTable('mv_weighing_volumes', {
  tenantId: text('tenant_id').notNull(),
  commodity: text('commodity').notNull(),
  customerId: text('customer_id'),
  siteId: text('site_id'),
  period: text('period').notNull(), // YYYY-MM-DD or YYYY-MM format
  totalWeight: decimal('total_weight', { precision: 15, scale: 3 }).default('0'),
  totalTickets: integer('total_tickets').default(0),
  avgWeight: decimal('avg_weight', { precision: 10, scale: 3 }),
  withinTolerance: integer('within_tolerance').default(0),
  outsideTolerance: integer('outside_tolerance').default(0),
  lastUpdated: timestamp('last_updated').defaultNow().notNull(),
}, (table) => ({
  tenantCommodityPeriodIdx: index('mv_weighing_volumes_tenant_commodity_period_idx').on(table.tenantId, table.commodity, table.period),
}));