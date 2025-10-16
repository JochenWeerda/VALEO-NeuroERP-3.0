import { inject, injectable } from 'inversify'
import { WorkflowExecution, WorkflowExecutionStatus } from '../../core/entities/workflow-rule.entity'
import { WorkflowExecutionRepository } from '../../core/repositories/workflow-execution.repository'
import { AuditService } from './audit.service'

export interface CreateWorkflowExecutionData {
  ruleId: string
  triggerEntity: string
  triggerAction: string
  targetEntity: string
  targetAction: string
  actorId: string
  tenantId: string
}

export class WorkflowExecutionService {
  constructor(
    private repository: WorkflowExecutionRepository,
    private auditService: AuditService
  ) {}

  async createWorkflowExecution(data: CreateWorkflowExecutionData): Promise<WorkflowExecution> {
    // Validierung
    this.validateWorkflowExecutionData(data)

    // Workflow-Execution erstellen
    const execution = WorkflowExecution.create(data)

    // Speichern
    const savedExecution = await this.repository.save(execution)

    // Audit-Log
    await this.auditService.log({
      actorId: data.actorId,
      entity: 'WorkflowExecution',
      entityId: savedExecution.id,
      action: 'CREATE',
      after: savedExecution,
      tenantId: data.tenantId
    })

    return savedExecution
  }

  async getWorkflowExecutionById(id: string, tenantId: string): Promise<WorkflowExecution | null> {
    return this.repository.findById(id, tenantId)
  }

  async getWorkflowExecutionsByTenant(tenantId: string, options?: {
    status?: WorkflowExecutionStatus
    ruleId?: string
    actorId?: string
    limit?: number
    offset?: number
  }): Promise<WorkflowExecution[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getWorkflowExecutionsByRule(ruleId: string, tenantId: string): Promise<WorkflowExecution[]> {
    return this.repository.findByRule(ruleId, tenantId)
  }

  async startWorkflowExecution(id: string, tenantId: string, actorId: string): Promise<WorkflowExecution> {
    const execution = await this.repository.findById(id, tenantId)
    if (!execution) {
      throw new Error('Workflow-Execution nicht gefunden')
    }

    if (execution.status !== WorkflowExecutionStatus.PENDING) {
      throw new Error('Nur ausstehende Workflow-Executions können gestartet werden')
    }

    const startedExecution = execution.start()
    const saved = await this.repository.update(startedExecution)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowExecution',
      entityId: id,
      action: 'START',
      before: execution,
      after: saved,
      tenantId
    })

    return saved
  }

  async succeedWorkflowExecution(id: string, tenantId: string, actorId: string): Promise<WorkflowExecution> {
    const execution = await this.repository.findById(id, tenantId)
    if (!execution) {
      throw new Error('Workflow-Execution nicht gefunden')
    }

    if (execution.status !== WorkflowExecutionStatus.RUNNING) {
      throw new Error('Nur laufende Workflow-Executions können erfolgreich abgeschlossen werden')
    }

    const succeededExecution = execution.succeed()
    const saved = await this.repository.update(succeededExecution)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowExecution',
      entityId: id,
      action: 'SUCCEED',
      before: execution,
      after: saved,
      tenantId
    })

    return saved
  }

  async failWorkflowExecution(id: string, tenantId: string, actorId: string, errorMessage: string): Promise<WorkflowExecution> {
    const execution = await this.repository.findById(id, tenantId)
    if (!execution) {
      throw new Error('Workflow-Execution nicht gefunden')
    }

    if (execution.status !== WorkflowExecutionStatus.RUNNING) {
      throw new Error('Nur laufende Workflow-Executions können fehlschlagen')
    }

    const failedExecution = execution.fail(errorMessage)
    const saved = await this.repository.update(failedExecution)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowExecution',
      entityId: id,
      action: 'FAIL',
      before: execution,
      after: saved,
      tenantId
    })

    return saved
  }

  async getRunningWorkflowExecutions(tenantId: string): Promise<WorkflowExecution[]> {
    return this.repository.findRunning(tenantId)
  }

  async getFailedWorkflowExecutions(tenantId: string): Promise<WorkflowExecution[]> {
    return this.repository.findFailed(tenantId)
  }

  async retryWorkflowExecution(id: string, tenantId: string, actorId: string): Promise<WorkflowExecution> {
    const execution = await this.repository.findById(id, tenantId)
    if (!execution) {
      throw new Error('Workflow-Execution nicht gefunden')
    }

    if (execution.status !== WorkflowExecutionStatus.FAILED) {
      throw new Error('Nur fehlgeschlagene Workflow-Executions können wiederholt werden')
    }

    // Neue Execution mit denselben Parametern erstellen
    const retryData: CreateWorkflowExecutionData = {
      ruleId: execution.ruleId,
      triggerEntity: execution.triggerEntity,
      triggerAction: execution.triggerAction,
      targetEntity: execution.targetEntity,
      targetAction: execution.targetAction,
      actorId,
      tenantId
    }

    return this.createWorkflowExecution(retryData)
  }

  async getWorkflowExecutionStats(tenantId: string): Promise<{
    total: number
    pending: number
    running: number
    succeeded: number
    failed: number
    averageDuration: number | null
  }> {
    const allExecutions = await this.repository.findByTenant(tenantId)

    const stats = {
      total: allExecutions.length,
      pending: allExecutions.filter(e => e.status === WorkflowExecutionStatus.PENDING).length,
      running: allExecutions.filter(e => e.status === WorkflowExecutionStatus.RUNNING).length,
      succeeded: allExecutions.filter(e => e.status === WorkflowExecutionStatus.SUCCESS).length,
      failed: allExecutions.filter(e => e.status === WorkflowExecutionStatus.FAILED).length,
      averageDuration: null as number | null
    }

    // Berechne durchschnittliche Dauer für abgeschlossene Executions
    const completedExecutions = allExecutions.filter(e => e.isCompleted() && e.getDuration() !== null)
    if (completedExecutions.length > 0) {
      const totalDuration = completedExecutions.reduce((sum, e) => sum + (e.getDuration() || 0), 0)
      stats.averageDuration = totalDuration / completedExecutions.length
    }

    return stats
  }

  private validateWorkflowExecutionData(data: CreateWorkflowExecutionData): void {
    if (!data.ruleId.trim()) {
      throw new Error('Rule-ID ist erforderlich')
    }

    if (!data.triggerEntity.trim()) {
      throw new Error('Trigger-Entity ist erforderlich')
    }

    if (!data.triggerAction.trim()) {
      throw new Error('Trigger-Action ist erforderlich')
    }

    if (!data.targetEntity.trim()) {
      throw new Error('Target-Entity ist erforderlich')
    }

    if (!data.targetAction.trim()) {
      throw new Error('Target-Action ist erforderlich')
    }
  }
}