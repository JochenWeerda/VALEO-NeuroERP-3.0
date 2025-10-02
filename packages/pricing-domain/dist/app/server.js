"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.start = start;
exports.stop = stop;
const fastify_1 = __importDefault(require("fastify"));
const swagger_1 = __importDefault(require("@fastify/swagger"));
const swagger_ui_1 = __importDefault(require("@fastify/swagger-ui"));
const dotenv_1 = __importDefault(require("dotenv"));
const quotes_1 = require("./routes/quotes");
const publisher_1 = require("../infra/messaging/publisher");
const pino_1 = __importDefault(require("pino"));
dotenv_1.default.config();
const server = (0, fastify_1.default)({
    logger: (0, pino_1.default)({ level: process.env.LOG_LEVEL || 'info' }),
    disableRequestLogging: false,
    requestIdLogLabel: 'requestId',
});
server.register(swagger_1.default, {
    openapi: {
        openapi: '3.0.3',
        info: {
            title: 'Pricing Domain API',
            description: 'REST API for Price Calculation (PriceLists, Conditions, Formulas, Quotes)',
            version: '1.0.0',
        },
        servers: [{ url: process.env.API_BASE_URL || 'http://localhost:3060' }],
        tags: [
            { name: 'quotes', description: 'Price quote calculation' },
            { name: 'pricelists', description: 'Price list management' },
            { name: 'conditions', description: 'Customer conditions' },
            { name: 'formulas', description: 'Dynamic formulas' },
        ],
    },
});
server.register(swagger_ui_1.default, {
    routePrefix: '/documentation',
    uiConfig: { docExpansion: 'list', deepLinking: true },
});
server.get('/health', async () => ({ status: 'ok', service: 'pricing-domain', timestamp: new Date().toISOString() }));
server.get('/ready', async () => ({ status: 'ready' }));
server.get('/live', async () => ({ status: 'alive' }));
server.register(quotes_1.registerQuoteRoutes, { prefix: '/pricing/api/v1' });
server.get('/pricing/api/v1/openapi.json', async () => server.swagger());
async function start() {
    try {
        await (0, publisher_1.initEventPublisher)();
        const port = parseInt(process.env.PORT || '3060', 10);
        const host = process.env.HOST || '0.0.0.0';
        await server.listen({ port, host });
        server.log.info(`🚀 Pricing Domain listening on ${host}:${port}`);
        server.log.info(`📚 Docs: http://${host}:${port}/documentation`);
    }
    catch (error) {
        server.log.error(error);
        process.exit(1);
    }
}
async function stop() {
    try {
        await (0, publisher_1.closeEventPublisher)();
        await server.close();
        server.log.info('Server stopped');
    }
    catch (error) {
        server.log.error(error);
    }
}
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
if (require.main === module) {
    start();
}
exports.default = server;
//# sourceMappingURL=server.js.map