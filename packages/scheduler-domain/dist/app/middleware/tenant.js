"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tenantMiddleware = tenantMiddleware;
async function tenantMiddleware(request, reply) {
    if (!request.auth) {
        return reply.code(401).send({
            error: 'Unauthorized',
            message: 'Authentication required',
        });
    }
    const { tenantId } = request.auth;
    request.tenantId = tenantId;
}
//# sourceMappingURL=tenant.js.map