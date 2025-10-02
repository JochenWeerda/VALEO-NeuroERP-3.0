/**
 * Branded Types for VALEO NeuroERP 3.0
 * Type-safe identifiers using TypeScript branded types
 */
type Brand<K, T> = K & {
    __brand: T;
};
export type UserId = Brand<string, 'UserId'>;
export type RoleId = Brand<string, 'RoleId'>;
export type PermissionId = Brand<string, 'PermissionId'>;
export type TenantId = Brand<string, 'TenantId'>;
export type SessionId = Brand<string, 'SessionId'>;
export type EntityId = Brand<string, 'EntityId'>;
export type AuditId = Brand<string, 'AuditId'>;
export type VersionId = Brand<string, 'VersionId'>;
export type ReferenceId = Brand<string, 'ReferenceId'>;
export type FileId = Brand<string, 'FileId'>;
export type DocumentId = Brand<string, 'DocumentId'>;
export type AttachmentId = Brand<string, 'AttachmentId'>;
export type NotificationId = Brand<string, 'NotificationId'>;
export type MessageId = Brand<string, 'MessageId'>;
export type TemplateId = Brand<string, 'TemplateId'>;
export type ConfigId = Brand<string, 'ConfigId'>;
export type SettingId = Brand<string, 'SettingId'>;
export type PreferenceId = Brand<string, 'PreferenceId'>;
export type WorkflowId = Brand<string, 'WorkflowId'>;
export type ProcessId = Brand<string, 'ProcessId'>;
export type TaskId = Brand<string, 'TaskId'>;
export declare const createUserId: (value: string) => UserId;
export declare const createRoleId: (value: string) => RoleId;
export declare const createPermissionId: (value: string) => PermissionId;
export declare const createTenantId: (value: string) => TenantId;
export declare const createSessionId: (value: string) => SessionId;
export declare const createEntityId: (value: string) => EntityId;
export declare const createAuditId: (value: string) => AuditId;
export declare const createVersionId: (value: string) => VersionId;
export declare const createReferenceId: (value: string) => ReferenceId;
export declare const createFileId: (value: string) => FileId;
export declare const createDocumentId: (value: string) => DocumentId;
export declare const createAttachmentId: (value: string) => AttachmentId;
export declare const createNotificationId: (value: string) => NotificationId;
export declare const createMessageId: (value: string) => MessageId;
export declare const createTemplateId: (value: string) => TemplateId;
export declare const createConfigId: (value: string) => ConfigId;
export declare const createSettingId: (value: string) => SettingId;
export declare const createPreferenceId: (value: string) => PreferenceId;
export declare const createWorkflowId: (value: string) => WorkflowId;
export declare const createProcessId: (value: string) => ProcessId;
export declare const createTaskId: (value: string) => TaskId;
export {};
//# sourceMappingURL=branded-types.d.ts.map