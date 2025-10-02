/**
 * Integration Routes Configuration
 */
import { Router } from 'express';
import { IntegrationController } from '../controllers/integration-controller.js';
import { RequestValidatorMiddleware } from '../middleware/request-validator.js';
import { LoggerMiddleware } from '../middleware/logger.js';
import { z } from 'zod';
export class IntegrationRoutes {
    router;
    controller;
    validator;
    logger;
    constructor(integrationService) {
        this.router = Router();
        this.controller = new IntegrationController(integrationService);
        this.validator = new RequestValidatorMiddleware();
        this.logger = new LoggerMiddleware();
        this.setupRoutes();
    }
    setupRoutes() {
        // Apply logging middleware to all routes
        this.router.use(this.logger.requestLogger);
        // GET /integrations - List integrations with pagination and filtering
        this.router.get('/', this.validator.validate({
            query: z.object({
                page: z.string().optional().transform(val => val ? parseInt(val) : 1),
                limit: z.string().optional().transform(val => val ? parseInt(val) : 10),
                sortBy: z.string().optional(),
                sortOrder: z.enum(['asc', 'desc']).optional(),
                type: z.string().optional(),
                status: z.string().optional(),
                tags: z.string().optional(),
                isActive: z.string().optional().transform(val => val === 'true')
            })
        }), this.wrapAsync(this.controller.listIntegrations.bind(this.controller)));
        // GET /integrations/health - Health check
        this.router.get('/health', this.wrapAsync(this.controller.healthCheck.bind(this.controller)));
        // GET /integrations/statistics - Get integration statistics
        this.router.get('/statistics', this.wrapAsync(this.controller.getStatistics.bind(this.controller)));
        // GET /integrations/active - Get active integrations
        this.router.get('/active', this.wrapAsync(this.controller.getActiveIntegrations.bind(this.controller)));
        // GET /integrations/by-type/:type - Get integrations by type
        this.router.get('/by-type/:type', this.validator.validate({
            params: z.object({
                type: z.string().min(1)
            })
        }), this.wrapAsync(this.controller.getIntegrationsByType.bind(this.controller)));
        // GET /integrations/by-name/:name - Get integration by name
        this.router.get('/by-name/:name', this.validator.validate({
            params: z.object({
                name: z.string().min(1)
            })
        }), this.wrapAsync(this.controller.getIntegrationByName.bind(this.controller)));
        // GET /integrations/:id - Get integration by ID
        this.router.get('/:id', this.validator.validate({
            params: z.object({
                id: z.string().uuid()
            })
        }), this.wrapAsync(this.controller.getIntegration.bind(this.controller)));
        // POST /integrations - Create new integration
        this.router.post('/', this.validator.validate({
            body: z.object({
                name: z.string().min(1).max(255),
                type: z.enum(['api', 'webhook', 'file', 'database', 'message-queue']),
                config: z.record(z.unknown()),
                description: z.string().optional(),
                tags: z.array(z.string()).default([])
            })
        }), this.wrapAsync(this.controller.createIntegration.bind(this.controller)));
        // PUT /integrations/:id - Update integration
        this.router.put('/:id', this.validator.validate({
            params: z.object({
                id: z.string().uuid()
            }),
            body: z.object({
                name: z.string().min(1).max(255).optional(),
                config: z.record(z.unknown()).optional(),
                description: z.string().optional(),
                tags: z.array(z.string()).optional(),
                status: z.enum(['active', 'inactive', 'pending', 'error']).optional(),
                isActive: z.boolean().optional()
            })
        }), this.wrapAsync(this.controller.updateIntegration.bind(this.controller)));
        // DELETE /integrations/:id - Delete integration
        this.router.delete('/:id', this.validator.validate({
            params: z.object({
                id: z.string().uuid()
            })
        }), this.wrapAsync(this.controller.deleteIntegration.bind(this.controller)));
        // POST /integrations/:id/activate - Activate integration
        this.router.post('/:id/activate', this.validator.validate({
            params: z.object({
                id: z.string().uuid()
            })
        }), this.wrapAsync(this.controller.activateIntegration.bind(this.controller)));
        // POST /integrations/:id/deactivate - Deactivate integration
        this.router.post('/:id/deactivate', this.validator.validate({
            params: z.object({
                id: z.string().uuid()
            })
        }), this.wrapAsync(this.controller.deactivateIntegration.bind(this.controller)));
        // Apply error logging middleware
        this.router.use(this.logger.errorLogger);
    }
    // Utility method to wrap async controller methods
    wrapAsync(fn) {
        return (req, res, next) => {
            Promise.resolve(fn(req, res, next)).catch(next);
        };
    }
    getRouter() {
        return this.router;
    }
}
//# sourceMappingURL=integration-routes.js.map