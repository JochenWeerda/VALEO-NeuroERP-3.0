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
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fastify_1 = __importDefault(require("fastify"));
const tickets_1 = require("./routes/tickets");
const weighing_service_1 = require("../domain/services/weighing-service");
const weighing_ticket_repository_1 = require("../infra/repo/weighing-ticket-repository");
const node_postgres_1 = require("drizzle-orm/node-postgres");
const pg_1 = require("pg");
const pool = new pg_1.Pool({
    connectionString: process.env.DATABASE_URL || process.env.POSTGRES_URL,
});
const db = (0, node_postgres_1.drizzle)(pool);
const ticketRepository = new weighing_ticket_repository_1.WeighingTicketRepository(db);
const weighingService = new weighing_service_1.WeighingService(ticketRepository);
const app = (0, fastify_1.default)({
    logger: {
        level: process.env.LOG_LEVEL || 'info',
        transport: {
            target: 'pino-pretty',
            options: {
                translateTime: 'HH:MM:ss Z',
                ignore: 'pid,hostname',
            },
        },
    },
});
app.register(Promise.resolve().then(() => __importStar(require('@fastify/swagger'))), {
    openapi: {
        openapi: '3.0.0',
        info: {
            title: 'Weighing Domain API',
            description: 'API for agricultural weighing operations',
            version: '1.0.0',
        },
        servers: [
            {
                url: `http://localhost:${process.env.PORT || 3005}`,
                description: 'Development server',
            },
        ],
        tags: [
            { name: 'weighing-tickets', description: 'Weighing ticket operations' },
        ],
    },
});
app.register(Promise.resolve().then(() => __importStar(require('@fastify/swagger-ui'))), {
    routePrefix: '/documentation',
    uiConfig: {
        docExpansion: 'full',
        deepLinking: false,
    },
});
app.get('/health', async () => {
    return { status: 'ok', service: 'weighing-domain' };
});
app.get('/ready', async () => {
    try {
        await pool.query('SELECT 1');
        return { status: 'ready', database: 'connected' };
    }
    catch (error) {
        app.log.error({ error }, 'Database health check failed');
        return { status: 'not ready', database: 'disconnected' };
    }
});
app.get('/live', async () => {
    return { status: 'live', timestamp: new Date().toISOString() };
});
(0, tickets_1.registerTicketRoutes)(app, weighingService);
const closeGracefully = async (signal) => {
    app.log.info(`Received signal ${signal}, shutting down gracefully`);
    try {
        await app.close();
        await pool.end();
        process.exit(0);
    }
    catch (error) {
        app.log.error({ error }, 'Error during shutdown');
        process.exit(1);
    }
};
process.on('SIGINT', () => closeGracefully('SIGINT'));
process.on('SIGTERM', () => closeGracefully('SIGTERM'));
const start = async () => {
    try {
        const port = parseInt(process.env.PORT || '3005', 10);
        const host = process.env.HOST || '0.0.0.0';
        await app.listen({ port, host });
        app.log.info(`Weighing Domain API listening on http://${host}:${port}`);
        app.log.info(`API Documentation available at http://${host}:${port}/documentation`);
    }
    catch (error) {
        app.log.error({ error }, 'Failed to start server');
        process.exit(1);
    }
};
start();
//# sourceMappingURL=server.js.map