"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.authMiddleware = authMiddleware;
const jwt_1 = require("../../infra/security/jwt");
async function authMiddleware(request, reply) {
    try {
        const authHeader = request.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return reply.code(401).send({
                error: 'Unauthorized',
                message: 'Missing or invalid authorization header',
            });
        }
        const token = authHeader.substring(7); // Remove 'Bearer ' prefix
        // Verify JWT token
        const payload = await (0, jwt_1.verifyJWT)(token);
        // Attach user to request
        request.user = {
            userId: payload.sub,
            tenantId: payload.tenantId || request.headers['x-tenant-id'],
            roles: payload.roles || [],
            permissions: payload.permissions || [],
        };
        // Continue to next middleware
    }
    catch (error) {
        request.log.error('Authentication error:', error);
        return reply.code(401).send({
            error: 'Unauthorized',
            message: 'Invalid or expired token',
        });
    }
}
//# sourceMappingURL=auth.js.map