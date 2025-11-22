/**
 * Sales Invoice Repository
 * Complete CRUD operations for Sales Invoices
 */

import { SalesInvoice, SalesInvoiceStatus } from '../../domain/entities/sales-invoice';

export interface SalesInvoiceFilter {
  customerId?: string;
  sourceOrderId?: string;
  sourceDeliveryNoteId?: string;
  status?: SalesInvoiceStatus;
  invoiceDateFrom?: Date;
  invoiceDateTo?: Date;
  dueDateFrom?: Date;
  dueDateTo?: Date;
  totalAmountMin?: number;
  totalAmountMax?: number;
  overdue?: boolean;
  createdBy?: string;
  search?: string; // Search in invoiceNumber, subject, description
}

export interface SalesInvoiceSort {
  field: 'createdAt' | 'updatedAt' | 'invoiceDate' | 'dueDate' | 'totalAmount' | 'invoiceNumber' | 'status' | 'remainingAmount';
  direction: 'asc' | 'desc';
}

export interface PaginatedSalesInvoiceResult {
  items: SalesInvoice[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export class SalesInvoiceRepository {
  private invoices: Map<string, SalesInvoice> = new Map();

  async create(invoice: SalesInvoice): Promise<SalesInvoice> {
    this.invoices.set(invoice.id, invoice);
    return invoice;
  }

  async findById(id: string): Promise<SalesInvoice | null> {
    return this.invoices.get(id) || null;
  }

  async findByInvoiceNumber(invoiceNumber: string): Promise<SalesInvoice | null> {
    for (const invoice of this.invoices.values()) {
      if (invoice.invoiceNumber === invoiceNumber) {
        return invoice;
      }
    }
    return null;
  }

  async update(invoice: SalesInvoice): Promise<SalesInvoice> {
    if (!this.invoices.has(invoice.id)) {
      throw new Error('Invoice not found');
    }
    this.invoices.set(invoice.id, invoice);
    return invoice;
  }

  async delete(id: string): Promise<boolean> {
    return this.invoices.delete(id);
  }

  async findByCustomerId(customerId: string): Promise<SalesInvoice[]> {
    const invoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (invoice.customerId === customerId) {
        invoices.push(invoice);
      }
    }
    return invoices.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByOrderId(orderId: string): Promise<SalesInvoice[]> {
    const invoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (invoice.sourceOrderId === orderId) {
        invoices.push(invoice);
      }
    }
    return invoices.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByDeliveryNoteId(deliveryNoteId: string): Promise<SalesInvoice[]> {
    const invoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (invoice.sourceDeliveryNoteId === deliveryNoteId) {
        invoices.push(invoice);
      }
    }
    return invoices.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findByStatus(status: SalesInvoiceStatus): Promise<SalesInvoice[]> {
    const invoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (invoice.status === status) {
        invoices.push(invoice);
      }
    }
    return invoices.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async findOverdueInvoices(): Promise<SalesInvoice[]> {
    const overdueInvoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (invoice.isOverdue()) {
        overdueInvoices.push(invoice);
      }
    }
    return overdueInvoices.sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());
  }

