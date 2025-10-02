import { InteractionEntity, CreateInteractionInput, UpdateInteractionInput, InteractionTypeType } from '../entities';
import { InteractionRepository } from '../../infra/repo';
export interface InteractionServiceDependencies {
    interactionRepo: InteractionRepository;
}
export interface CreateInteractionData extends CreateInteractionInput {
    tenantId: string;
    occurredAt: Date;
}
export interface UpdateInteractionData extends UpdateInteractionInput {
    tenantId: string;
    occurredAt?: Date;
}
export declare class InteractionService {
    private deps;
    constructor(deps: InteractionServiceDependencies);
    createInteraction(data: CreateInteractionData): Promise<InteractionEntity>;
    getInteraction(id: string, tenantId: string): Promise<InteractionEntity | null>;
    getInteractionsByCustomer(customerId: string, tenantId: string, filters?: {
        type?: InteractionTypeType;
        from?: Date;
        to?: Date;
    }, pagination?: {
        page: number;
        pageSize: number;
    }): Promise<import("../../infra/repo/interaction-repository").PaginatedResult<InteractionEntity>>;
    updateInteraction(id: string, data: UpdateInteractionData): Promise<InteractionEntity>;
    deleteInteraction(id: string, tenantId: string): Promise<boolean>;
    getUpcomingInteractions(tenantId: string, from?: Date): Promise<InteractionEntity[]>;
    getOverdueInteractions(tenantId: string): Promise<InteractionEntity[]>;
    getTodaysInteractions(tenantId: string): Promise<InteractionEntity[]>;
    getInteractionsByType(type: InteractionTypeType, tenantId: string): Promise<InteractionEntity[]>;
    addAttachment(interactionId: string, tenantId: string, attachment: {
        filename: string;
        url: string;
        size: number;
        mimeType: string;
    }): Promise<InteractionEntity>;
    removeAttachment(interactionId: string, tenantId: string, attachmentId: string): Promise<InteractionEntity>;
}
//# sourceMappingURL=interaction-service.d.ts.map