/**
 * Express Application Setup
 */

import express, { Application, NextFunction, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { IntegrationRoutes } from './routes/integration-routes.js';
import { ErrorHandlerMiddleware } from './middleware/error-handler.js';
import { LoggerMiddleware } from './middleware/logger.js';
import { HttpStatusCode } from './errors/api-errors.js';

export interface AppConfig {
  port: number;
  cors?: {
    origin: string | string[];
    credentials: boolean;
  };
  helmet?: boolean;
  compression?: boolean;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export class IntegrationApiApp {
  private app: Application;
  private config: Required<AppConfig>;

  constructor(
    private readonly integrationService: any,
    config: AppConfig
  ) {
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

  private setupMiddleware(): void {
    // Security middleware
    if (this.config.helmet) {
      this.app.use(helmet());
    }

    // CORS middleware
    this.app.use(cors(this.config.cors));

    // Compression middleware
    if (this.config.compression) {
      this.app.use(compression() as any);
    }

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging
    const logger = new LoggerMiddleware(this.config.logLevel);
    this.app.use(logger.requestLogger as any);

    // Trust proxy (for accurate IP addresses)
    this.app.set('trust proxy', 1);
  }

  private setupRoutes(): void {
    // Health check endpoint
    this.app.get('/health', (req: Request, res: Response) => {
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
    this.app.get('/api-docs', (req: Request, res: Response) => {
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
    this.app.use('/api/integrations', integrationRoutes.getRouter() as any);

    // 404 handler for API routes
    this.app.use('/api/*', (req: Request, res: Response) => {
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
    this.app.get('/', (req: Request, res: Response) => {
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

  private setupErrorHandling(): void {
    const errorHandler = new ErrorHandlerMiddleware({
      includeStack: process.env.NODE_ENV === 'development',
      logErrors: true
    });

    // 404 handler for non-API routes
    this.app.use((req: Request, res: Response) => {
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
    this.app.use((error: any, req: Request, res: Response, next: NextFunction) => {
      errorHandler.middleware(error, req, res, next);
    });
  }

  getApp(): Application {
    return this.app;
  }

  start(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.app.listen(this.config.port, () => {
          console.log(`🚀 Integration Domain API server running on port ${this.config.port}`);
          console.log(`📚 API Documentation: http://localhost:${this.config.port}/api-docs`);
          console.log(`❤️  Health Check: http://localhost:${this.config.port}/health`);
          resolve();
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  // Graceful shutdown
  shutdown(): Promise<void> {
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
