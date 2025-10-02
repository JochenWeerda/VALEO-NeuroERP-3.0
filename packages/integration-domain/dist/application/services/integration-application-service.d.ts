/**
 * Integration Application Service
 */
import type { UnitOfWork } from '@domain/interfaces/repositories.js';
import type { Result } from '@domain/interfaces/repositories.js';
import type { CreateIntegrationRequest, UpdateIntegrationRequest, IntegrationQuery, IntegrationResponse, IntegrationListResponse } from '../dto/integration-dto.js';
export declare class IntegrationApplicationService {
    private unitOfWork;
    private createIntegrationUseCase;
    private updateIntegrationUseCase;
    private deleteIntegrationUseCase;
    private activateIntegrationUseCase;
    private deactivateIntegrationUseCase;
    private getIntegrationQueryHandler;
    private listIntegrationsQueryHandler;
    constructor(unitOfWork: UnitOfWork);
    createIntegration(request: CreateIntegrationRequest, userId: string): Promise<Result<IntegrationResponse, Error>>;
    updateIntegration(id: string, request: UpdateIntegrationRequest, userId: string): Promise<Result<IntegrationResponse, Error>>;
    deleteIntegration(id: string, userId: string): Promise<Result<void, Error>>;
    activateIntegration(id: string, userId: string): Promise<Result<IntegrationResponse, Error>>;
    deactivateIntegration(id: string, userId: string): Promise<Result<IntegrationResponse, Error>>;
    getIntegration(id: string): Promise<Result<IntegrationResponse | null, Error>>;
    listIntegrations(query: IntegrationQuery): Promise<Result<IntegrationListResponse, Error>>;
    getIntegrationByName(name: string): Promise<Result<IntegrationResponse | null, Error>>;
    getIntegrationsByType(type: string): Promise<Result<IntegrationResponse[], Error>>;
    getActiveIntegrations(): Promise<Result<IntegrationResponse[], Error>>;
    healthCheck(): Promise<Result<{
        status: string;
        timestamp: string;
    }, Error>>;
    getStatistics(): Promise<Result<{
        total: number;
        active: number;
        inactive: number;
        byType: Record<string, number>;
    }, Error>>;
    private mapToResponse;
}
//# sourceMappingURL=integration-application-service.d.ts.map