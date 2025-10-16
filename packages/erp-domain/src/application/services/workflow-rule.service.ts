import { inject, injectable } from 'inversify'
import { WorkflowRule } from '../../core/entities/workflow-rule.entity'
import { WorkflowRuleRepository } from '../../core/repositories/workflow-rule.repository'
import { AuditService } from './audit.service'

export interface CreateWorkflowRuleData {
  triggerEntity: string
  triggerAction: string
  targetEntity: string
  targetAction: string
  condition?: string
  active?: boolean
  tenantId: string
}

export interface UpdateWorkflowRuleData {
  triggerEntity?: string
  triggerAction?: string
  targetEntity?: string
  targetAction?: string
  condition?: string
  active?: boolean
}

export class WorkflowRuleService {
  constructor(
    private repository: WorkflowRuleRepository,
    private auditService: AuditService
  ) {}

  async createWorkflowRule(data: CreateWorkflowRuleData): Promise<WorkflowRule> {
    // Validierung
    this.validateWorkflowRuleData(data)

    // Workflow-Regel erstellen
    const rule = WorkflowRule.create(data)

    // Speichern
    const savedRule = await this.repository.save(rule)

    // Audit-Log
    await this.auditService.log({
      actorId: 'system', // TODO: Aus Context holen
      entity: 'WorkflowRule',
      entityId: savedRule.id,
      action: 'CREATE',
      after: savedRule,
      tenantId: data.tenantId
    })

    return savedRule
  }

  async getWorkflowRuleById(id: string, tenantId: string): Promise<WorkflowRule | null> {
    return this.repository.findById(id, tenantId)
  }

  async getWorkflowRulesByTenant(tenantId: string, options?: {
    triggerEntity?: string
    triggerAction?: string
    targetEntity?: string
    targetAction?: string
    active?: boolean
    limit?: number
    offset?: number
  }): Promise<WorkflowRule[]> {
    return this.repository.findByTenant(tenantId, options)
  }

  async getMatchingRules(triggerEntity: string, triggerAction: string, tenantId: string): Promise<WorkflowRule[]> {
    return this.repository.findMatchingRules(triggerEntity, triggerAction, tenantId)
  }

  async activateWorkflowRule(id: string, tenantId: string, actorId: string): Promise<WorkflowRule> {
    const rule = await this.repository.findById(id, tenantId)
    if (!rule) {
      throw new Error('Workflow-Regel nicht gefunden')
    }

    if (rule.active) {
      throw new Error('Workflow-Regel ist bereits aktiv')
    }

    const activatedRule = rule.activate()
    const saved = await this.repository.update(activatedRule)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowRule',
      entityId: id,
      action: 'ACTIVATE',
      before: rule,
      after: saved,
      tenantId
    })

    return saved
  }

  async deactivateWorkflowRule(id: string, tenantId: string, actorId: string): Promise<WorkflowRule> {
    const rule = await this.repository.findById(id, tenantId)
    if (!rule) {
      throw new Error('Workflow-Regel nicht gefunden')
    }

    if (!rule.active) {
      throw new Error('Workflow-Regel ist bereits inaktiv')
    }

    const deactivatedRule = rule.deactivate()
    const saved = await this.repository.update(deactivatedRule)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowRule',
      entityId: id,
      action: 'DEACTIVATE',
      before: rule,
      after: saved,
      tenantId
    })

    return saved
  }

  async updateWorkflowRule(id: string, tenantId: string, data: UpdateWorkflowRuleData, actorId: string): Promise<WorkflowRule> {
    const rule = await this.repository.findById(id, tenantId)
    if (!rule) {
      throw new Error('Workflow-Regel nicht gefunden')
    }

    // TODO: Workflow-Regel mit neuen Daten aktualisieren
    // const updatedRule = rule.update(data)
    // const saved = await this.repository.update(updatedRule)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowRule',
      entityId: id,
      action: 'UPDATE',
      before: rule,
      after: rule, // TODO: updatedRule
      tenantId
    })

    return rule // TODO: saved
  }

  async deleteWorkflowRule(id: string, tenantId: string, actorId: string): Promise<void> {
    const rule = await this.repository.findById(id, tenantId)
    if (!rule) {
      throw new Error('Workflow-Regel nicht gefunden')
    }

    await this.repository.delete(id, tenantId)

    // Audit-Log
    await this.auditService.log({
      actorId,
      entity: 'WorkflowRule',
      entityId: id,
      action: 'DELETE',
      before: rule,
      tenantId
    })
  }

  async executeWorkflowRules(triggerEntity: string, triggerAction: string, tenantId: string, data?: any): Promise<{
    executedRules: WorkflowRule[]
    failedRules: { rule: WorkflowRule; error: string }[]
  }> {
    const matchingRules = await this.repository.findMatchingRules(triggerEntity, triggerAction, tenantId)

    const executedRules: WorkflowRule[] = []
    const failedRules: { rule: WorkflowRule; error: string }[] = []

    for (const rule of matchingRules) {
      try {
        // Bedingung prüfen
        if (!rule.evaluateCondition(data)) {
          continue
        }

        // TODO: Workflow-Aktion ausführen
        // await this.executeWorkflowAction(rule, data)

        executedRules.push(rule)
      } catch (error) {
        failedRules.push({
          rule,
          error: error instanceof Error ? error.message : 'Unbekannter Fehler'
        })
      }
    }

    return { executedRules, failedRules }
  }

  private validateWorkflowRuleData(data: CreateWorkflowRuleData): void {
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