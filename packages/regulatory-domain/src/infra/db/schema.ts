import { pgTable, uuid, text, timestamp, boolean, jsonb, numeric, index } from 'drizzle-orm/pg-core';

/**
 * Regulatory Policies - Compliance-Regelwerke
 */
export const regulatoryPolicies = pgTable('regulatory_policies', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Policy-Identifikation
  key: text('key').notNull(), // VLOG, QS, REDII, PSM, etc.
  version: text('version').default('1.0').notNull(),
  name: text('name').notNull(),
  description: text('description'),
  
  // Geltungsbereich
  scope: text('scope').notNull(), // Commodity, Process, Site, Contract, Supplier, Global
  scopeValue: text('scope_value'),
  
  // Regeln (als JSONB)
  rules: jsonb('rules').notNull(), // Array of PolicyRule
  
  // Status
  active: boolean('active').default(true).notNull(),
  validFrom: timestamp('valid_from', { withTimezone: true }).notNull(),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Referenzen
  standardReference: text('standard_reference'),
  legalBasis: text('legal_basis'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  updatedBy: text('updated_by'),
}, (table) => ({
  tenantIdx: index('rp_tenant_idx').on(table.tenantId),
  keyIdx: index('rp_key_idx').on(table.key),
  scopeIdx: index('rp_scope_idx').on(table.scope),
  activeIdx: index('rp_active_idx').on(table.active),
}));

/**
 * Labels - Zertifikate/Qualitätssiegel
 */
export const labels = pgTable('labels', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Label-Info
  code: text('code').notNull(), // VLOG_OGT, QS, REDII_COMPLIANT, etc.
  name: text('name').notNull(),
  description: text('description'),
  
  // Geltungsbereich
  targetType: text('target_type').notNull(), // Batch, Contract, Site, Commodity, Supplier
  targetId: text('target_id').notNull(),
  
  // Status
  status: text('status').default('Pending').notNull(), // Eligible, Ineligible, Conditional, Suspended, Expired, Pending
  
  // Evidenzen
  evidenceRefs: jsonb('evidence_refs').default([]).notNull(), // Array of UUID strings
  missingEvidences: jsonb('missing_evidences'), // Array of strings
  
  // Gültigkeit
  issuedAt: timestamp('issued_at', { withTimezone: true }),
  issuedBy: text('issued_by'),
  validFrom: timestamp('valid_from', { withTimezone: true }),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Widerruf
  revokedAt: timestamp('revoked_at', { withTimezone: true }),
  revokedBy: text('revoked_by'),
  revokedReason: text('revoked_reason'),
  
  // Policy-Referenz
  policyId: uuid('policy_id'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('label_tenant_idx').on(table.tenantId),
  codeIdx: index('label_code_idx').on(table.code),
  targetIdx: index('label_target_idx').on(table.targetType, table.targetId),
  statusIdx: index('label_status_idx').on(table.status),
}));

/**
 * Evidence - Compliance-Nachweise
 */
export const evidences = pgTable('evidences', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Evidenz-Info
  type: text('type').notNull(), // Certificate, LabReport, SupplierDeclaration, etc.
  title: text('title').notNull(),
  description: text('description'),
  
  // Dokument
  uri: text('uri'),
  hash: text('hash'), // SHA-256
  mimeType: text('mime_type'),
  fileSize: numeric('file_size'),
  
  // Aussteller
  issuedBy: text('issued_by').notNull(),
  issuedAt: timestamp('issued_at', { withTimezone: true }).notNull(),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Status
  status: text('status').default('Valid').notNull(), // Valid, Expired, Pending, Rejected, Archived
  
  // Verknüpfungen (als JSONB)
  relatedRef: jsonb('related_ref'), // {type, id}
  supportingLabels: jsonb('supporting_labels').default([]).notNull(), // Array of label codes
  supportingPolicies: jsonb('supporting_policies').default([]).notNull(), // Array of policy IDs
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  createdBy: text('created_by'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('ev_tenant_idx').on(table.tenantId),
  typeIdx: index('ev_type_idx').on(table.type),
  statusIdx: index('ev_status_idx').on(table.status),
  validToIdx: index('ev_valid_to_idx').on(table.validTo),
}));

/**
 * PSM Product References - Pflanzenschutzmittel (BVL-Cache)
 */
