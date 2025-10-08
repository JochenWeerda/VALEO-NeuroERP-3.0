import { GHGCalculationInput, GHGPathway } from '../entities/ghg-pathway';
export declare function calculateGHG(tenantId: string, input: GHGCalculationInput, userId: string): Promise<GHGPathway>;
export declare function getGHGPathways(tenantId: string, filters?: {
    commodity?: string;
    method?: string;
}): Promise<GHGPathway[]>;
//# sourceMappingURL=ghg-calculation-service.d.ts.map