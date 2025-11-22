/**
 * Delivery Note Service
 * Complete Delivery Management with Order-to-Delivery Conversion
 */

import { DeliveryNote, DeliveryNoteItem, CreateDeliveryNoteInput, UpdateDeliveryNoteInput, DeliveryNoteStatus } from '../entities/delivery-note';
import { DeliveryNoteRepository, DeliveryNoteFilter, DeliveryNoteSort, PaginatedDeliveryNoteResult } from '../../infra/repositories/delivery-note-repository';
import { SalesOrderService } from './sales-order-service';
import { SalesOrder } from '../entities/sales-order';

export interface DeliveryNoteServiceDependencies {
  deliveryNoteRepository: DeliveryNoteRepository;
  salesOrderService: SalesOrderService;
}

export interface ConvertOrderToDeliveryOptions {
  plannedDeliveryDate?: Date;
  carrierInfo?: {
    carrierName: string;
    trackingNumber?: string;
    carrierService?: string;
  };
  specialInstructions?: string;
  deliveryAddress?: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  partialDelivery?: {
    itemQuantities: { [itemId: string]: number }; // Partial quantities per item
  };
}

export class DeliveryNoteService {
  constructor(private deps: DeliveryNoteServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createDeliveryNote(
    input: CreateDeliveryNoteInput,
    createdBy: string
  ): Promise<DeliveryNote> {
    // Convert items to full DeliveryNoteItem objects
    const deliveryItems: DeliveryNoteItem[] = input.items.map(item => ({
      ...item,
      id: '', // Will be set by entity constructor
      createdAt: new Date(),
      updatedAt: new Date()
    }));

    const deliveryNote = new DeliveryNote(
      input.orderId,
      input.customerId,
      input.deliveryAddress,
      input.plannedDeliveryDate,
      deliveryItems,
      createdBy,
      {
        carrierInfo: input.carrierInfo,
        specialInstructions: input.specialInstructions
      }
    );

    return await this.deps.deliveryNoteRepository.create(deliveryNote);
  }

  async getDeliveryNoteById(id: string): Promise<DeliveryNote | null> {
    return await this.deps.deliveryNoteRepository.findById(id);
  }

  async getDeliveryNoteByNumber(deliveryNoteNumber: string): Promise<DeliveryNote | null> {
    return await this.deps.deliveryNoteRepository.findByDeliveryNoteNumber(deliveryNoteNumber);
  }

  async updateDeliveryNote(
    id: string,
    updates: UpdateDeliveryNoteInput,
    updatedBy: string
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(id);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.updateBasicInfo(updates, updatedBy);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  async deleteDeliveryNote(id: string): Promise<boolean> {
    const deliveryNote = await this.getDeliveryNoteById(id);
    if (!deliveryNote) {
      return false;
    }

    if (deliveryNote.status !== 'PREPARED') {
      throw new Error('Can only delete prepared delivery notes');
    }

    return await this.deps.deliveryNoteRepository.delete(id);
  }

  // ======================================
  // CRITICAL: ORDER-TO-DELIVERY CONVERSION
  // ======================================

  async convertOrderToDeliveryNote(
    orderId: string,
    convertedBy: string,
    options: ConvertOrderToDeliveryOptions = {}
  ): Promise<DeliveryNote> {
    // 1. Get and validate the sales order
    const order = await this.deps.salesOrderService.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    // 2. Validate order status - must be CONFIRMED or IN_PROGRESS
    if (!['CONFIRMED', 'IN_PROGRESS'].includes(order.status)) {
      throw new Error('Can only create delivery notes from confirmed or in-progress orders');
    }

    // 3. Check if order can be delivered
    if (!order.canBeDelivered()) {
      throw new Error('Order cannot be delivered in current status');
    }

    // 4. Check for existing delivery notes
    const existingDeliveryNotes = await this.getDeliveryNotesByOrderId(orderId);
    const hasActiveDeliveries = existingDeliveryNotes.some(dn => 
      !['DELIVERED', 'CONFIRMED', 'CANCELLED', 'RETURNED'].includes(dn.status)
    );
    
    if (hasActiveDeliveries && !options.partialDelivery) {
      throw new Error('Order already has active delivery notes. Use partial delivery if needed.');
    }

    // 5. Determine delivery quantities
    const deliveryItems: Omit<DeliveryNoteItem, 'id' | 'createdAt' | 'updatedAt'>[] = order.items.map(orderItem => {
      let deliveredQuantity = orderItem.quantity;

      // Handle partial delivery
      if (options.partialDelivery?.itemQuantities?.[orderItem.id]) {
        deliveredQuantity = Math.min(
          options.partialDelivery.itemQuantities[orderItem.id],
          orderItem.quantity - (orderItem.deliveredQuantity || 0)
        );
      } else {
        // Full delivery of remaining quantity
        deliveredQuantity = orderItem.quantity - (orderItem.deliveredQuantity || 0);
      }

      if (deliveredQuantity <= 0) {
        throw new Error(`Item ${orderItem.id} has no remaining quantity to deliver`);
      }

      return {
        sourceOrderItemId: orderItem.id,
        itemType: orderItem.itemType,
        articleId: orderItem.articleId,
        description: orderItem.description,
        orderedQuantity: orderItem.quantity,
        deliveredQuantity: deliveredQuantity,
        unitPrice: orderItem.unitPrice,
        discountPercent: orderItem.discountPercent,
        netAmount: deliveredQuantity * orderItem.unitPrice * (1 - orderItem.discountPercent / 100),
        taxRate: orderItem.taxRate,
        taxAmount: 0, // Will be calculated by entity
        totalAmount: 0, // Will be calculated by entity
        deliveryDate: orderItem.deliveryDate,
        notes: orderItem.notes
      };
    });

    // Calculate tax amounts
    deliveryItems.forEach(item => {
      item.taxAmount = item.netAmount * (item.taxRate / 100);
      item.totalAmount = item.netAmount + item.taxAmount;
    });

    // 6. Determine delivery address
    let deliveryAddress = options.deliveryAddress;
    if (!deliveryAddress) {
      if (order.shippingAddress) {
        deliveryAddress = {
          name: `Customer ${order.customerId}`,
          street: order.shippingAddress.street,
          postalCode: order.shippingAddress.postalCode,
          city: order.shippingAddress.city,
          country: order.shippingAddress.country,
          state: order.shippingAddress.state
        };
      } else {
        throw new Error('No delivery address provided and no shipping address in order');
      }
    }

    // 7. Create delivery note input
    const deliveryNoteInput: CreateDeliveryNoteInput = {
      orderId: order.id,
      customerId: order.customerId,
      deliveryAddress: deliveryAddress,
      plannedDeliveryDate: options.plannedDeliveryDate || order.deliveryDate,
      carrierInfo: options.carrierInfo,
      specialInstructions: options.specialInstructions,
      items: deliveryItems
    };

    // 8. Create the delivery note
    const deliveryNote = await this.createDeliveryNote(deliveryNoteInput, convertedBy);

    // 9. Update order status and item quantities
    await this.updateOrderAfterDeliveryCreation(order, deliveryNote, convertedBy);

    return deliveryNote;
  }

  private async updateOrderAfterDeliveryCreation(
    order: SalesOrder,
    deliveryNote: DeliveryNote,
    updatedBy: string
  ): Promise<void> {
    // Update delivered quantities in order items
    for (const deliveryItem of deliveryNote.items) {
      if (deliveryItem.sourceOrderItemId) {
        const currentDeliveredQuantity = deliveryItem.deliveredQuantity;
        
        await this.deps.salesOrderService.updateOrderItem(
          order.id,
          deliveryItem.sourceOrderItemId,
          {
            deliveredQuantity: (order.items.find(i => i.id === deliveryItem.sourceOrderItemId)?.deliveredQuantity || 0) + currentDeliveredQuantity
          }
        );
      }
    }

    // Check if order is fully delivered
    const updatedOrder = await this.deps.salesOrderService.getSalesOrderById(order.id);
    if (updatedOrder) {
      const allItemsDelivered = updatedOrder.items.every(item => 
        (item.deliveredQuantity || 0) >= item.quantity
      );

      if (allItemsDelivered) {
        await this.deps.salesOrderService.markDelivered(order.id, updatedBy);
      } else {
        await this.deps.salesOrderService.markPartiallyDelivered(order.id, updatedBy);
      }
    }
  }

  // ======================================
  // STATUS WORKFLOWS
  // ======================================

  async markReadyForPickup(deliveryNoteId: string, preparedBy: string): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.markReadyForPickup(preparedBy);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  async markInTransit(
    deliveryNoteId: string,
    shippedBy: string,
    trackingNumber?: string
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.markInTransit(shippedBy, trackingNumber);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  async markDelivered(
    deliveryNoteId: string,
    deliveredAt?: Date
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.markDelivered(deliveredAt);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  async confirmDelivery(
    deliveryNoteId: string,
    confirmedBy: string,
    deliveryProof?: {
      signatureBase64?: string;
      photoBase64?: string;
      recipientName?: string;
      notes?: string;
    }
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.confirmDelivery(confirmedBy, deliveryProof);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  async cancelDeliveryNote(
    deliveryNoteId: string,
    cancelledBy: string,
    reason: string
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    deliveryNote.cancel(cancelledBy, reason);
    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listDeliveryNotes(
    filter: DeliveryNoteFilter = {},
    sort: DeliveryNoteSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedDeliveryNoteResult> {
    return await this.deps.deliveryNoteRepository.list(filter, sort, page, pageSize);
  }

  async getDeliveryNotesByOrderId(orderId: string): Promise<DeliveryNote[]> {
    return await this.deps.deliveryNoteRepository.findByOrderId(orderId);
  }

  async getDeliveryNotesByStatus(status: DeliveryNoteStatus): Promise<DeliveryNote[]> {
    const result = await this.deps.deliveryNoteRepository.list(
      { status },
      { field: 'plannedDeliveryDate', direction: 'asc' },
      1,
      1000
    );
    return result.items;
  }

  async getOverdueDeliveries(): Promise<DeliveryNote[]> {
    const result = await this.deps.deliveryNoteRepository.list(
      { overdue: true },
      { field: 'plannedDeliveryDate', direction: 'asc' },
      1,
      1000
    );
    return result.items;
  }

  async getDeliveriesToday(): Promise<DeliveryNote[]> {
    const today = new Date();
    const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);

    const result = await this.deps.deliveryNoteRepository.list(
      {
        plannedDeliveryDateFrom: startOfDay,
        plannedDeliveryDateTo: endOfDay
      },
      { field: 'plannedDeliveryDate', direction: 'asc' },
      1,
      1000
    );
    return result.items;
  }

  // ======================================
  // BUSINESS INTELLIGENCE & ANALYTICS
  // ======================================

  async getDeliveryStatistics(): Promise<{
    total: number;
    byStatus: Record<DeliveryNoteStatus, number>;
    totalValue: number;
    averageValue: number;
    overdueCount: number;
    inTransitCount: number;
    deliveredTodayCount: number;
    averageDeliveryTime: number | null;
    onTimeDeliveryRate: number;
  }> {
    // This would be implemented in the repository, but for now return basic stats
    const allDeliveries = await this.deps.deliveryNoteRepository.list({}, { field: 'createdAt', direction: 'desc' }, 1, 10000);
    
    const byStatus: Record<DeliveryNoteStatus, number> = {
      'PREPARED': 0,
      'READY_FOR_PICKUP': 0,
      'IN_TRANSIT': 0,
      'DELIVERED': 0,
      'CONFIRMED': 0,
      'RETURNED': 0,
      'CANCELLED': 0
    };

    let totalValue = 0;
    let overdueCount = 0;
    let deliveredTodayCount = 0;
    let totalDeliveryTime = 0;
    let deliveredCount = 0;
    let onTimeCount = 0;

    const today = new Date();
    const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);

    for (const delivery of allDeliveries.items) {
      byStatus[delivery.status]++;
      totalValue += delivery.totalAmount;

      if (delivery.isOverdue()) {
        overdueCount++;
      }

      if (delivery.actualDeliveryDate && 
          delivery.actualDeliveryDate >= startOfDay && 
          delivery.actualDeliveryDate <= endOfDay) {
        deliveredTodayCount++;
      }

      const deliveryTime = delivery.getDeliveryDuration();
      if (deliveryTime !== null) {
        totalDeliveryTime += deliveryTime;
        deliveredCount++;
      }

      if (delivery.actualDeliveryDate && delivery.actualDeliveryDate <= delivery.plannedDeliveryDate) {
        onTimeCount++;
      }
    }

    return {
      total: allDeliveries.total,
      byStatus,
      totalValue,
      averageValue: allDeliveries.total > 0 ? totalValue / allDeliveries.total : 0,
      overdueCount,
      inTransitCount: byStatus['IN_TRANSIT'],
      deliveredTodayCount,
      averageDeliveryTime: deliveredCount > 0 ? totalDeliveryTime / deliveredCount : null,
      onTimeDeliveryRate: deliveredCount > 0 ? (onTimeCount / deliveredCount) * 100 : 0
    };
  }

  // ======================================
  // INTEGRATION HELPERS
  // ======================================

  async prepareForInvoicing(deliveryNoteId: string): Promise<{
    canPrepareInvoice: boolean;
    invoiceableItems: DeliveryNoteItem[];
    issues: string[];
  }> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    const canPrepareInvoice = deliveryNote.canBeConfirmed() || deliveryNote.status === 'CONFIRMED';
    const invoiceableItems = deliveryNote.items.filter(item => 
      item.deliveredQuantity > 0
    );
    
    const issues: string[] = [];
    if (!canPrepareInvoice) {
      issues.push(`Delivery note status '${deliveryNote.status}' does not allow invoice preparation`);
    }
    if (invoiceableItems.length === 0) {
      issues.push('No delivered items available for invoicing');
    }

    return {
      canPrepareInvoice,
      invoiceableItems,
      issues
    };
  }

  async updateDeliveryQuantities(
    deliveryNoteId: string,
    itemQuantities: { [itemId: string]: number },
    updatedBy: string
  ): Promise<DeliveryNote> {
    const deliveryNote = await this.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    for (const [itemId, quantity] of Object.entries(itemQuantities)) {
      deliveryNote.updateItem(itemId, { deliveredQuantity: quantity }, updatedBy);
    }

    return await this.deps.deliveryNoteRepository.update(deliveryNote);
  }
}
