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
        const token = authHeader.substring(7);
        const authenticator = (0, jwt_1.getJWTAuthenticator)();
        const user = await authenticator.authenticate(token);
        const tenantId = request.headers['x-tenant-id'] || user.tenantId;
        if (!tenantId) {
            return reply.code(400).send({
                error: 'Bad Request',
                message: 'Missing tenant ID',
            });
        }
        request.auth = {
            user,
            token,
            tenantId,
        };
    }
    catch (error) {
        return reply.code(401).send({
            error: 'Unauthorized',
            message: error instanceof Error ? error.message : 'Authentication failed',
        });
    }
}
//# sourceMappingURL=auth.js.map