/**
 * Branded Types for VALEO NeuroERP 3.0
 * Type-safe identifiers using TypeScript branded types
 */

// Base branded type factory
export type Brand<K, T> = K & { __brand: T };

// User and Authentication Types
export type UserId = Brand<string, 'UserId'>;
export type RoleId = Brand<string, 'RoleId'>;
export type PermissionId = Brand<string, 'PermissionId'>;
export type TenantId = Brand<string, 'TenantId'>;
export type SessionId = Brand<string, 'SessionId'>;

// Common Entity Types
export type EntityId = Brand<string, 'EntityId'>;
export type AuditId = Brand<string, 'AuditId'>;
export type VersionId = Brand<string, 'VersionId'>;
export type ReferenceId = Brand<string, 'ReferenceId'>;

// File and Document Types
export type FileId = Brand<string, 'FileId'>;
export type DocumentId = Brand<string, 'DocumentId'>;
export type AttachmentId = Brand<string, 'AttachmentId'>;

// Notification and Communication Types
export type NotificationId = Brand<string, 'NotificationId'>;
export type MessageId = Brand<string, 'MessageId'>;
export type TemplateId = Brand<string, 'TemplateId'>;

// Configuration and Settings Types
export type ConfigId = Brand<string, 'ConfigId'>;
export type SettingId = Brand<string, 'SettingId'>;
export type PreferenceId = Brand<string, 'PreferenceId'>;

// Workflow and Process Types
export type WorkflowId = Brand<string, 'WorkflowId'>;
export type ProcessId = Brand<string, 'ProcessId'>;
export type TaskId = Brand<string, 'TaskId'>;

// Utility functions for creating branded types
export const createUserId = (value: string): UserId => value as UserId;
export const createRoleId = (value: string): RoleId => value as RoleId;
export const createPermissionId = (value: string): PermissionId => value as PermissionId;
export const createTenantId = (value: string): TenantId => value as TenantId;
export const createSessionId = (value: string): SessionId => value as SessionId;
export const createEntityId = (value: string): EntityId => value as EntityId;
export const createAuditId = (value: string): AuditId => value as AuditId;
export const createVersionId = (value: string): VersionId => value as VersionId;
export const createReferenceId = (value: string): ReferenceId => value as ReferenceId;
export const createFileId = (value: string): FileId => value as FileId;
export const createDocumentId = (value: string): DocumentId => value as DocumentId;
export const createAttachmentId = (value: string): AttachmentId => value as AttachmentId;
export const createNotificationId = (value: string): NotificationId => value as NotificationId;
export const createMessageId = (value: string): MessageId => value as MessageId;
export const createTemplateId = (value: string): TemplateId => value as TemplateId;
export const createConfigId = (value: string): ConfigId => value as ConfigId;
export const createSettingId = (value: string): SettingId => value as SettingId;
export const createPreferenceId = (value: string): PreferenceId => value as PreferenceId;
export const createWorkflowId = (value: string): WorkflowId => value as WorkflowId;
export const createProcessId = (value: string): ProcessId => value as ProcessId;
export const createTaskId = (value: string): TaskId => value as TaskId;


