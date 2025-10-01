/**
 * GHG Calculation Input
 */
export const GHGCalculationInputSchema = z.object({
  commodity: z.string().min(1, 'Commodity is required'),
  method: GHGMethodEnum,
  
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
  
  // Kontext
  originRegion: z.string().optional(), // NUTS-2 Region (für KTBL)
  destinationRegion: z.string().optional(),
  processingRoute: z.string().optional(), // z.B. "Crushing-Extraction-Refining"
});

export type GHGCalculationInput = z.infer<typeof GHGCalculationInputSchema>;

/**
 * GHG Calculation Method
 */
export const GHGMethodEnum = z.enum([
  'Default',        // RED II Default-Werte (Annex V)
  'Actual',         // Tatsächliche Werte (NUTS-2-Disaggregation)
  'Hybrid',         // Kombination Default + Actual
]);

export type GHGMethod = z.infer<typeof GHGMethodEnum>;

/**
 * GHG Standard
 */
export const GHGStandardEnum = z.enum([
  'REDII',          // RED II (EU 2018/2001)
  'REDIII',         // RED III (ab 2024)
  'ISCC',           // ISCC
  'RTRS',           // RTRS
  'Custom',         // Kundenspezifisch
]);

export type GHGStandard = z.infer<typeof GHGStandardEnum>;

/**
 * GHG Factors - Emissionsfaktoren
 */
export const GHGFactorsSchema = z.object({
  // Upstream (Anbau, Dünger, Pestizide)
  cultivation: z.number().default(0), // gCO2eq/MJ
  
  // Processing (Verarbeitung, Extraktion)
  processing: z.number().default(0),
  
  // Transport & Logistik
  transport: z.number().default(0),
  
  // Land Use Change (LUC)
  landUseChange: z.number().default(0),
  
  // Weitere Faktoren
  distribution: z.number().optional(),
  storage: z.number().optional(),
  packaging: z.number().optional(),
  
  // Gutschriften (Credits)
  credits: z.number().optional(),
});

export type GHGFactors = z.infer<typeof GHGFactorsSchema>;

/**
 * GHG Pathway - Treibhausgas-Pfad
 */
export const GHGPathwaySchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1, 'Tenant ID is required'),
  
  // Pathway-Identifikation
  commodity: z.string().min(1, 'Commodity is required'), // z.B. "RAPE_OIL"
  pathwayKey: z.string().min(1, 'Pathway key is required'), // z.B. "EU-Rape-Biodiesel"
  description: z.string().optional(),
  
  // Methode & Standard
  method: GHGMethodEnum,
  standard: GHGStandardEnum.default('REDII'),
  
  // Emissionsfaktoren
  factors: GHGFactorsSchema,
  
  // Ergebnis
  totalEmissions: z.number(), // gCO2eq/MJ
  emissionsPerTon: z.number().optional(), // kgCO2eq/t
  savingsVsFossil: z.number().optional(), // % Einsparung vs. Fossil (RED II: mind. 50-65%)
  
  // RED II Compliance
  rediiThreshold: z.number().optional(), // z.B. 50, 60, 65% je nach Zeitraum
  rediiCompliant: z.boolean().optional(),
  
  // Datenquellen
  dataSources: z.array(z.object({
    factor: z.string(),
    source: z.string(), // z.B. "JRC Database", "KTBL BEK", "Operator Data"
    value: z.number(),
  })).optional(),
  
  // Berechnung
  calculatedAt: z.string().datetime().optional(),
  calculatedBy: z.string().optional(),
  
  // Gültigkeit
  validFrom: z.string().datetime().optional(),
  validTo: z.string().datetime().optional(),
  
  // Metadata
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type GHGPathway = z.infer<typeof GHGPathwaySchema>;

/**
 * Create GHG Pathway DTO
 */
export const CreateGHGPathwaySchema = GHGPathwaySchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  calculatedAt: true,
});

export type CreateGHGPathway = z.infer<typeof CreateGHGPathwaySchema>;

/**
 * RED II Default Values (Annex V - Vereinfachte Version)
 */
export const REDII_DEFAULT_VALUES: Record<string, { totalEmissions: number; savingsVsFossil: number }> = {
  'RAPE_OIL_BIODIESEL': { totalEmissions: 52, savingsVsFossil: 38 }, // gCO2eq/MJ, % Savings
  'SUNFLOWER_OIL_BIODIESEL': { totalEmissions: 35, savingsVsFossil: 58 },
  'SOYBEAN_OIL_BIODIESEL': { totalEmissions: 40, savingsVsFossil: 52 },
  'PALM_OIL_BIODIESEL': { totalEmissions: 56, savingsVsFossil: 33 },
  'UCO_BIODIESEL': { totalEmissions: 14, savingsVsFossil: 83 }, // Used Cooking Oil
  'RAPE_MEAL_FEED': { totalEmissions: 20, savingsVsFossil: 0 }, // Feed, kein Fossil-Vergleich
};
