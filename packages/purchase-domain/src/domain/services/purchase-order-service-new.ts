/**
 * Purchase Order Service
 * ISO 27001 Communications Security Compliant
 * Procurement-to-Pay Automation Engine
 */

import { PurchaseOrder, PurchaseOrderStatus, PurchaseOrderItem, CreatePurchaseOrderInput, UpdatePurchaseOrderInput } from '../entities/purchase-order';
import { PurchaseOrderRepository, PurchaseOrderFilter, PurchaseOrderSort, PaginatedResult } from '../../infra/repositories/purchase-order-repository';
import { ISMSAuditLogger } from '../../security/isms-audit-logger';
import { CryptoService } from '../../security/crypto-service';

export interface PurchaseOrderServiceDependencies {
  repository: PurchaseOrderRepository;
  auditLogger: ISMSAuditLogger;
  cryptoService: CryptoService;
}

export class PurchaseOrderService {
  constructor(private deps: PurchaseOrderServiceDependencies) {}

  /**
   * Create a new purchase order
   */
  async createPurchaseOrder(
    input: CreatePurchaseOrderInput,
    createdBy: string
  ): Promise<PurchaseOrder> {
    try {
      // Create items
      const items: PurchaseOrderItem[] = input.items.map(itemInput =>
        new PurchaseOrderItem(
          '', // Will be set after PO creation
          itemInput.itemType,
          itemInput.description,
          itemInput.quantity,
          itemInput.unitPrice,
          itemInput.discountPercent || 0,
          itemInput.articleId,
          itemInput.deliveryDate,
          itemInput.notes
        )
      );

      // Create purchase order
      const purchaseOrder = new PurchaseOrder(
        input.supplierId,
        input.subject,
        input.description,
        input.deliveryDate,
        items,
        createdBy,
        {
          ...(input.contactPerson && { contactPerson: input.contactPerson }),
          ...(input.paymentTerms && { paymentTerms: input.paymentTerms }),
          ...(input.currency && { currency: input.currency }),
          ...(input.taxRate && { taxRate: input.taxRate }),
          ...(input.shippingAddress && { shippingAddress: input.shippingAddress }),
          ...(input.notes && { notes: input.notes })
        }
      );

      // Update item purchase order IDs
      items.forEach(item => {
        (item as any).purchaseOrderId = purchaseOrder.id;
      });

      // Save to repository
      const savedOrder = await this.deps.repository.create(purchaseOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_CREATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        supplierId: savedOrder.supplierId,
        totalAmount: savedOrder.totalAmount,
        currency: savedOrder.currency,
        itemCount: savedOrder.items.length
      }, 'tenant-id', createdBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_CREATION_FAILED', {
        supplierId: input.supplierId,
        totalAmount: input.items.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0),
        error: (error as Error).message
      }, 'tenant-id', createdBy);
      throw error;
    }
  }

  /**
   * Get purchase order by ID
   */
  async getPurchaseOrderById(id: string): Promise<PurchaseOrder | null> {
    return await this.deps.repository.findById(id);
  }

  /**
   * Get purchase order by purchase order number
   */
  async getPurchaseOrderByNumber(purchaseOrderNumber: string): Promise<PurchaseOrder | null> {
    return await this.deps.repository.findByPurchaseOrderNumber(purchaseOrderNumber);
  }

  /**
   * List purchase orders with filtering and pagination
   */
  async listPurchaseOrders(
    filter: PurchaseOrderFilter = {},
    sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<PurchaseOrder>> {
    return await this.deps.repository.findAll(filter, sort, page, pageSize);
  }

  /**
   * Update purchase order
   */
  async updatePurchaseOrder(
    id: string,
    updates: UpdatePurchaseOrderInput,
    updatedBy: string
  ): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      if (!existingOrder.canBeModified()) {
        throw new Error('Purchase order cannot be modified in its current status');
      }

      // Create updated order
      const updatedOrder = new PurchaseOrder(
        existingOrder.supplierId,
        updates.subject || existingOrder.subject,
        updates.description || existingOrder.description,
        updates.deliveryDate || existingOrder.deliveryDate,
        existingOrder.items,
        existingOrder.createdBy,
        {
          id: existingOrder.id,
          purchaseOrderNumber: existingOrder.purchaseOrderNumber,
          contactPerson: updates.contactPerson || existingOrder.contactPerson,
          paymentTerms: updates.paymentTerms || existingOrder.paymentTerms,
          currency: existingOrder.currency,
          taxRate: updates.taxRate || existingOrder.taxRate,
          shippingAddress: updates.shippingAddress || existingOrder.shippingAddress,
          notes: updates.notes || existingOrder.notes,
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

      const savedOrder = await this.deps.repository.update(id, updatedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_UPDATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        updatedFields: Object.keys(updates),
        version: savedOrder.version
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_UPDATE_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Approve purchase order
   */
  async approvePurchaseOrder(id: string, approvedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      const approvedOrder = existingOrder.approve(approvedBy);
      const savedOrder = await this.deps.repository.update(id, approvedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_APPROVED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        approvedBy: savedOrder.approvedBy,
        totalAmount: savedOrder.totalAmount
      }, 'tenant-id', approvedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_APPROVAL_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', approvedBy);
      throw error;
    }
  }

  /**
   * Order purchase order (send to supplier)
   */
  async orderPurchaseOrder(id: string, orderedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      const orderedOrder = existingOrder.order(orderedBy);
      const savedOrder = await this.deps.repository.update(id, orderedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_ORDERED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        orderedBy: savedOrder.orderedBy,
        supplierId: savedOrder.supplierId
      }, 'tenant-id', orderedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_ORDERING_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', orderedBy);
      throw error;
    }
  }

  /**
   * Get purchase order (alias for getPurchaseOrderById for backward compatibility)
   */
  async getPurchaseOrder(id: string): Promise<PurchaseOrder | null> {
    return await this.getPurchaseOrderById(id);
  }

  /**
   * Mark purchase order as partially delivered
   */
  async markPartiallyDelivered(id: string, updatedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      const updatedOrder = existingOrder.markPartiallyDelivered();
      const savedOrder = await this.deps.repository.update(id, updatedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_PARTIALLY_DELIVERED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        status: savedOrder.status,
        updatedBy
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_DELIVERY_UPDATE_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Mark purchase order as delivered (alias for markFullyDelivered)
   */
  async markDelivered(id: string, updatedBy: string): Promise<PurchaseOrder> {
    return await this.markFullyDelivered(id, updatedBy);
  }

  /**
   * Mark purchase order as fully delivered
   */
  async markFullyDelivered(id: string, updatedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      // Validate that the order can be marked as delivered
      if (existingOrder.status !== PurchaseOrderStatus.BESTELLT &&
          existingOrder.status !== PurchaseOrderStatus.TEILGELIEFERT) {
        throw new Error('Purchase order must be ordered or partially delivered to be marked as fully delivered');
      }

      const updatedOrder = existingOrder.markDelivered();
      const savedOrder = await this.deps.repository.update(id, updatedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_FULLY_DELIVERED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        status: savedOrder.status,
        updatedBy,
        previousStatus: existingOrder.status
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_DELIVERY_UPDATE_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Update delivery status (generic method for delivery status changes)
   */
  async updateDeliveryStatus(
    id: string,
    deliveryStatus: 'PARTIAL' | 'FULL',
    updatedBy: string
  ): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      let updatedOrder: PurchaseOrder;

      if (deliveryStatus === 'PARTIAL') {
        if (existingOrder.status !== PurchaseOrderStatus.BESTELLT &&
            existingOrder.status !== PurchaseOrderStatus.TEILGELIEFERT) {
          throw new Error('Purchase order must be ordered to be marked as partially delivered');
        }
        updatedOrder = existingOrder.markPartiallyDelivered();
      } else if (deliveryStatus === 'FULL') {
        if (existingOrder.status !== PurchaseOrderStatus.BESTELLT &&
            existingOrder.status !== PurchaseOrderStatus.TEILGELIEFERT) {
          throw new Error('Purchase order must be ordered or partially delivered to be marked as fully delivered');
        }
        updatedOrder = existingOrder.markDelivered();
      } else {
        throw new Error('Invalid delivery status');
      }

      const savedOrder = await this.deps.repository.update(id, updatedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_DELIVERY_STATUS_UPDATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        deliveryStatus,
        status: savedOrder.status,
        updatedBy,
        previousStatus: existingOrder.status
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_DELIVERY_STATUS_UPDATE_FAILED', {
        purchaseOrderId: id,
        deliveryStatus,
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Mark purchase order as invoiced (supplier invoice received)
   */
  async markAsInvoiced(id: string, invoicedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      // Validate that the order can be marked as invoiced
      if (existingOrder.status !== PurchaseOrderStatus.GELIEFERT) {
        throw new Error('Purchase order must be delivered before it can be marked as invoiced');
      }

      // For purchase orders, marking as invoiced doesn't change the main status
      // but we track that invoice was received
      // This could be stored as additional metadata or a separate status field
      // For now, we'll log the event but keep the status as delivered

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_INVOICED', {
        purchaseOrderId: existingOrder.id,
        purchaseOrderNumber: existingOrder.purchaseOrderNumber,
        supplierId: existingOrder.supplierId,
        totalAmount: existingOrder.totalAmount,
        invoicedBy
      }, 'tenant-id', invoicedBy);

      // Return the existing order (no status change needed)
      return existingOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_INVOICING_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', invoicedBy);
      throw error;
    }
  }

  /**
   * Cancel purchase order
   */
  async cancelPurchaseOrder(id: string, updatedBy: string): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      const cancelledOrder = existingOrder.cancel();
      const savedOrder = await this.deps.repository.update(id, cancelledOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_CANCELLED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        status: savedOrder.status,
        cancelledBy: updatedBy
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_CANCELLATION_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Delete purchase order
   */
  async deletePurchaseOrder(id: string): Promise<boolean> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        return false;
      }

      if (existingOrder.status !== PurchaseOrderStatus.ENTWURF) {
        throw new Error('Only draft purchase orders can be deleted');
      }

      const success = await this.deps.repository.delete(id);

      if (success) {
        await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_DELETED', {
          purchaseOrderId: id,
          purchaseOrderNumber: existingOrder.purchaseOrderNumber
        }, 'tenant-id', 'system');
      }

      return success;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_DELETION_FAILED', {
        purchaseOrderId: id,
        error: (error as Error).message
      }, 'tenant-id', 'system');
      throw error;
    }
  }

  /**
   * Get purchase orders by supplier
   */
  async getPurchaseOrdersBySupplier(supplierId: string): Promise<PurchaseOrder[]> {
    return await this.deps.repository.findBySupplierId(supplierId);
  }

  /**
   * Search purchase orders with advanced filters (analogous to sales-domain searchOrders)
   */
  async searchPurchaseOrders(
    filters: {
      supplierId?: string;
      status?: PurchaseOrderStatus;
      search?: string; // Text search in subject, description, PO number
      deliveryDateFrom?: Date;
      deliveryDateTo?: Date;
      totalAmountMin?: number;
      totalAmountMax?: number;
      createdBy?: string;
    } = {},
    sort: PurchaseOrderSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedResult<PurchaseOrder>> {
    // Enhanced filter for search term
    const enhancedFilters: PurchaseOrderFilter = { ...filters };

    if (filters.search) {
      // For in-memory repository, we'll handle text search in the service layer
      // In a real database, this would be handled by the repository with SQL LIKE queries
      const allOrders = await this.deps.repository.findAll({}, sort, 1, 1000); // Get all for filtering
      const searchTerm = filters.search.toLowerCase();

      const filteredOrders = allOrders.items.filter(order =>
        order.purchaseOrderNumber.toLowerCase().includes(searchTerm) ||
        order.subject.toLowerCase().includes(searchTerm) ||
        order.description.toLowerCase().includes(searchTerm) ||
        order.supplierId.toLowerCase().includes(searchTerm)
      );

      // Apply pagination to filtered results
      const total = filteredOrders.length;
      const totalPages = Math.ceil(total / pageSize);
      const startIndex = (page - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedOrders = filteredOrders.slice(startIndex, endIndex);

      return {
        items: paginatedOrders,
        total,
        page,
        pageSize,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      };
    }

    return await this.deps.repository.findAll(enhancedFilters, sort, page, pageSize);
  }

  /**
   * Get overdue purchase orders
   */
  async getOverduePurchaseOrders(): Promise<PurchaseOrder[]> {
    return await this.deps.repository.findOverdue();
  }

  /**
   * Get purchase orders pending approval
   */
  async getPendingApprovalPurchaseOrders(): Promise<PurchaseOrder[]> {
    return await this.deps.repository.findPendingApproval();
  }

  /**
   * Update delivery date for purchase order
   */
  async updateDeliveryDate(
    id: string,
    newDeliveryDate: Date,
    updatedBy: string
  ): Promise<PurchaseOrder> {
    try {
      const existingOrder = await this.deps.repository.findById(id);
      if (!existingOrder) {
        throw new Error(`Purchase order with id ${id} not found`);
      }

      if (!existingOrder.canBeModified()) {
        throw new Error('Purchase order cannot be modified in its current status');
      }

      // Validate delivery date is not in the past
      if (newDeliveryDate < new Date()) {
        throw new Error('Delivery date cannot be in the past');
      }

      // Create updated order with new delivery date
      const updatedOrder = new PurchaseOrder(
        existingOrder.supplierId,
        existingOrder.subject,
        existingOrder.description,
        newDeliveryDate, // New delivery date
        existingOrder.items,
        existingOrder.createdBy,
        {
          id: existingOrder.id,
          purchaseOrderNumber: existingOrder.purchaseOrderNumber,
          contactPerson: existingOrder.contactPerson,
          paymentTerms: existingOrder.paymentTerms,
          currency: existingOrder.currency,
          taxRate: existingOrder.taxRate,
          shippingAddress: existingOrder.shippingAddress,
          notes: existingOrder.notes,
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

      const savedOrder = await this.deps.repository.update(id, updatedOrder);

      await this.deps.auditLogger.logSecureEvent('PURCHASE_ORDER_DELIVERY_DATE_UPDATED', {
        purchaseOrderId: savedOrder.id,
        purchaseOrderNumber: savedOrder.purchaseOrderNumber,
        oldDeliveryDate: existingOrder.deliveryDate.toISOString(),
        newDeliveryDate: newDeliveryDate.toISOString(),
        updatedBy
      }, 'tenant-id', updatedBy);

      return savedOrder;

    } catch (error) {
      await this.deps.auditLogger.logSecurityIncident('PURCHASE_ORDER_DELIVERY_DATE_UPDATE_FAILED', {
        purchaseOrderId: id,
        newDeliveryDate: newDeliveryDate.toISOString(),
        error: (error as Error).message
      }, 'tenant-id', updatedBy);
      throw error;
    }
  }

  /**
   * Get purchase orders by delivery date range
   */
  async getPurchaseOrdersByDeliveryDateRange(
    startDate: Date,
    endDate: Date
  ): Promise<PurchaseOrder[]> {
    return await this.deps.repository.findByDeliveryDateRange(startDate, endDate);
  }

  /**
   * Check if a purchase order is overdue
   */
  async isPurchaseOrderOverdue(id: string): Promise<boolean> {
    const order = await this.deps.repository.findById(id);
    return order ? order.isOverdue() : false;
  }

  /**
   * Get purchase order statistics
   */
  async getPurchaseOrderStatistics(): Promise<{
    total: number;
    byStatus: Record<PurchaseOrderStatus, number>;
    totalValue: number;
    averageValue: number;
    overdueCount: number;
    pendingApprovalCount: number;
  }> {
    return await this.deps.repository.getStatistics();
  }
}
