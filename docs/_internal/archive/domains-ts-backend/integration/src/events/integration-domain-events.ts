// domains/integration/src/events/integration-domain-events.ts
import { DomainEvent } from '@packages/data-models/domain-events';
import { IntegrationId, WebhookId, ApiKeyId } from '@packages/data-models/branded-types';

// Integration Events
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

// Webhook Events
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

// Sync Events
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

// API Key Events
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

// Health Events
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

// Union type for all Integration domain events
export type IntegrationDomainEvent = 
  | IntegrationCreatedEvent
  | IntegrationUpdatedEvent
  | IntegrationStatusChangedEvent
  | IntegrationDeletedEvent
  | WebhookCreatedEvent
  | WebhookTriggeredEvent
  | WebhookFailedEvent
  | SyncStartedEvent
  | SyncCompletedEvent
  | SyncFailedEvent
  | SyncProgressEvent
  | ApiKeyCreatedEvent
  | ApiKeyRevokedEvent
  | IntegrationHealthCheckEvent
  | IntegrationAlertEvent;

// Event Handlers
export class IntegrationDomainEventHandler {
  async handleIntegrationCreated(event: IntegrationCreatedEvent): Promise<void> {
    console.log(`Integration created: ${event.integrationName} (${event.integrationType})`);
    // Additional business logic for integration creation
  }

  async handleIntegrationUpdated(event: IntegrationUpdatedEvent): Promise<void> {
    console.log(`Integration updated: ${event.integrationId}`, event.changes);
    // Additional business logic for integration updates
  }

  async handleIntegrationStatusChanged(event: IntegrationStatusChangedEvent): Promise<void> {
    console.log(`Integration status changed: ${event.integrationId} from ${event.oldStatus} to ${event.newStatus}`);
    // Additional business logic for status changes
  }

  async handleIntegrationDeleted(event: IntegrationDeletedEvent): Promise<void> {
    console.log(`Integration deleted: ${event.integrationName} (${event.integrationId})`);
    // Additional business logic for integration deletion
  }

  async handleWebhookCreated(event: WebhookCreatedEvent): Promise<void> {
    console.log(`Webhook created: ${event.webhookName} for integration ${event.integrationId}`);
    // Additional business logic for webhook creation
  }

  async handleWebhookTriggered(event: WebhookTriggeredEvent): Promise<void> {
    console.log(`Webhook triggered: ${event.webhookId} - Status: ${event.responseStatus}, Time: ${event.responseTime}ms`);
    // Additional business logic for webhook execution
  }

  async handleWebhookFailed(event: WebhookFailedEvent): Promise<void> {
    console.log(`Webhook failed: ${event.webhookId} - ${event.error} (Retry: ${event.retryCount})`);
    // Additional business logic for webhook failures
  }

  async handleSyncStarted(event: SyncStartedEvent): Promise<void> {
    console.log(`Sync started: ${event.syncJobId} for integration ${event.integrationId} (${event.syncType})`);
    // Additional business logic for sync start
  }

  async handleSyncCompleted(event: SyncCompletedEvent): Promise<void> {
    console.log(`Sync completed: ${event.syncJobId} - ${event.recordsProcessed} processed, ${event.recordsFailed} failed`);
    // Additional business logic for sync completion
  }

  async handleSyncFailed(event: SyncFailedEvent): Promise<void> {
    console.log(`Sync failed: ${event.syncJobId} - ${event.error} (Retry: ${event.retryCount})`);
    // Additional business logic for sync failures
  }

  async handleSyncProgress(event: SyncProgressEvent): Promise<void> {
    console.log(`Sync progress: ${event.syncJobId} - ${event.progress}% (${event.recordsProcessed}/${event.recordsTotal})`);
    // Additional business logic for sync progress
  }

  async handleApiKeyCreated(event: ApiKeyCreatedEvent): Promise<void> {
    console.log(`API key created: ${event.apiKeyName} for integration ${event.integrationId}`);
    // Additional business logic for API key creation
  }

  async handleApiKeyRevoked(event: ApiKeyRevokedEvent): Promise<void> {
    console.log(`API key revoked: ${event.apiKeyId} - Reason: ${event.reason}`);
    // Additional business logic for API key revocation
  }

  async handleIntegrationHealthCheck(event: IntegrationHealthCheckEvent): Promise<void> {
    console.log(`Health check: ${event.integrationId} - Status: ${event.healthStatus}, Score: ${event.healthScore}`);
    // Additional business logic for health checks
  }

  async handleIntegrationAlert(event: IntegrationAlertEvent): Promise<void> {
    console.log(`Integration alert: ${event.alertType} - ${event.alertMessage} (${event.severity})`);
    // Additional business logic for alerts
  }
}

export const integrationDomainEventHandler = new IntegrationDomainEventHandler();
