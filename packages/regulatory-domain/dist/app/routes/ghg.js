"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerGHGRoutes = registerGHGRoutes;
const ghg_pathway_1 = require("../../domain/entities/ghg-pathway");
const ghg_calculation_service_1 = require("../../domain/services/ghg-calculation-service");
async function registerGHGRoutes(server) {
    server.post('/ghg/calc', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const userId = request.authContext?.userId || 'system';
        const input = ghg_pathway_1.GHGCalculationInputSchema.parse(request.body);
        const pathway = await (0, ghg_calculation_service_1.calculateGHG)(tenantId, input, userId);
        reply.code(201).send(pathway);
    });
    server.get('/ghg/pathways', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const query = request.query;
        const pathways = await (0, ghg_calculation_service_1.getGHGPathways)(tenantId, {
            commodity: query.commodity ?? undefined,
            method: query.method ?? undefined,
        });
        reply.send({ data: pathways, count: pathways.length });
    });
}
//# sourceMappingURL=ghg.js.map