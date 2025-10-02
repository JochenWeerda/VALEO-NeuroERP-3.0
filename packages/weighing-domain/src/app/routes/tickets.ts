import { FastifyInstance } from 'fastify';
import { WeighingService } from '../../domain/services/weighing-service';
import {
  CreateWeighingTicketContractSchema,
  UpdateWeighingTicketContractSchema,
  RecordWeightContractSchema,
  WeighingTicketQueryContractSchema,
  WeighingTicketResponseContractSchema,
  WeighingTicketListResponseContractSchema
} from '../../contracts/weighing-ticket-contracts';

export async function registerTicketRoutes(
  fastify: FastifyInstance,
  weighingService: WeighingService
) {
  // Create weighing ticket
  fastify.post('/tickets', {
    schema: {
      description: 'Create a new weighing ticket',
      tags: ['weighing-tickets'],
      body: CreateWeighingTicketContractSchema,
      response: {
        201: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const tenantId = request.headers['x-tenant-id'] as string;
      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.createTicket({
          ...(request.body as any),
          tenantId
        });

        return reply.code(201).send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to create ticket' });
      }
    }
  });

  // Get ticket by ID
  fastify.get('/tickets/:id', {
    schema: {
      description: 'Get weighing ticket by ID',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.getTicket(id, tenantId);

        if (!ticket) {
          return reply.code(404).send({ error: 'Ticket not found' });
        }

        return reply.send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to get ticket' });
      }
    }
  });

  // Get ticket by number
  fastify.get('/tickets/number/:number', {
    schema: {
      description: 'Get weighing ticket by ticket number',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          number: { type: 'string' }
        },
        required: ['number']
      },
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { number } = request.params as { number: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.getTicketByNumber(number, tenantId);

        if (!ticket) {
          return reply.code(404).send({ error: 'Ticket not found' });
        }

        return reply.send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to get ticket' });
      }
    }
  });

  // List tickets with filtering and pagination
  fastify.get('/tickets', {
    schema: {
      description: 'List weighing tickets with filtering and pagination',
      tags: ['weighing-tickets'],
      querystring: WeighingTicketQueryContractSchema,
      response: {
        200: WeighingTicketListResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const tenantId = request.headers['x-tenant-id'] as string;
      const query = request.query as any;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const result = await weighingService.getTickets(tenantId, query, {
          page: query.page,
          pageSize: query.pageSize
        });

        return reply.send(result);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to list tickets' });
      }
    }
  });

  // Update ticket
  fastify.patch('/tickets/:id', {
    schema: {
      description: 'Update weighing ticket',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      body: UpdateWeighingTicketContractSchema,
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.updateTicket(id, tenantId, request.body as any);

        return reply.send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to update ticket' });
      }
    }
  });

  // Record weight measurement
  fastify.post('/tickets/:id/weigh', {
    schema: {
      description: 'Record weight measurement for a ticket',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      body: RecordWeightContractSchema,
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.recordWeight({
          ticketId: id,
          tenantId,
          ...(request.body as any)
        });

        return reply.send(ticket);
      } catch (error) {
        request.log.error({ error });
        return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
      }
    }
  });

  // Complete ticket
  fastify.post('/tickets/:id/complete', {
    schema: {
      description: 'Complete a weighing ticket',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.completeTicket(id, tenantId);

        return reply.send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
      }
    }
  });

  // Cancel ticket
  fastify.post('/tickets/:id/cancel', {
    schema: {
      description: 'Cancel a weighing ticket',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      body: {
        type: 'object',
        properties: {
          reason: { type: 'string' }
        }
      },
      response: {
        200: WeighingTicketResponseContractSchema
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;
      const { reason } = request.body as { reason?: string };

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const ticket = await weighingService.cancelTicket(id, tenantId, reason);

        return reply.send(ticket);
      } catch (error) {
        request.log.error(error);
        return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
      }
    }
  });

  // Delete ticket (only draft tickets)
  fastify.delete('/tickets/:id', {
    schema: {
      description: 'Delete a draft weighing ticket',
      tags: ['weighing-tickets'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' }
        },
        required: ['id']
      },
      response: {
        204: { type: 'null' }
      }
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const deleted = await weighingService.deleteTicket(id, tenantId);

        if (!deleted) {
          return reply.code(404).send({ error: 'Ticket not found' });
        }

        return reply.code(204).send();
      } catch (error) {
        request.log.error(error);
        return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
      }
    }
  });

  // Get active tickets
  fastify.get('/tickets/active', {
    schema: {
      description: 'Get all active (in-progress) tickets',
      tags: ['weighing-tickets'],
      response: {
        200: {
          type: 'array',
          items: WeighingTicketResponseContractSchema
        }
      }
    },
    handler: async (request, reply) => {
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const tickets = await weighingService.getActiveTickets(tenantId);

        return reply.send(tickets);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to get active tickets' });
      }
    }
  });

  // Get completed tickets today
  fastify.get('/tickets/completed-today', {
    schema: {
      description: 'Get tickets completed today',
      tags: ['weighing-tickets'],
      response: {
        200: {
          type: 'array',
          items: WeighingTicketResponseContractSchema
        }
      }
    },
    handler: async (request, reply) => {
      const tenantId = request.headers['x-tenant-id'] as string;

      if (!tenantId) {
        return reply.code(400).send({ error: 'Tenant ID required' });
      }

      try {
        const tickets = await weighingService.getCompletedTicketsToday(tenantId);

        return reply.send(tickets);
      } catch (error) {
        request.log.error(error);
        return reply.code(500).send({ error: 'Failed to get completed tickets' });
      }
    }
  });
}