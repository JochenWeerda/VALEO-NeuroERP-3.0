"use strict";
/**
 * HR Domain Server for VALEO NeuroERP 3.0
 * Fastify server with OpenAPI documentation
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fastify_1 = __importDefault(require("fastify"));
const swagger_1 = __importDefault(require("@fastify/swagger"));
const swagger_ui_1 = __importDefault(require("@fastify/swagger-ui"));
const cors_1 = __importDefault(require("@fastify/cors"));
// import postgres from 'postgres';
// Import middleware
const auth_1 = require("./middleware/auth");
// Import routes
const employees_1 = require("./routes/employees");
const time_entries_1 = require("./routes/time-entries");
// Import services
const employee_service_1 = require("../domain/services/employee-service");
const time_entry_service_1 = require("../domain/services/time-entry-service");
// Import repositories
const postgres_employee_repository_1 = require("../infra/repo/postgres-employee-repository");
// Configuration
const PORT = Number(process.env.PORT || 3030);
const HOST = process.env.HOST || '0.0.0.0';
const POSTGRES_URL = process.env.POSTGRES_URL || 'postgres://user:pass@localhost:5432/hr_domain';
// Initialize database connection (placeholder)
// const sql = postgres(POSTGRES_URL);
// const db = drizzle(sql, { schema });
const db = {}; // Placeholder for now
// Initialize repositories
const employeeRepository = new postgres_employee_repository_1.PostgresEmployeeRepository(db);
// TODO: Initialize other repositories (TimeEntryRepository, etc.)
// Event publisher (placeholder - would connect to NATS/Kafka)
const eventPublisher = async (event) => {
    console.log('📤 Publishing domain event:', event.eventType, event.eventId);
    // TODO: Implement actual event publishing to NATS/Kafka
};
// Initialize services
const employeeService = new employee_service_1.EmployeeService(employeeRepository, eventPublisher);
const timeEntryService = new time_entry_service_1.TimeEntryService({}, // TODO: Initialize TimeEntryRepository
employeeRepository, eventPublisher);
// Create Fastify instance
const fastify = (0, fastify_1.default)({
    logger: {
        level: process.env.LOG_LEVEL || 'info',
        transport: process.env.NODE_ENV === 'development' ? {
            target: 'pino-pretty',
            options: {
                colorize: true
            }
        } : undefined
    }
});
// Register plugins
async function registerPlugins() {
    // CORS
    await fastify.register(cors_1.default, {
        origin: true,
        credentials: true
    });
    // Swagger/OpenAPI
    await fastify.register(swagger_1.default, {
        openapi: {
            info: {
                title: 'VALEO NeuroERP 3.0 - HR Domain API',
                description: 'Human Resources Domain API for employee management, time tracking, and payroll preparation',
                version: '1.0.0'
            },
            servers: [
                {
                    url: `http://${HOST}:${PORT}`,
                    description: 'HR Domain Server'
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
            },
            security: [
                {
                    bearerAuth: []
                }
            ]
        }
    });
    await fastify.register(swagger_ui_1.default, {
        routePrefix: '/docs',
        uiConfig: {
            docExpansion: 'full',
            deepLinking: false
        },
        uiHooks: {
            onRequest: function (request, reply, next) {
                next();
            },
            preHandler: function (request, reply, next) {
                next();
            }
        },
        staticCSP: true,
        transformStaticCSP: (header) => header,
        transformSpecification: (swaggerObject, request, reply) => {
            return swaggerObject;
        },
        transformSpecificationClone: true
    });
}
// Register middleware
async function registerMiddleware() {
    // Initialize authentication
    await (0, auth_1.initializeAuth)();
    // Add authentication middleware to all routes
    fastify.addHook('onRequest', auth_1.authMiddleware);
}
// Register routes
async function registerRoutes() {
    // Health check endpoints
    fastify.get('/health', {
        schema: {
            description: 'Health check endpoint',
            tags: ['health'],
            response: {
                200: {
                    description: 'Service is healthy',
                    type: 'object',
                    properties: {
                        ok: { type: 'boolean' },
                        service: { type: 'string' },
                        timestamp: { type: 'string' },
                        uptime: { type: 'number' }
                    }
                }
            }
        }
    }, async (request, reply) => {
        return {
            ok: true,
            service: 'hr-domain',
            timestamp: new Date().toISOString(),
            uptime: process.uptime()
        };
    });
    fastify.get('/ready', {
        schema: {
            description: 'Readiness check endpoint',
            tags: ['health'],
            response: {
                200: {
                    description: 'Service is ready',
                    type: 'object',
                    properties: {
                        ok: { type: 'boolean' },
                        database: { type: 'boolean' },
                        timestamp: { type: 'string' }
                    }
                }
            }
        }
    }, async (request, reply) => {
        // TODO: Test database connection when implemented
        return {
            ok: true,
            database: true,
            timestamp: new Date().toISOString()
        };
    });
    fastify.get('/live', {
        schema: {
            description: 'Liveness check endpoint',
            tags: ['health'],
            response: {
                200: {
                    description: 'Service is alive',
                    type: 'object',
                    properties: {
                        ok: { type: 'boolean' },
                        timestamp: { type: 'string' }
                    }
                }
            }
        }
    }, async (request, reply) => {
        return {
            ok: true,
            timestamp: new Date().toISOString()
        };
    });
    // Register domain routes
    (0, employees_1.registerEmployeeRoutes)(fastify, employeeService);
    (0, time_entries_1.registerTimeEntryRoutes)(fastify, timeEntryService);
    // TODO: Register other domain routes (shifts, leaves, payroll, roles)
}
// Error handler
fastify.setErrorHandler(async (error, request, reply) => {
    fastify.log.error(error);
    // Handle validation errors
    if (error.validation) {
        return reply.code(400).send({
            error: 'Validation failed',
            details: error.validation
        });
    }
    // Handle authentication errors
    if (error.statusCode === 401) {
        return reply.code(401).send({
            error: 'Unauthorized',
            message: error.message
        });
    }
    // Handle authorization errors
    if (error.statusCode === 403) {
        return reply.code(403).send({
            error: 'Forbidden',
            message: error.message
        });
    }
    // Handle not found errors
    if (error.statusCode === 404) {
        return reply.code(404).send({
            error: 'Not found',
            message: error.message
        });
    }
    // Default error response
    return reply.code(500).send({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An unexpected error occurred'
    });
});
// Graceful shutdown
async function gracefulShutdown() {
    console.log('🔄 Gracefully shutting down...');
    try {
        await fastify.close();
        // await sql.end(); // TODO: Close database connection when implemented
        console.log('✅ Server shut down successfully');
        process.exit(0);
    }
    catch (error) {
        console.error('❌ Error during shutdown:', error);
        process.exit(1);
    }
}
// Handle shutdown signals
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);
// Start server
async function start() {
    try {
        console.log('🚀 Starting VALEO NeuroERP 3.0 HR Domain Server...');
        // Register everything
        await registerPlugins();
        await registerMiddleware();
        await registerRoutes();
        // Start listening
        await fastify.listen({ port: PORT, host: HOST });
        console.log(`✅ HR Domain Server running on http://${HOST}:${PORT}`);
        console.log(`📚 API Documentation: http://${HOST}:${PORT}/docs`);
        console.log(`❤️  Health Check: http://${HOST}:${PORT}/health`);
        console.log(`🔧 Ready Check: http://${HOST}:${PORT}/ready`);
        console.log(`💓 Live Check: http://${HOST}:${PORT}/live`);
    }
    catch (error) {
        console.error('❌ Failed to start server:', error);
        process.exit(1);
    }
}
// Start the server
if (require.main === module) {
    start();
}
exports.default = fastify;
//# sourceMappingURL=server.js.map