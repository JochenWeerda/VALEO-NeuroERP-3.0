/**
 * Error Handling Middleware
 */
import { ApiError, HttpStatusCode, createInternalServerError } from '../errors/api-errors.js';
import { ZodError } from 'zod';
export class ErrorHandlerMiddleware {
    options;
    constructor(options = {}) {
        this.options = {
            includeStack: false,
            logErrors: true,
            ...options
        };
    }
    handle(error) {
        // Log error if enabled
        if (this.options.logErrors) {
            console.error('API Error:', error);
        }
        // Handle different error types
        if (error instanceof ApiError) {
            return {
                statusCode: error.statusCode,
                body: error.toJSON()
            };
        }
        if (error instanceof ZodError) {
            const validationError = this.handleZodError(error);
            return {
                statusCode: validationError.statusCode,
                body: validationError.toJSON()
            };
        }
        if (error instanceof Error) {
            const apiError = createInternalServerError('An unexpected error occurred', this.options.includeStack ? { stack: error.stack } : undefined);
            return {
                statusCode: apiError.statusCode,
                body: apiError.toJSON()
            };
        }
        // Handle unknown error types
        const unknownError = createInternalServerError('An unknown error occurred', this.options.includeStack ? { originalError: String(error) } : undefined);
        return {
            statusCode: unknownError.statusCode,
            body: unknownError.toJSON()
        };
    }
    handleZodError(zodError) {
        const validationErrors = zodError.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
            value: 'received' in err ? err.received : undefined
        }));
        return new ApiError('Validation failed', HttpStatusCode.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', {
            validationErrors
        });
    }
    // Express-style middleware function
    middleware = (error, req, res, next) => {
        const result = this.handle(error);
        res.status(result.statusCode).json(result.body);
    };
}
//# sourceMappingURL=error-handler.js.map