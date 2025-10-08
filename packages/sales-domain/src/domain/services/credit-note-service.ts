import { CreditNoteEntity, CreateCreditNoteInput, UpdateCreditNoteInput, CreditNoteStatusType } from '../entities';
import { CreditNoteRepository } from '../../infra/repo';

export interface CreditNoteServiceDependencies {
  creditNoteRepo: CreditNoteRepository;
}

export interface CreateCreditNoteData extends CreateCreditNoteInput {
  tenantId: string;
  creditNumber: string;
  lines: any[];
}

export interface UpdateCreditNoteData extends UpdateCreditNoteInput {
  tenantId: string;
}

export class CreditNoteService {
  constructor(private deps: CreditNoteServiceDependencies) {}

  async createCreditNote(data: CreateCreditNoteData): Promise<CreditNoteEntity> {
    // Business validation
    if (data.lines.length === 0) {
      throw new Error('Credit note must have at least one line item');
    }

    // Check if credit number already exists
    const existingCreditNote = await this.deps.creditNoteRepo.findByNumber(data.creditNumber, data.tenantId);
    if (existingCreditNote) {
      throw new Error(`Credit note number ${data.creditNumber} already exists`);
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

    const creditNote = await this.deps.creditNoteRepo.create(data);
    return creditNote;
  }

  async getCreditNote(id: string, tenantId: string): Promise<CreditNoteEntity | null> {
    return this.deps.creditNoteRepo.findById(id, tenantId);
  }

  async updateCreditNote(id: string, data: UpdateCreditNoteData): Promise<CreditNoteEntity> {
    const existingCreditNote = await this.deps.creditNoteRepo.findById(id, data.tenantId);
    if (existingCreditNote === undefined || existingCreditNote === null) {
      throw new Error(`Credit note ${id} not found`);
    }

    const updatedCreditNote = await this.deps.creditNoteRepo.update(id, data.tenantId, data);

    if (updatedCreditNote === undefined || updatedCreditNote === null) {
      throw new Error(`Failed to update credit note ${id}`);
    }

    return updatedCreditNote;
  }

  async settleCreditNote(id: string, tenantId: string): Promise<CreditNoteEntity> {
    const creditNote = await this.deps.creditNoteRepo.findById(id, tenantId);
    if (creditNote === undefined || creditNote === null) {
      throw new Error(`Credit note ${id} not found`);
    }

    if (!creditNote.canBeSettled()) {
      throw new Error('Credit note cannot be settled in its current state');
    }

    const updatedCreditNote = await this.deps.creditNoteRepo.updateStatus(id, tenantId, 'Settled');

    if (updatedCreditNote === undefined || updatedCreditNote === null) {
      throw new Error(`Failed to settle credit note`);
    }

    return updatedCreditNote;
  }

  async searchCreditNotes(
    tenantId: string,
    filters: {
      customerId?: string;
      invoiceId?: string;
      status?: CreditNoteStatusType;
      search?: string;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.creditNoteRepo.findAll(tenantId, filters, pagination);
  }

  async getCreditNotesByCustomer(
    customerId: string,
    tenantId: string,
    filters: {
      invoiceId?: string;
      status?: CreditNoteStatusType;
      search?: string;
    } = {},
    pagination: { page: number; pageSize: number } = { page: 1, pageSize: 20 }
  ) {
    return this.deps.creditNoteRepo.findByCustomerId(customerId, tenantId, filters, pagination);
  }

  async getCreditNotesByInvoice(invoiceId: string, tenantId: string): Promise<CreditNoteEntity[]> {
    return this.deps.creditNoteRepo.findByInvoiceId(invoiceId, tenantId);
  }
}
