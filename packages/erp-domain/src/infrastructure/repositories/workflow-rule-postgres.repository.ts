import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { WorkflowRule } from '../../core/entities/workflow-rule.entity'
import { WorkflowRuleRepository } from '../../core/repositories/workflow-rule.repository'

@injectable()
export class WorkflowRulePostgresRepository implements WorkflowRuleRepository {
  constructor(private prisma: PrismaClient) {}

  async save(rule: WorkflowRule): Promise<WorkflowRule> {
    const data = {
      id: rule.id,
      triggerEntity: rule.triggerEntity,
      triggerAction: rule.triggerAction,
      targetEntity: rule.targetEntity,
      targetAction: rule.targetAction,
      tenantId: rule.tenantId,
      condition: rule.condition,
      active: rule.active,
      createdAt: rule.createdAt,
      updatedAt: rule.updatedAt
    }

    const saved = await this.prisma.workflowRule.upsert({
      where: { id: rule.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<WorkflowRule | null> {
    const result = await this.prisma.workflowRule.findFirst({
      where: {
        id,
        tenantId
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByTenant(tenantId: string, options?: {
    triggerEntity?: string
    triggerAction?: string
    targetEntity?: string
    targetAction?: string
    active?: boolean
    limit?: number
    offset?: number
  }): Promise<WorkflowRule[]> {
    const where: any = { tenantId }

    if (options?.triggerEntity) where.triggerEntity = options.triggerEntity
    if (options?.triggerAction) where.triggerAction = options.triggerAction
    if (options?.targetEntity) where.targetEntity = options.targetEntity
    if (options?.targetAction) where.targetAction = options.targetAction
    if (options?.active !== undefined) where.active = options.active

    const results = await this.prisma.workflowRule.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findMatchingRules(triggerEntity: string, triggerAction: string, tenantId: string): Promise<WorkflowRule[]> {
    const results = await this.prisma.workflowRule.findMany({
      where: {
        triggerEntity,
        triggerAction,
        active: true,
        tenantId
      },
      orderBy: { createdAt: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(rule: WorkflowRule): Promise<WorkflowRule> {
    const data = {
      triggerEntity: rule.triggerEntity,
      triggerAction: rule.triggerAction,
      targetEntity: rule.targetEntity,
      targetAction: rule.targetAction,
      tenantId: rule.tenantId,
      condition: rule.condition,
      active: rule.active,
      updatedAt: rule.updatedAt
    }

    const updated = await this.prisma.workflowRule.update({
      where: { id: rule.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.workflowRule.delete({
      where: { id }
    })
  }

  async countByTenant(tenantId: string, active?: boolean): Promise<number> {
    const where: any = { tenantId }

    if (active !== undefined) where.active = active

    return this.prisma.workflowRule.count({ where })
  }

  private mapToEntity(data: any): WorkflowRule {
    return new WorkflowRule(
      data.id,
      data.triggerEntity,
      data.triggerAction,
      data.targetEntity,
      data.targetAction,
      data.tenantId,
      data.condition,
      data.active,
      data.createdAt,
      data.updatedAt
    )
  }
}