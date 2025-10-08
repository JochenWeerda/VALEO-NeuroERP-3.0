"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.REDII_DEFAULT_VALUES = exports.CreateGHGPathwaySchema = exports.GHGPathwaySchema = exports.GHGFactorsSchema = exports.GHGStandardEnum = exports.GHGMethodEnum = exports.GHGCalculationInputSchema = void 0;
exports.GHGCalculationInputSchema = z.object({
    commodity: z.string().min(1, 'Commodity is required'),
    method: exports.GHGMethodEnum,
    actualData: z.object({
        cultivationEmissions: z.number().optional(),
        processingEmissions: z.number().optional(),
        transportDistance: z.number().optional(),
        transportMode: z.enum(['Truck', 'Train', 'Ship', 'Pipeline']).optional(),
        landUseChange: z.number().optional(),
        yieldPerHa: z.number().optional(),
        nitrogenFertilizer: z.number().optional(),
        useKTBL: z.boolean().optional(),
    }).optional(),
    originRegion: z.string().optional(),
    destinationRegion: z.string().optional(),
    processingRoute: z.string().optional(),
});
exports.GHGMethodEnum = z.enum([
    'Default',
    'Actual',
    'Hybrid',
]);
exports.GHGStandardEnum = z.enum([
    'REDII',
    'REDIII',
    'ISCC',
    'RTRS',
    'Custom',
]);
exports.GHGFactorsSchema = z.object({
    cultivation: z.number().default(0),
    processing: z.number().default(0),
    transport: z.number().default(0),
    landUseChange: z.number().default(0),
    distribution: z.number().optional(),
    storage: z.number().optional(),
    packaging: z.number().optional(),
    credits: z.number().optional(),
});
exports.GHGPathwaySchema = z.object({
    id: z.string().uuid().optional(),
    tenantId: z.string().min(1, 'Tenant ID is required'),
    commodity: z.string().min(1, 'Commodity is required'),
    pathwayKey: z.string().min(1, 'Pathway key is required'),
    description: z.string().optional(),
    method: exports.GHGMethodEnum,
    standard: exports.GHGStandardEnum.default('REDII'),
    factors: exports.GHGFactorsSchema,
    totalEmissions: z.number(),
    emissionsPerTon: z.number().optional(),
    savingsVsFossil: z.number().optional(),
    rediiThreshold: z.number().optional(),
    rediiCompliant: z.boolean().optional(),
    dataSources: z.array(z.object({
        factor: z.string(),
        source: z.string(),
        value: z.number(),
    })).optional(),
    calculatedAt: z.string().datetime().optional(),
    calculatedBy: z.string().optional(),
    validFrom: z.string().datetime().optional(),
    validTo: z.string().datetime().optional(),
    createdAt: z.string().datetime().optional(),
    updatedAt: z.string().datetime().optional(),
});
exports.CreateGHGPathwaySchema = exports.GHGPathwaySchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    calculatedAt: true,
});
exports.REDII_DEFAULT_VALUES = {
    'RAPE_OIL_BIODIESEL': { totalEmissions: 52, savingsVsFossil: 38 },
    'SUNFLOWER_OIL_BIODIESEL': { totalEmissions: 35, savingsVsFossil: 58 },
    'SOYBEAN_OIL_BIODIESEL': { totalEmissions: 40, savingsVsFossil: 52 },
    'PALM_OIL_BIODIESEL': { totalEmissions: 56, savingsVsFossil: 33 },
    'UCO_BIODIESEL': { totalEmissions: 14, savingsVsFossil: 83 },
    'RAPE_MEAL_FEED': { totalEmissions: 20, savingsVsFossil: 0 },
};
//# sourceMappingURL=ghg-pathway.js.map