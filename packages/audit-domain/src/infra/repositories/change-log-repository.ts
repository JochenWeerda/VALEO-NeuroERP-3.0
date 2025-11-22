/**
 * Change Log Repository
 * In-memory implementation (would be replaced with database in production)
 */

import { ChangeLog } from '../../domain/entities/change-log';
import {
  ChangeLogRepository as IChangeLogRepository,
  ChangeLogFilters,
} from '../../domain/services/change-log-service';

export class ChangeLogRepository implements IChangeLogRepository {
  private changeLogs: Map<string, ChangeLog> = new Map();

  async create(changeLog: ChangeLog): Promise<ChangeLog> {
    this.changeLogs.set(changeLog.id, changeLog);
    return changeLog;
  }

  async findById(id: string): Promise<ChangeLog | null> {
    return this.changeLogs.get(id) || null;
  }

  async findByEntity(
    entityType: string,
    entityId: string,
    filters?: ChangeLogFilters
  ): Promise<ChangeLog[]> {
    let logs = Array.from(this.changeLogs.values()).filter(
      log => log.entityType === entityType && log.entityId === entityId
    );

    if (filters) {
      logs = this.applyFilters(logs, filters);
    }

    return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  async findMany(filters: ChangeLogFilters): Promise<ChangeLog[]> {
    let logs = Array.from(this.changeLogs.values());

    logs = this.applyFilters(logs, filters);

    return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  async count(filters?: ChangeLogFilters): Promise<number> {
    if (!filters) {
      return this.changeLogs.size;
    }

    const logs = this.applyFilters(Array.from(this.changeLogs.values()), filters);
    return logs.length;
  }

  private applyFilters(logs: ChangeLog[], filters: ChangeLogFilters): ChangeLog[] {
    let filtered = logs;

    if (filters.tenantId) {
      filtered = filtered.filter(log => log.tenantId === filters.tenantId);
    }

    if (filters.entityType) {
      filtered = filtered.filter(log => log.entityType === filters.entityType);
    }

    if (filters.entityId) {
      filtered = filtered.filter(log => log.entityId === filters.entityId);
    }

    if (filters.action) {
      filtered = filtered.filter(log => log.action === filters.action);
    }

    if (filters.userId) {
      filtered = filtered.filter(log => log.userId === filters.userId);
    }

    if (filters.dateFrom) {
      filtered = filtered.filter(log => log.timestamp >= filters.dateFrom!);
    }

    if (filters.dateTo) {
      filtered = filtered.filter(log => log.timestamp <= filters.dateTo!);
    }

    if (filters.hasReason !== undefined) {
      if (filters.hasReason) {
        filtered = filtered.filter(log => log.reason !== undefined && log.reason.length > 0);
      } else {
        filtered = filtered.filter(log => !log.reason || log.reason.length === 0);
      }
    }

    return filtered;
  }
}

