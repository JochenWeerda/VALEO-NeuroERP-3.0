"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fetchFromBVL = fetchFromBVL;
exports.searchPSM = searchPSM;
const pino_1 = __importDefault(require("pino"));
const logger = (0, pino_1.default)({ name: 'bvl-api' });
const BVL_API_BASE_URL = process.env.BVL_API_URL || 'https://apps2.bvl.bund.de/psm/jsp';
async function fetchFromBVL(identifier) {
    logger.info({ identifier }, 'Fetching PSM from BVL (Mock)');
    try {
        const mockDatabase = {
            '024266-00': {
                bvlId: '024266-00',
                name: 'Roundup PowerFlex',
                activeSubstances: ['Glyphosat'],
                approvalStatus: 'Approved',
                approvalValidTo: '2025-12-31T23:59:59Z',
                approvalNumber: '024266-00',
                usageScope: 'Getreide, Raps, Mais',
                restrictions: ['Nicht in Wasserschutzgebieten'],
                sourceUrl: `${BVL_API_BASE_URL}/index.jsp?id=024266-00`,
            },
            'Roundup': {
                bvlId: '024266-00',
                name: 'Roundup PowerFlex',
                activeSubstances: ['Glyphosat'],
                approvalStatus: 'Approved',
                approvalValidTo: '2025-12-31T23:59:59Z',
                usageScope: 'Getreide, Raps, Mais',
                sourceUrl: `${BVL_API_BASE_URL}/index.jsp`,
            },
            '006498-00': {
                bvlId: '006498-00',
                name: 'Karate Zeon',
                activeSubstances: ['Lambda-Cyhalothrin'],
                approvalStatus: 'Approved',
                approvalValidTo: '2026-06-30T23:59:59Z',
                usageScope: 'Raps, Getreide',
                restrictions: [],
                sourceUrl: `${BVL_API_BASE_URL}/index.jsp?id=006498-00`,
            },
        };
        const result = mockDatabase[identifier];
        if (result) {
            logger.info({ identifier, bvlId: result.bvlId }, 'PSM found in BVL (Mock)');
            return result;
        }
        for (const [key, value] of Object.entries(mockDatabase)) {
            if (value.name.toLowerCase().includes(identifier.toLowerCase())) {
                logger.info({ identifier, found: value.name }, 'PSM found by partial match (Mock)');
                return value;
            }
        }
        logger.warn({ identifier }, 'PSM not found in BVL (Mock)');
        return null;
    }
    catch (error) {
        logger.error({ error, identifier }, 'Failed to fetch PSM from BVL');
        return null;
    }
}
async function searchPSM(query, filters) {
    logger.info({ query, filters }, 'Searching PSM in BVL (Mock)');
    const mockResults = [
        {
            bvlId: '024266-00',
            name: 'Roundup PowerFlex',
            activeSubstances: ['Glyphosat'],
            approvalStatus: 'Approved',
            usageScope: 'Getreide, Raps, Mais',
        },
        {
            bvlId: '006498-00',
            name: 'Karate Zeon',
            activeSubstances: ['Lambda-Cyhalothrin'],
            approvalStatus: 'Approved',
            usageScope: 'Raps, Getreide',
        },
    ];
    let filtered = mockResults.filter(item => item.name.toLowerCase().includes(query.toLowerCase()));
    if (filters?.activeSubstance) {
        filtered = filtered.filter(item => item.activeSubstances.some(s => s.toLowerCase().includes(filters.activeSubstance.toLowerCase())));
    }
    if (filters?.crop) {
        filtered = filtered.filter(item => item.usageScope.toLowerCase().includes(filters.crop.toLowerCase()));
    }
    return filtered;
}
//# sourceMappingURL=bvl-api.js.map