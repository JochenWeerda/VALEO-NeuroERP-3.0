"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loggerMiddleware = loggerMiddleware;
async function loggerMiddleware(request, reply) {
    // Additional logging setup can be done here
    // Fastify already handles basic request/response logging
    // Log user and tenant information for security auditing
    if (request.user) {
        request.log.info({
            userId: request.user.userId,
            tenantId: request.tenantId,
            roles: request.user.roles,
        }, 'Authenticated request');
    }
    // Continue to next middleware
}
//# sourceMappingURL=logger.js.map