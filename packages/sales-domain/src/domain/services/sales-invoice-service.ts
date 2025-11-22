/**
 * Sales Invoice Service
 * Complete Invoice Management with Delivery-to-Invoice Conversion
 */

import { SalesInvoice, SalesInvoiceItem, CreateSalesInvoiceInput, UpdateSalesInvoiceInput, SalesInvoiceStatus } from '../entities/sales-invoice';
import { SalesInvoiceRepository, SalesInvoiceFilter, SalesInvoiceSort, PaginatedSalesInvoiceResult } from '../../infra/repositories/sales-invoice-repository';
import { DeliveryNoteService } from './delivery-note-service';
import { SalesOrderService } from './sales-order-service';
import { DeliveryNote } from '../entities/delivery-note';
import { SalesOrder } from '../entities/sales-order';

export interface SalesInvoiceServiceDependencies {
  salesInvoiceRepository: SalesInvoiceRepository;
  deliveryNoteService: DeliveryNoteService;
  salesOrderService: SalesOrderService;
}

export interface ConvertDeliveryToInvoiceOptions {
  invoiceDate?: Date;
  dueDate?: Date;
  paymentTerms?: string;
  currency?: string;
  taxRate?: number;
  billingAddress?: {
    name: string;
    street: string;
    postalCode: string;
    city: string;
    country: string;
    state?: string;
  };
  notes?: string;
  partialInvoicing?: {
    itemQuantities: { [itemId: string]: number }; // Partial quantities per item
  };
}

export class SalesInvoiceService {
  constructor(private deps: SalesInvoiceServiceDependencies) {}

  // ======================================
  // CORE CRUD OPERATIONS
  // ======================================

  async createSalesInvoice(
    input: CreateSalesInvoiceInput,
    createdBy: string
  ): Promise<SalesInvoice> {
    // Convert items to full SalesInvoiceItem objects
    const invoiceItems: SalesInvoiceItem[] = input.items.map(item => ({
      ...item,
      id: '', // Will be set by entity constructor
      createdAt: new Date(),
      updatedAt: new Date()
    }));

    const invoice = new SalesInvoice(
      input.customerId,
      input.subject,
      input.description,
      input.invoiceDate,
      input.dueDate,
      input.billingAddress,
      invoiceItems,
      createdBy,
      {
        sourceOrderId: input.sourceOrderId,
        sourceDeliveryNoteId: input.sourceDeliveryNoteId,
        paymentTerms: input.paymentTerms,
        currency: input.currency,
        taxRate: input.taxRate,
        notes: input.notes
      }
    );

    return await this.deps.salesInvoiceRepository.create(invoice);
  }

  async getSalesInvoiceById(id: string): Promise<SalesInvoice | null> {
    return await this.deps.salesInvoiceRepository.findById(id);
  }

  async getSalesInvoiceByNumber(invoiceNumber: string): Promise<SalesInvoice | null> {
    return await this.deps.salesInvoiceRepository.findByInvoiceNumber(invoiceNumber);
  }

  async updateSalesInvoice(
    id: string,
    updates: UpdateSalesInvoiceInput,
    updatedBy: string
  ): Promise<SalesInvoice> {
    const invoice = await this.getSalesInvoiceById(id);
    if (!invoice) {
      throw new Error('Sales invoice not found');
    }

    invoice.updateBasicInfo(updates, updatedBy);
    return await this.deps.salesInvoiceRepository.update(invoice);
  }

  async deleteSalesInvoice(id: string): Promise<boolean> {
    const invoice = await this.getSalesInvoiceById(id);
    if (!invoice) {
      return false;
    }

    if (invoice.status !== 'DRAFT') {
      throw new Error('Can only delete draft invoices');
    }

    return await this.deps.salesInvoiceRepository.delete(id);
  }

  // ======================================
  // CRITICAL: DELIVERY-TO-INVOICE CONVERSION
  // ======================================

