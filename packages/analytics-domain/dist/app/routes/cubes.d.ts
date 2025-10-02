import { FastifyInstance } from 'fastify';
import { drizzle } from 'drizzle-orm/node-postgres';
import { AggregationService } from '../../domain/services/aggregation-service';
export declare function registerCubeRoutes(fastify: FastifyInstance, db: ReturnType<typeof drizzle>, aggregationService: AggregationService): Promise<void>;
declare module 'fastify' {
    interface FastifyRequest {
        tenantId: string;
    }
}
//# sourceMappingURL=cubes.d.ts.map