import { FastifyInstance } from 'fastify';

export async function registerCreditNoteRoutes(fastify: FastifyInstance) {
  fastify.register(async (creditNoteRoutes) => {
    // GET /credit-notes - List credit notes
    creditNoteRoutes.get('/', async (request, reply) => {
      return { data: [], pagination: { page: 1, pageSize: 20, total: 0, totalPages: 0 } };
    });

    // POST /credit-notes - Create credit note
    creditNoteRoutes.post('/', async (request, reply) => {
      return reply.code(201).send({ id: 'credit-note-123' });
    });

    // GET /credit-notes/:id - Get credit note by ID
    creditNoteRoutes.get('/:id', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, status: 'Issued' };
    });

    // PATCH /credit-notes/:id - Update credit note
    creditNoteRoutes.patch('/:id', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, updated: true };
    });

    // POST /credit-notes/:id/settle - Settle credit note
    creditNoteRoutes.post('/:id/settle', async (request, reply) => {
      const { id } = request.params as { id: string };
      return { id, status: 'Settled' };
    });
  }, { prefix: '/credit-notes' });
}