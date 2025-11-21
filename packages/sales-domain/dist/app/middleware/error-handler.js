"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorHandler = errorHandler;
function errorHandler(error, request, reply) {
    // Log the error
    reply.log.error({
        error: error.message,
        stack: error.stack,
        code: error.code,
        statusCode: error.statusCode,
    }, 'Request error');
    // Handle different types of errors
    if (error.validation) {
        return reply.code(400).send({
            error: 'Validation Error',
            message: 'Request validation failed',
            details: error.validation,
        });
    }
    if (error.code === 'FST_ERR_NOT_FOUND') {
        return reply.code(404).send({
            error: 'Not Found',
            message: 'The requested resource was not found',
        });
    }
    // Default error response
    const statusCode = error.statusCode || 500;
    const message = statusCode >= 500 ? 'Internal server error' : error.message;
    return reply.code(statusCode).send({
        error: error.name ?? 'Error',
        message,
        ...(process.env.NODE_ENV === 'development' && { stack: error.stack }),
    });
}
//# sourceMappingURL=error-handler.js.map