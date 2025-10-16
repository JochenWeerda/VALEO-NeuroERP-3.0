import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { AuditLog } from '../../core/entities/workflow-rule.entity'
import { AuditLogRepository } from '../../core/repositories/audit-log.repository'

@injectable()
export class AuditLogPostgresRepository implements AuditLogRepository {
  constructor(private prisma: PrismaClient) {}

  async save(log: AuditLog): Promise<AuditLog> {
    const data = {
      id: log.id,
      actorId: log.actorId,
      entity: log.entity,
      entityId: log.entityId,
      action: log.action,
      before: log.before,
      after: log.after,
      timestamp: log.timestamp,
      tenantId: log.tenantId,
      ipAddress: log.ipAddress,
      userAgent: log.userAgent
    }

    const saved = await this.prisma.auditLog.upsert({
      where: { id: log.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<AuditLog | null> {
    const result = await this.prisma.auditLog.findFirst({
      where: {
        id,
        tenantId
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByEntity(entity: string, entityId: string, tenantId: string): Promise<AuditLog[]> {
    const results = await this.prisma.auditLog.findMany({
      where: {
        entity,
        entityId,
        tenantId
      },
      orderBy: { timestamp: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async findByActor(actorId: string, tenantId: string, options?: {
    limit?: number
    offset?: number
  }): Promise<AuditLog[]> {
    const results = await this.prisma.auditLog.findMany({
      where: {
        actorId,
        tenantId
      },
      orderBy: { timestamp: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findByTenant(tenantId: string, options?: {
    entity?: string
    entityId?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
    limit?: number
    offset?: number
  }): Promise<AuditLog[]> {
    const where: any = {
      tenantId
    }

    if (options?.entity) where.entity = options.entity
    if (options?.entityId) where.entityId = options.entityId
    if (options?.actorId) where.actorId = options.actorId
    if (options?.action) where.action = options.action

    if (options?.fromDate || options?.toDate) {
      where.timestamp = {}
      if (options.fromDate) where.timestamp.gte = options.fromDate
      if (options.toDate) where.timestamp.lte = options.toDate
    }

    const results = await this.prisma.auditLog.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findRecent(tenantId: string, limit: number = 100): Promise<AuditLog[]> {
    const results = await this.prisma.auditLog.findMany({
      where: { tenantId },
      orderBy: { timestamp: 'desc' },
      take: limit
    })

    return results.map(this.mapToEntity)
  }

  async countByTenant(tenantId: string, options?: {
    entity?: string
    actorId?: string
    action?: string
    fromDate?: Date
    toDate?: Date
  }): Promise<number> {
    const where: any = { tenantId }

    if (options?.entity) where.entity = options.entity
    if (options?.actorId) where.actorId = options.actorId
    if (options?.action) where.action = options.action

    if (options?.fromDate || options?.toDate) {
      where.timestamp = {}
      if (options.fromDate) where.timestamp.gte = options.fromDate
      if (options.toDate) where.timestamp.lte = options.toDate
    }

    return this.prisma.auditLog.count({ where })
  }

  private mapToEntity(data: any): AuditLog {
    return new AuditLog(
      data.id,
      data.actorId,
      data.entity,
      data.entityId,
      data.action,
      data.tenantId,
      data.before,
      data.after,
      data.timestamp,
      data.ipAddress,
      data.userAgent
    )
  }
}