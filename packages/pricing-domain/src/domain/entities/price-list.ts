import { z } from 'zod';

/**
 * Price List Status
 */
export const PriceListStatusEnum = z.enum([
  'Draft',      // Entwurf
  'Active',     // Aktiv
  'Archived',   // Archiviert
]);

export type PriceListStatus = z.infer<typeof PriceListStatusEnum>;

/**
 * Tier Break - Staffelpreis
 */
export const TierBreakSchema = z.object({
  minQty: z.number().min(0),
  maxQty: z.number().optional(),
  price: z.number(),
});

export type TierBreak = z.infer<typeof TierBreakSchema>;

/**
 * Price List Line - Einzelposition
 */
export const PriceListLineSchema = z.object({
  sku: z.string().min(1, 'SKU is required'),           // z.B. "WHEAT-11.5", "RAPE-00"
  commodity: z.string().optional(),                      // z.B. "WHEAT", "RAPE_OIL"
  basePrice: z.number(),                                 // Grundpreis
  uom: z.string().default('t'),                          // Unit of Measure (t, kg, l)
  currency: z.string().default('EUR'),
  
  // Staffelpreise (optional)
  tierBreaks: z.array(TierBreakSchema).optional(),
  
  // Mindestmenge
  minQty: z.number().optional(),
  
  // Sonstiges
  description: z.string().optional(),
  active: z.boolean().default(true),
});

export type PriceListLine = z.infer<typeof PriceListLineSchema>;

/**
 * Price List - Preisliste
 */
export const PriceListSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Identifikation
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  code: z.string().optional(), // z.B. "PL-2025-Q1"
  
  // Währung
  currency: z.string().default('EUR'),
  
  // Gültigkeit
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),
  
  // Lines
  lines: z.array(PriceListLineSchema).min(1, 'At least one line is required'),
  
  // Status
  status: PriceListStatusEnum.default('Draft'),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  createdBy: z.string().optional(),
  updatedAt: z.string().datetime().optional(),
  updatedBy: z.string().optional(),
  activatedAt: z.string().datetime().optional(),
  activatedBy: z.string().optional(),
});

export type PriceList = z.infer<typeof PriceListSchema>;

/**
 * Create Price List DTO
 */
export const CreatePriceListSchema = PriceListSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  activatedAt: true,
});

export type CreatePriceList = z.infer<typeof CreatePriceListSchema>;

/**
 * Update Price List DTO
 */
export const UpdatePriceListSchema = PriceListSchema.partial().omit({
  id: true,
  tenantId: true,
  createdAt: true,
  createdBy: true,
});

export type UpdatePriceList = z.infer<typeof UpdatePriceListSchema>;
