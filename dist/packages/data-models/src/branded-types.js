/**
 * Branded type helpers used across VALEO NeuroERP 3.0.
 *
 * The implementation keeps the original intent of the documentation-only file
 * but exposes compile-time safe helpers that can be imported by every domain.
 */
/**
 * Utility used by repositories/services to generate strongly typed identifiers.
 * Falls back to Math.random in environments where `crypto.randomUUID` is not available.
 */
export function createId(brand) {
    const value = typeof globalThis.crypto?.randomUUID === 'function'
        ? globalThis.crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    return value;
}
/**
 * Cast helper to brand an existing primitive.
 */
export function brandValue(value, brand) {
    return value;
}
/**
 * Creates a branded Inventory ID
 */
export function createInventoryId(value) {
    if (!value || typeof value !== 'string') {
        throw new Error('Invalid Inventory ID: must be a non-empty string');
    }
    return value;
}
/**
 * Type guard for InventoryId
 */
export function isInventoryId(value) {
    return typeof value === 'string' && value.length > 0;
}
/**
 * Creates a branded Report ID
 */
export function createReportId(value) {
    if (!value || typeof value !== 'string') {
        throw new Error('Invalid Report ID: must be a non-empty string');
    }
    return value;
}
/**
 * Type guard for ReportId
 */
export function isReportId(value) {
    return typeof value === 'string' && value.length > 0;
}
/**
 * Creates a branded Dashboard ID
 */
export function createDashboardId(value) {
    if (!value || typeof value !== 'string') {
        throw new Error('Invalid Dashboard ID: must be a non-empty string');
    }
    return value;
}
/**
 * Type guard for DashboardId
 */
export function isDashboardId(value) {
    return typeof value === 'string' && value.length > 0;
}
/**
 * Creates a branded Webhook ID
 */
export function createWebhookId(value) {
    if (!value || typeof value !== 'string') {
        throw new Error('Invalid Webhook ID: must be a non-empty string');
    }
    return value;
}
/**
 * Type guard for WebhookId
 */
export function isWebhookId(value) {
    return typeof value === 'string' && value.length > 0;
}
/**
 * Creates a branded SyncJob ID
 */
export function createSyncJobId(value) {
    if (!value || typeof value !== 'string') {
        throw new Error('Invalid SyncJob ID: must be a non-empty string');
    }
    return value;
}
/**
 * Type guard for SyncJobId
 */
export function isSyncJobId(value) {
    return typeof value === 'string' && value.length > 0;
}