  async convertDeliveryToInvoice(
    deliveryNoteId: string,
    convertedBy: string,
    options: ConvertDeliveryToInvoiceOptions = {}
  ): Promise<SalesInvoice> {
    // 1. Get and validate the delivery note
    const deliveryNote = await this.deps.deliveryNoteService.getDeliveryNoteById(deliveryNoteId);
    if (!deliveryNote) {
      throw new Error('Delivery note not found');
    }

    // 2. Validate delivery note status - must be DELIVERED or CONFIRMED
    if (!['DELIVERED', 'CONFIRMED'].includes(deliveryNote.status)) {
      throw new Error('Can only create invoices from delivered or confirmed delivery notes');
    }

    // 3. Check if delivery note can be invoiced
    const preparationInfo = await this.deps.deliveryNoteService.prepareForInvoicing(deliveryNoteId);
    if (!preparationInfo.canPrepareInvoice) {
      throw new Error(`Cannot prepare invoice: ${preparationInfo.issues.join(', ')}`);
    }

    // 4. Check for existing invoices
    const existingInvoices = await this.getSalesInvoicesByDeliveryNote(deliveryNoteId);
    const hasActiveInvoices = existingInvoices.some(inv => 
      !['CANCELLED'].includes(inv.status)
    );
    
    if (hasActiveInvoices && !options.partialInvoicing) {
      throw new Error('Delivery note already has active invoices. Use partial invoicing if needed.');
    }

    // 5. Get related order for additional context
    let relatedOrder: SalesOrder | null = null;
    if (deliveryNote.orderId) {
      relatedOrder = await this.deps.salesOrderService.getSalesOrderById(deliveryNote.orderId);
    }

    // 6. Determine invoice quantities
    const invoiceItems: Omit<SalesInvoiceItem, 'id' | 'createdAt' | 'updatedAt'>[] = deliveryNote.items.map(deliveryItem => {
      let invoicedQuantity = deliveryItem.deliveredQuantity;

      // Handle partial invoicing
      if (options.partialInvoicing?.itemQuantities?.[deliveryItem.id]) {
        invoicedQuantity = Math.min(
          options.partialInvoicing.itemQuantities[deliveryItem.id],
          deliveryItem.deliveredQuantity
        );
      }

      if (invoicedQuantity <= 0) {
        throw new Error(`Item ${deliveryItem.id} has no quantity to invoice`);
      }

      // Calculate amounts based on invoiced quantity
      const unitPrice = deliveryItem.unitPrice;
      const discountPercent = deliveryItem.discountPercent;
      const taxRate = options.taxRate || deliveryItem.taxRate;
      
      const netAmount = invoicedQuantity * unitPrice * (1 - discountPercent / 100);
      const taxAmount = netAmount * (taxRate / 100);
      const totalAmount = netAmount + taxAmount;

      return {
        sourceOrderItemId: deliveryItem.sourceOrderItemId,
        sourceDeliveryItemId: deliveryItem.id,
        itemType: deliveryItem.itemType,
        articleId: deliveryItem.articleId,
        description: deliveryItem.description,
        deliveredQuantity: deliveryItem.deliveredQuantity,
        invoicedQuantity: invoicedQuantity,
        unitPrice: unitPrice,
        discountPercent: discountPercent,
        netAmount: netAmount,
        taxRate: taxRate,
        taxAmount: taxAmount,
        totalAmount: totalAmount,
        notes: deliveryItem.notes
      };
    });

    // 7. Determine billing address
    let billingAddress = options.billingAddress;
    if (!billingAddress) {
      billingAddress = {
        name: `Customer ${deliveryNote.customerId}`,
        street: deliveryNote.deliveryAddress.street,
        postalCode: deliveryNote.deliveryAddress.postalCode,
        city: deliveryNote.deliveryAddress.city,
        country: deliveryNote.deliveryAddress.country,
        state: deliveryNote.deliveryAddress.state
      };
    }

    // 8. Calculate dates
    const invoiceDate = options.invoiceDate || new Date();
    let dueDate = options.dueDate;
    if (!dueDate) {
      // Default 30 days from invoice date
      dueDate = new Date(invoiceDate);
      dueDate.setDate(dueDate.getDate() + 30);
    }

    // 9. Create invoice input
    const invoiceInput: CreateSalesInvoiceInput = {
      customerId: deliveryNote.customerId,
      sourceOrderId: deliveryNote.orderId,
      sourceDeliveryNoteId: deliveryNote.id,
      subject: relatedOrder?.subject || `Invoice for Delivery ${deliveryNote.deliveryNoteNumber}`,
      description: relatedOrder?.description || `Invoice for delivered goods according to delivery note ${deliveryNote.deliveryNoteNumber}`,
      invoiceDate: invoiceDate,
      dueDate: dueDate,
      paymentTerms: options.paymentTerms || relatedOrder?.paymentTerms || '30 days net',
      currency: options.currency || relatedOrder?.currency || 'EUR',
      taxRate: options.taxRate || relatedOrder?.taxRate || 19.0,
      billingAddress: billingAddress,
      notes: options.notes,
      items: invoiceItems
    };

    // 10. Create the invoice
    const invoice = await this.createSalesInvoice(invoiceInput, convertedBy);

    // 11. Update related order item invoiced quantities
    await this.updateOrderAfterInvoiceCreation(relatedOrder, invoice, convertedBy);

    return invoice;
  }

