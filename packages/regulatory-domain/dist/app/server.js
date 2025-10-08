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
const labels_1 = require("./routes/labels");
const psm_1 = require("./routes/psm");
const ghg_1 = require("./routes/ghg");
const ktbl_1 = require("./routes/ktbl");
const publisher_1 = require("../infra/messaging/publisher");
const pino_1 = __importDefault(require("pino"));
dotenv_1.default.config();
const server = (0, fastify_1.default)({
    logger: (0, pino_1.default)({
        level: process.env.LOG_LEVEL || 'info',
    }),
    disableRequestLogging: false,
    requestIdLogLabel: 'requestId',
});
server.register(swagger_1.default, {
    openapi: {
        openapi: '3.0.3',
        info: {
            title: 'Regulatory Domain API',
            description: 'REST API for Regulatory Compliance (VLOG, QS, PSM, RED II, Labels)',
            version: '1.0.0',
        },
        servers: [
            {
                url: process.env.API_BASE_URL || 'http://localhost:3008',
                description: 'Development server',
            },
        ],
        tags: [
            { name: 'labels', description: 'Label & Compliance evaluation' },
            { name: 'psm', description: 'PSM (Pflanzenschutzmittel) checks' },
            { name: 'ghg', description: 'GHG/THG emissions (RED II)' },
            { name: 'policies', description: 'Regulatory policies' },
            { name: 'evidence', description: 'Compliance evidence' },
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
        security: [{ bearerAuth: [] }],
    },
});
server.register(swagger_ui_1.default, {
    routePrefix: '/documentation',
    uiConfig: {
        docExpansion: 'list',
        deepLinking: true,
    },
});
server.get('/health', async () => ({ status: 'ok', service: 'regulatory-domain', timestamp: new Date().toISOString() }));
server.get('/ready', async () => ({ status: 'ready', timestamp: new Date().toISOString() }));
server.get('/live', async () => ({ status: 'alive', timestamp: new Date().toISOString() }));
server.register(labels_1.registerLabelRoutes, { prefix: '/regulatory/api/v1' });
server.register(psm_1.registerPSMRoutes, { prefix: '/regulatory/api/v1' });
server.register(ghg_1.registerGHGRoutes, { prefix: '/regulatory/api/v1' });
server.register(ktbl_1.registerKTBLRoutes, { prefix: '/regulatory/api/v1' });
server.get('/regulatory/api/v1/openapi.json', async () => {
    return server.swagger();
});
async function start() {
    try {
        await (0, publisher_1.initEventPublisher)();
        const port = parseInt(process.env.PORT || '3008', 10);
        const host = process.env.HOST || '0.0.0.0';
        await server.listen({ port, host });
        server.log.info(`🚀 Regulatory Domain server listening on ${host}:${port}`);
        server.log.info(`📚 API Documentation: http://${host}:${port}/documentation`);
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
        server.log.info('Server stopped gracefully');
    }
    catch (error) {
        server.log.error(error);
        process.exit(1);
    }
}
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
if (require.main === module) {
    start();
}
exports.default = server;
//# sourceMappingURL=server.js.map