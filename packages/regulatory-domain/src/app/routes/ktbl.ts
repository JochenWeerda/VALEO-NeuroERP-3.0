import { FastifyInstance } from 'fastify';
import { getKTBLStatus, fetchKTBLEmissionParameters, calculateCropEmissions } from '../../infra/integrations/ktbl-api';

export async function registerKTBLRoutes(server: FastifyInstance): Promise<void> {
  // Get KTBL service status
  server.get('/ktbl/status', async (request, reply) => {
    const status = await getKTBLStatus();
    reply.send(status);
  });

  // Get emission parameters for crop
  server.get('/ktbl/crop-emissions/:crop', async (request, reply) => {
    const { crop } = request.params as { crop: string };
    const query = request.query as Record<string, string>;

    const parameters = await fetchKTBLEmissionParameters(crop, query.region);

    if (parameters === undefined || parameters === null) {
      reply.code(404).send({
        error: 'NotFound',
        message: `No KTBL parameters found for crop: ${crop}`,
      });
      return;
    }

    reply.send(parameters);
  });

  // Calculate crop emissions with custom parameters
  server.post('/ktbl/calculate', async (request, reply) => {
    const { crop, yieldPerHa, fertilizer, region } = request.body as {
      crop: string;
      yieldPerHa?: number;
      fertilizer?: number;
      region?: string;
    };

    if (crop === undefined || crop === null) {
      reply.code(400).send({
        error: 'BadRequest',
        message: 'Crop is required',
      });
      return;
    }

    const result = await calculateCropEmissions(crop, {
      yieldPerHa: yieldPerHa ?? undefined,
      fertilizer: fertilizer ?? undefined,
      region: region ?? undefined,
    } as any);

    reply.send(result);
  });
}

