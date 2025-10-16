import { inject, injectable } from 'inversify'
import { PurchaseOrderRepository } from '../../core/repositories/purchaseOrder.repository'
import { PurchaseOrder } from '../../core/entities/purchaseOrder.entity'
import { PurchaseOrderItem } from '../../core/entities/purchaseOrderItem.entity'
// @ts-ignore - Module to be created
import { NumberRangeService } from './numberRange.service'
import { AuditService } from './audit.service'
// @ts-ignore - Module to be created  
import { ValidationError } from '../../core/errors/validation.error'

@injectable()
export class PurchaseOrderService {
  constructor(
    @inject('PurchaseOrderRepository') private repository: PurchaseOrderRepository,
    @inject('NumberRangeService') private numberRangeService: NumberRangeService,
    @inject('AuditService') private auditService: AuditService
  ) {}

  async create(tenantId: string, data: any, actorId: string): Promise<PurchaseOrder> {
    // Validate business rules
    this.validatePurchaseOrderData(data)

    // Generate order number
    const orderNumber = await this.numberRangeService.generateNumber('BE', tenantId)

    const order = new PurchaseOrder({
      id: '', // Will be set by repository
      tenantId,
      no: orderNumber,
      supplierId: data.supplierId,
      status: 'ENTWURF',
      currency: data.currency || 'EUR',
      items: data.items?.map((item: any) => new PurchaseOrderItem({
        id: '',
        poId: '',
        articleId: item.articleId,
        qty: item.qty,
        uom: item.uom,
        price: item.price,
        taxKeyId: item.taxKeyId,
        deliveryDate: item.deliveryDate
      })) || [],
      version: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    })

    const savedOrder = await this.repository.save(order)

    // Audit log
    await this.auditService.log({
      actorId,
      entity: 'PurchaseOrder',
      entityId: savedOrder.id,
      action: 'CREATE',
      before: null,
      after: savedOrder,
      tenantId
    })

    return savedOrder
  }

  async update(id: string, data: any, version: number, actorId: string): Promise<PurchaseOrder> {
    const existingOrder = await this.repository.findById(id)
    if (!existingOrder) {
      throw new Error('Purchase order not found')
    }

    // Optimistic locking
    if (existingOrder.version !== version) {
      throw new ValidationError('Purchase order was modified by another user')
    }

    // Validate business rules
    this.validatePurchaseOrderData(data)

    const updatedOrder = new PurchaseOrder({
      ...existingOrder,
      supplierId: data.supplierId || existingOrder.supplierId,
      currency: data.currency || existingOrder.currency,
      items: data.items?.map((item: any) => new PurchaseOrderItem({
        id: item.id || '',
        poId: id,
        articleId: item.articleId,
        qty: item.qty,
        uom: item.uom,
        price: item.price,
        taxKeyId: item.taxKeyId,
        deliveryDate: item.deliveryDate
      })) || existingOrder.items,
      version: existingOrder.version + 1,
      updatedAt: new Date()
    })

    const savedOrder = await this.repository.save(updatedOrder)

    // Audit log
    await this.auditService.log({
      actorId,
      entity: 'PurchaseOrder',
      entityId: savedOrder.id,
      action: 'UPDATE',
      before: existingOrder,
      after: savedOrder,
      tenantId: existingOrder.tenantId
    })

    return savedOrder
  }

  async findById(id: string): Promise<PurchaseOrder | null> {
    return this.repository.findById(id)
  }

  async findByTenant(tenantId: string, filters?: any): Promise<PurchaseOrder[]> {
    return this.repository.findByTenant(tenantId, filters)
  }

  async submit(id: string, actorId: string): Promise<PurchaseOrder> {
    const order = await this.repository.findById(id)
    if (!order) {
      throw new Error('Purchase order not found')
    }

    if (order.status !== 'ENTWURF') {
      throw new ValidationError('Only draft orders can be submitted')
    }

    // Business rule validations
    this.validateForSubmission(order)

    const updatedOrder = new PurchaseOrder({
      ...order,
      status: 'FREIGEGEBEN',
      version: order.version + 1,
      updatedAt: new Date()
    })

    const savedOrder = await this.repository.save(updatedOrder)

    // Audit log
    await this.auditService.log({
      actorId,
      entity: 'PurchaseOrder',
      entityId: savedOrder.id,
      action: 'SUBMIT',
      before: order,
      after: savedOrder,
      tenantId: order.tenantId
    })

    return savedOrder
  }

  async cancel(id: string, actorId: string): Promise<PurchaseOrder> {
    const order = await this.repository.findById(id)
    if (!order) {
      throw new Error('Purchase order not found')
    }

    if (!['ENTWURF', 'FREIGEGEBEN'].includes(order.status)) {
      throw new ValidationError('Order cannot be cancelled in current status')
    }

    const updatedOrder = new PurchaseOrder({
      ...order,
      status: 'STORNIERT',
      version: order.version + 1,
      updatedAt: new Date()
    })

    const savedOrder = await this.repository.save(updatedOrder)

    // Audit log
    await this.auditService.log({
      actorId,
      entity: 'PurchaseOrder',
      entityId: savedOrder.id,
      action: 'CANCEL',
      before: order,
      after: savedOrder,
      tenantId: order.tenantId
    })

    return savedOrder
  }

  private validatePurchaseOrderData(data: any): void {
    if (!data.supplierId) {
      throw new ValidationError('Supplier is required')
    }

    if (!data.items || data.items.length === 0) {
      throw new ValidationError('At least one item is required')
    }

    // Validate items
    data.items.forEach((item: any, index: number) => {
      if (!item.articleId) {
        throw new ValidationError(`Item ${index + 1}: Article is required`)
      }
      if (!item.qty || item.qty <= 0) {
        throw new ValidationError(`Item ${index + 1}: Quantity must be greater than 0`)
      }
      if (!item.uom) {
        throw new ValidationError(`Item ${index + 1}: Unit of measure is required`)
      }
      if (item.price < 0) {
        throw new ValidationError(`Item ${index + 1}: Price cannot be negative`)
      }
    })
  }

  private validateForSubmission(order: PurchaseOrder): void {
    // Check if all required fields are filled
    if (!order.supplierId) {
      throw new ValidationError('Supplier is required for submission')
    }

    // Check delivery dates
    const now = new Date()
    order.items.forEach((item, index) => {
      if (item.deliveryDate && item.deliveryDate < now) {
        throw new ValidationError(`Item ${index + 1}: Delivery date cannot be in the past`)
      }
    })

    // Additional business rules can be added here
  }
}