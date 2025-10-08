import { FastifyInstance } from 'fastify';
import { CalcQuoteInputSchema } from '../../domain/entities/price-quote';
import { calculateQuote, getQuoteById } from '../../domain/services/price-calculator';

export async function registerQuoteRoutes(server: FastifyInstance): Promise<void> {
  // Calculate price quote
  server.post('/quotes/calc', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = (request as any).authContext?.userId ?? 'system';

    const input = CalcQuoteInputSchema.parse(request.body);
    const quote = await calculateQuote(tenantId, input, userId);

    reply.code(201).send(quote);
  });

  // Get quote by ID
  server.get('/quotes/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const quote = await getQuoteById(tenantId, id);
    
    if (quote === undefined || quote === null) {
      reply.code(404).send({ error: 'NotFound', message: 'Quote not found or expired' });
      return;
    }

    reply.send(quote);
  });
}

