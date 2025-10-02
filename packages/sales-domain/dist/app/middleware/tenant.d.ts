import { FastifyRequest, FastifyReply } from 'fastify';
declare module 'fastify' {
    interface FastifyRequest {
        tenantId?: string;
    }
}
export declare function tenantMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
//***REMOVED*** sourceMappingURL=tenant.d.ts.map