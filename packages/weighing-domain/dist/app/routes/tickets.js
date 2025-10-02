"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerTicketRoutes = registerTicketRoutes;
const weighing_ticket_contracts_1 = require("../../contracts/weighing-ticket-contracts");
async function registerTicketRoutes(fastify, weighingService) {
    fastify.post('/tickets', {
        schema: {
            description: 'Create a new weighing ticket',
            tags: ['weighing-tickets'],
            body: weighing_ticket_contracts_1.CreateWeighingTicketContractSchema,
            response: {
                201: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.createTicket({
                    ...request.body,
                    tenantId
                });
                return reply.code(201).send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to create ticket' });
            }
        }
    });
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
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.getTicket(id, tenantId);
                if (!ticket) {
                    return reply.code(404).send({ error: 'Ticket not found' });
                }
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to get ticket' });
            }
        }
    });
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
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { number } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.getTicketByNumber(number, tenantId);
                if (!ticket) {
                    return reply.code(404).send({ error: 'Ticket not found' });
                }
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to get ticket' });
            }
        }
    });
    fastify.get('/tickets', {
        schema: {
            description: 'List weighing tickets with filtering and pagination',
            tags: ['weighing-tickets'],
            querystring: weighing_ticket_contracts_1.WeighingTicketQueryContractSchema,
            response: {
                200: weighing_ticket_contracts_1.WeighingTicketListResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const tenantId = request.headers['x-tenant-id'];
            const query = request.query;
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const result = await weighingService.getTickets(tenantId, query, {
                    page: query.page,
                    pageSize: query.pageSize
                });
                return reply.send(result);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to list tickets' });
            }
        }
    });
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
            body: weighing_ticket_contracts_1.UpdateWeighingTicketContractSchema,
            response: {
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.updateTicket(id, tenantId, request.body);
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to update ticket' });
            }
        }
    });
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
            body: weighing_ticket_contracts_1.RecordWeightContractSchema,
            response: {
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.recordWeight({
                    ticketId: id,
                    tenantId,
                    ...request.body
                });
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error({ error });
                return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
            }
        }
    });
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
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.completeTicket(id, tenantId);
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
            }
        }
    });
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
                200: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
            }
        },
        handler: async (request, reply) => {
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            const { reason } = request.body;
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const ticket = await weighingService.cancelTicket(id, tenantId, reason);
                return reply.send(ticket);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
            }
        }
    });
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
            const { id } = request.params;
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const deleted = await weighingService.deleteTicket(id, tenantId);
                if (!deleted) {
                    return reply.code(404).send({ error: 'Ticket not found' });
                }
                return reply.code(204).send();
            }
            catch (error) {
                request.log.error(error);
                return reply.code(400).send({ error: error instanceof Error ? error.message : 'Unknown error' });
            }
        }
    });
    fastify.get('/tickets/active', {
        schema: {
            description: 'Get all active (in-progress) tickets',
            tags: ['weighing-tickets'],
            response: {
                200: {
                    type: 'array',
                    items: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
                }
            }
        },
        handler: async (request, reply) => {
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const tickets = await weighingService.getActiveTickets(tenantId);
                return reply.send(tickets);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to get active tickets' });
            }
        }
    });
    fastify.get('/tickets/completed-today', {
        schema: {
            description: 'Get tickets completed today',
            tags: ['weighing-tickets'],
            response: {
                200: {
                    type: 'array',
                    items: weighing_ticket_contracts_1.WeighingTicketResponseContractSchema
                }
            }
        },
        handler: async (request, reply) => {
            const tenantId = request.headers['x-tenant-id'];
            if (!tenantId) {
                return reply.code(400).send({ error: 'Tenant ID required' });
            }
            try {
                const tickets = await weighingService.getCompletedTicketsToday(tenantId);
                return reply.send(tickets);
            }
            catch (error) {
                request.log.error(error);
                return reply.code(500).send({ error: 'Failed to get completed tickets' });
            }
        }
    });
}
//# sourceMappingURL=tickets.js.map