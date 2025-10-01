import { z } from 'zod';

/**
 * PSM Approval Status
 */
export const PSMApprovalStatusEnum = z.enum([
  'Approved',       // Zugelassen
  'Expired',        // Zulassung abgelaufen
  'Withdrawn',      // Zurückgezogen
  'Restricted',     // Eingeschränkt
  'Pending',        // Zulassung beantragt
  'Unknown',        // Nicht in BVL-Datenbank gefunden
]);

export type PSMApprovalStatus = z.infer<typeof PSMApprovalStatusEnum>;

/**
 * PSM Product Reference (BVL-Datenbank)
 */
export const PSMProductRefSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // BVL-Referenz
  bvlId: z.string().optional(), // Offizielle BVL-Zulassungsnummer
  name: z.string().min(1, 'Name is required'),
  
  // Wirkstoffe
  activeSubstances: z.array(z.string()).default([]),
  
  // Zulassungsstatus
  approvalStatus: PSMApprovalStatusEnum.default('Unknown'),
  approvalValidTo: z.string().datetime().optional(),
  approvalNumber: z.string().optional(),
  
  // Anwendungsbereich
  usageScope: z.string().optional(), // z.B. "Raps, Getreide"
  restrictions: z.array(z.string()).optional(), // Einschränkungen
  
  // Cache-Info
  lastCheckedAt: z.string().datetime().optional(),
  lastCheckedBy: z.string().optional(),
  sourceUrl: z.string().optional(), // BVL-Link
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type PSMProductRef = z.infer<typeof PSMProductRefSchema>;

/**
 * PSM Check Input - Prüfung verwendeter PSM
 */
export const PSMCheckInputSchema = z.object({
  items: z.array(z.object({
    name: z.string().min(1, 'PSM name is required'),
    bvlId: z.string().optional(),
    useDate: z.string().datetime(),
    cropOrUseCase: z.string().optional(),
    quantity: z.number().optional(),
    unit: z.string().optional(),
  })).min(1, 'At least one PSM item is required'),
  batchId: z.string().uuid().optional(),
  contractId: z.string().uuid().optional(),
});

export type PSMCheckInput = z.infer<typeof PSMCheckInputSchema>;

/**
 * PSM Check Result
 */
export const PSMCheckResultSchema = z.object({
  compliant: z.boolean(),
  items: z.array(z.object({
    name: z.string(),
    bvlId: z.string().optional(),
    status: PSMApprovalStatusEnum,
    approved: z.boolean(),
    validUntil: z.string().datetime().optional(),
    issues: z.array(z.string()).default([]),
  })),
  violations: z.array(z.object({
    name: z.string(),
    reason: z.string(),
    severity: z.enum(['Minor', 'Major', 'Critical']),
  })),
  recommendation: z.string(),
});

export type PSMCheckResult = z.infer<typeof PSMCheckResultSchema>;

/**
 * Create PSM Product DTO
 */
export const CreatePSMProductRefSchema = PSMProductRefSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreatePSMProductRef = z.infer<typeof CreatePSMProductRefSchema>;
