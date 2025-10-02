import { FastifyInstance } from 'fastify';
import { drizzle } from 'drizzle-orm/node-postgres';
export interface ReportGenerator {
    generateReport(tenantId: string, type: string, parameters: any, format: string): Promise<{
        data: any;
        uri?: string;
        recordCount: number;
    }>;
}
export declare function registerReportRoutes(fastify: FastifyInstance, db: ReturnType<typeof drizzle>, reportGenerator: ReportGenerator): Promise<void>;
declare module 'fastify' {
    interface FastifyRequest {
        tenantId: string;
    }
}
//# sourceMappingURL=reports.d.ts.map