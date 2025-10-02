/**
 * Express Application Setup
 */
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { IntegrationRoutes } from './routes/integration-routes.js';
import { ErrorHandlerMiddleware } from './middleware/error-handler.js';
import { LoggerMiddleware } from './middleware/logger.js';
import { HttpStatusCode } from './errors/api-errors.js';
export class IntegrationApiApp {
    integrationService;
    app;
    config;
    constructor(integrationService, config) {
        this.integrationService = integrationService;
        this.app = express();
        this.config = {
            cors: {
                origin: '*',
                credentials: true
            },
            helmet: true,
            compression: true,
            logLevel: 'info',
            ...config
        };
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }
    setupMiddleware() {
        // Security middleware
        if (this.config.helmet) {
            this.app.use(helmet());
        }
        // CORS middleware
        this.app.use(cors(this.config.cors));
        // Compression middleware
        if (this.config.compression) {
            this.app.use(compression());
        }
        // Body parsing middleware
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
        // Request logging
        const logger = new LoggerMiddleware(this.config.logLevel);
        this.app.use(logger.requestLogger);
        // Trust proxy (for accurate IP addresses)
        this.app.set('trust proxy', 1);
    }
    setupRoutes() {
        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: {
                    status: 'healthy',
                    timestamp: new Date().toISOString(),
                    version: '3.0.0',
                    service: 'integration-domain'
                }
            });
        });
        // API documentation endpoint
        this.app.get('/api-docs', (req, res) => {
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: {
                    title: 'Integration Domain API',
                    version: '3.0.0',
                    description: 'VALEO NeuroERP 3.0 - Integration Domain API',
                    endpoints: {
                        integrations: '/api/integrations',
                        health: '/health',
                        documentation: '/api-docs'
                    }
                }
            });
        });
        // API routes
        const integrationRoutes = new IntegrationRoutes(this.integrationService);
        this.app.use('/api/integrations', integrationRoutes.getRouter());
        // 404 handler for API routes
        this.app.use('/api/*', (req, res) => {
            res.status(HttpStatusCode.NOT_FOUND).json({
                success: false,
                error: {
                    message: `API endpoint not found: ${req.method} ${req.originalUrl}`,
                    code: 'NOT_FOUND',
                    statusCode: HttpStatusCode.NOT_FOUND,
                    timestamp: new Date().toISOString()
                }
            });
        });
        // Root endpoint
        this.app.get('/', (req, res) => {
            res.status(HttpStatusCode.OK).json({
                success: true,
                data: {
                    message: 'VALEO NeuroERP 3.0 - Integration Domain API',
                    version: '3.0.0',
                    documentation: '/api-docs',
                    health: '/health'
                }
            });
        });
    }
    setupErrorHandling() {
        const errorHandler = new ErrorHandlerMiddleware({
            includeStack: process.env.NODE_ENV === 'development',
            logErrors: true
        });
        // 404 handler for non-API routes
        this.app.use((req, res) => {
            res.status(HttpStatusCode.NOT_FOUND).json({
                success: false,
                error: {
                    message: `Endpoint not found: ${req.method} ${req.originalUrl}`,
                    code: 'NOT_FOUND',
                    statusCode: HttpStatusCode.NOT_FOUND,
                    timestamp: new Date().toISOString()
                }
            });
        });
        // Global error handler
        this.app.use((error, req, res, next) => {
            errorHandler.middleware(error, req, res, next);
        });
    }
    getApp() {
        return this.app;
    }
    start() {
        return new Promise((resolve, reject) => {
            try {
                this.app.listen(this.config.port, () => {
                    console.log(`🚀 Integration Domain API server running on port ${this.config.port}`);
                    console.log(`📚 API Documentation: http://localhost:${this.config.port}/api-docs`);
                    console.log(`❤️  Health Check: http://localhost:${this.config.port}/health`);
                    resolve();
                });
            }
            catch (error) {
                reject(error);
            }
        });
    }
    // Graceful shutdown
    shutdown() {
        return new Promise((resolve) => {
            console.log('🛑 Shutting down Integration Domain API server...');
            // In a real implementation, you would close database connections, etc.
            setTimeout(() => {
                console.log('✅ Integration Domain API server shut down gracefully');
                resolve();
            }, 1000);
        });
    }
}
//# sourceMappingURL=app.js.map