  private async updateOrderAfterInvoiceCreation(
    order: SalesOrder | null,
    invoice: SalesInvoice,
    updatedBy: string
  ): Promise<void> {
    if (!order) return;

    // Update invoiced quantities in order items
    for (const invoiceItem of invoice.items) {
      if (invoiceItem.sourceOrderItemId) {
        const currentInvoicedQuantity = invoiceItem.invoicedQuantity;
        
        await this.deps.salesOrderService.updateOrderItem(
          order.id,
          invoiceItem.sourceOrderItemId,
          {
            invoicedQuantity: (order.items.find(i => i.id === invoiceItem.sourceOrderItemId)?.invoicedQuantity || 0) + currentInvoicedQuantity
          }
        );
      }
    }

    // Check if order is fully invoiced
    const updatedOrder = await this.deps.salesOrderService.getSalesOrderById(order.id);
    if (updatedOrder) {
      const allItemsInvoiced = updatedOrder.items.every(item => 
        (item.invoicedQuantity || 0) >= (item.deliveredQuantity || 0)
      );

      if (allItemsInvoiced && updatedOrder.status === 'DELIVERED') {
        await this.deps.salesOrderService.markInvoiced(order.id, updatedBy);
      }
    }
  }

  // ======================================
  // STATUS WORKFLOWS
  // ======================================

  async issueInvoice(invoiceId: string, issuedBy: string): Promise<SalesInvoice> {
    const invoice = await this.getSalesInvoiceById(invoiceId);
    if (!invoice) {
      throw new Error('Sales invoice not found');
    }

    invoice.issue(issuedBy);
    return await this.deps.salesInvoiceRepository.update(invoice);
  }

  async sendInvoice(invoiceId: string, sentBy: string): Promise<SalesInvoice> {
    const invoice = await this.getSalesInvoiceById(invoiceId);
    if (!invoice) {
      throw new Error('Sales invoice not found');
    }

    invoice.send(sentBy);
    return await this.deps.salesInvoiceRepository.update(invoice);
  }

  async recordPayment(
    invoiceId: string,
    amount: number,
    paidBy: string
  ): Promise<SalesInvoice> {
    const invoice = await this.getSalesInvoiceById(invoiceId);
    if (!invoice) {
      throw new Error('Sales invoice not found');
    }

    invoice.recordPayment(amount, paidBy);
    return await this.deps.salesInvoiceRepository.update(invoice);
  }

