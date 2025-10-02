"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerInvoiceRoutes = registerInvoiceRoutes;
async function registerInvoiceRoutes(fastify) {
    fastify.register(async (invoiceRoutes) => {
        // GET /invoices - List invoices
        invoiceRoutes.get('/', async (request, reply) => {
            return { data: [], pagination: { page: 1, pageSize: 20, total: 0, totalPages: 0 } };
        });
        // POST /invoices - Create invoice
        invoiceRoutes.post('/', async (request, reply) => {
            return reply.code(201).send({ id: 'invoice-123' });
        });
        // GET /invoices/:id - Get invoice by ID
        invoiceRoutes.get('/:id', async (request, reply) => {
            const { id } = request.params;
            return { id, status: 'Issued' };
        });
        // PATCH /invoices/:id - Update invoice
        invoiceRoutes.patch('/:id', async (request, reply) => {
            const { id } = request.params;
            return { id, updated: true };
        });
        // POST /invoices/:id/pay - Mark invoice as paid
        invoiceRoutes.post('/:id/pay', async (request, reply) => {
            const { id } = request.params;
            return { id, status: 'Paid' };
        });
    }, { prefix: '/invoices' });
}
//# sourceMappingURL=invoices.js.map