/**
 * Change Log Service
 * Service for managing change logs and audit trails
 */

import { ChangeLog, ChangeLogEntity, CreateChangeLogInput } from '../entities/change-log';

export interface ChangeLogRepository {
  create(changeLog: ChangeLog): Promise<ChangeLog>;
  findById(id: string): Promise<ChangeLog | null>;
  findByEntity(
    entityType: string,
    entityId: string,
    filters?: ChangeLogFilters
  ): Promise<ChangeLog[]>;
  findMany(filters: ChangeLogFilters): Promise<ChangeLog[]>;
  count(filters?: ChangeLogFilters): Promise<number>;
}

export interface ChangeLogFilters {
  tenantId?: string;
  entityType?: string;
  entityId?: string;
  action?: string;
  userId?: string;
  dateFrom?: Date;
  dateTo?: Date;
  hasReason?: boolean;
}

export interface ChangeLogServiceDependencies {
  changeLogRepository: ChangeLogRepository;
}

export class ChangeLogService {
  constructor(private deps: ChangeLogServiceDependencies) {}

  /**
   * Create a change log entry
   */
  async logChange(input: CreateChangeLogInput): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.create(input);
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log CREATE action
   */
  async logCreate(
    entityType: string,
    entityId: string,
    newValue: Record<string, any>,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForCreate(
      entityType,
      entityId,
      newValue,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log UPDATE action
   */
  async logUpdate(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    newValue: Record<string, any>,
    userId: string,
    tenantId: string,
    options?: {
      reason?: string;
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForUpdate(
      entityType,
      entityId,
      oldValue,
      newValue,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log DELETE action
   */
  async logDelete(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForDelete(
      entityType,
      entityId,
      oldValue,
      reason,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log CANCEL action
   */
  async logCancel(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForCancel(
      entityType,
      entityId,
      oldValue,
      reason,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log AMEND action
   */
  async logAmend(
    entityType: string,
    entityId: string,
    oldValue: Record<string, any>,
    newValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForAmend(
      entityType,
      entityId,
      oldValue,
      newValue,
      reason,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Log RESTORE action
   */
  async logRestore(
    entityType: string,
    entityId: string,
    newValue: Record<string, any>,
    reason: string,
    userId: string,
    tenantId: string,
    options?: {
      userName?: string;
      userEmail?: string;
      ipAddress?: string;
      userAgent?: string;
      metadata?: Record<string, any>;
    }
  ): Promise<ChangeLog> {
    const changeLog = ChangeLogEntity.createForRestore(
      entityType,
      entityId,
      newValue,
      reason,
      userId,
      tenantId,
      options
    );
    return await this.deps.changeLogRepository.create(changeLog);
  }

  /**
   * Get change log by ID
   */
  async getChangeLog(id: string): Promise<ChangeLog | null> {
    return await this.deps.changeLogRepository.findById(id);
  }

  /**
   * Get audit trail for an entity
   */
  async getAuditTrail(
    entityType: string,
    entityId: string,
    filters?: ChangeLogFilters
  ): Promise<ChangeLog[]> {
    return await this.deps.changeLogRepository.findByEntity(
      entityType,
      entityId,
      filters
    );
  }

  /**
   * Get change logs with filters
   */
  async getChangeLogs(filters: ChangeLogFilters): Promise<ChangeLog[]> {
    return await this.deps.changeLogRepository.findMany(filters);
  }

  /**
   * Count change logs
   */
  async countChangeLogs(filters?: ChangeLogFilters): Promise<number> {
    return await this.deps.changeLogRepository.count(filters);
  }
}

