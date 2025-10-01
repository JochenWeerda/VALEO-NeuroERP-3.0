import { z } from 'zod';

/**
 * Price Component Type - Art der Preiskomponente
 */
export const PriceComponentTypeEnum = z.enum([
  'Base',        // Basis-Preis aus PriceList
  'Condition',   // Kondition (Rabatt/Aufschlag)
  'Dynamic',     // Dynamische Formel
  'Charge',      // Abgabe/Fee
  'Tax',         // Steuer (nur Referenz!)
]);

export type PriceComponentType = z.infer<typeof PriceComponentTypeEnum>;

/**
 * Price Component - Einzelne Komponente
 */
export const PriceComponentSchema = z.object({
  type: PriceComponentTypeEnum,
  key: z.string(),                    // z.B. "Base-WHEAT-11.5", "Discount-Volume", "VAT-19"
  description: z.string().optional(),
  value: z.number(),                  // Positiv oder negativ
  basis: z.number().optional(),       // Basis für Prozentual-Berechnung
  calculatedFrom: z.string().optional(), // Source (z.B. "PriceList-123", "ConditionSet-456")
});

export type PriceComponent = z.infer<typeof PriceComponentSchema>;

/**
 * Price Quote Input - Eingabe für Kalkulation
 */
export const CalcQuoteInputSchema = z.object({
  customerId: z.string().min(1, 'Customer ID is required'),
  sku: z.string().min(1, 'SKU is required'),
  qty: z.number().positive('Quantity must be positive'),
  
  // Optional
  channel: z.enum(['Web', 'Mobile', 'BackOffice', 'EDI']).optional(),
  deliveryWindow: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }).optional(),
  siteId: z.string().optional(),
  contractRef: z.string().optional(),
  
  // Context (für Formula-Evaluation)
  context: z.record(z.string(), z.any()).optional(),
});

export type CalcQuoteInput = z.infer<typeof CalcQuoteInputSchema>;

/**
 * Price Quote - Berechnetes Preisangebot
 */
export const PriceQuoteSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Input-Referenz
  inputs: CalcQuoteInputSchema,
  
  // Komponenten (Breakdown)
  components: z.array(PriceComponentSchema),
  
  // Ergebnis
  totalNet: z.number(),                          // Netto-Gesamtpreis (ohne USt)
  totalGross: z.number().optional(),             // Brutto (inkl. USt), falls berechnet
  currency: z.string().default('EUR'),
  
  // Gültigkeit
  calculatedAt: z.string().datetime().optional(),
  expiresAt: z.string().datetime(),              // Quote-Gültigkeit (z.B. 24h)
  
  // Signatur (optional, für Verifizierung)
  signature: z.string().optional(),
  
  // Metadata
  createdBy: z.string().optional(),
});

export type PriceQuote = z.infer<typeof PriceQuoteSchema>;

/**
 * Create Price Quote DTO (wird vom Service berechnet)
 */
export const CreatePriceQuoteSchema = PriceQuoteSchema.omit({
  id: true,
  calculatedAt: true,
  signature: true,
});

export type CreatePriceQuote = z.infer<typeof CreatePriceQuoteSchema>;
