import { InteractionEntity, CreateInteractionInput, UpdateInteractionInput, InteractionTypeType } from '../../domain/entities';
export interface InteractionFilters {
    customerId: string;
    contactId?: string;
    type?: InteractionTypeType;
    from?: Date;
    to?: Date;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    sortBy?: 'subject' | 'type' | 'occurredAt' | 'createdAt' | 'updatedAt';
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
export declare class InteractionRepository {
    findById(id: string, tenantId: string): Promise<InteractionEntity | null>;
    findByCustomerId(customerId: string, tenantId: string, filters?: Omit<InteractionFilters, 'customerId'>, pagination?: PaginationOptions): Promise<PaginatedResult<InteractionEntity>>;
    findAll(tenantId: string, filters: InteractionFilters, pagination?: PaginationOptions): Promise<PaginatedResult<InteractionEntity>>;
    create(input: CreateInteractionInput & {
        tenantId: string;
    }): Promise<InteractionEntity>;
    update(id: string, tenantId: string, input: UpdateInteractionInput): Promise<InteractionEntity | null>;
    delete(id: string, tenantId: string): Promise<boolean>;
    exists(id: string, tenantId: string): Promise<boolean>;
    getByType(type: InteractionTypeType, tenantId: string): Promise<InteractionEntity[]>;
    getUpcomingInteractions(tenantId: string, from?: Date): Promise<InteractionEntity[]>;
    getOverdueInteractions(tenantId: string): Promise<InteractionEntity[]>;
    getTodaysInteractions(tenantId: string): Promise<InteractionEntity[]>;
}
//# sourceMappingURL=interaction-repository.d.ts.map