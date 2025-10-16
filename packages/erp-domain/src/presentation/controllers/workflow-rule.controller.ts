import { Request, Response } from 'express'
import { WorkflowRuleService } from '../../application/services/workflow-rule.service'
import { CreateWorkflowRuleData } from '../../application/services/workflow-rule.service'

export class WorkflowRuleController {
  constructor(private workflowRuleService: WorkflowRuleService) {}

  async createWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system' // TODO: Aus Auth-Middleware

      const data: CreateWorkflowRuleData = {
        triggerEntity: req.body.triggerEntity,
        triggerAction: req.body.triggerAction,
        targetEntity: req.body.targetEntity,
        targetAction: req.body.targetAction,
        condition: req.body.condition,
        active: req.body.active,
        tenantId
      }

      const rule = await this.workflowRuleService.createWorkflowRule(data)

      res.status(201).json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Workflow-Regel:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async getWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const rule = await this.workflowRuleService.getWorkflowRuleById(id, tenantId)

      if (!rule) {
        res.status(404).json({
          success: false,
          error: 'Workflow-Regel nicht gefunden'
        })
        return
      }

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Regel:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getWorkflowRules(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const options = {
        triggerEntity: req.query.triggerEntity as string,
        triggerAction: req.query.triggerAction as string,
        targetEntity: req.query.targetEntity as string,
        targetAction: req.query.targetAction as string,
        active: req.query.active ? req.query.active === 'true' : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const rules = await this.workflowRuleService.getWorkflowRulesByTenant(tenantId, options)

      res.json({
        success: true,
        data: rules,
        total: rules.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Regeln:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getMatchingRules(req: Request, res: Response): Promise<void> {
    try {
      const { triggerEntity, triggerAction } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const rules = await this.workflowRuleService.getMatchingRules(triggerEntity, triggerAction, tenantId)

      res.json({
        success: true,
        data: rules
      })
    } catch (error) {
      console.error('Fehler beim Laden der passenden Workflow-Regeln:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async activateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rule = await this.workflowRuleService.activateWorkflowRule(id, tenantId, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Aktivieren der Workflow-Regel:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deactivateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rule = await this.workflowRuleService.deactivateWorkflowRule(id, tenantId, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Deaktivieren der Workflow-Regel:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async updateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      const rule = await this.workflowRuleService.updateWorkflowRule(id, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Workflow-Regel:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async deleteWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const actorId = req.user?.id || 'system'

      await this.workflowRuleService.deleteWorkflowRule(id, tenantId, actorId)

      res.json({
        success: true,
        message: 'Workflow-Regel gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Workflow-Regel:', error)
      res.status(error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    }
  }

  async executeWorkflowRules(req: Request, res: Response): Promise<void> {
    try {
      const { triggerEntity, triggerAction } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const result = await this.workflowRuleService.executeWorkflowRules(triggerEntity, triggerAction, tenantId, req.body)

      res.json({
        success: true,
        data: result
      })
    } catch (error) {
      console.error('Fehler beim Ausführen der Workflow-Regeln:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}