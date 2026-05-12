import { Request, Response } from 'express'
import { AuditLogService } from '../../application/services/audit-log.service'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveTenantId, respondControllerError } from '../utils/request-context'

export class AuditLogController {
  constructor(private auditLogService: AuditLogService) {}

  async getAuditLogs(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        entity: req.query.entity as string,
        entityId: req.query.entityId as string,
        actorId: req.query.actorId as string,
        action: req.query.action as string,
        fromDate: req.query.fromDate ? new Date(req.query.fromDate as string) : undefined,
        toDate: req.query.toDate ? new Date(req.query.toDate as string) : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const { items, total } = await this.auditLogService.getAuditLogsByTenant(tenantId, options)
      const limit = clampLimit(options.limit)
      const offset = clampOffset(options.offset)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Audit-Logs:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAuditLogsByEntity(req: Request, res: Response): Promise<void> {
    try {
      const { entity, entityId } = req.params
      const tenantId = resolveTenantId(req)

      const logs = await this.auditLogService.getAuditLogsByEntity(entity as string, entityId as string, tenantId)

      res.json({
        success: true,
        data: logs
      })
    } catch (error) {
      console.error('Fehler beim Laden der Entity-Audit-Logs:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAuditLogsByActor(req: Request, res: Response): Promise<void> {
    try {
      const { actorId } = req.params
      const tenantId = resolveTenantId(req)
      const options = {
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        offset: req.query.offset ? parseInt(req.query.offset as string) : undefined
      }

      const logs = await this.auditLogService.getAuditLogsByActor(actorId as string, tenantId, options)

      res.json({
        success: true,
        data: logs
      })
    } catch (error) {
      console.error('Fehler beim Laden der Actor-Audit-Logs:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAuditTrail(req: Request, res: Response): Promise<void> {
    try {
      const { entity, entityId } = req.params
      const tenantId = resolveTenantId(req)

      const trail = await this.auditLogService.getAuditTrail(entity as string, entityId as string, tenantId)

      res.json({
        success: true,
        data: trail
      })
    } catch (error) {
      console.error('Fehler beim Laden des Audit-Trails:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getRecentAuditLogs(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 100

      const logs = await this.auditLogService.getRecentAuditLogs(tenantId, limit)

      res.json({
        success: true,
        data: logs
      })
    } catch (error) {
      console.error('Fehler beim Laden der letzten Audit-Logs:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getUserActivityReport(req: Request, res: Response): Promise<void> {
    try {
      const { actorId } = req.params
      const tenantId = resolveTenantId(req)
      const fromDate = new Date(req.query.fromDate as string)
      const toDate = new Date(req.query.toDate as string)

      const report = await this.auditLogService.getUserActivityReport(actorId as string, tenantId, fromDate, toDate)

      res.json({
        success: true,
        data: report
      })
    } catch (error) {
      console.error('Fehler beim Laden des User-Activity-Reports:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getComplianceReport(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const fromDate = new Date(req.query.fromDate as string)
      const toDate = new Date(req.query.toDate as string)

      const report = await this.auditLogService.getComplianceReport(tenantId, fromDate, toDate)

      res.json({
        success: true,
        data: report
      })
    } catch (error) {
      console.error('Fehler beim Laden des Compliance-Reports:', error)
      respondControllerError(res, error, 500)
    }
  }

  async getAuditLogCount(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = resolveTenantId(req)
      const options = {
        entity: req.query.entity as string,
        actorId: req.query.actorId as string,
        action: req.query.action as string,
        fromDate: req.query.fromDate ? new Date(req.query.fromDate as string) : undefined,
        toDate: req.query.toDate ? new Date(req.query.toDate as string) : undefined
      }

      const count = await this.auditLogService.getAuditLogCount(tenantId, options)

      res.json({
        success: true,
        data: { count }
      })
    } catch (error) {
      console.error('Fehler beim Laden der Audit-Log-Anzahl:', error)
      respondControllerError(res, error, 500)
    }
  }
}
