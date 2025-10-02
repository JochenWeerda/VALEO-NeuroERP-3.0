"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.integrationDomainService = exports.IntegrationDomainService = void 0;
// domains/integration/src/services/integration-domain-service.ts
const base_service_1 = require("@packages/utilities/base-service");
const business_logic_orchestrator_1 = require("@packages/business-rules/business-logic-orchestrator");
class IntegrationDomainService extends base_service_1.BaseService {
    constructor() {
        super();
        this.initializeBusinessRules();
    }
    initializeBusinessRules() {
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Integration', new IntegrationValidationRule());
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Integration', new WebhookValidationRule());
    }
    // Integration Management
    async createIntegration(request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Integration',
            metadata: { source: 'integration-service' }
        };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Integration', request, 'create', context);
        if (!result.success) {
            throw new Error(`Integration creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const integration = {
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
    async updateIntegration(integrationId, updates) {
        const existingIntegration = await this.repository.findById(integrationId);
        if (!existingIntegration) {
            throw new Error(`Integration ${integrationId} not found`);
        }
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'update',
            domain: 'Integration',
            metadata: { source: 'integration-service', integrationId }
        };
        const updateData = { ...existingIntegration, ...updates };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Integration', updateData, 'update', context);
        if (!result.success) {
            throw new Error(`Integration update failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const updatedIntegration = {
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
    async createWebhook(integrationId, webhookData) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Integration',
            metadata: { source: 'integration-service', integrationId }
        };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Integration', webhookData, 'create', context);
        if (!result.success) {
            throw new Error(`Webhook creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const webhook = {
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
    async startSync(integrationId, type = 'incremental') {
        const integration = await this.repository.findById(integrationId);
        if (!integration) {
            throw new Error(`Integration ${integrationId} not found`);
        }
        const syncJob = {
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
    async executeSync(syncJob) {
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
        }
        catch (error) {
            await this.updateSyncJobStatus(syncJob.id, 'failed', error.message);
            throw error;
        }
    }
    async updateSyncJobStatus(syncJobId, status, errorMessage, recordsProcessed, recordsFailed) {
        const syncJob = await this.repository.findById(syncJobId);
        if (!syncJob) {
            throw new Error(`Sync job ${syncJobId} not found`);
        }
        const updates = {
            status,
            errorMessage,
            recordsProcessed: recordsProcessed ?? syncJob.recordsProcessed,
            recordsFailed: recordsFailed ?? syncJob.recordsFailed
        };
        if (status === 'running') {
            updates.startedAt = new Date();
        }
        else if (status === 'completed' || status === 'failed') {
            updates.completedAt = new Date();
        }
        await this.repository.update(syncJobId, { ...syncJob, ...updates });
    }
    // Helper Methods
    async getIntegration(integrationId) {
        return this.repository.findById(integrationId);
    }
    async getIntegrations(filters) {
        return this.repository.find(filters);
    }
    async getWebhooks(integrationId) {
        return this.repository.find({ integrationId });
    }
    async getSyncJobs(integrationId) {
        return this.repository.find({ integrationId });
    }
    generateIntegrationId() {
        return `INT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateWebhookId() {
        return `WEBHOOK_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateSyncJobId() {
        return `SYNC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    getCurrentUserId() {
        return 'system';
    }
    async publishDomainEvent(eventType, data) {
        console.log(`Publishing domain event: ${eventType}`, data);
    }
}
exports.IntegrationDomainService = IntegrationDomainService;
// Integration Business Rules
class IntegrationValidationRule {
    name = 'INTEGRATION_VALIDATION';
    description = 'Validates integration creation and updates';
    priority = 100;
    domain = 'Integration';
    version = '1.0.0';
    enabled = true;
    async validate(data) {
        const errors = [];
        const warnings = [];
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
    async validate(data) {
        const errors = [];
        const warnings = [];
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
exports.integrationDomainService = new IntegrationDomainService();
