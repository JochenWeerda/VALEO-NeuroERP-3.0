import { FastifyInstance } from 'fastify';
import { drizzle } from 'drizzle-orm/node-postgres';
export declare function registerKpiRoutes(fastify: FastifyInstance, db: ReturnType<typeof drizzle>): Promise<void>;
declare module 'fastify' {
    interface FastifyRequest {
        tenantId: string;
    }
}
//# sourceMappingURL=kpis.d.ts.map