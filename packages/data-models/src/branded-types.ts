// Branded Types for VALEO NeuroERP 3.0

export type CustomerId = string & { readonly __brand: 'CustomerId' };
export type ProductId = string & { readonly __brand: 'ProductId' };
export type OrderId = string & { readonly __brand: 'OrderId' };
export type SupplierId = string & { readonly __brand: 'SupplierId' };
export type InvoiceId = string & { readonly __brand: 'InvoiceId' };
export type InventoryId = string & { readonly __brand: 'InventoryId' };

// Generic ID type and factory
export type Id = string;
export const createId = (id: string): Id => id;

// Factory functions
export const createCustomerId = (id: string): CustomerId => id as CustomerId;
export const createProductId = (id: string): ProductId => id as ProductId;
export const createOrderId = (id: string): OrderId => id as OrderId;
export const createSupplierId = (id: string): SupplierId => id as SupplierId;
export const createInvoiceId = (id: string): InvoiceId => id as InvoiceId;
export const createInventoryId = (id: string): InventoryId => id as InventoryId;

// Analytics domain types
export type DashboardId = string & { readonly __brand: 'DashboardId' };
export type ReportId = string & { readonly __brand: 'ReportId' };
export type MetricId = string & { readonly __brand: 'MetricId' };

export const createDashboardId = (id: string): DashboardId => id as DashboardId;
export const createReportId = (id: string): ReportId => id as ReportId;
export const createMetricId = (id: string): MetricId => id as MetricId;

// Integration domain types
export type SyncJobId = string & { readonly __brand: 'SyncJobId' };
export type WebhookId = string & { readonly __brand: 'WebhookId' };
export type ApiKeyId = string & { readonly __brand: 'ApiKeyId' };
export type IntegrationId = string & { readonly __brand: 'IntegrationId' };

export const createSyncJobId = (id: string): SyncJobId => id as SyncJobId;
export const createWebhookId = (id: string): WebhookId => id as WebhookId;
export const createApiKeyId = (id: string): ApiKeyId => id as ApiKeyId;
export const createIntegrationId = (id: string): IntegrationId => id as IntegrationId;

// Additional Integration types
export type ApiGatewayId = string & { readonly __brand: 'ApiGatewayId' };
export type SyncJobRepositoryId = string & { readonly __brand: 'SyncJobRepositoryId' };
export type WebhookRepositoryId = string & { readonly __brand: 'WebhookRepositoryId' };

export const createApiGatewayId = (id: string): ApiGatewayId => id as ApiGatewayId;
export const createSyncJobRepositoryId = (id: string): SyncJobRepositoryId => id as SyncJobRepositoryId;
export const createWebhookRepositoryId = (id: string): WebhookRepositoryId => id as WebhookRepositoryId;

// Brand type
export type Brand = string;
