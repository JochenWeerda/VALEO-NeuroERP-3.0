/**
 * VALEO-NeuroERP-3.0 Express Application Setup
 * Main application configuration with middleware and routes
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import swaggerUi from 'swagger-ui-express';
import swaggerJSDoc from 'swagger-jsdoc';

import { config, validateConfig } from './core/config';
import { logger } from './core/logging';

// Validate configuration on startup
validateConfig();

// Create Express application
export async function createApp() {
  const app = express();

// Security middleware
app.use(helmet({
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
app.use(cors(config.cors));

// Rate limiting
const limiter = rateLimit(config.rateLimit);
app.use('/api/', limiter);

// Compression
app.use(compression());

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('HTTP Request', {
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
    environment: config.environment,
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
        url: `http://localhost:${config.port}`,
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

const swaggerSpec = swaggerJSDoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

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
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Unhandled error:', error);

  // Don't leak error details in production
  const isDevelopment = config.environment === 'development';

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
  logger.info('SIGTERM received, shutting down gracefully');
  // Close database connections, etc.
});

  return app;
}