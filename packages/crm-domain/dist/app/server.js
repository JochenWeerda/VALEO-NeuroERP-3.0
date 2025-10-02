"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fastify_1 = __importDefault(require("fastify"));
const swagger_1 = __importDefault(require("@fastify/swagger"));
const swagger_ui_1 = __importDefault(require("@fastify/swagger-ui"));
const connection_1 = require("../infra/db/connection");
const publisher_1 = require("../infra/messaging/publisher");
const repo_1 = require("../infra/repo");
const services_1 = require("../domain/services");
const customers_1 = require("./routes/customers");
const contacts_1 = require("./routes/contacts");
const opportunities_1 = require("./routes/opportunities");
const interactions_1 = require("./routes/interactions");
// Create Fastify instance
const server = (0, fastify_1.default)({
    logger: process.env.NODE_ENV === 'development' ? {
        level: process.env.LOG_LEVEL || 'info',
        transport: {
            target: 'pino-pretty',
            options: {
                colorize: true,
                translateTime: 'SYS:yyyy-mm-dd HH:MM:ss.l',
                ignore: 'pid,hostname'
            }
        }
    } : {
        level: process.env.LOG_LEVEL || 'info'
    }
});
// Register Swagger/OpenAPI
server.register(swagger_1.default, {
    openapi: {
        info: {
            title: 'CRM Domain API',
            description: 'Customer Relationship Management Domain Service API',
            version: '1.0.0'
        },
        servers: [
            {
                url: 'http://localhost:3010',
                description: 'Development server'
            }
        ],
        components: {
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT'
                }
            }
        }
    }
});
// Register Swagger UI
server.register(swagger_ui_1.default, {
    routePrefix: '/docs',
    uiConfig: {
        docExpansion: 'list',
        deepLinking: false
    },
    staticCSP: true,
    transformStaticCSP: (header) => header
});
// Health check endpoints
server.get('/health', async () => {
    const dbHealthy = await (0, connection_1.checkDatabaseConnection)();
    const eventPublisher = (0, publisher_1.getEventPublisher)();
    const messagingHealthy = eventPublisher.isHealthy();
    const health = {
        status: dbHealthy && messagingHealthy ? 'healthy' : 'unhealthy',
        timestamp: new Date().toISOString(),
        services: {
            database: dbHealthy ? 'healthy' : 'unhealthy',
            messaging: messagingHealthy ? 'healthy' : 'unhealthy'
        }
    };
    return health;
});
// Readiness check
server.get('/ready', async () => {
    const dbHealthy = await (0, connection_1.checkDatabaseConnection)();
    const eventPublisher = (0, publisher_1.getEventPublisher)();
    const messagingHealthy = eventPublisher.isHealthy();
    if (!dbHealthy || !messagingHealthy) {
        throw new Error('Service not ready');
    }
    return {
        status: 'ready',
        timestamp: new Date().toISOString()
    };
});
// Liveness check
server.get('/live', async () => {
    return {
        status: 'alive',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    };
});
// OpenAPI JSON endpoint
server.get('/openapi.json', async () => {
    return server.swagger();
});
// Initialize services
async function initializeServices() {
    try {
        // Initialize database connection
        const dbHealthy = await (0, connection_1.checkDatabaseConnection)();
        if (!dbHealthy) {
            throw new Error('Database connection failed');
        }
        // Initialize event publisher
        const eventPublisher = (0, publisher_1.getEventPublisher)();
        await eventPublisher.connect();
        // Initialize repositories and services
        const customerRepo = new repo_1.CustomerRepository();
        const customerService = new services_1.CustomerService({ customerRepo });
        return {
            customerService
        };
    }
    catch (error) {
        server.log.error('Failed to initialize services:', error);
        throw error;
    }
}
// Register routes
async function registerRoutes() {
    const services = await initializeServices();
    // Register API routes
    await (0, customers_1.registerCustomerRoutes)(server, services);
    await (0, contacts_1.registerContactRoutes)(server, services);
    await (0, opportunities_1.registerOpportunityRoutes)(server, services);
    await (0, interactions_1.registerInteractionRoutes)(server, services);
}
// Graceful shutdown
async function gracefulShutdown() {
    server.log.info('Starting graceful shutdown...');
    try {
        // Close event publisher connection
        const eventPublisher = (0, publisher_1.getEventPublisher)();
        await eventPublisher.disconnect();
        // Close server
        await server.close();
        server.log.info('Graceful shutdown completed');
    }
    catch (error) {
        server.log.error('Error during graceful shutdown:', error);
        process.exit(1);
    }
}
// Handle shutdown signals
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);
// Start server
async function startServer() {
    try {
        const port = Number(process.env.PORT) || 3010;
        const host = '0.0.0.0';
        await registerRoutes();
        await server.listen({ port, host });
        server.log.info(`CRM Domain API server listening on ${host}:${port}`);
        server.log.info(`API Documentation available at http://localhost:${port}/docs`);
    }
    catch (error) {
        server.log.error('Failed to start server:', error);
        process.exit(1);
    }
}
// Start the server
startServer();
//# sourceMappingURL=server.js.map