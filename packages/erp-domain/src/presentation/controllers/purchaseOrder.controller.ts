import { Request, Response } from 'express'
import { inject, injectable } from 'inversify'
import { PurchaseOrderService } from '../../application/services/purchaseOrder.service'
import { clampLimit, clampOffset } from '../types/api-pagination'
import { resolveActorId, resolveTenantId, respondControllerError } from '../utils/request-context'

@injectable()
export class PurchaseOrderController {
  constructor(
    @inject('PurchaseOrderService') private service: PurchaseOrderService
  ) {}

  list = async (req: Request, res: Response): Promise<void> => {
    try {
      const tenantId = resolveTenantId(req)
      const { status, supplierId } = req.query
      const limitRaw = req.query.limit !== undefined ? parseInt(String(req.query.limit), 10) : undefined
      const offsetRaw = req.query.offset !== undefined ? parseInt(String(req.query.offset), 10) : undefined

      const { items, total } = await this.service.getPurchaseOrdersByTenant(tenantId, {
        status: status as string | undefined,
        supplierId: supplierId as string | undefined,
        limit: limitRaw,
        offset: offsetRaw,
      })
      const limit = clampLimit(limitRaw)
      const offset = clampOffset(offsetRaw)

      res.json({
        success: true,
        data: items,
        pagination: { total, limit, offset },
      })
    } catch (error) {
      console.error('Error listing purchase orders:', error)
      respondControllerError(res, error, 500)
    }
  }

  getById = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const order = await this.service.findById(id as string, tenantId)

      if (!order) {
        res.status(404).json({
          success: false,
          error: 'Purchase order not found'
        })
        return
      }

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error getting purchase order:', error)
      respondControllerError(res, error, 500)
    }
  }

  create = async (req: Request, res: Response): Promise<void> => {
    try {
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)
      const orderData = req.body

      const order = await this.service.create(tenantId, orderData, actorId)

      res.status(201).json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error creating purchase order:', error)
      respondControllerError(res, error, 400)
    }
  }

  update = async (req: Request, res: Response): Promise<void> => {
    try {
      const tenantId = resolveTenantId(req)
      const { id } = req.params
      const { version, ...orderData } = req.body
      const actorId = resolveActorId(req)

      const order = await this.service.update(tenantId, id as string, orderData, version, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error updating purchase order:', error)
      respondControllerError(res, error, 400)
    }
  }

  submit = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const order = await this.service.submit(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error submitting purchase order:', error)
      respondControllerError(res, error, 400)
    }
  }

  cancel = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const tenantId = resolveTenantId(req)
      const actorId = resolveActorId(req)

      const order = await this.service.cancel(id as string, tenantId, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error cancelling purchase order:', error)
      respondControllerError(res, error, 400)
    }
  }

  delete = async (req: Request, res: Response): Promise<void> => {
    try {
      const tenantId = resolveTenantId(req)
      const { id } = req.params
      await this.service.delete(tenantId, id as string)

      res.json({
        success: true
      })
    } catch (error) {
      console.error('Error deleting purchase order:', error)
      respondControllerError(res, error, 404)
    }
  }
}
