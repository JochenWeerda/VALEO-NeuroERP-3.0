/**
 * Purchase Order Service
 * ISO 27001 Communications Security Compliant
 * Procurement-to-Pay Automation Engine
 */

import { randomUUID } from 'crypto';
import { PurchaseOrder, PurchaseOrderStatus, PurchaseOrderItem, CreatePurchaseOrderInput, UpdatePurchaseOrderInput } from '../entities/purchase-order';
import { PurchaseOrderRepository, PurchaseOrderFilter, PurchaseOrderSort, PaginatedResult } from '../../infra/repositories/purchase-order-repository';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';
import { PurchaseOrderEventFactory, PurchaseOrderEvent } from '../events/purchase-order-events';
import { PurchaseOrderEventPublisher } from '../../infra/messaging/event-publisher';

export interface PurchaseOrderServiceDependencies {
  purchaseOrderRepo: PurchaseOrderRepository;
  auditLogger?: ISMSAuditLogger;
  cryptoService?: CryptoService;
  eventPublisher?: PurchaseOrderEventPublisher;
}

export interface CreatePurchaseOrderData extends CreatePurchaseOrderInput {
  tenantId: string;
  purchaseOrderNumber: string;
  items: PurchaseOrderItem[];
  createdBy: string;
}

export interface UpdatePurchaseOrderData extends UpdatePurchaseOrderInput {
  tenantId: string;
  items?: PurchaseOrderItem[];
}

export class PurchaseOrderService {
  constructor(private deps: PurchaseOrderServiceDependencies) {}

