import { Request, Response } from 'express'
import { WorkflowRuleService } from '../../application/services/workflow-rule.service'
import { CreateWorkflowRuleData } from '../../application/services/workflow-rule.service'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError, respondDomainMutationError } from '../utils/request-context'

export class WorkflowRuleController {
  constructor(private workflowRuleService: WorkflowRuleService) {}

  async createWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const auditActorId = resolveActorId(req)

      const data: CreateWorkflowRuleData = {
        triggerEntity: req.body.triggerEntity,
        triggerAction: req.body.triggerAction,
        targetEntity: req.body.targetEntity,
        targetAction: req.body.targetAction,
        condition: req.body.condition,
        active: req.body.active,
        tenantId
      }

      const rule = await this.workflowRuleService.createWorkflowRule(data, auditActorId)

      res.status(201).json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Erstellen der Workflow-Regel:', error)
      respondControllerError(res, error, 400)
    }
  }

  async getWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)

      const rule = await this.workflowRuleService.getWorkflowRuleById(id as string, tenantId)

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
      respondControllerError(res, error, 500)
    }
  }

  async getWorkflowRules(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        triggerEntity: req.query.triggerEntity as string,
        triggerAction: req.query.triggerAction as string,
        targetEntity: req.query.targetEntity as string,
        targetAction: req.query.targetAction as string,
        active: req.query.active ? req.query.active === 'true' : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string, 10) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string, 10) : undefined
      }

      const { items, total } = await this.workflowRuleService.getWorkflowRulesByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Workflow-Regeln:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getMatchingRules(req: Request, res: Response): Promise<void> {
    try {
      const { triggerEntity, triggerAction } = req.params
      const tenantId = resolveTenantId(req)

      const rules = await this.workflowRuleService.getMatchingRules(triggerEntity as string, triggerAction as string, tenantId)

      res.json({
        success: true,
        data: rules
      })
    } catch (error) {
      console.error('Fehler beim Laden der passenden Workflow-Regeln:', error)
      respondControllerError(res, error, 500)
    }
  }

  async activateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rule = await this.workflowRuleService.activateWorkflowRule(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Aktivieren der Workflow-Regel:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deactivateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rule = await this.workflowRuleService.deactivateWorkflowRule(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Deaktivieren der Workflow-Regel:', error)
      respondDomainMutationError(res, error)
    }
  }

  async updateWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const rule = await this.workflowRuleService.updateWorkflowRule(id as string, tenantId, req.body, actorId)

      res.json({
        success: true,
        data: rule
      })
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Workflow-Regel:', error)
      respondDomainMutationError(res, error)
    }
  }

  async deleteWorkflowRule(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      await this.workflowRuleService.deleteWorkflowRule(id as string, tenantId, actorId)

      res.json({
        success: true,
        message: 'Workflow-Regel gelöscht'
      })
    } catch (error) {
      console.error('Fehler beim Löschen der Workflow-Regel:', error)
      respondDomainMutationError(res, error)
    }
  }

  async executeWorkflowRules(req: Request, res: Response): Promise<void> {
    try {
      const { triggerEntity, triggerAction } = req.params
      const tenantId = resolveTenantId(req)

      const result = await this.workflowRuleService.executeWorkflowRules(triggerEntity as string, triggerAction as string, tenantId, req.body)

      res.json({
        success: true,
        data: result
      })
    } catch (error) {
      console.error('Fehler beim Ausführen der Workflow-Regeln:', error)
      respondControllerError(res, error, 500)
    }
  }
}
