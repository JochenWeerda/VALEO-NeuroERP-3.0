import { OpportunityEntity, CreateOpportunityInput, UpdateOpportunityInput, OpportunityStageType } from '../../domain/entities';
export interface OpportunityFilters {
    customerId?: string;
    stage?: OpportunityStageType;
    ownerUserId?: string;
    amountMin?: number;
    amountMax?: number;
    expectedCloseDateFrom?: Date;
    expectedCloseDateTo?: Date;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'title' | 'stage' | 'amountNet' | 'expectedCloseDate' | 'createdAt' | 'updatedAt';
    sortOrder?: 'asc' | 'desc';
}
export interface PaginatedResult<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export declare class OpportunityRepository {
    findById(id: string, tenantId: string): Promise<OpportunityEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: OpportunityFilters, pagination?: PaginationOptions): Promise<PaginatedResult<OpportunityEntity>>;
    findAll(tenantId: string, filters?: OpportunityFilters, pagination?: PaginationOptions): Promise<PaginatedResult<OpportunityEntity>>;
    create(input: CreateOpportunityInput & {
        tenantId: string;
    }): Promise<OpportunityEntity>;
    update(id: string, tenantId: string, input: UpdateOpportunityInput): Promise<OpportunityEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    updateStage(id: string, tenantId: string, stage: OpportunityStageType): Promise<OpportunityEntity | null>;
    markAsWon(id: string, tenantId: string): Promise<OpportunityEntity | null>;
    markAsLost(id: string, tenantId: string): Promise<OpportunityEntity | null>;
    getByStage(stage: OpportunityStageType, tenantId: string): Promise<OpportunityEntity[]>;
    getOpenOpportunities(tenantId: string): Promise<OpportunityEntity[]>;
}
//# sourceMappingURL=opportunity-repository.d.ts.map