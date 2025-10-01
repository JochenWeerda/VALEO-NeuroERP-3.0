import { pgTable, uuid, text, timestamp, boolean, integer, numeric, jsonb, index } from 'drizzle-orm/pg-core';

/**
 * Quality Plans - Prüfpläne
 */
export const qualityPlans = pgTable('quality_plans', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  name: text('name').notNull(),
  description: text('description'),
  
  // Context
  commodity: text('commodity'),
  contractId: uuid('contract_id'),
  productionContext: text('production_context'),
  
  // Status
  active: boolean('active').default(true).notNull(),
  
  // Rules als JSONB
  rules: jsonb('rules').notNull(), // Array of QualityPlanRule
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
  version: integer('version').default(1).notNull(),
}, (table) => ({
  tenantIdx: index('qp_tenant_idx').on(table.tenantId),
  commodityIdx: index('qp_commodity_idx').on(table.commodity),
  contractIdx: index('qp_contract_idx').on(table.contractId),
  activeIdx: index('qp_active_idx').on(table.active),
}));

/**
 * Samples - Proben
 */
export const samples = pgTable('samples', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Context
  batchId: uuid('batch_id'),
  contractId: uuid('contract_id'),
  lotId: uuid('lot_id'),
  source: text('source').notNull(), // Production|Contract|Inbound|Outbound|Quarantine|RetainCheck
  
  // Identifikation
  sampleCode: text('sample_code').notNull(),
  description: text('description'),
  
  // Probenahme
  takenAt: timestamp('taken_at', { withTimezone: true }).notNull(),
  takenBy: text('taken_by').notNull(),
  takenLocation: text('taken_location'),
  
  // Prüfplan
  planId: uuid('plan_id'),
  
  // Rückstellprobe
  retained: boolean('retained').default(false).notNull(),
  retainedLocation: text('retained_location'),
  retainedUntil: timestamp('retained_until', { withTimezone: true }),
  
  // Status
  status: text('status').default('Pending').notNull(), // Pending|InProgress|Analyzed|Retained|Disposed
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  disposedAt: timestamp('disposed_at', { withTimezone: true }),
  disposedBy: text('disposed_by'),
}, (table) => ({
  tenantIdx: index('sample_tenant_idx').on(table.tenantId),
  batchIdx: index('sample_batch_idx').on(table.batchId),
  contractIdx: index('sample_contract_idx').on(table.contractId),
  lotIdx: index('sample_lot_idx').on(table.lotId),
  codeIdx: index('sample_code_idx').on(table.sampleCode),
  statusIdx: index('sample_status_idx').on(table.status),
  takenAtIdx: index('sample_taken_at_idx').on(table.takenAt),
}));

/**
 * Sample Results - Analyseergebnisse
 */
export const sampleResults = pgTable('sample_results', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  sampleId: uuid('sample_id').notNull().references(() => samples.id, { onDelete: 'cascade' }),
  
  // Analyse
  analyte: text('analyte').notNull(),
  value: numeric('value', { precision: 15, scale: 6 }).notNull(),
  unit: text('unit').notNull(),
  method: text('method').notNull(),
  
  // Labor
  labId: text('lab_id'),
  analyzedAt: timestamp('analyzed_at', { withTimezone: true }),
  analyzedBy: text('analyzed_by'),
  
  // Bewertung
  result: text('result').notNull(), // Pass|Fail|Investigate|NA
  limits: jsonb('limits'), // {min?, max?, target?}
  
  // Kommentar
  comment: text('comment'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('sr_tenant_idx').on(table.tenantId),
  sampleIdx: index('sr_sample_idx').on(table.sampleId),
  analyteIdx: index('sr_analyte_idx').on(table.analyte),
  resultIdx: index('sr_result_idx').on(table.result),
}));

/**
 * Non-Conformities - Abweichungen
 */
