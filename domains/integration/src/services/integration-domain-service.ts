// domains/integration/src/services/integration-domain-service.ts
import { BaseService } from '@packages/utilities/base-service';
import { IntegrationId, WebhookId, ApiKeyId } from '@packages/data-models/branded-types';
import { businessLogicOrchestrator } from '@packages/business-rules/business-logic-orchestrator';

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

export class IntegrationDomainService extends BaseService {
  constructor() {
    super();
    this.initializeBusinessRules();
  }

  private initializeBusinessRules(): void {
    businessLogicOrchestrator.registerRule('Integration', new IntegrationValidationRule());
    businessLogicOrchestrator.registerRule('Integration', new WebhookValidationRule());
  }

  // Integration Management
  async createIntegration(request: IntegrationRequest): Promise<Integration> {
    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'create' as const,
      domain: 'Integration',
      metadata: { source: 'integration-service' }
    };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Integration',
      request,
      'create',
      context
    );

    if (!result.success) {
      throw new Error(`Integration creation failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const integration: Integration = {
      id: this.generateIntegrationId(),
      ...result.data,
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await this.repository.create(integration);

    await this.publishDomainEvent('IntegrationCreated', {
      integrationId: integration.id,
      integrationName: integration.name,
      integrationType: integration.type,
      timestamp: new Date()
    });

    return integration;
  }

  async updateIntegration(integrationId: IntegrationId, updates: Partial<Integration>): Promise<Integration> {
    const existingIntegration = await this.repository.findById(integrationId);
    if (!existingIntegration) {
      throw new Error(`Integration ${integrationId} not found`);
    }

    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'update' as const,
      domain: 'Integration',
      metadata: { source: 'integration-service', integrationId }
    };

    const updateData = { ...existingIntegration, ...updates };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Integration',
      updateData,
      'update',
      context
    );

    if (!result.success) {
      throw new Error(`Integration update failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const updatedIntegration: Integration = {
      ...result.data,
      updatedAt: new Date()
    };

    await this.repository.update(integrationId, updatedIntegration);

    await this.publishDomainEvent('IntegrationUpdated', {
      integrationId: updatedIntegration.id,
      changes: updates,
      timestamp: new Date()
    });

    return updatedIntegration;
  }

  // Webhook Management
  async createWebhook(integrationId: IntegrationId, webhookData: Omit<Webhook, 'id' | 'integrationId' | 'createdAt' | 'updatedAt'>): Promise<Webhook> {
    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'create' as const,
      domain: 'Integration',
      metadata: { source: 'integration-service', integrationId }
    };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Integration',
      webhookData,
      'create',
      context
    );

    if (!result.success) {
      throw new Error(`Webhook creation failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const webhook: Webhook = {
      id: this.generateWebhookId(),
      integrationId,
      ...result.data,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await this.repository.create(webhook);

    await this.publishDomainEvent('WebhookCreated', {
      webhookId: webhook.id,
      integrationId: webhook.integrationId,
      webhookName: webhook.name,
      timestamp: new Date()
    });

    return webhook;
  }

  // Sync Operations
  async startSync(integrationId: IntegrationId, type: 'full' | 'incremental' = 'incremental'): Promise<SyncJob> {
    const integration = await this.repository.findById(integrationId);
    if (!integration) {
      throw new Error(`Integration ${integrationId} not found`);
    }

    const syncJob: SyncJob = {
      id: this.generateSyncJobId(),
      integrationId,
      type,
      status: 'pending',
      recordsProcessed: 0,
      recordsFailed: 0
    };

    await this.repository.create(syncJob);

    // Start sync asynchronously
    this.executeSync(syncJob).catch(error => {
      console.error(`Sync failed for integration ${integrationId}:`, error);
      this.updateSyncJobStatus(syncJob.id, 'failed', error.message);
    });

    await this.publishDomainEvent('SyncStarted', {
      syncJobId: syncJob.id,
      integrationId: syncJob.integrationId,
      syncType: syncJob.type,
      timestamp: new Date()
    });

    return syncJob;
  }

  private async executeSync(syncJob: SyncJob): Promise<void> {
    try {
      await this.updateSyncJobStatus(syncJob.id, 'running');
      
      const integration = await this.repository.findById(syncJob.integrationId);
      if (!integration) {
        throw new Error(`Integration ${syncJob.integrationId} not found`);
      }

      // Simulate sync process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const recordsProcessed = Math.floor(Math.random() * 1000) + 100;
      const recordsFailed = Math.floor(Math.random() * 10);

      await this.updateSyncJobStatus(syncJob.id, 'completed', undefined, recordsProcessed, recordsFailed);

      // Update integration last sync time
      await this.repository.update(syncJob.integrationId, {
        ...integration,
        lastSyncAt: new Date(),
        updatedAt: new Date()
      });

      await this.publishDomainEvent('SyncCompleted', {
        syncJobId: syncJob.id,
        integrationId: syncJob.integrationId,
        recordsProcessed,
        recordsFailed,
        timestamp: new Date()
      });
    } catch (error) {
      await this.updateSyncJobStatus(syncJob.id, 'failed', error.message);
      throw error;
    }
  }

  private async updateSyncJobStatus(syncJobId: string, status: string, errorMessage?: string, recordsProcessed?: number, recordsFailed?: number): Promise<void> {
    const syncJob = await this.repository.findById(syncJobId);
    if (!syncJob) {
      throw new Error(`Sync job ${syncJobId} not found`);
    }

    const updates: Partial<SyncJob> = {
      status,
      errorMessage,
      recordsProcessed: recordsProcessed ?? syncJob.recordsProcessed,
      recordsFailed: recordsFailed ?? syncJob.recordsFailed
    };

    if (status === 'running') {
      updates.startedAt = new Date();
    } else if (status === 'completed' || status === 'failed') {
      updates.completedAt = new Date();
    }

    await this.repository.update(syncJobId, { ...syncJob, ...updates });
  }

  // Helper Methods
  async getIntegration(integrationId: IntegrationId): Promise<Integration | null> {
    return this.repository.findById(integrationId);
  }

  async getIntegrations(filters?: {
    type?: string;
    status?: string;
  }): Promise<Integration[]> {
    return this.repository.find(filters);
  }

  async getWebhooks(integrationId: IntegrationId): Promise<Webhook[]> {
    return this.repository.find({ integrationId });
  }

  async getSyncJobs(integrationId: IntegrationId): Promise<SyncJob[]> {
    return this.repository.find({ integrationId });
  }

  private generateIntegrationId(): IntegrationId {
    return `INT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as IntegrationId;
  }

  private generateWebhookId(): WebhookId {
    return `WEBHOOK_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as WebhookId;
  }

  private generateSyncJobId(): string {
    return `SYNC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string {
    return 'system';
  }

  private async publishDomainEvent(eventType: string, data: any): Promise<void> {
    console.log(`Publishing domain event: ${eventType}`, data);
  }
}

// Integration Business Rules
class IntegrationValidationRule {
  name = 'INTEGRATION_VALIDATION';
  description = 'Validates integration creation and updates';
  priority = 100;
  domain = 'Integration';
  version = '1.0.0';
  enabled = true;

  async validate(data: any): Promise<any> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (!data.name || data.name.trim().length === 0) {
      errors.push({
        field: 'name',
        message: 'Integration name is required',
        code: 'INTEGRATION_NAME_REQUIRED',
        severity: 'error'
      });
    }

    const validTypes = ['api', 'webhook', 'sftp', 'database', 'message_queue'];
    if (!data.type || !validTypes.includes(data.type)) {
      errors.push({
        field: 'type',
        message: `Integration type must be one of: ${validTypes.join(', ')}`,
        code: 'INTEGRATION_INVALID_TYPE',
        severity: 'error'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

class WebhookValidationRule {
  name = 'WEBHOOK_VALIDATION';
  description = 'Validates webhook creation';
  priority = 95;
  domain = 'Integration';
  version = '1.0.0';
  enabled = true;

  async validate(data: any): Promise<any> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (!data.url || data.url.trim().length === 0) {
      errors.push({
        field: 'url',
        message: 'Webhook URL is required',
        code: 'WEBHOOK_URL_REQUIRED',
        severity: 'error'
      });
    }

    const validMethods = ['GET', 'POST', 'PUT', 'DELETE'];
    if (!data.method || !validMethods.includes(data.method)) {
      errors.push({
        field: 'method',
        message: `Webhook method must be one of: ${validMethods.join(', ')}`,
        code: 'WEBHOOK_INVALID_METHOD',
        severity: 'error'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

export const integrationDomainService = new IntegrationDomainService();
