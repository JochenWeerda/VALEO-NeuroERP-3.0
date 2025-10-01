import { z } from 'zod';

/**
 * Formula Input Source - Woher kommen die Variablen?
 */
export const FormulaInputSourceEnum = z.enum([
  'Index',       // Börsenindex (z.B. MATIF, CBOT)
  'Futures',     // Futures-Kontrakt
  'Basis',       // Basis-Spread
  'FX',          // Wechselkurs
  'Custom',      // Kundenspezifisch
  'Static',      // Statischer Wert
]);

export type FormulaInputSource = z.infer<typeof FormulaInputSourceEnum>;

/**
 * Formula Input - Variable in der Formel
 */
export const FormulaInputSchema = z.object({
  key: z.string().min(1, 'Key is required'),                // z.B. "MATIF_NOV", "BASIS", "EUR_USD"
  source: FormulaInputSourceEnum,
  sourceRef: z.string().optional(),                          // Referenz (z.B. "MATIF:RAPESEED:NOV25")
  fallback: z.number().optional(),                           // Fallback-Wert wenn Source nicht verfügbar
  description: z.string().optional(),
});

export type FormulaInput = z.infer<typeof FormulaInputSchema>;

/**
 * Rounding Configuration
 */
export const RoundingConfigSchema = z.object({
  step: z.number().optional(),                               // z.B. 0.25 für Viertel-EUR
  mode: z.enum(['up', 'down', 'nearest']).default('nearest'),
});

export type RoundingConfig = z.infer<typeof RoundingConfigSchema>;

/**
 * Price Caps - Min/Max-Grenzen
 */
export const PriceCapsSchema = z.object({
  min: z.number().optional(),
  max: z.number().optional(),
});

export type PriceCaps = z.infer<typeof PriceCapsSchema>;

/**
 * Dynamic Formula - Dynamische Preisformel
 */
export const DynamicFormulaSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Identifikation
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Formel (safe DSL)
  expression: z.string().min(1, 'Expression is required'), // z.B. "MATIF_NOV + BASIS - FREIGHT"
  
  // Inputs (Variablen)
  inputs: z.array(FormulaInputSchema).min(1, 'At least one input is required'),
  
  // Rundung
  rounding: RoundingConfigSchema.optional(),
  
  // Grenzen
  caps: PriceCapsSchema.optional(),
  
  // Anwendungsbereich
  sku: z.string().optional(),                              // Für spezifisches Produkt
  commodity: z.string().optional(),                        // Für Warengruppe
  
  // Gültigkeit
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Status
  active: z.boolean().default(true),
  
  // Test/Validation
  testInputs: z.record(z.string(), z.number()).optional(), // Für Testing
  expectedResult: z.number().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type DynamicFormula = z.infer<typeof DynamicFormulaSchema>;

/**
 * Create Dynamic Formula DTO
 */
export const CreateDynamicFormulaSchema = DynamicFormulaSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateDynamicFormula = z.infer<typeof CreateDynamicFormulaSchema>;

/**
 * Update Dynamic Formula DTO
 */
export const UpdateDynamicFormulaSchema = DynamicFormulaSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateDynamicFormula = z.infer<typeof UpdateDynamicFormulaSchema>;

/**
 * Formula Evaluation Result
 */
export const FormulaEvaluationResultSchema = z.object({
  formulaId: z.string().uuid(),
  result: z.number(),
  inputs: z.record(z.string(), z.number()),
  expression: z.string(),
  cappedValue: z.number().optional(),
  roundedValue: z.number(),
  calculatedAt: z.string().datetime(),
});

export type FormulaEvaluationResult = z.infer<typeof FormulaEvaluationResultSchema>;
