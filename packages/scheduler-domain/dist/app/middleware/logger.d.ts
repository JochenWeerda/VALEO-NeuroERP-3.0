import { FastifyRequest, FastifyReply } from 'fastify';
declare module 'fastify' {
    interface FastifyRequest {
        startTime?: number;
        requestId?: string;
    }
}
export declare function requestLoggerMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void>;
//***REMOVED*** sourceMappingURL=logger.d.ts.map