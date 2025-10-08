"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.calculateGHG = calculateGHG;
exports.getGHGPathways = getGHGPathways;
const connection_1 = require("../../infra/db/connection");
const schema_1 = require("../../infra/db/schema");
const ghg_pathway_1 = require("../entities/ghg-pathway");
const publisher_1 = require("../../infra/messaging/publisher");
const ktbl_api_1 = require("../../infra/integrations/ktbl-api");
const drizzle_orm_1 = require("drizzle-orm");
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'ghg-calculation' });
async function calculateGHG(tenantId, input, userId) {
    logger.info({ tenantId, commodity: input.commodity, method: input.method }, 'Calculating GHG emissions');
    let factors;
    let totalEmissions;
    let savingsVsFossil;
    const dataSources = [];
    if (input.method === 'Default') {
        const defaultKey = `${input.commodity}_BIODIESEL`;
        const defaultValues = ghg_pathway_1.REDII_DEFAULT_VALUES[defaultKey];
        if (!defaultValues) {
            throw new Error(`No RED II default values found for ${input.commodity}`);
        }
        totalEmissions = defaultValues.totalEmissions;
        savingsVsFossil = defaultValues.savingsVsFossil;
        factors = {
            cultivation: totalEmissions * 0.4,
            processing: totalEmissions * 0.3,
            transport: totalEmissions * 0.2,
            landUseChange: totalEmissions * 0.1,
        };
        dataSources.push({
            factor: 'total',
            source: 'RED II Annex V Default Values',
            value: totalEmissions,
        });
    }
    else if (input.method === 'Actual' && input.actualData) {
        let cultivationEmissions = input.actualData.cultivationEmissions || 0;
        let cultivationSource = 'Operator Data';
        try {
            const ktblStatus = await (0, ktbl_api_1.getKTBLStatus)();
            if (ktblStatus.available || ktblStatus.fallbackActive) {
                const ktblData = await (0, ktbl_api_1.calculateCropEmissions)(input.commodity, {
                    yieldPerHa: input.actualData.yieldPerHa,
                    fertilizer: input.actualData.nitrogenFertilizer,
                    region: input.originRegion,
                });
                cultivationEmissions = ktblData.emissionsPerTon / 40;
                cultivationSource = ktblData.dataSource;
                dataSources.push({
                    factor: 'cultivation',
                    source: `KTBL BEK: ${cultivationSource}`,
                    value: cultivationEmissions,
                });
            }
        }
        catch (error) {
            logger.warn({ error }, 'KTBL integration failed, using operator data');
        }
        factors = {
            cultivation: cultivationEmissions,
            processing: input.actualData.processingEmissions || 0,
            transport: calculateTransportEmissions(input.actualData.transportDistance, input.actualData.transportMode),
            landUseChange: input.actualData.landUseChange || 0,
        };
        totalEmissions = factors.cultivation + factors.processing + factors.transport + factors.landUseChange;
        const fossilBaseline = 94;
        savingsVsFossil = Math.round(((fossilBaseline - totalEmissions) / fossilBaseline) * 100);
        if (!dataSources.find(ds => ds.factor === 'cultivation')) {
            dataSources.push({ factor: 'cultivation', source: cultivationSource, value: factors.cultivation });
        }
        dataSources.push({ factor: 'processing', source: 'Operator Data', value: factors.processing }, { factor: 'transport', source: 'Calculated', value: factors.transport });
    }
    else {
        throw new Error('Invalid method or missing actualData for Actual calculation');
    }
    const rediiThreshold = determineREDIIThreshold(new Date());
    const rediiCompliant = savingsVsFossil !== undefined && savingsVsFossil >= rediiThreshold;
    const pathwayKey = generatePathwayKey(input.commodity, input.originRegion, input.method);
    const [pathway] = await connection_1.db.insert(schema_1.ghgPathways).values({
        tenantId,
        commodity: input.commodity,
        pathwayKey,
        method: input.method,
        standard: 'REDII',
        factors: factors,
        totalEmissions: totalEmissions.toString(),
        savingsVsFossil: savingsVsFossil?.toString(),
        rediiThreshold: rediiThreshold.toString(),
        rediiCompliant,
        dataSources: dataSources,
        calculatedAt: new Date(),
        calculatedBy: userId,
    }).returning();
    if (!pathway) {
        throw new Error('Failed to create GHG pathway');
    }
    await (0, publisher_1.publishEvent)('ghg.pathway.created', {
        tenantId,
        pathwayId: pathway.id,
        commodity: pathway.commodity,
        method: pathway.method,
        totalEmissions,
        savingsVsFossil,
        rediiCompliant,
        occurredAt: new Date().toISOString(),
    });
    return pathway;
}
function calculateTransportEmissions(distance, mode) {
    if (!distance)
        return 0;
    const emissionFactors = {
        'Truck': 0.062,
        'Train': 0.022,
        'Ship': 0.008,
        'Pipeline': 0.003,
    };
    const factor = emissionFactors[mode || 'Truck'] || 0.062;
    return distance * factor;
}
function determineREDIIThreshold(date) {
    const year = date.getFullYear();
    if (year < 2021)
        return 50;
    if (year < 2026)
        return 60;
    return 65;
}
function generatePathwayKey(commodity, region, method) {
    const parts = [region || 'EU', commodity, method || 'Default'];
    return parts.join('-');
}
async function getGHGPathways(tenantId, filters = {}) {
    let query = connection_1.db.select().from(schema_1.ghgPathways).where((0, drizzle_orm_1.eq)(schema_1.ghgPathways.tenantId, tenantId));
    const results = await query;
    let filtered = results;
    if (filters.commodity) {
        filtered = filtered.filter(p => p.commodity === filters.commodity);
    }
    if (filters.method) {
        filtered = filtered.filter(p => p.method === filters.method);
    }
    return filtered;
}
//# sourceMappingURL=ghg-calculation-service.js.map