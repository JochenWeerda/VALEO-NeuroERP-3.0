"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createServer = createServer;
exports.startServer = startServer;
const fastify_1 = __importDefault(require("fastify"));
const schedules_1 = require("./routes/schedules");
const auth_1 = require("./middleware/auth");
const tenant_1 = require("./middleware/tenant");
const logger_1 = require("./middleware/logger");
const jwt_1 = require("../infra/security/jwt");
const tracer_1 = require("../infra/telemetry/tracer");
const logger_2 = require("../infra/telemetry/logger");
const schedule_repository_1 = require("../infra/repo/schedule-repository");
const logger = (0, logger_2.getLogger)();
async function createServer() {
    const server = (0, fastify_1.default)({
        logger: false,
        disableRequestLogging: true,
        trustProxy: true,
    });
    await (0, jwt_1.initializeJWTAuthenticator)();
    await (0, tracer_1.initializeTracing)();
    server.addHook('onRequest', logger_1.requestLoggerMiddleware);
    server.addHook('onRequest', auth_1.authMiddleware);
    server.addHook('onRequest', tenant_1.tenantMiddleware);
    server.get('/health', async () => {
        return { status: 'ok', timestamp: new Date().toISOString() };
    });
    server.get('/ready', async () => {
        try {
            await schedule_repository_1.scheduleRepository.countByTenant('health-check');
            return {
                status: 'ready',
                database: 'connected',
                timestamp: new Date().toISOString()
            };
        }
        catch (error) {
            logger.error('Database health check failed', error);
            throw new Error('Database not ready');
        }
    });
    server.get('/live', async () => {
        return {
            status: 'alive',
            timestamp: new Date().toISOString()
        };
    });
    await (0, schedules_1.registerScheduleRoutes)(server, schedule_repository_1.scheduleRepository);
    server.setErrorHandler((error, request, reply) => {
        logger.error('Request error', error, {
            requestId: request.requestId,
            tenantId: request.auth?.tenantId,
            userId: request.auth?.user.sub,
            method: request.method,
            url: request.url,
        });
        const statusCode = error.statusCode || 500;
        const message = statusCode >= 500 ? 'Internal server error' : error.message;
        reply.code(statusCode).send({
            error: error.name || 'Error',
            message,
            requestId: request.requestId,
        });
    });
    server.setNotFoundHandler((request, reply) => {
        logger.warn('Route not found', {
            requestId: request.requestId,
            method: request.method,
            url: request.url,
        });
        reply.code(404).send({
            error: 'Not Found',
            message: 'Route not found',
            requestId: request.requestId,
        });
    });
    return server;
}
async function startServer() {
    try {
        const server = await createServer();
        const port = parseInt(process.env.PORT || '3080');
        const host = process.env.HOST || '0.0.0.0';
        await server.listen({ port, host });
        logger.info('Scheduler domain server started', {
            port,
            host,
            environment: process.env.NODE_ENV || 'development',
        });
        const shutdown = async (signal) => {
            logger.info(`Received ${signal}, shutting down gracefully`);
            await server.close();
            try {
                const { shutdownTracing } = await Promise.resolve().then(() => __importStar(require('../infra/telemetry/tracer')));
                await shutdownTracing();
            }
            catch (error) {
                logger.error('Error shutting down tracing', error);
            }
            process.exit(0);
        };
        process.on('SIGTERM', () => shutdown('SIGTERM'));
        process.on('SIGINT', () => shutdown('SIGINT'));
    }
    catch (error) {
        logger.error('Failed to start server', error);
        process.exit(1);
    }
}
if (require.main === module) {
    startServer();
}
//# sourceMappingURL=server.js.map