import { z } from 'zod';

/**
 * CAPA Type - Corrective vs Preventive Action
 */
export const CapaTypeEnum = z.enum([
  'Corrective',    // Korrekturmaßnahme (reagiert auf eingetretene Abweichung)
  'Preventive',    // Vorbeugungsmaßnahme (verhindert potenzielle Abweichung)
  'Both',          // Kombiniert
]);

export type CapaType = z.infer<typeof CapaTypeEnum>;

/**
 * CAPA Status
 */
export const CapaStatusEnum = z.enum([
  'Open',           // Neu erstellt
  'InProgress',     // In Bearbeitung
  'Implemented',    // Umgesetzt
  'Verifying',      // In Überprüfung
  'Verified',       // Verifiziert (wirksam)
  'Closed',         // Abgeschlossen
  'Rejected',       // Zurückgewiesen (nicht wirksam)
  'Cancelled',      // Abgebrochen
]);

export type CapaStatus = z.infer<typeof CapaStatusEnum>;

/**
 * CAPA - Corrective and Preventive Action
 */
export const CapaSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Verknüpfte NCs
  linkedNcIds: z.array(z.string().uuid()).default([]),
  
  // CAPA-Identifikation
  capaNumber: z.string().min(1, 'CAPA number is required'), // z.B. "CAPA-2025-00045"
  type: CapaTypeEnum,
  
  // Beschreibung
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  action: z.string().min(1, 'Action is required'), // Die konkrete Maßnahme
  
  // Ursachenanalyse (5 Why, Ishikawa etc.)
  rootCauseAnalysis: z.string().optional(),
  preventionStrategy: z.string().optional(),
  
  // Zuständigkeit
  responsibleUserId: z.string().min(1, 'Responsible user is required'),
  responsibleDepartment: z.string().optional(),
  teamMembers: z.array(z.string()).optional(), // User IDs
  
  // Zeitplan
  dueDate: z.string().datetime(),
  implementedAt: z.string().datetime().optional(),
  verifiedAt: z.string().datetime().optional(),
  
  // Status
  status: CapaStatusEnum.default('Open'),
  
  // Wirksamkeit
  effectivenessCheck: z.boolean().optional(),
  effectivenessComment: z.string().optional(),
  
  // Verifikation
  verifiedBy: z.string().optional(), // User ID
  verificationMethod: z.string().optional(),
  verificationResult: z.string().optional(),
  
  // Kosten
  estimatedCost: z.number().optional(),
  actualCost: z.number().optional(),
  
  // Eskalation
  escalated: z.boolean().default(false),
  escalatedTo: z.string().optional(), // User ID oder Abteilung
  escalatedAt: z.string().datetime().optional(),
  escalationReason: z.string().optional(),
  
  // Abschluss
  closedAt: z.string().datetime().optional(),
  closedBy: z.string().optional(),
  closureComment: z.string().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type Capa = z.infer<typeof CapaSchema>;

/**
 * Create CAPA DTO
 */
export const CreateCapaSchema = CapaSchema.omit({
  id: true,
  capaNumber: true, // Auto-generated
  createdAt: true,
  updatedAt: true,
  implementedAt: true,
  verifiedAt: true,
  closedAt: true,
  closedBy: true,
  escalatedAt: true,
});

export type CreateCapa = z.infer<typeof CreateCapaSchema>;

/**
 * Update CAPA DTO
 */
export const UpdateCapaSchema = CapaSchema.partial().omit({
  id: true,
  tenantId: true,
  capaNumber: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateCapa = z.infer<typeof UpdateCapaSchema>;