  async findUnpaidInvoices(): Promise<SalesInvoice[]> {
    const unpaidInvoices: SalesInvoice[] = [];
    for (const invoice of this.invoices.values()) {
      if (['ISSUED', 'SENT', 'PARTIAL_PAID', 'OVERDUE'].includes(invoice.status)) {
        unpaidInvoices.push(invoice);
      }
    }
    return unpaidInvoices.sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());
  }

  async list(
    filter: SalesInvoiceFilter = {},
    sort: SalesInvoiceSort = { field: 'createdAt', direction: 'desc' },
    page: number = 1,
    pageSize: number = 20
  ): Promise<PaginatedSalesInvoiceResult> {
    let filteredInvoices = Array.from(this.invoices.values());

    // Apply filters
    if (filter.customerId) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.customerId === filter.customerId);
    }

    if (filter.sourceOrderId) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.sourceOrderId === filter.sourceOrderId);
    }

    if (filter.sourceDeliveryNoteId) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.sourceDeliveryNoteId === filter.sourceDeliveryNoteId);
    }

    if (filter.status) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.status === filter.status);
    }

    if (filter.invoiceDateFrom) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.invoiceDate >= filter.invoiceDateFrom!);
    }

    if (filter.invoiceDateTo) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.invoiceDate <= filter.invoiceDateTo!);
    }

    if (filter.dueDateFrom) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.dueDate >= filter.dueDateFrom!);
    }

    if (filter.dueDateTo) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.dueDate <= filter.dueDateTo!);
    }

    if (filter.totalAmountMin !== undefined) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.totalAmount >= filter.totalAmountMin!);
    }

    if (filter.totalAmountMax !== undefined) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.totalAmount <= filter.totalAmountMax!);
    }

    if (filter.overdue === true) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.isOverdue());
    }

    if (filter.createdBy) {
      filteredInvoices = filteredInvoices.filter(invoice => invoice.createdBy === filter.createdBy);
    }

    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      filteredInvoices = filteredInvoices.filter(invoice => 
        invoice.invoiceNumber.toLowerCase().includes(searchLower) ||
        invoice.subject.toLowerCase().includes(searchLower) ||
        invoice.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply sorting
    filteredInvoices.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sort.field) {
        case 'createdAt':
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
          break;
        case 'updatedAt':
          aValue = a.updatedAt.getTime();
          bValue = b.updatedAt.getTime();
          break;
        case 'invoiceDate':
          aValue = a.invoiceDate.getTime();
          bValue = b.invoiceDate.getTime();
          break;
        case 'dueDate':
          aValue = a.dueDate.getTime();
          bValue = b.dueDate.getTime();
          break;
        case 'totalAmount':
          aValue = a.totalAmount;
          bValue = b.totalAmount;
          break;
        case 'remainingAmount':
          aValue = a.remainingAmount;
          bValue = b.remainingAmount;
          break;
        case 'invoiceNumber':
          aValue = a.invoiceNumber;
          bValue = b.invoiceNumber;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          aValue = a.createdAt.getTime();
          bValue = b.createdAt.getTime();
      }

      if (sort.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    // Apply pagination
    const total = filteredInvoices.length;
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const items = filteredInvoices.slice(startIndex, endIndex);

    return {
      items,
      total,
      page,
      pageSize,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    };
  }

  async getStatistics(): Promise<{
    total: number;
    byStatus: Record<SalesInvoiceStatus, number>;
    totalValue: number;
    totalOutstanding: number;
    totalPaid: number;
    averageValue: number;
    overdueCount: number;
    overdueAmount: number;
    collectionRate: number;
  }> {
    const allInvoices = Array.from(this.invoices.values());
    const total = allInvoices.length;

    // Count by status
    const byStatus: Record<SalesInvoiceStatus, number> = {
      'DRAFT': 0,
      'ISSUED': 0,
      'SENT': 0,
      'PAID': 0,
      'PARTIAL_PAID': 0,
      'OVERDUE': 0,
      'CANCELLED': 0
    };

    let totalValue = 0;
    let totalPaid = 0;
    let overdueCount = 0;
    let overdueAmount = 0;

    for (const invoice of allInvoices) {
      byStatus[invoice.status]++;
      totalValue += invoice.totalAmount;
      totalPaid += invoice.paidAmount;

      if (invoice.isOverdue()) {
        overdueCount++;
        overdueAmount += invoice.remainingAmount;
      }
    }

    const totalOutstanding = totalValue - totalPaid;
    const averageValue = total > 0 ? totalValue / total : 0;
    const collectionRate = totalValue > 0 ? (totalPaid / totalValue) * 100 : 0;

    return {
      total,
      byStatus,
      totalValue,
      totalOutstanding,
      totalPaid,
      averageValue,
      overdueCount,
      overdueAmount,
      collectionRate
    };
  }

  async isInvoiceNumberUnique(invoiceNumber: string, excludeId?: string): Promise<boolean> {
    for (const invoice of this.invoices.values()) {
      if (invoice.invoiceNumber === invoiceNumber && invoice.id !== excludeId) {
        return false;
      }
    }
    return true;
  }
}
