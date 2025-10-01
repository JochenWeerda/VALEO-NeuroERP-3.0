import { z } from 'zod';

/**
 * Compliance Case Type
 */
export const ComplianceCaseTypeEnum = z.enum([
  'Violation',          // Regelverstoß
  'AuditFinding',       // Audit-Feststellung
  'DocMissing',         // Fehlende Dokumentation
  'LabelRevocation',    // Label-Entzug
  'Contamination',      // Kontamination (GVO, Fremdstoff)
  'Expiry',             // Ablauf von Zertifikaten
  'Other',              // Sonstiges
]);

export type ComplianceCaseType = z.infer<typeof ComplianceCaseTypeEnum>;

/**
 * Severity (analog zu quality-domain NC)
 */
export const ComplianceSeverityEnum = z.enum([
  'Minor',      // Geringfügig
  'Major',      // Erheblich
  'Critical',   // Kritisch, Label-Entzug
]);

export type ComplianceSeverity = z.infer<typeof ComplianceSeverityEnum>;

/**
 * Compliance Case Status
 */
export const ComplianceCaseStatusEnum = z.enum([
  'Open',           // Neu
  'Investigating',  // In Untersuchung
  'ActionRequired', // Maßnahme erforderlich
  'Resolved',       // Behoben
  'Closed',         // Abgeschlossen
  'Escalated',      // Eskaliert
]);

export type ComplianceCaseStatus = z.infer<typeof ComplianceCaseStatusEnum>;

/**
 * Compliance Case - Compliance-Vorfall
 */
export const ComplianceCaseSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Case-Identifikation
  caseNumber: z.string().min(1, 'Case number is required'), // z.B. "COMP-2025-00123"
  type: ComplianceCaseTypeEnum,
  severity: ComplianceSeverityEnum,
  
  // Referenz - Wo trat der Vorfall auf?
  ref: z.object({
    type: z.enum(['Batch', 'Contract', 'Site', 'Shipment', 'Supplier', 'Process']),
    id: z.string(),
  }),
  
  // Beschreibung
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  
  // Policy/Label-Bezug
  policyId: z.string().uuid().optional(),
  labelCode: z.string().optional(), // Betroffenes Label
  ruleId: z.string().optional(), // Verletzte Regel
  
  // Erfassung
  detectedAt: z.string().datetime(),
  detectedBy: z.string().min(1, 'Detected by is required'),
  detectionMethod: z.enum(['Automated', 'Audit', 'Sample', 'Manual']).optional(),
  
  // Status
  status: ComplianceCaseStatusEnum.default('Open'),
  
  // Maßnahmen
  immediateAction: z.string().optional(),
  capaId: z.string().uuid().optional(), // Verknüpfung zu quality-domain CAPA
  
  // Auswirkungen
  impactedBatches: z.array(z.string().uuid()).optional(),
  impactedLabels: z.array(z.string()).optional(), // Label-Codes die betroffen sind
  
  // Abschluss
  resolvedAt: z.string().datetime().optional(),
  resolvedBy: z.string().optional(),
  resolution: z.string().optional(),
  
  closedAt: z.string().datetime().optional(),
  closedBy: z.string().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type ComplianceCase = z.infer<typeof ComplianceCaseSchema>;

/**
 * Create Compliance Case DTO
 */
export const CreateComplianceCaseSchema = ComplianceCaseSchema.omit({
  id: true,
  caseNumber: true, // Auto-generated
  createdAt: true,
  updatedAt: true,
  resolvedAt: true,
  closedAt: true,
});

export type CreateComplianceCase = z.infer<typeof CreateComplianceCaseSchema>;

/**
 * Update Compliance Case DTO
 */
export const UpdateComplianceCaseSchema = ComplianceCaseSchema.partial().omit({
  id: true,
  tenantId: true,
  caseNumber: true,
  createdAt: true,
});

export type UpdateComplianceCase = z.infer<typeof UpdateComplianceCaseSchema>;
