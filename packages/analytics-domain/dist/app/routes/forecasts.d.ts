import { FastifyInstance } from 'fastify';
import { drizzle } from 'drizzle-orm/node-postgres';
import { ForecastingService } from '../../domain/services/forecasting-service';
export declare function registerForecastRoutes(fastify: FastifyInstance, db: ReturnType<typeof drizzle>, forecastingService: ForecastingService): Promise<void>;
declare module 'fastify' {
    interface FastifyRequest {
        tenantId: string;
    }
}
//# sourceMappingURL=forecasts.d.ts.map