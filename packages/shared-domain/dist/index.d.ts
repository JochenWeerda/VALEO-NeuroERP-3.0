/**
 * VALEO NeuroERP 3.0 - Shared Domain
 * Clean Architecture Implementation
 *
 * This package provides shared domain functionality across all domains,
 * including common entities, value objects, repositories, and services.
 */
export * from './domain/index.js';
export * from './application/index.js';
export * from './infrastructure/index.js';
export type { UserId, RoleId, PermissionId, TenantId, SessionId, EntityId, AuditId, VersionId, ReferenceId, FileId, DocumentId, AttachmentId, NotificationId, MessageId, TemplateId, ConfigId, SettingId, PreferenceId, WorkflowId, ProcessId, TaskId } from './domain/value-objects/branded-types.js';
export type { User, UserProps } from './domain/entities/user.js';
export type { UserDto, CreateUserDto, UpdateUserDto, UserSearchDto, PaginationDto, UserListResponseDto, UserStatsDto } from './application/dto/user-dto.js';
export type { UserRepository } from './domain/interfaces/user-repository.js';
export type { Repository, QueryBuilder, PaginationOptions, PaginatedResult, UnitOfWork, TransactionManager, RepositoryFactory, AuditRepository, AuditEntry, VersionHistory, QueryOperator } from './domain/interfaces/repository.js';
//# sourceMappingURL=index.d.ts.map