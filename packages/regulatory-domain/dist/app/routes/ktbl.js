"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerKTBLRoutes = registerKTBLRoutes;
const ktbl_api_1 = require("../../infra/integrations/ktbl-api");
async function registerKTBLRoutes(server) {
    server.get('/ktbl/status', async (request, reply) => {
        const status = await (0, ktbl_api_1.getKTBLStatus)();
        reply.send(status);
    });
    server.get('/ktbl/crop-emissions/:crop', async (request, reply) => {
        const { crop } = request.params;
        const query = request.query;
        const parameters = await (0, ktbl_api_1.fetchKTBLEmissionParameters)(crop, query.region);
        if (!parameters) {
            reply.code(404).send({
                error: 'NotFound',
                message: `No KTBL parameters found for crop: ${crop}`,
            });
            return;
        }
        reply.send(parameters);
    });
    server.post('/ktbl/calculate', async (request, reply) => {
        const { crop, yieldPerHa, fertilizer, region } = request.body;
        if (!crop) {
            reply.code(400).send({
                error: 'BadRequest',
                message: 'Crop is required',
            });
            return;
        }
        const result = await (0, ktbl_api_1.calculateCropEmissions)(crop, {
            yieldPerHa: yieldPerHa ?? undefined,
            fertilizer: fertilizer ?? undefined,
            region: region ?? undefined,
        });
        reply.send(result);
    });
}
//# sourceMappingURL=ktbl.js.map