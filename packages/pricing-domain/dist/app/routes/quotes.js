"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerQuoteRoutes = registerQuoteRoutes;
const price_quote_1 = require("../../domain/entities/price-quote");
const price_calculator_1 = require("../../domain/services/price-calculator");
async function registerQuoteRoutes(server) {
    server.post('/quotes/calc', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const userId = request.authContext?.userId || 'system';
        const input = price_quote_1.CalcQuoteInputSchema.parse(request.body);
        const quote = await (0, price_calculator_1.calculateQuote)(tenantId, input, userId);
        reply.code(201).send(quote);
    });
    server.get('/quotes/:id', async (request, reply) => {
        const tenantId = request.headers['x-tenant-id'];
        const { id } = request.params;
        const quote = await (0, price_calculator_1.getQuoteById)(tenantId, id);
        if (!quote) {
            reply.code(404).send({ error: 'NotFound', message: 'Quote not found or expired' });
            return;
        }
        reply.send(quote);
    });
}
//# sourceMappingURL=quotes.js.map