import { z } from 'zod';

/**
 * Condition Type
 */
export const ConditionTypeEnum = z.enum([
  'Discount',    // Rabatt
  'Markup',      // Aufschlag
  'Rebate',      // Rückvergütung
  'Surcharge',   // Zuschlag
]);

export type ConditionType = z.infer<typeof ConditionTypeEnum>;

/**
 * Condition Scope - Wo gilt die Kondition?
 */
export const ConditionScopeEnum = z.enum([
  'SKU',         // Für spezifisches Produkt
  'Commodity',   // Für Warengruppe
  'All',         // Für alle Produkte
]);

export type ConditionScope = z.infer<typeof ConditionScopeEnum>;

/**
 * Condition Method - Berechnung
 */
export const ConditionMethodEnum = z.enum([
  'ABS',         // Absolut (z.B. -5 EUR/t)
  'PCT',         // Prozentual (z.B. -2.5%)
]);

export type ConditionMethod = z.infer<typeof ConditionMethodEnum>;

/**
 * Channel - Verkaufskanal
 */
export const ChannelEnum = z.enum([
  'Web',
  'Mobile',
  'BackOffice',
  'EDI',
  'All',
]);

export type Channel = z.infer<typeof ChannelEnum>;

/**
 * Condition Rule - Einzelne Konditionsregel
 */
export const ConditionRuleSchema = z.object({
  ruleId: z.string().optional(), // Auto-generated
  type: ConditionTypeEnum,
  scope: ConditionScopeEnum,
  
  // Selector - Was wird selektiert?
  selector: z.object({
    sku: z.string().optional(),
    commodity: z.string().optional(),
  }).optional(),
  
  // Berechnung
  method: ConditionMethodEnum,
  value: z.number(),
  
  // Mengen-Bedingungen
  minQty: z.number().optional(),
  maxQty: z.number().optional(),
  
  // Kanal
  channel: ChannelEnum.optional(),
  
  // Zeitfenster (optional, überschreibt ConditionSet-Gültigkeit)
  validFrom: z.string().datetime().optional(),
  validTo: z.string().datetime().optional(),
  
  // Kombinationslogik
  stackable: z.boolean().default(true), // Kann mit anderen kombiniert werden?
  
  // Beschreibung
  description: z.string().optional(),
});

export type ConditionRule = z.infer<typeof ConditionRuleSchema>;

/**
 * Condition Set - Konditionspaket (Kunde/Segment)
 */
export const ConditionSetSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Identifikation
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Zuordnung
  key: z.string().min(1, 'Key is required'), // customerId oder segmentKey (z.B. "CUST-123", "SEGMENT-PREMIUM")
  keyType: z.enum(['Customer', 'Segment', 'Region', 'PaymentTerm']),
  
  // Regeln
  rules: z.array(ConditionRuleSchema).min(1, 'At least one rule is required'),
  
  // Priorität (bei mehreren ConditionSets)
  priority: z.number().int().default(100), // Höher = höhere Priorität
  
  // Konfliktstrategie
  conflictStrategy: z.enum(['FirstWins', 'LastWins', 'MaxWins', 'MinWins', 'Stack']).default('Stack'),
  
  // Gültigkeit
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Status
  active: z.boolean().default(true),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type ConditionSet = z.infer<typeof ConditionSetSchema>;

/**
 * Create Condition Set DTO
 */
export const CreateConditionSetSchema = ConditionSetSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateConditionSet = z.infer<typeof CreateConditionSetSchema>;

/**
 * Update Condition Set DTO
 */
export const UpdateConditionSetSchema = ConditionSetSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateConditionSet = z.infer<typeof UpdateConditionSetSchema>;
