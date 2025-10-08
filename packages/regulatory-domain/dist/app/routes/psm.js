"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerPSMRoutes = registerPSMRoutes;
const psm_product_1 = require("../../domain/entities/psm-product");
const psm_check_service_1 = require("../../domain/services/psm-check-service");
const bvl_api_1 = require("../../infra/integrations/bvl-api");
async function registerPSMRoutes(server) {
    server.post('/psm/check', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const input = psm_product_1.PSMCheckInputSchema.parse({ ...request.body, tenantId });
        const result = await (0, psm_check_service_1.checkPSM)(tenantId, input);
        reply.send(result);
    });
    server.get('/psm/search', async (request, reply) => {
        const query = request.query;
        if (!query.q) {
            reply.code(400).send({ error: 'BadRequest', message: 'Query parameter "q" is required' });
            return;
        }
        const results = await (0, bvl_api_1.searchPSM)(query.q, {
            activeSubstance: query.activeSubstance ?? undefined,
            crop: query.crop ?? undefined,
        });
        reply.send({ data: results, count: results.length });
    });
}
//# sourceMappingURL=psm.js.map