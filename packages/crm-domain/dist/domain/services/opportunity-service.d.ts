import { OpportunityEntity, CreateOpportunityInput, UpdateOpportunityInput, OpportunityStageType } from '../entities';
import { OpportunityRepository } from '../../infra/repo';
export interface OpportunityServiceDependencies {
    opportunityRepo: OpportunityRepository;
}
export interface CreateOpportunityData extends CreateOpportunityInput {
    tenantId: string;
    title: string;
    customerId: string;
    stage: OpportunityStageType;
    probability: number;
    amountNet?: number;
}
export interface UpdateOpportunityData extends UpdateOpportunityInput {
    tenantId: string;
    amountNet?: number;
    probability?: number;
    stage?: OpportunityStageType;
}
export declare class OpportunityService {
    private deps;
    constructor(deps: OpportunityServiceDependencies);
    createOpportunity(data: CreateOpportunityData): Promise<OpportunityEntity>;
    getOpportunity(id: string, tenantId: string): Promise<OpportunityEntity | null>;
    getOpportunitiesByCustomer(customerId: string, tenantId: string, filters?: {
        stage?: OpportunityStageType;
        ownerUserId?: string;
        amountMin?: number;
        amountMax?: number;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/opportunity-repository").PaginatedResult<OpportunityEntity>>;
    updateOpportunity(id: string, data: UpdateOpportunityData): Promise<OpportunityEntity>;
    changeOpportunityStage(id: string, tenantId: string, stage: OpportunityStageType): Promise<OpportunityEntity>;
    markOpportunityAsWon(id: string, tenantId: string): Promise<OpportunityEntity>;
    markOpportunityAsLost(id: string, tenantId: string): Promise<OpportunityEntity>;
    deleteOpportunity(id: string, tenantId: string): Promise<boolean>;
    getOpenOpportunities(tenantId: string): Promise<OpportunityEntity[]>;
    getOpportunitiesByStage(stage: OpportunityStageType, tenantId: string): Promise<OpportunityEntity[]>;
    private validateStageTransition;
}
//# sourceMappingURL=opportunity-service.d.ts.map