export const nonConformities = pgTable('non_conformities', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Referenzen
  batchId: uuid('batch_id'),
  contractId: uuid('contract_id'),
  sampleId: uuid('sample_id'),
  lotId: uuid('lot_id'),
  supplierId: uuid('supplier_id'),
  
  // NC-Identifikation
  ncNumber: text('nc_number').notNull().unique(),
  type: text('type').notNull(), // SpecOut|Contamination|ProcessDeviation|Documentation|...
  severity: text('severity').notNull(), // Minor|Major|Critical
  
  // Beschreibung
  title: text('title').notNull(),
  description: text('description').notNull(),
  rootCause: text('root_cause'),
  
  // Erfassung
  detectedAt: timestamp('detected_at', { withTimezone: true }).notNull(),
  detectedBy: text('detected_by').notNull(),
  detectedLocation: text('detected_location'),
  
  // Zuständigkeit
  assignedTo: text('assigned_to'),
  responsibleDepartment: text('responsible_department'),
  
  // Status
  status: text('status').default('Open').notNull(), // Open|Investigating|ActionPlanned|ActionTaken|Verified|Closed|Rejected
  immediateAction: text('immediate_action'),
  
  // CAPA
  capaId: uuid('capa_id'),
  
  // Kosten & Impact
  estimatedCost: numeric('estimated_cost', { precision: 15, scale: 2 }),
  actualCost: numeric('actual_cost', { precision: 15, scale: 2 }),
  affectedQuantity: numeric('affected_quantity', { precision: 15, scale: 3 }),
  affectedUnit: text('affected_unit'),
  
  // Abschluss
  closedAt: timestamp('closed_at', { withTimezone: true }),
  closedBy: text('closed_by'),
  verifiedAt: timestamp('verified_at', { withTimezone: true }),
  verifiedBy: text('verified_by'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('nc_tenant_idx').on(table.tenantId),
  numberIdx: index('nc_number_idx').on(table.ncNumber),
  batchIdx: index('nc_batch_idx').on(table.batchId),
  contractIdx: index('nc_contract_idx').on(table.contractId),
  statusIdx: index('nc_status_idx').on(table.status),
  severityIdx: index('nc_severity_idx').on(table.severity),
  detectedAtIdx: index('nc_detected_at_idx').on(table.detectedAt),
}));

/**
 * CAPAs - Corrective and Preventive Actions
 */
export const capas = pgTable('capas', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Verknüpfte NCs
  linkedNcIds: jsonb('linked_nc_ids').default([]).notNull(), // Array of UUID strings
  
  // CAPA-Identifikation
  capaNumber: text('capa_number').notNull().unique(),
  type: text('type').notNull(), // Corrective|Preventive|Both
  
  // Beschreibung
  title: text('title').notNull(),
  description: text('description').notNull(),
  action: text('action').notNull(),
  
  // Ursachenanalyse
  rootCauseAnalysis: text('root_cause_analysis'),
  preventionStrategy: text('prevention_strategy'),
  
  // Zuständigkeit
  responsibleUserId: text('responsible_user_id').notNull(),
  responsibleDepartment: text('responsible_department'),
  teamMembers: jsonb('team_members'), // Array of User IDs
  
  // Zeitplan
  dueDate: timestamp('due_date', { withTimezone: true }).notNull(),
  implementedAt: timestamp('implemented_at', { withTimezone: true }),
  verifiedAt: timestamp('verified_at', { withTimezone: true }),
  
  // Status
  status: text('status').default('Open').notNull(), // Open|InProgress|Implemented|Verifying|Verified|Closed|Rejected|Cancelled
  
  // Wirksamkeit
  effectivenessCheck: boolean('effectiveness_check'),
  effectivenessComment: text('effectiveness_comment'),
  
  // Verifikation
  verifiedBy: text('verified_by'),
  verificationMethod: text('verification_method'),
  verificationResult: text('verification_result'),
  
  // Kosten
  estimatedCost: numeric('estimated_cost', { precision: 15, scale: 2 }),
  actualCost: numeric('actual_cost', { precision: 15, scale: 2 }),
  
  // Eskalation
  escalated: boolean('escalated').default(false).notNull(),
  escalatedTo: text('escalated_to'),
  escalatedAt: timestamp('escalated_at', { withTimezone: true }),
  escalationReason: text('escalation_reason'),
  
  // Abschluss
  closedAt: timestamp('closed_at', { withTimezone: true }),
  closedBy: text('closed_by'),
  closureComment: text('closure_comment'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
}, (table) => ({
  tenantIdx: index('capa_tenant_idx').on(table.tenantId),
  numberIdx: index('capa_number_idx').on(table.capaNumber),
  statusIdx: index('capa_status_idx').on(table.status),
  responsibleIdx: index('capa_responsible_idx').on(table.responsibleUserId),
  dueDateIdx: index('capa_due_date_idx').on(table.dueDate),
}));
