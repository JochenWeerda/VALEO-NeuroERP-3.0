import { AuditLog } from '../entities/workflow-rule.entity'

export interface AuditLogRepository {
  save(log: AuditLog): Promise<AuditLog>
  findById(id: string, tenantId: string): Promise<AuditLog | null>
  findByEntity(entity: string, entityId: string, tenantId: string): Promise<AuditLog[]>
  findByActor(actorId: string, tenantId: string, options?: {
    limit?: number
    offset?: number
  }): Promise<AuditLog[]>
  findByTenant(tenantId: string, options?: {
    entity?: string
    entityId?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
    limit?: number
    offset?: number
  }): Promise<AuditLog[]>
  findRecent(tenantId: string, limit?: number): Promise<AuditLog[]>
  countByTenant(tenantId: string, options?: {
    entity?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
  }): Promise<number>
}