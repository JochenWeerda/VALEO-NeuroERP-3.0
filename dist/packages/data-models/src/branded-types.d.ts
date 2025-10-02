/**
 * Branded type helpers used across VALEO NeuroERP 3.0.
 *
 * The implementation keeps the original intent of the documentation-only file
 * but exposes compile-time safe helpers that can be imported by every domain.
 */
export type Brand<TValue, TBrand extends string> = TValue & {
    readonly __brand: TBrand;
};
export type UserId = Brand<string, 'UserId'>;
export type ProductId = Brand<string, 'ProductId'>;
export type OrderId = Brand<string, 'OrderId'>;
export type CustomerId = Brand<string, 'CustomerId'>;
export type InvoiceId = Brand<string, 'InvoiceId'>;
export type PaymentId = Brand<string, 'PaymentId'>;
export type CategoryId = Brand<string, 'CategoryId'>;
export type SupplierId = Brand<string, 'SupplierId'>;
export type ProductRepositoryId = Brand<string, 'ProductRepositoryId'>;
export type InventoryRepositoryId = Brand<string, 'InventoryRepositoryId'>;
export type Email = Brand<string, 'Email'>;
export type PhoneNumber = Brand<string, 'PhoneNumber'>;
export type PostalCode = Brand<string, 'PostalCode'>;
export type Currency = Brand<string, 'Currency'>;
export type Language = Brand<string, 'Language'>;
export type OrderStatus = Brand<string, 'OrderStatus'>;
export type PaymentStatus = Brand<string, 'PaymentStatus'>;
export type UserRole = Brand<string, 'UserRole'>;
export type Permission = Brand<string, 'Permission'>;
/**
 * Utility used by repositories/services to generate strongly typed identifiers.
 * Falls back to Math.random in environments where `crypto.randomUUID` is not available.
 */
export declare function createId<TBrand extends string>(brand?: TBrand): Brand<string, TBrand>;
/**
 * Cast helper to brand an existing primitive.
 */
export declare function brandValue<TBrand extends string>(value: string, brand: TBrand): Brand<string, TBrand>;
/**
 * Branded type for Inventory ID to ensure type safety
 */
export type InventoryId = string & {
    readonly __brand: 'InventoryId';
};
/**
 * Creates a branded Inventory ID
 */
export declare function createInventoryId(value: string): InventoryId;
/**
 * Type guard for InventoryId
 */
export declare function isInventoryId(value: any): value is InventoryId;
/**
 * Branded type for Report ID to ensure type safety
 */
export type ReportId = string & {
    readonly __brand: 'ReportId';
};
/**
 * Creates a branded Report ID
 */
export declare function createReportId(value: string): ReportId;
/**
 * Type guard for ReportId
 */
export declare function isReportId(value: any): value is ReportId;
/**
 * Branded type for Dashboard ID to ensure type safety
 */
export type DashboardId = string & {
    readonly __brand: 'DashboardId';
};
/**
 * Creates a branded Dashboard ID
 */
export declare function createDashboardId(value: string): DashboardId;
/**
 * Type guard for DashboardId
 */
export declare function isDashboardId(value: any): value is DashboardId;
/**
 * Branded type for Webhook ID to ensure type safety
 */
export type WebhookId = string & {
    readonly __brand: 'WebhookId';
};
/**
 * Creates a branded Webhook ID
 */
export declare function createWebhookId(value: string): WebhookId;
/**
 * Type guard for WebhookId
 */
export declare function isWebhookId(value: any): value is WebhookId;
/**
 * Branded type for SyncJob ID to ensure type safety
 */
export type SyncJobId = string & {
    readonly __brand: 'SyncJobId';
};
/**
 * Creates a branded SyncJob ID
 */
export declare function createSyncJobId(value: string): SyncJobId;
/**
 * Type guard for SyncJobId
 */
export declare function isSyncJobId(value: any): value is SyncJobId;
//***REMOVED*** sourceMappingURL=branded-types.d.ts.map