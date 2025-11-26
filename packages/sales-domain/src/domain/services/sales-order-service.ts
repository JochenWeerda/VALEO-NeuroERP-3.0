/**
 * Sales Order Service
 * Complete Order Management with Offer-to-Order Conversion
 */

import { SalesOrder, SalesOrderItem, CreateSalesOrderInput, UpdateSalesOrderInput, SalesOrderStatus } from '../entities/sales-order';
import { SalesOrderRepository, SalesOrderFilter, SalesOrderSort, PaginatedSalesOrderResult } from '../../infra/repositories/sales-order-repository';
import { SalesOfferService } from './sales-offer-service';
import { SalesOffer } from '../entities/sales-offer';

export interface SalesOrderServiceDependencies {
  salesOrderRepository: SalesOrderRepository;
  salesOfferService: SalesOfferService;
}

export class SalesOrderService {
  constructor(private deps: SalesOrderServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createSalesOrder(
    input: CreateSalesOrderInput,
    createdBy: string
  ): Promise<SalesOrder> {
    // Convert items to full SalesOrderItem objects
    const orderItems: SalesOrderItem[] = input.items.map(item => ({
      ...item,
      id: '', // Will be set by entity constructor
      createdAt: new Date(),
      updatedAt: new Date(),
      deliveredQuantity: 0,
      invoicedQuantity: 0
    }));

    const order = new SalesOrder(
      input.customerId,
      input.subject,
      input.description,
      input.deliveryDate,
      orderItems,
      createdBy,
      {
        sourceOfferId: input.sourceOfferId,
        contactPerson: input.contactPerson,
        paymentTerms: input.paymentTerms,
        currency: input.currency,
        taxRate: input.taxRate,
        shippingAddress: input.shippingAddress,
        billingAddress: input.billingAddress,
        notes: input.notes
      }
    );

    return await this.deps.salesOrderRepository.create(order);
  }

  async getSalesOrderById(id: string): Promise<SalesOrder | null> {
    return await this.deps.salesOrderRepository.findById(id);
  }

  async getSalesOrderByNumber(orderNumber: string): Promise<SalesOrder | null> {
    return await this.deps.salesOrderRepository.findByOrderNumber(orderNumber);
  }

  async updateSalesOrder(
    id: string,
    updates: UpdateSalesOrderInput,
    updatedBy: string
  ): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(id);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.updateBasicInfo(updates, updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async deleteSalesOrder(id: string): Promise<boolean> {
    const order = await this.getSalesOrderById(id);
    if (!order) {
      return false;
    }

    if (order.status !== 'DRAFT') {
      throw new Error('Can only delete draft orders');
    }

    return await this.deps.salesOrderRepository.delete(id);
  }

  // ======================================
  // ITEM MANAGEMENT
  // ======================================

  async addItemToOrder(
    orderId: string,
    item: Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt' | 'deliveredQuantity' | 'invoicedQuantity'>
  ): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    const itemWithDefaults = {
      ...item,
      deliveredQuantity: 0,
      invoicedQuantity: 0
    };

    order.addItem(itemWithDefaults);
    return await this.deps.salesOrderRepository.update(order);
  }

  async updateOrderItem(
    orderId: string,
    itemId: string,
    updates: Partial<Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.updateItem(itemId, updates);
    return await this.deps.salesOrderRepository.update(order);
  }

  async removeItemFromOrder(orderId: string, itemId: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.removeItem(itemId);
    return await this.deps.salesOrderRepository.update(order);
  }

  // ======================================
  // STATUS WORKFLOWS
  // ======================================

  async confirmOrder(orderId: string, confirmedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.confirm(confirmedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async startOrderProgress(orderId: string, updatedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.startProgress(updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async markPartiallyDelivered(orderId: string, updatedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.markPartiallyDelivered(updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async markDelivered(orderId: string, updatedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.markDelivered(updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async markInvoiced(orderId: string, updatedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.markInvoiced(updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async markCompleted(orderId: string, updatedBy: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.markCompleted(updatedBy);
    return await this.deps.salesOrderRepository.update(order);
  }

  async cancelOrder(orderId: string, cancelledBy: string, reason: string): Promise<SalesOrder> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    order.cancel(cancelledBy, reason);
    return await this.deps.salesOrderRepository.update(order);
  }

  // ======================================
  // CRITICAL: OFFER-TO-ORDER CONVERSION
  // ======================================

  async convertOfferToOrder(
    offerId: string,
    convertedBy: string,
    options: {
      deliveryDate?: Date;
      notes?: string;
      paymentTerms?: string;
    } = {}
  ): Promise<SalesOrder> {
    // 1. Get and validate the sales offer
    const offer = await this.deps.salesOfferService.getSalesOfferById(offerId);
    if (!offer) {
      throw new Error('Sales offer not found');
    }

    // 2. Validate offer status - must be ACCEPTED
    if (offer.status !== 'ANGENOMMEN') {
      throw new Error('Can only convert accepted sales offers to orders');
    }

    // 3. Check if offer is still valid (not expired)
    if (offer.validUntil < new Date()) {
      throw new Error('Cannot convert expired sales offer');
    }

    // 4. Check if already converted
    const existingOrders = await this.getSalesOrdersBySourceOffer(offerId);
    if (existingOrders.length > 0) {
      throw new Error('Sales offer has already been converted to an order');
    }

    // 5. Convert offer items to order items
    const orderItems: Omit<SalesOrderItem, 'id' | 'createdAt' | 'updatedAt'>[] = offer.items.map(offerItem => ({
      itemType: offerItem.itemType,
      articleId: offerItem.articleId,
      description: offerItem.description,
      quantity: offerItem.quantity,
      unitPrice: offerItem.unitPrice,
      discountPercent: offerItem.discountPercent,
      netAmount: offerItem.netAmount,
      taxRate: offerItem.taxRate,
      taxAmount: offerItem.taxAmount,
      totalAmount: offerItem.totalAmount,
      deliveryDate: options.deliveryDate || offer.deliveryDate,
      notes: offerItem.notes,
      deliveredQuantity: 0,
      invoicedQuantity: 0
    }));

    // 6. Create order input from offer data
    const orderInput: CreateSalesOrderInput = {
      customerId: offer.customerId,
      sourceOfferId: offer.id,
      subject: `Auftrag aus Angebot ${offer.offerNumber}`,
      description: offer.description,
      deliveryDate: options.deliveryDate || offer.deliveryDate,
      contactPerson: offer.contactPerson,
      paymentTerms: options.paymentTerms || offer.paymentTerms,
      currency: offer.currency,
      taxRate: offer.taxRate,
      notes: options.notes || offer.notes,
      items: orderItems
    };

    // 7. Create the sales order
    const order = await this.createSalesOrder(orderInput, convertedBy);

    // 8. Update offer status to indicate it has been converted
    // Note: We might want to add a 'CONVERTED' status to SalesOffer in the future
    // For now, we keep it as 'ANGENOMMEN' and rely on the sourceOfferId link

    return order;
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listSalesOrders(
    filter: SalesOrderFilter = {},
    sort: SalesOrderSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedSalesOrderResult> {
    return await this.deps.salesOrderRepository.list(filter, sort, page, pageSize);
  }

  async getSalesOrdersByCustomer(customerId: string): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findByCustomerId(customerId);
  }

  async getSalesOrdersBySourceOffer(sourceOfferId: string): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findBySourceOfferId(sourceOfferId);
  }

  async getSalesOrdersByStatus(status: SalesOrderStatus): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findByStatus(status);
  }

  async getOverdueSalesOrders(): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findOverdueOrders();
  }

  async getPendingConfirmationOrders(): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findPendingConfirmation();
  }

  async getInProgressOrders(): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findInProgress();
  }

  async getSalesOrdersByDeliveryDateRange(startDate: Date, endDate: Date): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findByDeliveryDateRange(startDate, endDate);
  }

  // ======================================
  // STATISTICS & ANALYTICS
  // ======================================

  async getSalesOrderStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesOrderStatus, number>;
    totalValue: number;
    averageValue: number;
    overdueCount: number;
    pendingConfirmationCount: number;
    completionRate: number;
  }> {
    return await this.deps.salesOrderRepository.getStatistics();
  }

  async getHighValueOrders(minAmount: number = 10000): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findHighValueOrders(minAmount);
  }

  async getRecentOrdersForCustomer(customerId: string, limit: number = 5): Promise<SalesOrder[]> {
    return await this.deps.salesOrderRepository.findRecentOrdersForCustomer(customerId, limit);
  }

  // ======================================
  // VALIDATION HELPERS
  // ======================================

  async isOrderNumberUnique(orderNumber: string, excludeId?: string): Promise<boolean> {
    return await this.deps.salesOrderRepository.isOrderNumberUnique(orderNumber, excludeId);
  }

  async canOrderBeDelivered(orderId: string): Promise<boolean> {
    const order = await this.getSalesOrderById(orderId);
    return order ? order.canBeDelivered() : false;
  }

  async canOrderBeInvoiced(orderId: string): Promise<boolean> {
    const order = await this.getSalesOrderById(orderId);
    return order ? order.canBeInvoiced() : false;
  }

  async canOrderBeCancelled(orderId: string): Promise<boolean> {
    const order = await this.getSalesOrderById(orderId);
    return order ? order.canBeCancelled() : false;
  }

  // ======================================
  // BUSINESS LOGIC HELPERS
  // ======================================

  async updateDeliveryDate(
    orderId: string,
    newDeliveryDate: Date,
    updatedBy: string
  ): Promise<SalesOrder> {
    return await this.updateSalesOrder(orderId, { deliveryDate: newDeliveryDate }, updatedBy);
  }

  async updatePaymentTerms(
    orderId: string,
    newPaymentTerms: string,
    updatedBy: string
  ): Promise<SalesOrder> {
    return await this.updateSalesOrder(orderId, { paymentTerms: newPaymentTerms }, updatedBy);
  }

  async getOrdersByDateRange(startDate: Date, endDate: Date): Promise<SalesOrder[]> {
    return await this.listSalesOrders(
      {
        orderDateFrom: startDate,
        orderDateTo: endDate
      },
      { field: 'orderDate', direction: 'asc' },
      1,
      1000
    ).then(result => result.items);
  }

  async countOrdersByDate(startDate: Date, endDate: Date): Promise<number> {
    return await this.deps.salesOrderRepository.countOrdersByDate(startDate, endDate);
  }

  // ======================================
  // FUTURE: INTEGRATION HOOKS
  // ======================================

  async prepareForDelivery(orderId: string): Promise<{
    canPrepareDelivery: boolean;
    deliverableItems: SalesOrderItem[];
    issues: string[];
  }> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    const canPrepareDelivery = order.canBeDelivered();
    const deliverableItems = order.items.filter(item => 
      (item.deliveredQuantity || 0) < item.quantity
    );
    
    const issues: string[] = [];
    if (!canPrepareDelivery) {
      issues.push(`Order status '${order.status}' does not allow delivery preparation`);
    }
    if (deliverableItems.length === 0) {
      issues.push('All items have already been delivered');
    }

    return {
      canPrepareDelivery,
      deliverableItems,
      issues
    };
  }

  async prepareForInvoicing(orderId: string): Promise<{
    canPrepareInvoice: boolean;
    invoiceableItems: SalesOrderItem[];
    issues: string[];
  }> {
    const order = await this.getSalesOrderById(orderId);
    if (!order) {
      throw new Error('Sales order not found');
    }

    const canPrepareInvoice = order.canBeInvoiced();
    const invoiceableItems = order.items.filter(item => 
      (item.invoicedQuantity || 0) < (item.deliveredQuantity || 0)
    );
    
    const issues: string[] = [];
    if (!canPrepareInvoice) {
      issues.push(`Order status '${order.status}' does not allow invoice preparation`);
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
}
