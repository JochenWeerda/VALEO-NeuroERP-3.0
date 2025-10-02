import { ApiKeyId, IntegrationId } from '@valero-neuroerp/data-models';
export interface ApiKey {
    id: ApiKeyId;
    integrationId: IntegrationId;
    name: string;
    key: string;
    permissions: string[];
    isActive: boolean;
    expiresAt?: Date;
    createdAt: Date;
    updatedAt: Date;
}
export declare class ApiKeyCreatedEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        apiKeyId: ApiKeyId;
        integrationId: IntegrationId;
        name: string;
    };
    constructor(apiKeyId: ApiKeyId, integrationId: IntegrationId, name: string);
}
export declare class ApiKeyUpdatedEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        apiKeyId: ApiKeyId;
        changes: Partial<ApiKey>;
    };
    constructor(apiKeyId: ApiKeyId, changes: Partial<ApiKey>);
}
export declare function createApiKey(data: Omit<ApiKey, 'id' | 'createdAt' | 'updatedAt'>): ApiKey;
//# sourceMappingURL=apikey.d.ts.map