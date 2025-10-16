import { inject, injectable } from 'inversify'
import { AuditLog } from '../../core/entities/workflow-rule.entity'
import { AuditLogRepository } from '../../core/repositories/audit-log.repository'

export interface LogAuditData {
  actorId: string
  entity: string
  entityId: string
  action: string
  before?: any
  after?: any
  tenantId: string
  ipAddress?: string
  userAgent?: string
}

export class AuditLogService {
  constructor(
    private repository: AuditLogRepository
  ) {}

  async log(data: LogAuditData): Promise<AuditLog> {
    const auditLog = AuditLog.create(data)
    return this.repository.save(auditLog)
  }

  async getAuditLogsByEntity(entity: string, entityId: string, tenantId: string): Promise<AuditLog[]> {
    return this.repository.findByEntity(entity, entityId, tenantId)
  }

  async getAuditLogsByActor(actorId: string, tenantId: string, options?: {
    limit?: number
    offset?: number
  }): Promise<AuditLog[]> {
    return this.repository.findByActor(actorId, tenantId, options)
  }

  async getAuditLogsByTenant(tenantId: string, options?: {
    entity?: string
    entityId?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
    limit?: number
    offset?: number
  }): Promise<AuditLog[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getRecentAuditLogs(tenantId: string, limit: number = 100): Promise<AuditLog[]> {
    return this.repository.findRecent(tenantId, limit)
  }

  async getAuditLogCount(tenantId: string, options?: {
    entity?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
  }): Promise<number> {
    return this.repository.countByTenant(tenantId, options)
  }

  async getAuditTrail(entity: string, entityId: string, tenantId: string): Promise<AuditLog[]> {
    const logs = await this.repository.findByEntity(entity, entityId, tenantId)

    // Sortiere nach Timestamp (älteste zuerst für Timeline)
    return logs.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  }

  async getUserActivityReport(actorId: string, tenantId: string, fromDate: Date, toDate: Date): Promise<{
    totalActions: number
    actionsByType: Record<string, number>
    actionsByEntity: Record<string, number>
    logs: AuditLog[]
  }> {
    const logs = await this.repository.findByTenant(tenantId, {
      actorId,
      fromDate,
      toDate
    })

    const actionsByType: Record<string, number> = {}
    const actionsByEntity: Record<string, number> = {}

    for (const log of logs) {
      actionsByType[log.action] = (actionsByType[log.action] || 0) + 1
      actionsByEntity[log.entity] = (actionsByEntity[log.entity] || 0) + 1
    }

    return {
      totalActions: logs.length,
      actionsByType,
      actionsByEntity,
      logs
    }
  }

  async getComplianceReport(tenantId: string, fromDate: Date, toDate: Date): Promise<{
    totalLogs: number
    criticalActions: AuditLog[]
    dataModifications: AuditLog[]
    accessLogs: AuditLog[]
  }> {
    const allLogs = await this.repository.findByTenant(tenantId, {
      fromDate,
      toDate
    })

    // Kategorisiere Logs nach Compliance-Relevanz
    const criticalActions = allLogs.filter(log =>
      ['DELETE', 'ADMIN_ACCESS', 'PERMISSION_CHANGE'].includes(log.action)
    )

    const dataModifications = allLogs.filter(log =>
      ['CREATE', 'UPDATE', 'DELETE'].includes(log.action)
    )

    const accessLogs = allLogs.filter(log =>
      ['LOGIN', 'LOGOUT', 'ACCESS_DENIED'].includes(log.action)
    )

    return {
      totalLogs: allLogs.length,
      criticalActions,
      dataModifications,
      accessLogs
    }
  }
}