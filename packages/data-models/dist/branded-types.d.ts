export type CustomerId = string & {
    readonly __brand: 'CustomerId';
};
export type ProductId = string & {
    readonly __brand: 'ProductId';
};
export type OrderId = string & {
    readonly __brand: 'OrderId';
};
export type SupplierId = string & {
    readonly __brand: 'SupplierId';
};
export type InvoiceId = string & {
    readonly __brand: 'InvoiceId';
};
export type InventoryId = string & {
    readonly __brand: 'InventoryId';
};
export type Id = string;
export declare const createId: (id: string) => Id;
export declare const createCustomerId: (id: string) => CustomerId;
export declare const createProductId: (id: string) => ProductId;
export declare const createOrderId: (id: string) => OrderId;
export declare const createSupplierId: (id: string) => SupplierId;
export declare const createInvoiceId: (id: string) => InvoiceId;
export declare const createInventoryId: (id: string) => InventoryId;
export type DashboardId = string & {
    readonly __brand: 'DashboardId';
};
export type ReportId = string & {
    readonly __brand: 'ReportId';
};
export type MetricId = string & {
    readonly __brand: 'MetricId';
};
export declare const createDashboardId: (id: string) => DashboardId;
export declare const createReportId: (id: string) => ReportId;
export declare const createMetricId: (id: string) => MetricId;
export type SyncJobId = string & {
    readonly __brand: 'SyncJobId';
};
export type WebhookId = string & {
    readonly __brand: 'WebhookId';
};
export type ApiKeyId = string & {
    readonly __brand: 'ApiKeyId';
};
export type IntegrationId = string & {
    readonly __brand: 'IntegrationId';
};
export declare const createSyncJobId: (id: string) => SyncJobId;
export declare const createWebhookId: (id: string) => WebhookId;
export declare const createApiKeyId: (id: string) => ApiKeyId;
export declare const createIntegrationId: (id: string) => IntegrationId;
export type ApiGatewayId = string & {
    readonly __brand: 'ApiGatewayId';
};
export type SyncJobRepositoryId = string & {
    readonly __brand: 'SyncJobRepositoryId';
};
export type WebhookRepositoryId = string & {
    readonly __brand: 'WebhookRepositoryId';
};
export declare const createApiGatewayId: (id: string) => ApiGatewayId;
export declare const createSyncJobRepositoryId: (id: string) => SyncJobRepositoryId;
export declare const createWebhookRepositoryId: (id: string) => WebhookRepositoryId;
export type Brand = string;
//# sourceMappingURL=branded-types.d.ts.map