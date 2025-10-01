import { pgTable, uuid, text, timestamp, boolean, numeric, jsonb, integer, index } from 'drizzle-orm/pg-core';

/**
 * Price Lists - Preislisten
 */
export const priceLists = pgTable('price_lists', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Identifikation
  name: text('name').notNull(),
  description: text('description'),
  code: text('code'),
  
  // Währung
  currency: text('currency').default('EUR').notNull(),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }).notNull(),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Lines (als JSONB)
  lines: jsonb('lines').notNull(), // Array of PriceListLine
  
  // Status
  status: text('status').default('Draft').notNull(), // Draft, Active, Archived
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
  activatedAt: timestamp('activated_at', { withTimezone: true }),
  activatedBy: text('activated_by'),
}, (table) => ({
  tenantIdx: index('pl_tenant_idx').on(table.tenantId),
  statusIdx: index('pl_status_idx').on(table.status),
  validFromIdx: index('pl_valid_from_idx').on(table.validFrom),
}));

/**
 * Condition Sets - Kunden/Segment-Konditionen
 */
export const conditionSets = pgTable('condition_sets', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Identifikation
  name: text('name').notNull(),
  description: text('description'),
  
  // Zuordnung
  key: text('key').notNull(),                                   // customerId or segmentKey
  keyType: text('key_type').notNull(),                          // Customer, Segment, Region, PaymentTerm
  
  // Regeln (als JSONB)
  rules: jsonb('rules').notNull(),                              // Array of ConditionRule
  
  // Priorität
  priority: integer('priority').default(100).notNull(),
  
  // Konfliktstrategie
  conflictStrategy: text('conflict_strategy').default('Stack').notNull(),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }).notNull(),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Status
  active: boolean('active').default(true).notNull(),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
}, (table) => ({
  tenantIdx: index('cs_tenant_idx').on(table.tenantId),
  keyIdx: index('cs_key_idx').on(table.key),
  activeIdx: index('cs_active_idx').on(table.active),
}));

/**
 * Dynamic Formulas - Dynamische Preisformeln
 */
export const dynamicFormulas = pgTable('dynamic_formulas', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Identifikation
  name: text('name').notNull(),
  description: text('description'),
  
  // Formel
  expression: text('expression').notNull(),
  
  // Inputs (als JSONB)
  inputs: jsonb('inputs').notNull(),                            // Array of FormulaInput
  
  // Rundung & Caps (als JSONB)
  rounding: jsonb('rounding'),
  caps: jsonb('caps'),
  
  // Anwendungsbereich
  sku: text('sku'),
  commodity: text('commodity'),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }).notNull(),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Status
  active: boolean('active').default(true).notNull(),
  
  // Test
  testInputs: jsonb('test_inputs'),
  expectedResult: numeric('expected_result', { precision: 15, scale: 4 }),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
}, (table) => ({
  tenantIdx: index('df_tenant_idx').on(table.tenantId),
  skuIdx: index('df_sku_idx').on(table.sku),
  commodityIdx: index('df_commodity_idx').on(table.commodity),
  activeIdx: index('df_active_idx').on(table.active),
}));

/**
 * Tax Charge References - Steuer/Abgaben-Stammdaten
 */
export const taxChargeRefs = pgTable('tax_charge_refs', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Identifikation
  code: text('code').notNull(),
  name: text('name').notNull(),
  description: text('description'),
  
  // Typ
  type: text('type').notNull(), // VAT, Tax, Levy, Fee, Deposit, Surcharge
  
  // Berechnung
  method: text('method').notNull(), // ABS or PCT
  rateOrAmount: numeric('rate_or_amount', { precision: 10, scale: 4 }).notNull(),
  
  // Anwendungsbereich
  scope: text('scope').notNull(), // SKU, Commodity, All
  scopeValue: text('scope_value'),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }).notNull(),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Jurisdiktion
  country: text('country').default('DE').notNull(),
  region: text('region'),
  
  // Status
  active: boolean('active').default(true).notNull(),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
}, (table) => ({
  tenantIdx: index('tc_tenant_idx').on(table.tenantId),
  codeIdx: index('tc_code_idx').on(table.code),
  typeIdx: index('tc_type_idx').on(table.type),
  activeIdx: index('tc_active_idx').on(table.active),
}));

/**
 * Price Quotes - Berechnete Preisangebote (kurzlebig)
 */
export const priceQuotes = pgTable('price_quotes', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Input (als JSONB)
  inputs: jsonb('inputs').notNull(),                            // CalcQuoteInput
  
  // Komponenten (als JSONB)
  components: jsonb('components').notNull(),                    // Array of PriceComponent
  
  // Ergebnis
  totalNet: numeric('total_net', { precision: 15, scale: 2 }).notNull(),
  totalGross: numeric('total_gross', { precision: 15, scale: 2 }),
  currency: text('currency').default('EUR').notNull(),
  
  // Gültigkeit
  calculatedAt: timestamp('calculated_at', { withTimezone: true }).defaultNow().notNull(),
  expiresAt: timestamp('expires_at', { withTimezone: true }).notNull(),
  
  // Signatur
  signature: text('signature'),
  
  // Metadata
  createdBy: text('created_by'),
}, (table) => ({
  tenantIdx: index('pq_tenant_idx').on(table.tenantId),
  expiresAtIdx: index('pq_expires_at_idx').on(table.expiresAt),
}));
