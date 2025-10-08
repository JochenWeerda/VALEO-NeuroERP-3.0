"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fetchKTBLEmissionParameters = fetchKTBLEmissionParameters;
exports.calculateCropEmissions = calculateCropEmissions;
exports.getKTBLStatus = getKTBLStatus;
exports.getCachedKTBLData = getCachedKTBLData;
exports.setCachedKTBLData = setCachedKTBLData;
const axios_1 = __importDefault(require("axios"));
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'ktbl-api' });
const KTBL_API_BASE_URL = process.env.KTBL_API_URL || 'https://www.ktbl.de/webanwendungen/bek-parameter';
const KTBL_API_ENABLED = process.env.KTBL_API_ENABLED === 'true';
async function fetchKTBLEmissionParameters(crop, region) {
    if (!KTBL_API_ENABLED) {
        logger.warn('KTBL API is disabled, using fallback data');
        return getKTBLFallbackData(crop, region);
    }
    try {
        logger.info({ crop, region }, 'Fetching KTBL BEK parameters');
        const response = await axios_1.default.get(`${KTBL_API_BASE_URL}/api/crop-emissions`, {
            params: {
                crop,
                region,
            },
            timeout: 10000,
        });
        return response.data;
    }
    catch (error) {
        logger.error({ error, crop, region }, 'Failed to fetch KTBL parameters, using fallback');
        return getKTBLFallbackData(crop, region);
    }
}
function getKTBLFallbackData(crop, region) {
    const cropLower = crop.toLowerCase();
    const fallbackDatabase = {
        'raps': {
            direct: 420,
            indirect: 180,
            upstream: 250,
            total: 850,
        },
        'weizen': {
            direct: 380,
            indirect: 160,
            upstream: 220,
            total: 760,
        },
        'mais': {
            direct: 400,
            indirect: 170,
            upstream: 240,
            total: 810,
        },
        'soja': {
            direct: 350,
            indirect: 150,
            upstream: 200,
            total: 700,
        },
        'sonnenblume': {
            direct: 390,
            indirect: 165,
            upstream: 230,
            total: 785,
        },
    };
    const emissions = fallbackDatabase[cropLower] || {
        direct: 400,
        indirect: 170,
        upstream: 230,
        total: 800,
    };
    return {
        crop,
        region: region || 'DE-Generic',
        yieldPerHa: 3.5,
        nitrogenFertilizer: 150,
        emissions,
        source: 'Fallback Values (KTBL offline)',
        calculatedAt: new Date().toISOString(),
    };
}
async function calculateCropEmissions(crop, options) {
    const ktblData = await fetchKTBLEmissionParameters(crop, options?.region);
    if (!ktblData) {
        throw new Error(`No KTBL data available for crop: ${crop}`);
    }
    let emissionsPerTon = ktblData.emissions.total;
    if (options?.yieldPerHa && ktblData.yieldPerHa) {
        const yieldFactor = ktblData.yieldPerHa / options.yieldPerHa;
        emissionsPerTon = ktblData.emissions.total * yieldFactor;
    }
    if (options?.fertilizer && ktblData.nitrogenFertilizer) {
        const fertilizerDiff = options.fertilizer - ktblData.nitrogenFertilizer;
        const additionalN2O = fertilizerDiff * 4.5;
        emissionsPerTon += additionalN2O / (options.yieldPerHa || ktblData.yieldPerHa);
    }
    return {
        emissionsPerTon: Math.round(emissionsPerTon),
        breakdown: ktblData.emissions,
        dataSource: ktblData.source,
    };
}
async function getKTBLStatus() {
    if (!KTBL_API_ENABLED) {
        return {
            available: false,
            lastCheck: new Date().toISOString(),
            message: 'KTBL API is disabled in configuration',
            fallbackActive: true,
        };
    }
    try {
        const response = await axios_1.default.get(`${KTBL_API_BASE_URL}/status`, {
            timeout: 5000,
        });
        return {
            available: true,
            lastCheck: new Date().toISOString(),
            message: 'KTBL BEK-Parameter verfügbar',
            fallbackActive: false,
        };
    }
    catch (error) {
        logger.warn({ error }, 'KTBL service not available');
        return {
            available: false,
            lastCheck: new Date().toISOString(),
            message: 'KTBL BEK-Parameter werden überarbeitet (aktuell offline). Fallback-Daten werden verwendet.',
            fallbackActive: true,
        };
    }
}
const ktblCache = new Map();
const CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000;
function getCachedKTBLData(crop, region) {
    const cacheKey = `${crop}:${region || 'default'}`;
    const cached = ktblCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
        logger.debug({ crop, region }, 'KTBL cache hit');
        return cached.data;
    }
    return null;
}
function setCachedKTBLData(crop, region, data) {
    const cacheKey = `${crop}:${region || 'default'}`;
    ktblCache.set(cacheKey, { data, timestamp: Date.now() });
}
//# sourceMappingURL=ktbl-api.js.map