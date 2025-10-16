import { Request, Response } from 'express'
import { WorkflowExecutionService } from '../../application/services/workflow-execution.service'
import { CreateWorkflowExecutionData } from '../../application/services/workflow-execution.service'
import { WorkflowExecutionStatus } from '../../core/entities/workflow-rule.entity'

export class WorkflowExecutionController {
  constructor(private workflowExecutionService: WorkflowExecutionService) {}

  async createWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

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
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const execution = await this.workflowExecutionService.getWorkflowExecutionById(id, tenantId)

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
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        status: req.query.status as any,
        ruleId: req.query.ruleId as string,
        actorId: req.query.actorId as string,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const executions = await this.workflowExecutionService.getWorkflowExecutionsByTenant(tenantId, options)

      res.json({
        success: true,
        data: executions,
        total: executions.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Executions:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getWorkflowExecutionsByRule(req: Request, res: Response): Promise<void> {
    try {
      const { ruleId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const executions = await this.workflowExecutionService.getWorkflowExecutionsByRule(ruleId, tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Executions zur Regel:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async startWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const execution = await this.workflowExecutionService.startWorkflowExecution(id, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Starten der Workflow-Execution:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async succeedWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const execution = await this.workflowExecutionService.succeedWorkflowExecution(id, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim erfolgreichen Abschließen der Workflow-Execution:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async failWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'
      const errorMessage = req.body.errorMessage || 'Unbekannter Fehler'

      const execution = await this.workflowExecutionService.failWorkflowExecution(id, tenantId, actorId, errorMessage)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Fehlschlagen der Workflow-Execution:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async retryWorkflowExecution(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const execution = await this.workflowExecutionService.retryWorkflowExecution(id, tenantId, actorId)

      res.json({
        success: true,
        data: execution
      })
    } catch (error) {
      console.error('Fehler beim Wiederholen der Workflow-Execution:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getRunningWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const executions = await this.workflowExecutionService.getRunningWorkflowExecutions(tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der laufenden Workflow-Executions:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getFailedWorkflowExecutions(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const executions = await this.workflowExecutionService.getFailedWorkflowExecutions(tenantId)

      res.json({
        success: true,
        data: executions
      })
    } catch (error) {
      console.error('Fehler beim Laden der fehlgeschlagenen Workflow-Executions:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getWorkflowExecutionStats(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string

      const stats = await this.workflowExecutionService.getWorkflowExecutionStats(tenantId)

      res.json({
        success: true,
        data: stats
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Execution-Statistiken:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}