import { FastifyRequest, FastifyReply } from 'fastify';
export interface AuthenticatedUser {
    userId: string;
    tenantId: string;
    roles: string[];
    permissions: string[];
}
declare module 'fastify' {
    interface FastifyRequest {
        user?: AuthenticatedUser;
    }
}
export declare function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
//***REMOVED*** sourceMappingURL=auth.d.ts.map