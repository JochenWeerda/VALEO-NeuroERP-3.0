import { WorkflowRule } from '../entities/workflow-rule.entity'

export interface WorkflowRuleRepository {
  save(rule: WorkflowRule): Promise<WorkflowRule>
  findById(id: string, tenantId: string): Promise<WorkflowRule | null>
  findByTenant(tenantId: string, options?: {
    triggerEntity?: string
    triggerAction?: string
    targetEntity?: string
    targetAction?: string
    active?: boolean
    limit?: number
    offset?: number
  }): Promise<WorkflowRule[]>
  findMatchingRules(triggerEntity: string, triggerAction: string, tenantId: string): Promise<WorkflowRule[]>
  update(rule: WorkflowRule): Promise<WorkflowRule>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, active?: boolean): Promise<number>
}