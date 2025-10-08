import { InvoiceEntity, CreateInvoiceInput, UpdateInvoiceInput, InvoiceStatusType } from '../entities';
import { InvoiceRepository } from '../../infra/repo';

export interface InvoiceServiceDependencies {
  invoiceRepo: InvoiceRepository;
}

export interface CreateInvoiceData extends CreateInvoiceInput {
  tenantId: string;
  invoiceNumber: string;
  lines: any[];
}

export interface UpdateInvoiceData extends UpdateInvoiceInput {
  tenantId: string;
}

export class InvoiceService {
  constructor(private deps: InvoiceServiceDependencies) {}

  async createInvoice(data: CreateInvoiceData): Promise<InvoiceEntity> {
    // Business validation
    if (data.lines.length === 0) {
      throw new Error('Invoice must have at least one line item');
    }

    // Check if invoice number already exists
    const existingInvoice = await this.deps.invoiceRepo.findByNumber(data.invoiceNumber, data.tenantId);
    if (existingInvoice) {
      throw new Error(`Invoice number ${data.invoiceNumber} already exists`);
    }

    // Validate line items
    for (const line of data.lines) {
      if (line.quantity <= 0) {
        throw new Error('Line item quantity must be positive');
      }
      if (line.unitPrice < 0) {
        throw new Error('Line item unit price cannot be negative');
      }
    }

    const invoice = await this.deps.invoiceRepo.create(data);
    return invoice;
  }

  async getInvoice(id: string, tenantId: string): Promise<InvoiceEntity | null> {
    return this.deps.invoiceRepo.findById(id, tenantId);
  }

  async updateInvoice(id: string, data: UpdateInvoiceData): Promise<InvoiceEntity> {
    const existingInvoice = await this.deps.invoiceRepo.findById(id, data.tenantId);
    if (existingInvoice === undefined || existingInvoice === null) {
      throw new Error(`Invoice ${id} not found`);
    }

    const updatedInvoice = await this.deps.invoiceRepo.update(id, data.tenantId, data);

    if (updatedInvoice === undefined || updatedInvoice === null) {
      throw new Error(`Failed to update invoice ${id}`);
    }

    return updatedInvoice;
  }

  async markInvoiceAsPaid(id: string, tenantId: string): Promise<InvoiceEntity> {
    const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
    if (invoice === undefined || invoice === null) {
      throw new Error(`Invoice ${id} not found`);
    }

    if (!invoice.canBePaid()) {
      throw new Error('Invoice cannot be marked as paid in its current state');
    }

    const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Paid');

    if (updatedInvoice === undefined || updatedInvoice === null) {
      throw new Error(`Failed to mark invoice as paid`);
    }

    return updatedInvoice;
  }

  async markInvoiceAsOverdue(id: string, tenantId: string): Promise<InvoiceEntity> {
    const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
    if (invoice === undefined || invoice === null) {
      throw new Error(`Invoice ${id} not found`);
    }

    if (invoice.isOverdue()) {
      return invoice; // Already overdue
    }

    const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Overdue');

    if (updatedInvoice === undefined || updatedInvoice === null) {
      throw new Error(`Failed to mark invoice as overdue`);
    }

    return updatedInvoice;
  }

  async cancelInvoice(id: string, tenantId: string): Promise<InvoiceEntity> {
    const invoice = await this.deps.invoiceRepo.findById(id, tenantId);
    if (invoice === undefined || invoice === null) {
      throw new Error(`Invoice ${id} not found`);
    }

    if (!invoice.canBeCancelled()) {
      throw new Error('Invoice cannot be cancelled in its current state');
    }

    const updatedInvoice = await this.deps.invoiceRepo.updateStatus(id, tenantId, 'Cancelled');

    if (updatedInvoice === undefined || updatedInvoice === null) {
      throw new Error(`Failed to cancel invoice`);
    }

    return updatedInvoice;
  }

  async searchInvoices(
    tenantId: string,
    filters: {
      customerId?: string;
      orderId?: string;
      status?: InvoiceStatusType;
      search?: string;
      dueDateFrom?: Date;
      dueDateTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.invoiceRepo.findAll(tenantId, filters, pagination);
  }

  async getInvoicesByCustomer(
    customerId: string,
    tenantId: string,
    filters: {
      orderId?: string;
      status?: InvoiceStatusType;
      search?: string;
      dueDateFrom?: Date;
      dueDateTo?: Date;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.invoiceRepo.findByCustomerId(customerId, tenantId, filters, pagination);
  }

  async getOverdueInvoices(tenantId: string): Promise<InvoiceEntity[]> {
    return this.deps.invoiceRepo.getOverdueInvoices(tenantId);
  }
}
