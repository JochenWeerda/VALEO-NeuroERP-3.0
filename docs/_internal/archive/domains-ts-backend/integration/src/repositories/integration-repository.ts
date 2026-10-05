// domains/integration/src/repositories/integration-repository.ts
import { Repository } from '@packages/utilities/repository';
import { Integration, IntegrationId, Webhook, WebhookId, ApiKey, ApiKeyId, SyncJob } from '../services/integration-domain-service';

export class IntegrationRepository extends Repository<Integration, IntegrationId> {
  constructor() {
    super('integrations');
  }

  // Integration Queries
  async getIntegrationsByType(type: string): Promise<Integration[]> {
    return this.find({ type });
  }

  async getIntegrationsByStatus(status: string): Promise<Integration[]> {
    return this.find({ status });
  }

  async getActiveIntegrations(): Promise<Integration[]> {
    return this.getIntegrationsByStatus('active');
  }

  async getInactiveIntegrations(): Promise<Integration[]> {
    return this.getIntegrationsByStatus('inactive');
  }

  async getErrorIntegrations(): Promise<Integration[]> {
    return this.getIntegrationsByStatus('error');
  }

  async getMaintenanceIntegrations(): Promise<Integration[]> {
    return this.getIntegrationsByStatus('maintenance');
  }

  async getIntegrationsBySyncDate(dateFrom: Date, dateTo: Date): Promise<Integration[]> {
    return this.find({
      lastSyncAt: { $gte: dateFrom, $lte: dateTo }
    });
  }

  async getStaleIntegrations(daysThreshold: number = 7): Promise<Integration[]> {
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() - daysThreshold);
    
