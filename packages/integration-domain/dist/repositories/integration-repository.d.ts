import { Integration, IntegrationId, Webhook, SyncJob } from '../services/integration-domain-service';
export declare class IntegrationRepository extends Repository<Integration, IntegrationId> {
    constructor();
    getIntegrationsByType(type: string): Promise<Integration[]>;
    getIntegrationsByStatus(status: string): Promise<Integration[]>;
    getActiveIntegrations(): Promise<Integration[]>;
    getInactiveIntegrations(): Promise<Integration[]>;
    getErrorIntegrations(): Promise<Integration[]>;
    getMaintenanceIntegrations(): Promise<Integration[]>;
    getIntegrationsBySyncDate(dateFrom: Date, dateTo: Date): Promise<Integration[]>;
    getStaleIntegrations(daysThreshold?: number): Promise<Integration[]>;
    getWebhooks(): Promise<Webhook[]>;
    getWebhooksByIntegration(integrationId: IntegrationId): Promise<Webhook[]>;
    getActiveWebhooks(): Promise<Webhook[]>;
    getInactiveWebhooks(): Promise<Webhook[]>;
    getWebhooksByMethod(method: string): Promise<Webhook[]>;
    getWebhookStatistics(): Promise<{
        totalWebhooks: number;
        activeWebhooks: number;
        inactiveWebhooks: number;
        webhooksByMethod: Record<string, number>;
        webhooksByIntegration: Record<string, number>;
    }>;
    getSyncJobs(): Promise<SyncJob[]>;
    getSyncJobsByIntegration(integrationId: IntegrationId): Promise<SyncJob[]>;
    getSyncJobsByStatus(status: string): Promise<SyncJob[]>;
    getPendingSyncJobs(): Promise<SyncJob[]>;
    getRunningSyncJobs(): Promise<SyncJob[]>;
    getCompletedSyncJobs(): Promise<SyncJob[]>;
    getFailedSyncJobs(): Promise<SyncJob[]>;
    getRecentSyncJobs(limit?: number): Promise<SyncJob[]>;
    getSyncJobStatistics(): Promise<{
        totalSyncJobs: number;
        pendingSyncJobs: number;
        runningSyncJobs: number;
        completedSyncJobs: number;
        failedSyncJobs: number;
        averageRecordsProcessed: number;
        averageRecordsFailed: number;
        successRate: number;
    }>;
    getIntegrationStatistics(): Promise<{
        totalIntegrations: number;
        activeIntegrations: number;
        inactiveIntegrations: number;
        errorIntegrations: number;
        maintenanceIntegrations: number;
        integrationsByType: Record<string, number>;
        averageSyncFrequency: number;
        staleIntegrationsCount: number;
    }>;
    getIntegrationHealth(): Promise<{
        healthyIntegrations: number;
        unhealthyIntegrations: number;
        healthScore: number;
        criticalIssues: string[];
    }>;
}
export declare const integrationRepository: IntegrationRepository;
//# sourceMappingURL=integration-repository.d.ts.map