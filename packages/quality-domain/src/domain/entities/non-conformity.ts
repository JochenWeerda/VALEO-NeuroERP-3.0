import { z } from 'zod';

/**
 * Non-Conformity Type - Art der Abweichung
 */
export const NonConformityTypeEnum = z.enum([
  'SpecOut',               // Außerhalb Spezifikation
  'Contamination',         // Kontamination
  'ProcessDeviation',      // Prozessabweichung
  'Documentation',         // Dokumentationsfehler
  'PackagingDefect',       // Verpackungsmangel
  'QuantityDeviation',     // Mengendiskrepanz
  'IdentificationError',   // Falsche Kennzeichnung
  'Other',                 // Sonstige
]);

export type NonConformityType = z.infer<typeof NonConformityTypeEnum>;

/**
 * Severity Level
 */
export const SeverityEnum = z.enum([
  'Minor',      // Geringfügig, keine Auswirkung auf Funktion
  'Major',      // Erheblich, Funktion beeinträchtigt
  'Critical',   // Kritisch, nicht verwendbar, Rückruf nötig
]);

export type Severity = z.infer<typeof SeverityEnum>;

/**
 * Non-Conformity Status
 */
export const NonConformityStatusEnum = z.enum([
  'Open',           // Neu erfasst
  'Investigating',  // In Untersuchung
  'ActionPlanned',  // Maßnahme geplant
  'ActionTaken',    // Maßnahme durchgeführt
  'Verified',       // Verifiziert
  'Closed',         // Abgeschlossen
  'Rejected',       // Zurückgewiesen (keine echte NC)
]);

export type NonConformityStatus = z.infer<typeof NonConformityStatusEnum>;

/**
 * Non-Conformity - Abweichung/Reklamation
 */
export const NonConformitySchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Referenz - Wo trat die Abweichung auf?
  batchId: z.string().uuid().optional(),
  contractId: z.string().uuid().optional(),
  sampleId: z.string().uuid().optional(),
  lotId: z.string().uuid().optional(),
  supplierId: z.string().uuid().optional(),
  
  // NC-Identifikation
  ncNumber: z.string().min(1, 'NC number is required'), // z.B. "NC-2025-00123"
  type: NonConformityTypeEnum,
  severity: SeverityEnum,
  
  // Beschreibung
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  rootCause: z.string().optional(), // Ursachenanalyse
  
  // Erfassung
  detectedAt: z.string().datetime(),
  detectedBy: z.string().min(1, 'Detected by is required'), // User ID
  detectedLocation: z.string().optional(),
  
  // Zuständigkeit
  assignedTo: z.string().optional(), // User ID
  responsibleDepartment: z.string().optional(),
  
  // Status & Maßnahmen
  status: NonConformityStatusEnum.default('Open'),
  immediateAction: z.string().optional(), // Sofortmaßnahme
  
  // CAPA-Verknüpfung
  capaId: z.string().uuid().optional(),
  
  // Kosten & Impact
  estimatedCost: z.number().optional(),
  actualCost: z.number().optional(),
  affectedQuantity: z.number().optional(),
  affectedUnit: z.string().optional(),
  
  // Abschluss
  closedAt: z.string().datetime().optional(),
  closedBy: z.string().optional(),
  verifiedAt: z.string().datetime().optional(),
  verifiedBy: z.string().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type NonConformity = z.infer<typeof NonConformitySchema>;

/**
 * Create Non-Conformity DTO
 */
export const CreateNonConformitySchema = NonConformitySchema.omit({
  id: true,
  ncNumber: true, // Auto-generated
  createdAt: true,
  updatedAt: true,
  closedAt: true,
  closedBy: true,
  verifiedAt: true,
  verifiedBy: true,
});

export type CreateNonConformity = z.infer<typeof CreateNonConformitySchema>;

/**
 * Update Non-Conformity DTO
 */
export const UpdateNonConformitySchema = NonConformitySchema.partial().omit({
  id: true,
  tenantId: true,
  ncNumber: true,
  createdAt: true,
});

export type UpdateNonConformity = z.infer<typeof UpdateNonConformitySchema>;