    const allIntegrations = await this.findAll();
    return allIntegrations.filter(integration => 
      !integration.lastSyncAt || integration.lastSyncAt < thresholdDate
    );
  }

  // Webhook Queries
  async getWebhooks(): Promise<Webhook[]> {
    return this.repository.findAll();
  }

  async getWebhooksByIntegration(integrationId: IntegrationId): Promise<Webhook[]> {
    return this.repository.find({ integrationId });
  }

  async getActiveWebhooks(): Promise<Webhook[]> {
    return this.repository.find({ isActive: true });
  }

  async getInactiveWebhooks(): Promise<Webhook[]> {
    return this.repository.find({ isActive: false });
  }

  async getWebhooksByMethod(method: string): Promise<Webhook[]> {
    return this.repository.find({ method });
  }

  async getWebhookStatistics(): Promise<{
    totalWebhooks: number;
    activeWebhooks: number;
    inactiveWebhooks: number;
    webhooksByMethod: Record<string, number>;
    webhooksByIntegration: Record<string, number>;
  }> {
    const allWebhooks = await this.getWebhooks();
    
    const webhooksByMethod = allWebhooks.reduce((acc, webhook) => {
      acc[webhook.method] = (acc[webhook.method] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const webhooksByIntegration = allWebhooks.reduce((acc, webhook) => {
      acc[webhook.integrationId] = (acc[webhook.integrationId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalWebhooks: allWebhooks.length,
      activeWebhooks: allWebhooks.filter(webhook => webhook.isActive).length,
      inactiveWebhooks: allWebhooks.filter(webhook => !webhook.isActive).length,
      webhooksByMethod,
      webhooksByIntegration
    };
  }

  // Sync Job Queries
  async getSyncJobs(): Promise<SyncJob[]> {
    return this.repository.findAll();
  }

  async getSyncJobsByIntegration(integrationId: IntegrationId): Promise<SyncJob[]> {
    return this.repository.find({ integrationId });
  }

  async getSyncJobsByStatus(status: string): Promise<SyncJob[]> {
    return this.repository.find({ status });
  }

  async getPendingSyncJobs(): Promise<SyncJob[]> {
    return this.getSyncJobsByStatus('pending');
  }

  async getRunningSyncJobs(): Promise<SyncJob[]> {
    return this.getSyncJobsByStatus('running');
  }

  async getCompletedSyncJobs(): Promise<SyncJob[]> {
    return this.getSyncJobsByStatus('completed');
  }

  async getFailedSyncJobs(): Promise<SyncJob[]> {
    return this.getSyncJobsByStatus('failed');
  }

  async getRecentSyncJobs(limit: number = 50): Promise<SyncJob[]> {
    const allSyncJobs = await this.getSyncJobs();
    return allSyncJobs
      .sort((a, b) => (b.startedAt?.getTime() || 0) - (a.startedAt?.getTime() || 0))
      .slice(0, limit);
  }

  async getSyncJobStatistics(): Promise<{
    totalSyncJobs: number;
    pendingSyncJobs: number;
    runningSyncJobs: number;
    completedSyncJobs: number;
    failedSyncJobs: number;
    averageRecordsProcessed: number;
    averageRecordsFailed: number;
    successRate: number;
  }> {
    const allSyncJobs = await this.getSyncJobs();
    
    const completedJobs = allSyncJobs.filter(job => job.status === 'completed');
    const failedJobs = allSyncJobs.filter(job => job.status === 'failed');
    
    const totalRecordsProcessed = allSyncJobs.reduce((sum, job) => sum + job.recordsProcessed, 0);
    const totalRecordsFailed = allSyncJobs.reduce((sum, job) => sum + job.recordsFailed, 0);
    
    const averageRecordsProcessed = allSyncJobs.length > 0 ? totalRecordsProcessed / allSyncJobs.length : 0;
    const averageRecordsFailed = allSyncJobs.length > 0 ? totalRecordsFailed / allSyncJobs.length : 0;
    
    const successRate = allSyncJobs.length > 0 ? (completedJobs.length / allSyncJobs.length) * 100 : 0;

    return {
      totalSyncJobs: allSyncJobs.length,
      pendingSyncJobs: allSyncJobs.filter(job => job.status === 'pending').length,
      runningSyncJobs: allSyncJobs.filter(job => job.status === 'running').length,
      completedSyncJobs: completedJobs.length,
      failedSyncJobs: failedJobs.length,
      averageRecordsProcessed,
      averageRecordsFailed,
      successRate
    };
  }

  // Integration Statistics
  async getIntegrationStatistics(): Promise<{
    totalIntegrations: number;
    activeIntegrations: number;
    inactiveIntegrations: number;
    errorIntegrations: number;
    maintenanceIntegrations: number;
    integrationsByType: Record<string, number>;
    averageSyncFrequency: number;
    staleIntegrationsCount: number;
  }> {
    const allIntegrations = await this.findAll();
    
    const integrationsByType = allIntegrations.reduce((acc, integration) => {
      acc[integration.type] = (acc[integration.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const staleIntegrations = await this.getStaleIntegrations();
    
    // Calculate average sync frequency (simplified)
    const integrationsWithSync = allIntegrations.filter(integration => integration.lastSyncAt);
    const averageSyncFrequency = integrationsWithSync.length > 0 
      ? integrationsWithSync.reduce((sum, integration) => {
          const daysSinceSync = integration.lastSyncAt 
            ? Math.floor((Date.now() - integration.lastSyncAt.getTime()) / (1000 * 60 * 60 * 24))
            : 0;
          return sum + daysSinceSync;
        }, 0) / integrationsWithSync.length
      : 0;

    return {
      totalIntegrations: allIntegrations.length,
      activeIntegrations: allIntegrations.filter(integration => integration.status === 'active').length,
      inactiveIntegrations: allIntegrations.filter(integration => integration.status === 'inactive').length,
      errorIntegrations: allIntegrations.filter(integration => integration.status === 'error').length,
      maintenanceIntegrations: allIntegrations.filter(integration => integration.status === 'maintenance').length,
      integrationsByType,
      averageSyncFrequency,
      staleIntegrationsCount: staleIntegrations.length
    };
  }

  // Health Check Queries
  async getIntegrationHealth(): Promise<{
    healthyIntegrations: number;
    unhealthyIntegrations: number;
    healthScore: number;
    criticalIssues: string[];
  }> {
    const allIntegrations = await this.findAll();
    const staleIntegrations = await this.getStaleIntegrations();
    const errorIntegrations = await this.getErrorIntegrations();
    
    const healthyIntegrations = allIntegrations.filter(integration => 
      integration.status === 'active' && 
      integration.lastSyncAt && 
      !staleIntegrations.includes(integration)
    ).length;
    
    const unhealthyIntegrations = allIntegrations.length - healthyIntegrations;
    const healthScore = allIntegrations.length > 0 ? (healthyIntegrations / allIntegrations.length) * 100 : 0;
    
    const criticalIssues: string[] = [];
    if (errorIntegrations.length > 0) {
      criticalIssues.push(`${errorIntegrations.length} integrations in error state`);
    }
    if (staleIntegrations.length > 0) {
      criticalIssues.push(`${staleIntegrations.length} integrations haven't synced recently`);
    }

    return {
      healthyIntegrations,
      unhealthyIntegrations,
      healthScore,
      criticalIssues
    };
  }
}

export const integrationRepository = new IntegrationRepository();
