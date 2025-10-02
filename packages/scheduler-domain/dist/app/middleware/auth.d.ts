import { FastifyRequest, FastifyReply } from 'fastify';
import { AuthContext } from '../../infra/security/jwt';
declare module 'fastify' {
    interface FastifyRequest {
        auth?: AuthContext;
    }
}
export declare function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void>;
//# sourceMappingURL=auth.d.ts.map