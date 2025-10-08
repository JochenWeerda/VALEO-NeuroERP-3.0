/**
 * GHG Pathway Entities for RED II compliance
 */
import { z } from 'zod';

/**
 * GHG Calculation Input
 */
export const GHGCalculationInputSchema = z.object({
  commodity: z.string().min(1, 'Commodity is required'),
  method: z.enum(['Default', 'Actual', 'Disaggregated', 'NUTS2']),
  
  // Optionale Actual-Werte (wenn method = Actual)
  actualData: z.object({
    cultivationEmissions: z.number().optional(),
    processingEmissions: z.number().optional(),
    transportDistance: z.number().optional(), // km
    transportMode: z.enum(['Truck', 'Train', 'Ship', 'Pipeline']).optional(),
    landUseChange: z.number().optional(),
    
    // KTBL-spezifische Parameter (optional)
    yieldPerHa: z.number().optional(), // t/ha
    nitrogenFertilizer: z.number().optional(), // kg N/ha
    useKTBL: z.boolean().optional(), // Soll KTBL-Datenbank genutzt werden?
  }).optional(),
});

export type GHGCalculationInput = z.infer<typeof GHGCalculationInputSchema>;

export const GHGMethodEnum = z.enum(['Default', 'Actual', 'Disaggregated', 'NUTS2']);
export type GHGMethod = z.infer<typeof GHGMethodEnum>;

/**
 * GHG Pathway Entity
 */
export const GHGPathwaySchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  commodity: z.string(),
  method: GHGMethodEnum,
  
  // Emissionen (g CO2eq/MJ)
  emissions: z.object({
    cultivation: z.number(),
    processing: z.number(),
    transport: z.number(),
    total: z.number(),
    landUseChange: z.number().optional(),
  }),
  
  // Metadata
  calculatedBy: z.string(),
  calculatedAt: z.date(),
  validUntil: z.date().optional(),
  source: z.enum(['Default', 'KTBL', 'BLE', 'Custom']),
  certification: z.object({
    certificationScheme: z.string().optional(),
    certified: z.boolean(),
    certifiedBy: z.string().optional(),
    certifiedAt: z.date().optional(),
  }).optional(),
});

export type GHGPathway = z.infer<typeof GHGPathwaySchema>;

/**
 * Create GHG Pathway Input
 */
export const CreateGHGPathwaySchema = GHGPathwaySchema.omit({ id: true, calculatedAt: true });
export type CreateGHGPathwayInput = z.infer<typeof CreateGHGPathwaySchema>;
