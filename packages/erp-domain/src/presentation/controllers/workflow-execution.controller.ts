import { Request, Response } from 'express'
import { WorkflowExecutionService } from '../../application/services/workflow-execution.service'
import { CreateWorkflowExecutionData } from '../../application/services/workflow-execution.service'
import { WorkflowExecutionStatus } from '../../core/entities/workflow-rule.entity'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError, respondDomainMutationError } from '../utils/request-context'

export class WorkflowExecutionController {
  constructor(private workflowExecutionService: WorkflowExecutionService) {}

  async createWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const data: CreateWorkflowExecutionData = {
        ruleId: req.body.ruleId,
        triggerEntity: req.body.triggerEntity,
        triggerAction: req.body.triggerAction,
        targetEntity: req.body.targetEntity,
        targetAction: req.body.targetAction,
        actorId,
        tenantId
      }

      const execution = await this.workflowExecutionService.createWorkflowExecution(data)

      res.status(201).json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Workflow-Execution:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

      const execution = await this.workflowExecutionService.getWorkflowExecutionById(id as string, tenantId)

      if (!execution) {
        res.status(404).json({
          success: false,
          error: 'Workflow-Execution nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Execution:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        status: req.query.status as any,
        ruleId: req.query.ruleId as string,
        actorId: req.query.actorId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.workflowExecutionService.getWorkflowExecutionsByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Executions:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getWorkflowExecutionsByRule(req: Request, res: Response): Promise<void> {
    try {
      const { ruleId } = req.params
      const tenantId = resolveTenantId(req)

      const executions = await this.workflowExecutionService.getWorkflowExecutionsByRule(ruleId as string, tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Executions zur Regel:', error)
      respondControllerError(res, error, 500)
    }
  }

  async startWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const execution = await this.workflowExecutionService.startWorkflowExecution(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Starten der Workflow-Execution:', error)
      respondDomainMutationError(res, error)
    }
  }

  async succeedWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const execution = await this.workflowExecutionService.succeedWorkflowExecution(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim erfolgreichen Abschließen der Workflow-Execution:', error)
      respondDomainMutationError(res, error)
    }
  }

  async failWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)
      const errorMessage = req.body.errorMessage || 'Unbekannter Fehler'

      const execution = await this.workflowExecutionService.failWorkflowExecution(id as string, tenantId, actorId, errorMessage)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Fehlschlagen der Workflow-Execution:', error)
      respondDomainMutationError(res, error)
    }
  }

  async retryWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const execution = await this.workflowExecutionService.retryWorkflowExecution(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Wiederholen der Workflow-Execution:', error)
      respondDomainMutationError(res, error)
    }
  }

  async getRunningWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const executions = await this.workflowExecutionService.getRunningWorkflowExecutions(tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der laufenden Workflow-Executions:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getFailedWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const executions = await this.workflowExecutionService.getFailedWorkflowExecutions(tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der fehlgeschlagenen Workflow-Executions:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getWorkflowExecutionStats(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)

      const stats = await this.workflowExecutionService.getWorkflowExecutionStats(tenantId)

      res.json({
        success: true,
        data: stats
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Execution-Statistiken:', error)
      respondControllerError(res, error, 500)
    }
  }
}
