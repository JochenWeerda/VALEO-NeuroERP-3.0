import { Request, Response } from 'express'
import { inject, injectable } from 'inversify'
import { PurchaseOrderService } from '../../application/services/purchaseOrder.service'

@injectable()
export class PurchaseOrderController {
  constructor(
    @inject('PurchaseOrderService') private service: PurchaseOrderService
  ) {}

  list = async (req: Request, res: Response): Promise<void> => {
    try {
      const { tenantId } = req.user as any // From auth middleware
      const { status, supplierId, limit = 50, offset = 0 } = req.query

      const filters: any = {}
      if (status) filters.status = status
      if (supplierId) filters.supplierId = supplierId
      filters.limit = parseInt(limit as string)
      filters.offset = parseInt(offset as string)

      const orders = await this.service.findByTenant(tenantId, filters)
      const total = orders.length // TODO: Implement countByTenant

      res.json({
        success: true,
        data: orders,
        total,
        limit: filters.limit,
        offset: filters.offset
      })
    } catch (error) {
      console.error('Error listing purchase orders:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to list purchase orders'
      })
    }
  }

  getById = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const order = await this.service.findById(id as string)

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
      res.status(500).json({
        success: false,
        error: 'Failed to get purchase order'
      })
    }
  }

  create = async (req: Request, res: Response): Promise<void> => {
    try {
      const { tenantId, id: actorId } = req.user as any
      const orderData = req.body

      const order = await this.service.create(tenantId, orderData, actorId)

      res.status(201).json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error creating purchase order:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create purchase order'
      })
    }
  }

  update = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const { version, ...orderData } = req.body
      const { id: actorId } = req.user as any

      const order = await this.service.update(id as string, orderData, version, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error updating purchase order:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update purchase order'
      })
    }
  }

  submit = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const { id: actorId } = req.user as any

      const order = await this.service.submit(id as string, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error submitting purchase order:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to submit purchase order'
      })
    }
  }

  cancel = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      const { id: actorId } = req.user as any

      const order = await this.service.cancel(id as string, actorId)

      res.json({
        success: true,
        data: order
      })
    } catch (error) {
      console.error('Error cancelling purchase order:', error)
      res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to cancel purchase order'
      })
    }
  }

  delete = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params
      await (this.service as any).delete(id as string)

      res.json({
        success: true
      })
    } catch (error) {
      console.error('Error deleting purchase order:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to delete purchase order'
      })
    }
  }
}
