"use strict";
/**
 * VALEO-NeuroERP-3.0 Express Application Setup
 * Main application configuration with middleware and routes
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createApp = createApp;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const swagger_ui_express_1 = __importDefault(require("swagger-ui-express"));
const swagger_jsdoc_1 = __importDefault(require("swagger-jsdoc"));
const config_1 = require("./core/config");
const logging_1 = require("./core/logging");
// Validate configuration on startup
(0, config_1.validateConfig)();
// Create Express application
async function createApp() {
    const app = (0, express_1.default)();
    // Security middleware
    app.use((0, helmet_1.default)({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                styleSrc: ["'self'", "'unsafe-inline'"],
                scriptSrc: ["'self'"],
                imgSrc: ["'self'", "data:", "https:"],
            },
        },
    }));
    // CORS configuration
    app.use((0, cors_1.default)(config_1.config.cors));
    // Rate limiting
    const limiter = (0, express_rate_limit_1.default)(config_1.config.rateLimit);
    app.use('/api/', limiter);
    // Compression
    app.use((0, compression_1.default)());
    // Body parsing middleware
    app.use(express_1.default.json({ limit: '10mb' }));
    app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
    // Request logging middleware
    app.use((req, res, next) => {
        const start = Date.now();
        res.on('finish', () => {
            const duration = Date.now() - start;
            logging_1.logger.info('HTTP Request', {
                method: req.method,
                url: req.url,
                statusCode: res.statusCode,
                duration,
                ip: req.ip,
                userAgent: req.get('User-Agent'),
            });
        });
        next();
    });
    // Health check endpoint
    app.get('/health', (req, res) => {
        res.json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            service: 'valeo-neuro-erp',
            version: '3.0.0',
            environment: config_1.config.environment,
        });
    });
    // API Routes
    app.use('/api/v1', (req, res, next) => {
        // API versioning middleware
        res.setHeader('X-API-Version', 'v1');
        next();
    });
    // Swagger/OpenAPI documentation
    const swaggerOptions = {
        definition: {
            openapi: '3.0.0',
            info: {
                title: 'VALEO-NeuroERP-3.0 API',
                version: '3.0.0',
                description: 'Complete MSOA Enterprise ERP System API',
            },
            servers: [
                {
                    url: `http://localhost:${config_1.config.port}`,
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
        apis: ['./src/**/*.ts'], // Path to the API docs
    };
    const swaggerSpec = (0, swagger_jsdoc_1.default)(swaggerOptions);
    app.use('/api-docs', swagger_ui_express_1.default.serve, swagger_ui_express_1.default.setup(swaggerSpec));
    // API routes will be added here as domains are integrated
    // TODO: Add domain routes
    // app.use('/api/v1/crm', crmRoutes);
    // app.use('/api/v1/erp', erpRoutes);
    // app.use('/api/v1/analytics', analyticsRoutes);
    // 404 handler for API routes
    app.use('/api/*', (req, res) => {
        res.status(404).json({
            error: 'API endpoint not found',
            path: req.path,
            method: req.method,
        });
    });
    // Global error handler
    app.use((error, req, res, next) => {
        logging_1.logger.error('Unhandled error:', error);
        // Don't leak error details in production
        const isDevelopment = config_1.config.environment === 'development';
        res.status(error.status || 500).json({
            error: {
                message: isDevelopment ? error.message : 'Internal server error',
                ...(isDevelopment && { stack: error.stack }),
            },
            timestamp: new Date().toISOString(),
            path: req.path,
            method: req.method,
        });
    });
    // Graceful shutdown handler
    process.on('SIGTERM', () => {
        logging_1.logger.info('SIGTERM received, shutting down gracefully');
        // Close database connections, etc.
    });
    return app;
}
