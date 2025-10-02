import { BaseService } from '@valero-neuroerp/utilities/base-service';
import { IntegrationId, WebhookId, ApiKeyId } from '@valero-neuroerp/data-models/branded-types';
export interface Integration {
    id: IntegrationId;
    name: string;
    description: string;
    type: 'api' | 'webhook' | 'sftp' | 'database' | 'message_queue';
    status: 'active' | 'inactive' | 'error' | 'maintenance';
    configuration: Record<string, any>;
    credentials: Record<string, any>;
    createdAt: Date;
    updatedAt: Date;
    lastSyncAt?: Date;
}
export interface Webhook {
    id: WebhookId;
    integrationId: IntegrationId;
    name: string;
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE';
    headers: Record<string, string>;
    payload: Record<string, any>;
    isActive: boolean;
    retryCount: number;
    maxRetries: number;
    createdAt: Date;
    updatedAt: Date;
}
export interface ApiKey {
    id: ApiKeyId;
    integrationId: IntegrationId;
    name: string;
    key: string;
    secret?: string;
    permissions: string[];
    expiresAt?: Date;
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface SyncJob {
    id: string;
    integrationId: IntegrationId;
    type: 'full' | 'incremental';
    status: 'pending' | 'running' | 'completed' | 'failed';
    startedAt?: Date;
    completedAt?: Date;
    recordsProcessed: number;
    recordsFailed: number;
    errorMessage?: string;
}
export interface IntegrationRequest {
    name: string;
    description: string;
    type: string;
    configuration: Record<string, any>;
    credentials: Record<string, any>;
}
export declare class IntegrationDomainService extends BaseService {
    constructor();
    private initializeBusinessRules;
    createIntegration(request: IntegrationRequest): Promise<Integration>;
    updateIntegration(integrationId: IntegrationId, updates: Partial<Integration>): Promise<Integration>;
    createWebhook(integrationId: IntegrationId, webhookData: Omit<Webhook, 'id' | 'integrationId' | 'createdAt' | 'updatedAt'>): Promise<Webhook>;
    startSync(integrationId: IntegrationId, type?: 'full' | 'incremental'): Promise<SyncJob>;
    private executeSync;
    private updateSyncJobStatus;
    getIntegration(integrationId: IntegrationId): Promise<Integration | null>;
    getIntegrations(filters?: {
        type?: string;
        status?: string;
    }): Promise<Integration[]>;
    getWebhooks(integrationId: IntegrationId): Promise<Webhook[]>;
    getSyncJobs(integrationId: IntegrationId): Promise<SyncJob[]>;
    private generateIntegrationId;
    private generateWebhookId;
    private generateSyncJobId;
    private getCurrentUserId;
    private publishDomainEvent;
}
export declare const integrationDomainService: IntegrationDomainService;
//# sourceMappingURL=integration-domain-service.d.ts.map