import { FastifyInstance } from 'fastify';

export async function registerOrderRoutes(fastify: FastifyInstance) {
  fastify.register(async (orderRoutes) => {
    // GET /orders - List orders
    orderRoutes.get('/', async (request, reply) => {
      return { data: [], pagination: { page: 1, pageSize: 20, total: 0, totalPages: 0 } };
    });

    // POST /orders - Create order
    orderRoutes.post('/', async (request, reply) => {
      return reply.code(201).send({ id: 'order-123' });
    });

    // GET /orders/:id - Get order by ID
    orderRoutes.get('/:id', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, status: 'Draft' };
    });

    // PATCH /orders/:id - Update order
    orderRoutes.patch('/:id', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, updated: true };
    });

    // POST /orders/:id/confirm - Confirm order
    orderRoutes.post('/:id/confirm', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, status: 'Confirmed' };
    });
  }, { prefix: '/orders' });
}