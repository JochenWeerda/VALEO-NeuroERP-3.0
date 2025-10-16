import { Router } from 'express'
import { inject, injectable } from 'inversify'
import { PurchaseOrderController } from './purchaseOrder.controller'

@injectable()
export class PurchaseOrderRouter {
  constructor(
    @inject('PurchaseOrderController') private controller: PurchaseOrderController
  ) {}

  createRouter(): Router {
    const router = Router()

    // GET /api/einkauf/bestellungen - List purchase orders
    router.get('/bestellungen', this.controller.list)

    // GET /api/einkauf/bestellungen/:id - Get purchase order by ID
    router.get('/bestellungen/:id', this.controller.getById)

    // POST /api/einkauf/bestellungen - Create new purchase order
    router.post('/bestellungen', this.controller.create)

    // PUT /api/einkauf/bestellungen/:id - Update purchase order
    router.put('/bestellungen/:id', this.controller.update)

    // POST /api/einkauf/bestellungen/:id/submit - Submit purchase order
    router.post('/bestellungen/:id/submit', this.controller.submit)

    // POST /api/einkauf/bestellungen/:id/cancel - Cancel purchase order
    router.post('/bestellungen/:id/cancel', this.controller.cancel)

    // DELETE /api/einkauf/bestellungen/:id - Delete purchase order
    router.delete('/bestellungen/:id', this.controller.delete)

    return router
  }
}