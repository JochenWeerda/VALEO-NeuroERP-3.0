import { z } from 'zod';

/**
 * Evidence Type - Art des Nachweises
 */
export const EvidenceTypeEnum = z.enum([
  'Certificate',              // Zertifikat (VLOG, QS, Bio, etc.)
  'LabReport',                // Laborergebnis
  'SupplierDeclaration',      // Lieferanten-Erklärung (VLOG, Non-GMO)
  'AuditReport',              // Audit-Bericht
  'WeighingNote',             // Wiegeschein (Rückverfolgbarkeit)
  'ProcessDocument',          // Prozessdokumentation
  'CleaningProtocol',         // Reinigungsprotokoll (VLOG)
  'ContractClause',           // Vertragsklausel
  'InspectionReport',         // Inspektionsbericht
  'SelfDeclaration',          // Selbsterklärung
  'Invoice',                  // Rechnung/Lieferschein
  'TransportDocument',        // Transportdokument
  'Other',                    // Sonstiges
]);

export type EvidenceType = z.infer<typeof EvidenceTypeEnum>;

/**
 * Evidence Status
 */
export const EvidenceStatusEnum = z.enum([
  'Valid',          // Gültig
  'Expired',        // Abgelaufen
  'Pending',        // In Prüfung
  'Rejected',       // Zurückgewiesen
  'Archived',       // Archiviert
]);

export type EvidenceStatus = z.infer<typeof EvidenceStatusEnum>;

/**
 * Evidence - Compliance-Nachweis
 */
export const EvidenceSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Evidenz-Info
  type: EvidenceTypeEnum,
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  
  // Dokument
  uri: z.string().url().optional(), // URL zum Dokument (S3, Azure Blob, etc.)
  hash: z.string().optional(), // SHA-256 Hash zur Integritätsprüfung
  mimeType: z.string().optional(), // z.B. "application/pdf"
  fileSize: z.number().optional(), // in Bytes
  
  // Aussteller
  issuedBy: z.string().min(1, 'Issued by is required'), // Lieferant, Labor, Zertifizierungsstelle
  issuedAt: z.string().datetime(),
  
  // Gültigkeit
  validFrom: z.string().datetime().optional(),
  validTo: z.string().datetime().optional(),
  
  // Status
  status: EvidenceStatusEnum.default('Valid'),
  
  // Verknüpfungen
  relatedRef: z.object({
    type: z.enum(['Batch', 'Contract', 'Site', 'Supplier', 'Shipment', 'Sample']),
    id: z.string(),
  }).optional(),
  
  // Labels/Policies zu denen diese Evidenz beiträgt
  supportingLabels: z.array(z.string()).default([]), // Label-Codes
  supportingPolicies: z.array(z.string().uuid()).default([]), // Policy-IDs
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type Evidence = z.infer<typeof EvidenceSchema>;

/**
 * Create Evidence DTO
 */
export const CreateEvidenceSchema = EvidenceSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateEvidence = z.infer<typeof CreateEvidenceSchema>;

/**
 * Link Evidence DTO
 */
export const LinkEvidenceSchema = z.object({
  evidenceId: z.string().uuid(),
  targetRef: z.object({
    type: z.enum(['Batch', 'Contract', 'Site', 'Supplier', 'Label']),
    id: z.string(),
  }),
});

export type LinkEvidence = z.infer<typeof LinkEvidenceSchema>;
