/**
 * Integration Use Cases (Commands and Queries)
 */
import type { UnitOfWork } from '@domain/interfaces/repositories.js';
import type { Result } from '@domain/interfaces/repositories.js';
import type { CreateIntegrationRequest, UpdateIntegrationRequest, IntegrationQuery, IntegrationResponse, IntegrationListResponse } from '../dto/integration-dto.js';
export declare class CreateIntegrationCommand {
    request: CreateIntegrationRequest;
    userId: string;
    constructor(request: CreateIntegrationRequest, userId: string);
}
export declare class UpdateIntegrationCommand {
    id: string;
    request: UpdateIntegrationRequest;
    userId: string;
    constructor(id: string, request: UpdateIntegrationRequest, userId: string);
}
export declare class DeleteIntegrationCommand {
    id: string;
    userId: string;
    constructor(id: string, userId: string);
}
export declare class ActivateIntegrationCommand {
    id: string;
    userId: string;
    constructor(id: string, userId: string);
}
export declare class DeactivateIntegrationCommand {
    id: string;
    userId: string;
    constructor(id: string, userId: string);
}
export declare class GetIntegrationQuery {
    id: string;
    constructor(id: string);
}
export declare class ListIntegrationsQuery {
    query: IntegrationQuery;
    constructor(query: IntegrationQuery);
}
export declare class GetIntegrationByNameQuery {
    name: string;
    constructor(name: string);
}
export declare class GetIntegrationsByTypeQuery {
    type: string;
    constructor(type: string);
}
export declare class GetActiveIntegrationsQuery {
    constructor();
}
export declare class CreateIntegrationUseCase {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(command: CreateIntegrationCommand): Promise<Result<IntegrationResponse, Error>>;
    private mapToResponse;
}
export declare class UpdateIntegrationUseCase {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(command: UpdateIntegrationCommand): Promise<Result<IntegrationResponse, Error>>;
    private mapToResponse;
}
export declare class DeleteIntegrationUseCase {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(command: DeleteIntegrationCommand): Promise<Result<void, Error>>;
}
export declare class ActivateIntegrationUseCase {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(command: ActivateIntegrationCommand): Promise<Result<IntegrationResponse, Error>>;
    private mapToResponse;
}
export declare class DeactivateIntegrationUseCase {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(command: DeactivateIntegrationCommand): Promise<Result<IntegrationResponse, Error>>;
    private mapToResponse;
}
export declare class GetIntegrationQueryHandler {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(query: GetIntegrationQuery): Promise<Result<IntegrationResponse | null, Error>>;
    private mapToResponse;
}
export declare class ListIntegrationsQueryHandler {
    private unitOfWork;
    constructor(unitOfWork: UnitOfWork);
    execute(query: ListIntegrationsQuery): Promise<Result<IntegrationListResponse, Error>>;
}
//# sourceMappingURL=integration-use-cases.d.ts.map