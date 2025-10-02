import { IntegrationId } from '@valero-neuroerp/data-models';
export interface Integration {
    id: IntegrationId;
    name: string;
    type: 'API' | 'Webhook' | 'File' | 'Database';
    status: 'active' | 'inactive' | 'error';
    configuration: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
}
export declare class IntegrationCreatedEvent {
    id: string;
    aggregateType: string;
    version: number;
    occurredOn: Date;
    data: {
        integrationId: IntegrationId;
        name: string;
        type: string;
    };
    constructor(integrationId: IntegrationId, name: string, type: string);
}
export declare function createIntegration(data: Omit<Integration, 'id' | 'createdAt' | 'updatedAt'>): Integration;
//# sourceMappingURL=integration.d.ts.map