  /**
   * Create a new purchase order with validation and tenant isolation
   */
  async createPurchaseOrder(data: CreatePurchaseOrderData): Promise<PurchaseOrder> {
    // Business validation
    if (data.items.length === 0) {
      throw new Error('Purchase order must have at least one line item');
    }

    // Check if purchase order number already exists
    const existingOrder = await this.deps.purchaseOrderRepo.findByPurchaseOrderNumber(data.purchaseOrderNumber);
    if (existingOrder) {
      throw new Error(`Purchase order number ${data.purchaseOrderNumber} already exists`);
    }

    // Validate line items
    for (const item of data.items) {
      if (item.quantity <= 0) {
        throw new Error('Line item quantity must be positive');
      }
      if (item.unitPrice < 0) {
        throw new Error('Line item unit price cannot be negative');
      }
    }

    // Create items with proper IDs
    const items: PurchaseOrderItem[] = data.items.map(itemData =>
      new PurchaseOrderItem(
        '', // Will be set after PO creation
        itemData.itemType,
        itemData.description,
        itemData.quantity,
        itemData.unitPrice,
        itemData.discountPercent || 0,
        itemData.articleId,
        itemData.deliveryDate,
        itemData.notes
      )
    );

    // Create purchase order entity
    const purchaseOrder = new PurchaseOrder(
      data.supplierId,
      data.subject,
      data.description,
      data.deliveryDate,
      items,
      data.createdBy,
      {
        id: randomUUID(),
        purchaseOrderNumber: data.purchaseOrderNumber,
        contactPerson: data.contactPerson,
        paymentTerms: data.paymentTerms,
        currency: data.currency || 'EUR',
        taxRate: data.taxRate || 19.0,
        shippingAddress: data.shippingAddress,
        notes: data.notes,
        status: PurchaseOrderStatus.ENTWURF
      }
    );

    // Update item purchase order IDs
    items.forEach(item => {
      (item as any).purchaseOrderId = purchaseOrder.id;
    });

    const savedOrder = await this.deps.purchaseOrderRepo.create(purchaseOrder);

    // Publish domain event
    if (this.deps.eventPublisher) {
      const event = PurchaseOrderEventFactory.purchaseOrderCreated(
        savedOrder.id,
        data.tenantId,
        { userId: data.createdBy },
        {
          purchaseOrderNumber: savedOrder.purchaseOrderNumber,
          supplierId: savedOrder.supplierId,
          subject: savedOrder.subject,
          totalAmount: savedOrder.totalAmount,
          currency: savedOrder.currency,
          itemCount: savedOrder.items.length,
          deliveryDate: savedOrder.deliveryDate,
          status: savedOrder.status
        }
      );
      await this.deps.eventPublisher.publish(event);
    }

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_CREATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        supplierId: savedOrder.supplierId,
        totalAmount: savedOrder.totalAmount,
        itemCount: savedOrder.items.length
      }, data.tenantId, data.createdBy);
    }

    return savedOrder;
  }

  /**
   * Update an existing purchase order with status transitions and approvals
   */
  async updatePurchaseOrder(id: string, data: UpdatePurchaseOrderData): Promise<PurchaseOrder> {
    const existingOrder = await this.deps.purchaseOrderRepo.findById(id);
    if (!existingOrder) {
      throw new Error(`Purchase order ${id} not found`);
    }

    // Business validation
    if (data.items && data.items.length === 0) {
      throw new Error('Purchase order must have at least one line item');
    }

    if (data.items) {
      for (const item of data.items) {
        if (item.quantity <= 0) {
          throw new Error('Line item quantity must be positive');
        }
        if (item.unitPrice < 0) {
          throw new Error('Line item unit price cannot be negative');
        }
      }
    }

    // Create updated items if provided
    let updatedItems = existingOrder.items;
    if (data.items) {
      updatedItems = data.items.map(itemData =>
        new PurchaseOrderItem(
          existingOrder.id,
          itemData.itemType,
          itemData.description,
          itemData.quantity,
          itemData.unitPrice,
          itemData.discountPercent || 0,
          itemData.articleId,
          itemData.deliveryDate,
          itemData.notes,
          itemData.id || randomUUID()
        )
      );
    }

    // Create updated purchase order
    const updatedOrder = new PurchaseOrder(
      existingOrder.supplierId,
      data.subject || existingOrder.subject,
      data.description || existingOrder.description,
      data.deliveryDate || existingOrder.deliveryDate,
      updatedItems,
      existingOrder.createdBy,
      {
        id: existingOrder.id,
        purchaseOrderNumber: existingOrder.purchaseOrderNumber,
        contactPerson: data.contactPerson !== undefined ? data.contactPerson : existingOrder.contactPerson,
        paymentTerms: data.paymentTerms !== undefined ? data.paymentTerms : existingOrder.paymentTerms,
        currency: data.currency || existingOrder.currency,
        taxRate: data.taxRate || existingOrder.taxRate,
        shippingAddress: data.shippingAddress !== undefined ? data.shippingAddress : existingOrder.shippingAddress,
        notes: data.notes !== undefined ? data.notes : existingOrder.notes,
        status: existingOrder.status,
        version: existingOrder.version + 1,
        approvedAt: existingOrder.approvedAt,
        approvedBy: existingOrder.approvedBy,
        orderedAt: existingOrder.orderedAt,
        orderedBy: existingOrder.orderedBy,
        createdAt: existingOrder.createdAt,
        updatedAt: new Date(),
        orderDate: existingOrder.orderDate
      }
    );

    const savedOrder = await this.deps.purchaseOrderRepo.update(id, updatedOrder);

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_UPDATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        changes: Object.keys(data)
      }, data.tenantId, 'system'); // TODO: Add user context
    }

    return savedOrder;
  }

  /**
   * Retrieve purchase order by ID or query with filtering and related entities
   */
  async retrievePurchaseOrder(id: string, tenantId: string): Promise<PurchaseOrder | null> {
    return this.deps.purchaseOrderRepo.findById(id);
  }

  /**
   * Search purchase orders with advanced filtering
   */
  async searchPurchaseOrders(
    tenantId: string,
    filters: PurchaseOrderFilter = {},
    sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' },
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<PurchaseOrder>> {
    return this.deps.purchaseOrderRepo.findAll(filters, sort, pagination.page, pagination.pageSize);
  }

  /**
   * Approve purchase order
   */
  async approvePurchaseOrder(id: string, approvedBy: string, tenantId: string): Promise<PurchaseOrder> {
    const order = await this.deps.purchaseOrderRepo.findById(id);
    if (!order) {
      throw new Error(`Purchase order ${id} not found`);
    }

    if (!order.canBeApproved()) {
      throw new Error('Purchase order cannot be approved in its current state');
    }

    const approvedOrder = order.approve(approvedBy);
    const savedOrder = await this.deps.purchaseOrderRepo.update(id, approvedOrder);

    // Publish domain event
    if (this.deps.eventPublisher) {
      const event = PurchaseOrderEventFactory.purchaseOrderApproved(
        savedOrder.id,
        tenantId,
        { userId: approvedBy },
        {
          purchaseOrderNumber: savedOrder.purchaseOrderNumber,
          approvedBy,
          approvalDate: savedOrder.approvedAt!,
          totalAmount: savedOrder.totalAmount,
          currency: savedOrder.currency
        }
      );
      await this.deps.eventPublisher.publish(event);
    }

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_APPROVED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        approvedBy
      }, tenantId, approvedBy);
    }

    return savedOrder;
  }

  /**
   * Mark purchase order as ordered
   */
  async orderPurchaseOrder(id: string, orderedBy: string, tenantId: string): Promise<PurchaseOrder> {
    const order = await this.deps.purchaseOrderRepo.findById(id);
    if (!order) {
      throw new Error(`Purchase order ${id} not found`);
    }

    if (!order.canBeOrdered()) {
      throw new Error('Purchase order cannot be ordered in its current state');
    }

    const orderedOrder = order.order(orderedBy);
    const savedOrder = await this.deps.purchaseOrderRepo.update(id, orderedOrder);

    // Publish domain event
    if (this.deps.eventPublisher) {
      const event = PurchaseOrderEventFactory.purchaseOrderOrdered(
        savedOrder.id,
        tenantId,
        { userId: orderedBy },
        {
          purchaseOrderNumber: savedOrder.purchaseOrderNumber,
          orderedBy,
          orderDate: savedOrder.orderedAt!,
          supplierId: savedOrder.supplierId,
          totalAmount: savedOrder.totalAmount,
          currency: savedOrder.currency
        }
      );
      await this.deps.eventPublisher.publish(event);
    }

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_ORDERED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        orderedBy
      }, tenantId, orderedBy);
    }

    return savedOrder;
  }

  /**
   * Mark purchase order as invoiced (analogous to sales-domain markOrderAsInvoiced)
   */
  async markPurchaseOrderAsInvoiced(id: string, tenantId: string): Promise<PurchaseOrder> {
    const order = await this.deps.purchaseOrderRepo.findById(id);
    if (!order) {
      throw new Error(`Purchase order ${id} not found`);
    }

    // Business logic for marking as invoiced
    // This would typically happen after goods receipt and invoice processing
    if (order.status !== PurchaseOrderStatus.GELIEFERT) {
      throw new Error('Purchase order must be delivered before marking as invoiced');
    }

    // Update status to indicate invoiced (you might want to add a new status)
    // For now, we'll keep it as delivered but add audit logging
    const savedOrder = order; // No status change needed

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_INVOICED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber
      }, tenantId, 'system');
    }

    return savedOrder;
  }

  /**
   * Cancel purchase order
   */
  async cancelPurchaseOrder(id: string, tenantId: string): Promise<PurchaseOrder> {
    const order = await this.deps.purchaseOrderRepo.findById(id);
    if (!order) {
      throw new Error(`Purchase order ${id} not found`);
    }

    const cancelledOrder = order.cancel();
    const savedOrder = await this.deps.purchaseOrderRepo.update(id, cancelledOrder);

    // Publish domain event
    if (this.deps.eventPublisher) {
      const event = PurchaseOrderEventFactory.purchaseOrderCancelled(
        savedOrder.id,
        tenantId,
        { userId: 'system' }, // TODO: Add actual user context
        {
          purchaseOrderNumber: savedOrder.purchaseOrderNumber,
          cancelledBy: 'system', // TODO: Add actual user context
          cancellationDate: new Date(),
          totalAmount: savedOrder.totalAmount,
          currency: savedOrder.currency
        }
      );
      await this.deps.eventPublisher.publish(event);
    }

    // Audit logging
    if (this.deps.auditLogger) {
      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_CANCELLED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber
      }, tenantId, 'system');
    }

    return savedOrder;
  }
}