export const psmProductRefs = pgTable('psm_product_refs', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // BVL-Referenz
  bvlId: text('bvl_id'),
  name: text('name').notNull(),
  
  // Wirkstoffe
  activeSubstances: jsonb('active_substances').default([]).notNull(), // Array of strings
  
  // Zulassungsstatus
  approvalStatus: text('approval_status').default('Unknown').notNull(), // Approved, Expired, Withdrawn, etc.
  approvalValidTo: timestamp('approval_valid_to', { withTimezone: true }),
  approvalNumber: text('approval_number'),
  
  // Anwendungsbereich
  usageScope: text('usage_scope'),
  restrictions: jsonb('restrictions'), // Array of strings
  
  // Cache-Info
  lastCheckedAt: timestamp('last_checked_at', { withTimezone: true }),
  lastCheckedBy: text('last_checked_by'),
  sourceUrl: text('source_url'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('psm_tenant_idx').on(table.tenantId),
  bvlIdIdx: index('psm_bvl_id_idx').on(table.bvlId),
  nameIdx: index('psm_name_idx').on(table.name),
  statusIdx: index('psm_status_idx').on(table.approvalStatus),
}));

/**
 * GHG Pathways - THG-Emissionspfade
 */
export const ghgPathways = pgTable('ghg_pathways', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Pathway-Identifikation
  commodity: text('commodity').notNull(),
  pathwayKey: text('pathway_key').notNull(),
  description: text('description'),
  
  // Methode & Standard
  method: text('method').notNull(), // Default, Actual, Hybrid
  standard: text('standard').default('REDII').notNull(),
  
  // Emissionsfaktoren (als JSONB)
  factors: jsonb('factors').notNull(), // GHGFactors
  
  // Ergebnis
  totalEmissions: numeric('total_emissions', { precision: 10, scale: 2 }).notNull(), // gCO2eq/MJ
  emissionsPerTon: numeric('emissions_per_ton', { precision: 10, scale: 2 }),
  savingsVsFossil: numeric('savings_vs_fossil', { precision: 5, scale: 2 }), // %
  
  // RED II Compliance
  rediiThreshold: numeric('redii_threshold', { precision: 5, scale: 2 }),
  rediiCompliant: boolean('redii_compliant'),
  
  // Datenquellen
  dataSources: jsonb('data_sources'), // Array
  
  // Berechnung
  calculatedAt: timestamp('calculated_at', { withTimezone: true }),
  calculatedBy: text('calculated_by'),
  
  // Gültigkeit
  validFrom: timestamp('valid_from', { withTimezone: true }),
  validTo: timestamp('valid_to', { withTimezone: true }),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('ghg_tenant_idx').on(table.tenantId),
  commodityIdx: index('ghg_commodity_idx').on(table.commodity),
  pathwayIdx: index('ghg_pathway_idx').on(table.pathwayKey),
  methodIdx: index('ghg_method_idx').on(table.method),
}));

/**
 * Compliance Cases - Compliance-Vorfälle
 */
export const complianceCases = pgTable('compliance_cases', {
  id: uuid('id').primaryKey().defaultRandom(),
  tenantId: text('tenant_id').notNull(),
  
  // Case-Identifikation
  caseNumber: text('case_number').notNull().unique(),
  type: text('type').notNull(), // Violation, AuditFinding, DocMissing, etc.
  severity: text('severity').notNull(), // Minor, Major, Critical
  
  // Referenz (als JSONB)
  ref: jsonb('ref').notNull(), // {type, id}
  
  // Beschreibung
  title: text('title').notNull(),
  description: text('description').notNull(),
  
  // Policy/Label-Bezug
  policyId: uuid('policy_id'),
  labelCode: text('label_code'),
  ruleId: text('rule_id'),
  
  // Erfassung
  detectedAt: timestamp('detected_at', { withTimezone: true }).notNull(),
  detectedBy: text('detected_by').notNull(),
  detectionMethod: text('detection_method'), // Automated, Audit, Sample, Manual
  
  // Status
  status: text('status').default('Open').notNull(),
  
  // Maßnahmen
  immediateAction: text('immediate_action'),
  capaId: uuid('capa_id'),
  
  // Auswirkungen
  impactedBatches: jsonb('impacted_batches'), // Array of UUIDs
  impactedLabels: jsonb('impacted_labels'), // Array of label codes
  
  // Abschluss
  resolvedAt: timestamp('resolved_at', { withTimezone: true }),
  resolvedBy: text('resolved_by'),
  resolution: text('resolution'),
  
  closedAt: timestamp('closed_at', { withTimezone: true }),
  closedBy: text('closed_by'),
  
  // Metadata
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  tenantIdx: index('cc_tenant_idx').on(table.tenantId),
  caseNumberIdx: index('cc_case_number_idx').on(table.caseNumber),
  typeIdx: index('cc_type_idx').on(table.type),
  statusIdx: index('cc_status_idx').on(table.status),
  severityIdx: index('cc_severity_idx').on(table.severity),
  detectedAtIdx: index('cc_detected_at_idx').on(table.detectedAt),
}));
