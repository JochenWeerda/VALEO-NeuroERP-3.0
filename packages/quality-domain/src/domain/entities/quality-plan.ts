import { z } from 'zod';

/**
 * Quality Plan Rule - Definiert einzelne Prüfkriterien
 */
export const QualityPlanRuleSchema = z.object({
  analyte: z.string().min(1, 'Analyte is required'),
  method: z.string().min(1, 'Method is required'),
  unit: z.string().min(1, 'Unit is required'),
  target: z.number().optional(),
  min: z.number().optional(),
  max: z.number().optional(),
  frequency: z.enum(['perBatch', 'perDelivery', 'percentage', 'count']),
  frequencyValue: z.number().optional(), // z.B. alle 5 Batches, oder 10%
  retainSample: z.boolean().default(false),
  retentionDays: z.number().optional(), // Aufbewahrungsfrist in Tagen
});

export type QualityPlanRule = z.infer<typeof QualityPlanRuleSchema>;

/**
 * Quality Plan - Prüfplan für Qualitätssicherung
 */
export const QualityPlanSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Context: Wo gilt dieser Plan?
  commodity: z.string().optional(), // Commodity-Code
  contractId: z.string().uuid().optional(), // Spezifischer Vertrag
  productionContext: z.string().optional(), // z.B. "Line-A", "Supplier-XYZ"
  
  // Status
  active: z.boolean().default(true),
  
  // Rules
  rules: z.array(QualityPlanRuleSchema).min(1, 'At least one rule is required'),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
  version: z.number().int().default(1),
});

export type QualityPlan = z.infer<typeof QualityPlanSchema>;

/**
 * Create Quality Plan DTO
 */
export const CreateQualityPlanSchema = QualityPlanSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  version: true,
});

export type CreateQualityPlan = z.infer<typeof CreateQualityPlanSchema>;

/**
 * Update Quality Plan DTO
 */
export const UpdateQualityPlanSchema = QualityPlanSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateQualityPlan = z.infer<typeof UpdateQualityPlanSchema>;
