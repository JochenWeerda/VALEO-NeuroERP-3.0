import { inject, injectable } from 'inversify'
import { AuditLog } from '../../core/entities/workflow-rule.entity'
import { AuditLogRepository } from '../../core/repositories/audit-log.repository'

export interface AuditEntry {
  id?: string
  actorId: string
  entity: string
  entityId: string
  action: string
  before?: unknown
  after?: unknown
  timestamp?: Date
  tenantId: string
  ipAddress?: string
  userAgent?: string
}

@injectable()
export class AuditService {
  constructor(@inject('AuditLogRepository') private readonly auditLogRepository: AuditLogRepository) {}

  async log(entry: AuditEntry): Promise<void> {
    const auditLog = AuditLog.create({
      actorId: entry.actorId,
      entity: entry.entity,
      entityId: entry.entityId,
      action: entry.action,
      before: entry.before,
      after: entry.after,
      tenantId: entry.tenantId,
      ipAddress: entry.ipAddress,
      userAgent: entry.userAgent,
    })

    await this.auditLogRepository.save(auditLog)
  }

  async getEntityHistory(entity: string, entityId: string, tenantId: string): Promise<AuditLog[]> {
    return this.auditLogRepository.findByEntity(entity, entityId, tenantId)
  }

  async getUserActivity(actorId: string, tenantId: string, limit = 100): Promise<AuditLog[]> {
    return this.auditLogRepository.findByActor(actorId, tenantId, { limit, offset: 0 })
  }
}
