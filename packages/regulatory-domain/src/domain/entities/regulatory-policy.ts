import { z } from 'zod';

/**
 * Policy Scope - Wo gilt die Policy?
 */
export const PolicyScopeEnum = z.enum([
  'Commodity',     // Für bestimmte Rohstoffe
  'Process',       // Für Produktionsprozesse
  'Site',          // Für Standorte
  'Contract',      // Für spezifische Verträge
  'Supplier',      // Für Lieferanten
  'Global',        // Tenant-weit
]);

export type PolicyScope = z.infer<typeof PolicyScopeEnum>;

/**
 * Policy Key - Standard/Label-Typ
 */
export const PolicyKeyEnum = z.enum([
  'VLOG',          // VLOG "Ohne Gentechnik" Standard
  'QS',            // QS Qualität & Sicherheit
  'REDII',         // RED II Treibhausgas-Compliance
  'PSM',           // Pflanzenschutzmittel-Zulassungen
  'GMP_PLUS',      // GMP+ Feed Safety
  'NON_GMO',       // Non-GMO Project
  'ORGANIC',       // Bio-Zertifizierung
  'TRACEABILITY',  // Rückverfolgbarkeit (VO 178/2002, 183/2005)
  'HYGIENE',       // Futtermittelhygiene
  'CUSTOM',        // Kundenspezifisch
]);

export type PolicyKey = z.infer<typeof PolicyKeyEnum>;

/**
 * Policy Rule - Einzelne Compliance-Anforderung
 */
export const PolicyRuleSchema = z.object({
  ruleId: z.string(),
  description: z.string(),
  type: z.enum(['Input', 'Process', 'Documentation', 'Lab', 'Monitoring', 'GHG']),
  
  // Kriterien
  criteriaKey: z.string(), // z.B. "vlog.input.gvo_free", "qs.monitoring.mycotoxin"
  criteriaValue: z.any().optional(), // Erwarteter Wert oder Grenzwert
  
  // Frequenz/Prüfintervall
  frequency: z.enum(['PerBatch', 'Daily', 'Weekly', 'Monthly', 'Annually', 'OnDemand']).optional(),
  
  // Evidenz-Anforderung
  evidenceRequired: z.boolean().default(false),
  evidenceType: z.string().optional(), // z.B. "SupplierDeclaration", "LabReport"
  
  // Schweregrad bei Verstoß
  violationSeverity: z.enum(['Minor', 'Major', 'Critical']).default('Major'),
});

export type PolicyRule = z.infer<typeof PolicyRuleSchema>;

/**
 * Regulatory Policy - Compliance-Regelwerk
 */
export const RegulatoryPolicySchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Policy-Identifikation
  key: PolicyKeyEnum,
  version: z.string().default('1.0'),
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Geltungsbereich
  scope: PolicyScopeEnum,
  scopeValue: z.string().optional(), // z.B. "RAPE_OIL", "Site-Hamburg", "Contract-123"
  
  // Regeln
  rules: z.array(PolicyRuleSchema).min(1, 'At least one rule is required'),
  
  // Status
  active: z.boolean().default(true),
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Referenzen
  standardReference: z.string().optional(), // URL oder Dokumenten-Referenz
  legalBasis: z.string().optional(), // z.B. "EG VO 178/2002", "EGGenTDurchfG"
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type RegulatoryPolicy = z.infer<typeof RegulatoryPolicySchema>;

/**
 * Create Regulatory Policy DTO
 */
export const CreateRegulatoryPolicySchema = RegulatoryPolicySchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateRegulatoryPolicy = z.infer<typeof CreateRegulatoryPolicySchema>;

/**
 * Update Regulatory Policy DTO
 */
export const UpdateRegulatoryPolicySchema = RegulatoryPolicySchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateRegulatoryPolicy = z.infer<typeof UpdateRegulatoryPolicySchema>;

/**
 * VLOG-spezifische Policy-Defaults
 */
export const VLOG_DEFAULT_RULES: PolicyRule[] = [
  {
    ruleId: 'vlog-input-gvo-free',
    description: 'Alle Inputs müssen GVO-frei sein',
    type: 'Input',
    criteriaKey: 'vlog.input.gvo_free',
    criteriaValue: true,
    evidenceRequired: true,
    evidenceType: 'SupplierDeclaration',
    violationSeverity: 'Critical',
  },
  {
    ruleId: 'vlog-separation',
    description: 'Strikte Trennung von GVO/Nicht-GVO Material',
    type: 'Process',
    criteriaKey: 'vlog.process.separation',
    criteriaValue: true,
    evidenceRequired: true,
    evidenceType: 'ProcessDocument',
    violationSeverity: 'Critical',
  },
  {
    ruleId: 'vlog-cleaning',
    description: 'Reinigung zwischen GVO/Nicht-GVO Chargen',
    type: 'Process',
    criteriaKey: 'vlog.process.cleaning',
    criteriaValue: true,
    evidenceRequired: true,
    evidenceType: 'CleaningProtocol',
    violationSeverity: 'Major',
  },
  {
    ruleId: 'vlog-monitoring',
    description: 'GVO-Monitoring-Proben (Frequenz: mind. 1 pro Charge oder 0,5% der Menge)',
    type: 'Monitoring',
    criteriaKey: 'vlog.monitoring.frequency',
    frequency: 'PerBatch',
    evidenceRequired: true,
    evidenceType: 'LabReport',
    violationSeverity: 'Major',
  },
];

/**
 * QS-spezifische Policy-Defaults
 */
export const QS_DEFAULT_RULES: PolicyRule[] = [
  {
    ruleId: 'qs-mycotoxin-monitoring',
    description: 'Mykotoxin-Monitoring gemäß QS-Leitfaden',
    type: 'Lab',
    criteriaKey: 'qs.monitoring.mycotoxin',
    frequency: 'Monthly',
    evidenceRequired: true,
    evidenceType: 'LabReport',
    violationSeverity: 'Major',
  },
  {
    ruleId: 'qs-pesticide-residue',
    description: 'Rückstandsuntersuchung Pflanzenschutzmittel',
    type: 'Lab',
    criteriaKey: 'qs.monitoring.pesticide_residue',
    frequency: 'Monthly',
    evidenceRequired: true,
    evidenceType: 'LabReport',
    violationSeverity: 'Major',
  },
  {
    ruleId: 'qs-traceability',
    description: 'Rückverfolgbarkeit 1-up/1-down',
    type: 'Documentation',
    criteriaKey: 'qs.traceability.complete',
    criteriaValue: true,
    evidenceRequired: true,
    evidenceType: 'WeighingNote',
    violationSeverity: 'Critical',
  },
];
