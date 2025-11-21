"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.start = exports.server = void 0;
const fastify_1 = __importDefault(require("fastify"));
const swagger_1 = __importDefault(require("@fastify/swagger"));
const swagger_ui_1 = __importDefault(require("@fastify/swagger-ui"));
const quotes_1 = require("./routes/quotes");
const orders_1 = require("./routes/orders");
const invoices_1 = require("./routes/invoices");
const credit_notes_1 = require("./routes/credit-notes");
const sales_offers_1 = require("./routes/sales-offers");
const auth_1 = require("./middleware/auth");
const tenant_1 = require("./middleware/tenant");
const request_id_1 = require("./middleware/request-id");
const logger_1 = require("./middleware/logger");
const error_handler_1 = require("./middleware/error-handler");
const health_1 = require("./routes/health");
const publisher_1 = require("../infra/messaging/publisher");
const tracer_1 = require("../infra/telemetry/tracer");
const server = (0, fastify_1.default)({
    logger: {
        level: process.env.LOG_LEVEL ?? 'info',
        serializers: {
            req: (req) => ({
                method: req.method,
                url: req.url,
                hostname: req.hostname,
                remoteAddress: req.ip,
                remotePort: req.socket?.remotePort ?? undefined,
            }),
            res: (res) => ({
                statusCode: res.statusCode,
            }),
        },
    },
    disableRequestLogging: false,
    requestIdLogLabel: 'requestId',
    genReqId: () => require('crypto').randomUUID(),
});
exports.server = server;
// Register Swagger/OpenAPI
server.register(swagger_1.default, {
    openapi: {
        openapi: '3.0.3',
        info: {
            title: 'Sales Domain API',
            description: 'REST API for Sales Domain operations (Quotes, Sales Offers, Orders, Invoices, Credit Notes)',
            version: '1.0.0',
        },
        servers: [
            {
                url: process.env.API_BASE_URL ?? 'http://localhost:3001',
                description: 'Development server',
            },
        ],
        components: {
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT',
                },
            },
        },
        security: [
            {
                bearerAuth: [],
            },
        ],
    },
});
server.register(swagger_ui_1.default, {
    routePrefix: '/docs',
    uiConfig: {
        docExpansion: 'full',
        deepLinking: false,
    },
    staticCSP: true,
    transformStaticCSP: (header) => header,
});
// Initialize telemetry
(0, tracer_1.setupTelemetry)();
// Register middleware
server.addHook('onRequest', request_id_1.requestIdMiddleware);
server.addHook('onRequest', logger_1.loggerMiddleware);
server.addHook('onRequest', auth_1.authMiddleware);
server.addHook('onRequest', tenant_1.tenantMiddleware);
// Register tracing hooks
const tracing = (0, tracer_1.tracingMiddleware)();
server.addHook('onRequest', tracing.onRequest);
server.addHook('onResponse', tracing.onResponse);
server.addHook('onError', tracing.onError);
// Register error handler
server.setErrorHandler(error_handler_1.errorHandler);
// Register routes
server.register(health_1.healthRoutes);
server.register(quotes_1.registerQuoteRoutes);
server.register(sales_offers_1.registerSalesOfferRoutes);
server.register(orders_1.registerOrderRoutes);
server.register(invoices_1.registerInvoiceRoutes);
server.register(credit_notes_1.registerCreditNoteRoutes);
// Graceful shutdown
const gracefulShutdown = async (signal) => {
    server.log.info(`Received ${signal}, shutting down gracefully`);
    try {
        // Close event publisher
        const publisher = (0, publisher_1.getEventPublisher)();
        await publisher.disconnect();
        // Close server
        await server.close();
        server.log.info('Server closed successfully');
        process.exit(0);
    }
    catch (error) {
        server.log.error({ error }, 'Error during shutdown');
        process.exit(1);
    }
};
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
// Start server
const start = async () => {
    try {
        const port = Number(process.env.PORT) || 3001;
        const host = process.env.HOST ?? '0.0.0.0';
        // Initialize event publisher
        const publisher = (0, publisher_1.getEventPublisher)();
        await publisher.connect();
        await server.listen({ port, host });
        server.log.info(`Sales Domain API listening on http://${host}:${port}`);
        server.log.info(`API documentation available at http://${host}:${port}/docs`);
    }
    catch (err) {
        server.log.error(err);
        process.exit(1);
    }
};
exports.start = start;
//# sourceMappingURL=server.js.map