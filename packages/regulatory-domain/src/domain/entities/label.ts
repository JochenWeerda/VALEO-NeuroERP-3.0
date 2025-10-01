import { z } from 'zod';

/**
 * Label Code - Verfügbare Labels/Zertifikate
 */
export const LabelCodeEnum = z.enum([
  'VLOG_OGT',           // VLOG "Ohne Gentechnik"
  'QS',                 // QS Qualität & Sicherheit
  'GMP_PLUS',           // GMP+ Feed Safety
  'NON_GMO',            // Non-GMO Project
  'ORGANIC_EU',         // EU Bio-Zertifikat
  'REDII_COMPLIANT',    // RED II THG-konform
  'ISCC',               // ISCC Nachhaltigkeit
  'RTRS',               // RTRS (Soja)
  'RSPO',               // RSPO (Palmöl)
  'CUSTOM',             // Kundenspezifisch
]);

export type LabelCode = z.infer<typeof LabelCodeEnum>;

/**
 * Label Status
 */
export const LabelStatusEnum = z.enum([
  'Eligible',       // Erfüllt alle Anforderungen
  'Ineligible',     // Erfüllt Anforderungen NICHT
  'Conditional',    // Bedingt erfüllt, fehlende Evidenzen
  'Suspended',      // Temporär ausgesetzt (z.B. Audit-Finding)
  'Expired',        // Gültigkeit abgelaufen
  'Pending',        // In Prüfung
]);

export type LabelStatus = z.infer<typeof LabelStatusEnum>;

/**
 * Label - Zertifikat/Qualitätssiegel
 */
export const LabelSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Label-Info
  code: LabelCodeEnum,
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Geltungsbereich
  targetType: z.enum(['Batch', 'Contract', 'Site', 'Commodity', 'Supplier']),
  targetId: z.string().min(1, 'Target ID is required'),
  
  // Status
  status: LabelStatusEnum.default('Pending'),
  
  // Evidenzen (Nachweise)
  evidenceRefs: z.array(z.string().uuid()).default([]),
  missingEvidences: z.array(z.string()).optional(), // Was fehlt noch?
  
  // Gültigkeit
  issuedAt: z.string().datetime().optional(),
  issuedBy: z.string().optional(), // User ID oder Zertifizierungsstelle
  validFrom: z.string().datetime().optional(),
  validTo: z.string().datetime().optional(),
  
  // Widerruf/Aussetzung
  revokedAt: z.string().datetime().optional(),
  revokedBy: z.string().optional(),
  revokedReason: z.string().optional(),
  
  // Policy-Referenz
  policyId: z.string().uuid().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type Label = z.infer<typeof LabelSchema>;

/**
 * Label Evaluation Input
 */
export const LabelEvaluateInputSchema = z.object({
  targetRef: z.object({
    type: z.enum(['Batch', 'Contract', 'Site', 'Commodity', 'Supplier']),
    id: z.string(),
  }),
  labelCode: LabelCodeEnum,
  context: z.record(z.string(), z.any()).optional(), // Zusätzliche Kontext-Daten
});

export type LabelEvaluateInput = z.infer<typeof LabelEvaluateInputSchema>;

/**
 * Label Evaluation Result
 */
export const LabelEvaluationResultSchema = z.object({
  eligible: z.boolean(),
  status: LabelStatusEnum,
  missingEvidences: z.array(z.string()),
  violations: z.array(z.object({
    ruleId: z.string(),
    description: z.string(),
    severity: z.enum(['Minor', 'Major', 'Critical']),
  })),
  recommendation: z.string(),
  confidence: z.number().min(0).max(1).optional(), // KI-basierte Confidence
});

export type LabelEvaluationResult = z.infer<typeof LabelEvaluationResultSchema>;

/**
 * Create Label DTO
 */
export const CreateLabelSchema = LabelSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  issuedAt: true,
  revokedAt: true,
});

export type CreateLabel = z.infer<typeof CreateLabelSchema>;
