import { injectable } from 'inversify'
import { PrismaClient } from '@prisma/client'
import { WorkflowExecution, WorkflowExecutionStatus } from '../../core/entities/workflow-rule.entity'
import { WorkflowExecutionRepository } from '../../core/repositories/workflow-execution.repository'

@injectable()
export class WorkflowExecutionPostgresRepository implements WorkflowExecutionRepository {
  constructor(private prisma: PrismaClient) {}

  async save(execution: WorkflowExecution): Promise<WorkflowExecution> {
    const data = {
      id: execution.id,
      ruleId: execution.ruleId,
      triggerEntity: execution.triggerEntity,
      triggerAction: execution.triggerAction,
      targetEntity: execution.targetEntity,
      targetAction: execution.targetAction,
      status: execution.status,
      startedAt: execution.startedAt,
      completedAt: execution.completedAt,
      errorMessage: execution.errorMessage,
      actorId: execution.actorId,
      tenantId: execution.tenantId,
      createdAt: execution.createdAt
    }

    const saved = await this.prisma.workflowExecution.upsert({
      where: { id: execution.id },
      update: data,
      create: data
    })

    return this.mapToEntity(saved)
  }

  async findById(id: string, tenantId: string): Promise<WorkflowExecution | null> {
    const result = await this.prisma.workflowExecution.findFirst({
      where: {
        id,
        tenantId
      }
    })

    return result ? this.mapToEntity(result) : null
  }

  async findByRule(ruleId: string, tenantId: string): Promise<WorkflowExecution[]> {
    const results = await this.prisma.workflowExecution.findMany({
      where: {
        ruleId,
        tenantId
      },
      orderBy: { createdAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async findByTenant(tenantId: string, options?: {
    status?: WorkflowExecutionStatus
    ruleId?: string
    actorId?: string
    limit?: number
    offset?: number
  }): Promise<WorkflowExecution[]> {
    const where: any = { tenantId }

    if (options?.status) where.status = options.status
    if (options?.ruleId) where.ruleId = options.ruleId
    if (options?.actorId) where.actorId = options.actorId

    const results = await this.prisma.workflowExecution.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: options?.limit || 50,
      skip: options?.offset || 0
    })

    return results.map(this.mapToEntity)
  }

  async findRunning(tenantId: string): Promise<WorkflowExecution[]> {
    const results = await this.prisma.workflowExecution.findMany({
      where: {
        tenantId,
        status: WorkflowExecutionStatus.RUNNING
      },
      orderBy: { startedAt: 'asc' }
    })

    return results.map(this.mapToEntity)
  }

  async findFailed(tenantId: string): Promise<WorkflowExecution[]> {
    const results = await this.prisma.workflowExecution.findMany({
      where: {
        tenantId,
        status: WorkflowExecutionStatus.FAILED
      },
      orderBy: { completedAt: 'desc' }
    })

    return results.map(this.mapToEntity)
  }

  async update(execution: WorkflowExecution): Promise<WorkflowExecution> {
    const data = {
      ruleId: execution.ruleId,
      triggerEntity: execution.triggerEntity,
      triggerAction: execution.triggerAction,
      targetEntity: execution.targetEntity,
      targetAction: execution.targetAction,
      status: execution.status,
      startedAt: execution.startedAt,
      completedAt: execution.completedAt,
      errorMessage: execution.errorMessage,
      actorId: execution.actorId,
      tenantId: execution.tenantId,
      createdAt: execution.createdAt
    }

    const updated = await this.prisma.workflowExecution.update({
      where: { id: execution.id },
      data
    })

    return this.mapToEntity(updated)
  }

  async delete(id: string, tenantId: string): Promise<void> {
    await this.prisma.workflowExecution.delete({
      where: { id }
    })
  }

  async countByTenant(tenantId: string, status?: WorkflowExecutionStatus): Promise<number> {
    const where: any = { tenantId }

    if (status) where.status = status

    return this.prisma.workflowExecution.count({ where })
  }

  private mapToEntity(data: any): WorkflowExecution {
    return new WorkflowExecution(
      data.id,
      data.ruleId,
      data.triggerEntity,
      data.triggerAction,
      data.targetEntity,
      data.targetAction,
      data.status,
      data.startedAt,
      data.actorId,
      data.tenantId,
      data.completedAt,
      data.errorMessage,
      data.createdAt
    )
  }
}