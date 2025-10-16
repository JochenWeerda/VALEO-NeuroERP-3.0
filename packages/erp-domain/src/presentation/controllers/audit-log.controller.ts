import { Request, Response } from 'express'
import { AuditLogService } from '../../application/services/audit-log.service'

export class AuditLogController {
  constructor(private auditLogService: AuditLogService) {}

  async getAuditLogs(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
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

      const logs = await this.auditLogService.getAuditLogsByTenant(tenantId, options)

      res.json({
        success: true,
        data: logs,
        total: logs.length // TODO: Pagination-Info
      })
    } catch (error) {
      console.error('Fehler beim Laden der Audit-Logs:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuditLogsByEntity(req: Request, res: Response): Promise<void> {
    try {
      const { entity, entityId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const logs = await this.auditLogService.getAuditLogsByEntity(entity as string, entityId as string, tenantId)

      res.json({
        success: true,
        data: logs
      })
    } catch (error) {
      console.error('Fehler beim Laden der Entity-Audit-Logs:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuditLogsByActor(req: Request, res: Response): Promise<void> {
    try {
      const { actorId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
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
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuditTrail(req: Request, res: Response): Promise<void> {
    try {
      const { entity, entityId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string

      const trail = await this.auditLogService.getAuditTrail(entity as string, entityId as string, tenantId)

      res.json({
        success: true,
        data: trail
      })
    } catch (error) {
      console.error('Fehler beim Laden des Audit-Trails:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getRecentAuditLogs(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 100

      const logs = await this.auditLogService.getRecentAuditLogs(tenantId, limit)

      res.json({
        success: true,
        data: logs
      })
    } catch (error) {
      console.error('Fehler beim Laden der letzten Audit-Logs:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getUserActivityReport(req: Request, res: Response): Promise<void> {
    try {
      const { actorId } = req.params
      const tenantId = req.headers['x-tenant-id'] as string
      const fromDate = new Date(req.query.fromDate as string)
      const toDate = new Date(req.query.toDate as string)

      const report = await this.auditLogService.getUserActivityReport(actorId as string, tenantId, fromDate, toDate)

      res.json({
        success: true,
        data: report
      })
    } catch (error) {
      console.error('Fehler beim Laden des User-Activity-Reports:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getComplianceReport(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
      const fromDate = new Date(req.query.fromDate as string)
      const toDate = new Date(req.query.toDate as string)

      const report = await this.auditLogService.getComplianceReport(tenantId, fromDate, toDate)

      res.json({
        success: true,
        data: report
      })
    } catch (error) {
      console.error('Fehler beim Laden des Compliance-Reports:', error)
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }

  async getAuditLogCount(req: Request, res: Response): Promise<void> {
    try {
      const tenantId = req.headers['x-tenant-id'] as string
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
      res.status(500).json({
        success: false,
        error: 'Interner Serverfehler'
      })
    }
  }
}