  async markOverdue(): Promise<SalesInvoice[]> {
    const unpaidInvoices = await this.deps.salesInvoiceRepository.findUnpaidInvoices();
    const updatedInvoices: SalesInvoice[] = [];

    for (const invoice of unpaidInvoices) {
      if (invoice.isOverdue() && !['OVERDUE'].includes(invoice.status)) {
        invoice.markOverdue();
        await this.deps.salesInvoiceRepository.update(invoice);
        updatedInvoices.push(invoice);
      }
    }

    return updatedInvoices;
  }

  async cancelInvoice(
    invoiceId: string,
    cancelledBy: string,
    reason: string
  ): Promise<SalesInvoice> {
    const invoice = await this.getSalesInvoiceById(invoiceId);
    if (!invoice) {
      throw new Error('Sales invoice not found');
    }

    invoice.cancel(cancelledBy, reason);
    return await this.deps.salesInvoiceRepository.update(invoice);
  }

  // ======================================
  // QUERY METHODS
  // ======================================

  async listSalesInvoices(
    filter: SalesInvoiceFilter = {},
    sort: SalesInvoiceSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedSalesInvoiceResult> {
    return await this.deps.salesInvoiceRepository.list(filter, sort, page, pageSize);
  }

  async getSalesInvoicesByCustomer(customerId: string): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findByCustomerId(customerId);
  }

  async getSalesInvoicesByOrder(orderId: string): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findByOrderId(orderId);
  }

  async getSalesInvoicesByDeliveryNote(deliveryNoteId: string): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findByDeliveryNoteId(deliveryNoteId);
  }

  async getSalesInvoicesByStatus(status: SalesInvoiceStatus): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findByStatus(status);
  }

  async getOverdueInvoices(): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findOverdueInvoices();
  }

  async getUnpaidInvoices(): Promise<SalesInvoice[]> {
    return await this.deps.salesInvoiceRepository.findUnpaidInvoices();
  }

  // ======================================
  // BUSINESS INTELLIGENCE & ANALYTICS
  // ======================================

  async getSalesInvoiceStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesInvoiceStatus, number>;
    totalValue: number;
    totalOutstanding: number;
    totalPaid: number;
    averageValue: number;
    overdueCount: number;
    overdueAmount: number;
    collectionRate: number;
    averageDaysToPayment?: number;
    monthlyRevenue: { [month: string]: number };
  }> {
    const baseStats = await this.deps.salesInvoiceRepository.getStatistics();
    
    // Calculate additional metrics
    const paidInvoices = await this.getSalesInvoicesByStatus('PAID');
    let totalDaysToPayment = 0;
    let paidInvoiceCount = 0;

    for (const invoice of paidInvoices) {
      if (invoice.paidAt && invoice.issuedAt) {
        const daysToPayment = Math.ceil((invoice.paidAt.getTime() - invoice.issuedAt.getTime()) / (1000 * 60 * 60 * 24));
        totalDaysToPayment += daysToPayment;
        paidInvoiceCount++;
      }
    }

    const averageDaysToPayment = paidInvoiceCount > 0 ? totalDaysToPayment / paidInvoiceCount : undefined;

    // Calculate monthly revenue (last 12 months)
    const monthlyRevenue: { [month: string]: number } = {};
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
      monthlyRevenue[monthKey] = 0;
    }

    const allInvoices = await this.listSalesInvoices({}, { field: 'createdAt', direction: 'desc' }, 1, 10000);
    for (const invoice of allInvoices.items) {
      if (['PAID'].includes(invoice.status)) {
        const monthKey = `${invoice.invoiceDate.getFullYear()}-${(invoice.invoiceDate.getMonth() + 1).toString().padStart(2, '0')}`;
        if (monthlyRevenue[monthKey] !== undefined) {
          monthlyRevenue[monthKey] += invoice.totalAmount;
        }
      }
    }

    return {
      ...baseStats,
      averageDaysToPayment,
      monthlyRevenue
    };
  }
}
