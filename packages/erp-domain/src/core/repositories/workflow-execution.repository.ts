import { WorkflowExecution, WorkflowExecutionStatus } from '../entities/workflow-rule.entity'

export interface WorkflowExecutionRepository {
  save(execution: WorkflowExecution): Promise<WorkflowExecution>
  findById(id: string, tenantId: string): Promise<WorkflowExecution | null>
  findByRule(ruleId: string, tenantId: string): Promise<WorkflowExecution[]>
  findByTenant(tenantId: string, options?: {
    status?: WorkflowExecutionStatus
    ruleId?: string
    actorId?: string
    limit?: number
    offset?: number
  }): Promise<WorkflowExecution[]>
  findRunning(tenantId: string): Promise<WorkflowExecution[]>
  findFailed(tenantId: string): Promise<WorkflowExecution[]>
  update(execution: WorkflowExecution): Promise<WorkflowExecution>
  delete(id: string, tenantId: string): Promise<void>
  countByTenant(tenantId: string, status?: WorkflowExecutionStatus): Promise<number>
}