import { z } from 'zod';

/**
 * Tax/Charge Scope
 */
export const TaxChargeScopeEnum = z.enum([
  'SKU',         // Für spezifisches Produkt
  'Commodity',   // Für Warengruppe
  'All',         // Für alle Produkte
]);

export type TaxChargeScope = z.infer<typeof TaxChargeScopeEnum>;

/**
 * Tax/Charge Method
 */
export const TaxChargeMethodEnum = z.enum([
  'ABS',         // Absolut (z.B. 5 EUR/t)
  'PCT',         // Prozentual (z.B. 19%)
]);

export type TaxChargeMethod = z.infer<typeof TaxChargeMethodEnum>;

/**
 * Tax Charge Reference - Steuer/Abgaben-Stammdaten
 * 
 * WICHTIG: Keine Buchungslogik! Nur Referenzwerte für Preiskalkulation.
 * Tatsächliche Steuerberechnung/Buchung erfolgt in finance-domain.
 */
export const TaxChargeRefSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Identifikation
  code: z.string().min(1, 'Code is required'), // z.B. "VAT_19", "VAT_7", "EnvFee", "Deposit"
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  
  // Typ
  type: z.enum(['VAT', 'Tax', 'Levy', 'Fee', 'Deposit', 'Surcharge', 'Other']),
  
  // Berechnung
  method: TaxChargeMethodEnum,
  rateOrAmount: z.number(),                      // 19 (für 19%) oder 5 (für 5 EUR/t)
  
  // Anwendungsbereich
  scope: TaxChargeScopeEnum,
  scopeValue: z.string().optional(),             // SKU oder Commodity-Code
  
  // Gültigkeit
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Jurisdiktion
  country: z.string().default('DE'),
  region: z.string().optional(),                 // Bundesland, falls relevant
  
  // Status
  active: z.boolean().default(true),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
});

export type TaxChargeRef = z.infer<typeof TaxChargeRefSchema>;

/**
 * Create Tax Charge Ref DTO
 */
export const CreateTaxChargeRefSchema = TaxChargeRefSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type CreateTaxChargeRef = z.infer<typeof CreateTaxChargeRefSchema>;

/**
 * Update Tax Charge Ref DTO
 */
export const UpdateTaxChargeRefSchema = TaxChargeRefSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdateTaxChargeRef = z.infer<typeof UpdateTaxChargeRefSchema>;

/**
 * Common Tax Rates (Germany)
 */
export const COMMON_TAX_RATES = {
  VAT_19: { code: 'VAT_19', name: 'USt 19%', type: 'VAT' as const, method: 'PCT' as const, rateOrAmount: 19 },
  VAT_7: { code: 'VAT_7', name: 'USt 7%', type: 'VAT' as const, method: 'PCT' as const, rateOrAmount: 7 },
  VAT_0: { code: 'VAT_0', name: 'USt 0%', type: 'VAT' as const, method: 'PCT' as const, rateOrAmount: 0 },
};
