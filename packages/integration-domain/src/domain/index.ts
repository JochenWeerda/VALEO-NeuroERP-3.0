/**
 * Domain Layer Exports
 */

// Value Objects
export { IntegrationId } from './values/integration-id.js';
export { WebhookId } from './values/webhook-id.js';
export { SyncJobId } from './values/sync-job-id.js';
export { ApiKeyId } from './values/api-key-id.js';

// Domain Events
export { BaseDomainEvent } from './events/base-domain-event.js';
export { IntegrationCreatedEvent, IntegrationUpdatedEvent, IntegrationDeletedEvent } from './events/integration-events.js';
export { WebhookCreatedEvent, WebhookTriggeredEvent, WebhookFailedEvent } from './events/webhook-events.js';
export { SyncJobCreatedEvent, SyncJobStartedEvent, SyncJobCompletedEvent, SyncJobFailedEvent } from './events/sync-job-events.js';

// Domain Entities
export { Integration, type IntegrationType, type IntegrationConfig } from './entities/integration.js';
export { Webhook, type WebhookConfig } from './entities/webhook.js';
export { SyncJob, type SyncJobStatus, type SyncJobConfig } from './entities/sync-job.js';

// Repository Interfaces
export type {
  BaseRepository,
  IntegrationRepository,
  WebhookRepository,
  SyncJobRepository,
  UnitOfWork
} from './interfaces/repositories.js';
