import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
import { IntegrationId, WebhookId, ApiKeyId } from '@valero-neuroerp/data-models/branded-types';
export interface IntegrationCreatedEvent extends DomainEvent {
    type: 'IntegrationCreated';
    integrationId: IntegrationId;
    integrationName: string;
    integrationType: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface IntegrationUpdatedEvent extends DomainEvent {
    type: 'IntegrationUpdated';
    integrationId: IntegrationId;
    changes: Record<string, any>;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface IntegrationStatusChangedEvent extends DomainEvent {
    type: 'IntegrationStatusChanged';
    integrationId: IntegrationId;
    oldStatus: string;
    newStatus: string;
    reason?: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface IntegrationDeletedEvent extends DomainEvent {
    type: 'IntegrationDeleted';
    integrationId: IntegrationId;
    integrationName: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface WebhookCreatedEvent extends DomainEvent {
    type: 'WebhookCreated';
    webhookId: WebhookId;
    integrationId: IntegrationId;
    webhookName: string;
    webhookUrl: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface WebhookTriggeredEvent extends DomainEvent {
    type: 'WebhookTriggered';
    webhookId: WebhookId;
    integrationId: IntegrationId;
    responseStatus: number;
    responseTime: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface WebhookFailedEvent extends DomainEvent {
    type: 'WebhookFailed';
    webhookId: WebhookId;
    integrationId: IntegrationId;
    error: string;
    retryCount: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SyncStartedEvent extends DomainEvent {
    type: 'SyncStarted';
    syncJobId: string;
    integrationId: IntegrationId;
    syncType: 'full' | 'incremental';
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SyncCompletedEvent extends DomainEvent {
    type: 'SyncCompleted';
    syncJobId: string;
    integrationId: IntegrationId;
    recordsProcessed: number;
    recordsFailed: number;
    duration: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SyncFailedEvent extends DomainEvent {
    type: 'SyncFailed';
    syncJobId: string;
    integrationId: IntegrationId;
    error: string;
    retryCount: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SyncProgressEvent extends DomainEvent {
    type: 'SyncProgress';
    syncJobId: string;
    integrationId: IntegrationId;
    progress: number;
    recordsProcessed: number;
    recordsTotal: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface ApiKeyCreatedEvent extends DomainEvent {
    type: 'ApiKeyCreated';
    apiKeyId: ApiKeyId;
    integrationId: IntegrationId;
    apiKeyName: string;
    permissions: string[];
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface ApiKeyRevokedEvent extends DomainEvent {
    type: 'ApiKeyRevoked';
    apiKeyId: ApiKeyId;
    integrationId: IntegrationId;
    reason: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface IntegrationHealthCheckEvent extends DomainEvent {
    type: 'IntegrationHealthCheck';
    integrationId: IntegrationId;
    healthStatus: 'healthy' | 'unhealthy' | 'critical';
    healthScore: number;
    issues: string[];
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface IntegrationAlertEvent extends DomainEvent {
    type: 'IntegrationAlert';
    integrationId: IntegrationId;
    alertType: 'error' | 'warning' | 'info';
    alertMessage: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export type IntegrationDomainEvent = IntegrationCreatedEvent | IntegrationUpdatedEvent | IntegrationStatusChangedEvent | IntegrationDeletedEvent | WebhookCreatedEvent | WebhookTriggeredEvent | WebhookFailedEvent | SyncStartedEvent | SyncCompletedEvent | SyncFailedEvent | SyncProgressEvent | ApiKeyCreatedEvent | ApiKeyRevokedEvent | IntegrationHealthCheckEvent | IntegrationAlertEvent;
export declare class IntegrationDomainEventHandler {
    handleIntegrationCreated(event: IntegrationCreatedEvent): Promise<void>;
    handleIntegrationUpdated(event: IntegrationUpdatedEvent): Promise<void>;
    handleIntegrationStatusChanged(event: IntegrationStatusChangedEvent): Promise<void>;
    handleIntegrationDeleted(event: IntegrationDeletedEvent): Promise<void>;
    handleWebhookCreated(event: WebhookCreatedEvent): Promise<void>;
    handleWebhookTriggered(event: WebhookTriggeredEvent): Promise<void>;
    handleWebhookFailed(event: WebhookFailedEvent): Promise<void>;
    handleSyncStarted(event: SyncStartedEvent): Promise<void>;
    handleSyncCompleted(event: SyncCompletedEvent): Promise<void>;
    handleSyncFailed(event: SyncFailedEvent): Promise<void>;
    handleSyncProgress(event: SyncProgressEvent): Promise<void>;
    handleApiKeyCreated(event: ApiKeyCreatedEvent): Promise<void>;
    handleApiKeyRevoked(event: ApiKeyRevokedEvent): Promise<void>;
    handleIntegrationHealthCheck(event: IntegrationHealthCheckEvent): Promise<void>;
    handleIntegrationAlert(event: IntegrationAlertEvent): Promise<void>;
}
export declare const integrationDomainEventHandler: IntegrationDomainEventHandler;
//# sourceMappingURL=integration-domain-events.d.ts.map