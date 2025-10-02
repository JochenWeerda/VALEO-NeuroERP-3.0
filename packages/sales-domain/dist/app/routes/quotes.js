"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerQuoteRoutes = registerQuoteRoutes;
async function registerQuoteRoutes(fastify) {
    // Base path for quotes
    fastify.register(async (quoteRoutes) => {
        // GET /quotes - List quotes
        quoteRoutes.get('/', {
            schema: {
                description: 'List quotes with pagination and filtering',
                tags: ['Quotes'],
                querystring: {
                    type: 'object',
                    properties: {
                        customerId: { type: 'string' },
                        status: { type: 'string', enum: ['Draft', 'Sent', 'Accepted', 'Rejected', 'Expired'] },
                        page: { type: 'integer', minimum: 1, default: 1 },
                        pageSize: { type: 'integer', minimum: 1, maximum: 100, default: 20 },
                    },
                },
                response: {
                    200: {
                        type: 'object',
                        properties: {
                            data: { type: 'array' },
                            pagination: {
                                type: 'object',
                                properties: {
                                    page: { type: 'integer' },
                                    pageSize: { type: 'integer' },
                                    total: { type: 'integer' },
                                    totalPages: { type: 'integer' },
                                },
                            },
                        },
                    },
                },
            },
        }, async (request, reply) => {
            // TODO: Implement quote listing
            return {
                data: [],
                pagination: {
                    page: 1,
                    pageSize: 20,
                    total: 0,
                    totalPages: 0,
                },
            };
        });
        // POST /quotes - Create quote
        quoteRoutes.post('/', {
            schema: {
                description: 'Create a new quote',
                tags: ['Quotes'],
                body: {
                    type: 'object',
                    required: ['customerId', 'lines'],
                    properties: {
                        customerId: { type: 'string' },
                        lines: { type: 'array' },
                        validUntil: { type: 'string', format: 'date' },
                        notes: { type: 'string' },
                    },
                },
                response: {
                    201: { type: 'object' },
                },
            },
        }, async (request, reply) => {
            // TODO: Implement quote creation
            return reply.code(201).send({ id: 'quote-123' });
        });
        // GET /quotes/:id - Get quote by ID
        quoteRoutes.get('/:id', {
            schema: {
                description: 'Get quote by ID',
                tags: ['Quotes'],
                params: {
                    type: 'object',
                    required: ['id'],
                    properties: {
                        id: { type: 'string' },
                    },
                },
                response: {
                    200: { type: 'object' },
                    404: { type: 'object' },
                },
            },
        }, async (request, reply) => {
            // TODO: Implement quote retrieval
            const { id } = request.params;
            return { id, status: 'Draft' };
        });
        // PATCH /quotes/:id - Update quote
        quoteRoutes.patch('/:id', {
            schema: {
                description: 'Update quote',
                tags: ['Quotes'],
                params: {
                    type: 'object',
                    required: ['id'],
                    properties: {
                        id: { type: 'string' },
                    },
                },
                body: { type: 'object' },
                response: {
                    200: { type: 'object' },
                },
            },
        }, async (request, reply) => {
            // TODO: Implement quote update
            const { id } = request.params;
            return { id, updated: true };
        });
        // POST /quotes/:id/send - Send quote
        quoteRoutes.post('/:id/send', {
            schema: {
                description: 'Send quote to customer',
                tags: ['Quotes'],
                params: {
                    type: 'object',
                    required: ['id'],
                    properties: {
                        id: { type: 'string' },
                    },
                },
                response: {
                    200: { type: 'object' },
                },
            },
        }, async (request, reply) => {
            // TODO: Implement quote sending
            const { id } = request.params;
            return { id, status: 'Sent' };
        });
    }, { prefix: '/quotes' });
}
//# sourceMappingURL=quotes.js.map