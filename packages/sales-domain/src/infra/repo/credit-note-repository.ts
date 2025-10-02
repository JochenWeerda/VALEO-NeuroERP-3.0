import { eq, and, ilike, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { creditNotes } from '../db/schema';
import { CreditNoteEntity, CreditNote, CreateCreditNoteInput, UpdateCreditNoteInput, CreditNoteStatus, CreditNoteStatusType } from '../../domain/entities';

export interface CreditNoteFilters {
  customerId?: string;
  invoiceId?: string;
  status?: CreditNoteStatusType;
  search?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'creditNumber' | 'totalNet' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export class CreditNoteRepository {
  async findById(id: string, tenantId: string): Promise<CreditNoteEntity | null> {
    const result = await db
      .select()
      .from(creditNotes)
      .where(and(eq(creditNotes.id, id), eq(creditNotes.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return CreditNoteEntity.fromPersistence(result[0]);
  }

  async findByNumber(creditNumber: string, tenantId: string): Promise<CreditNoteEntity | null> {
    const result = await db
      .select()
      .from(creditNotes)
      .where(and(eq(creditNotes.creditNumber, creditNumber), eq(creditNotes.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return CreditNoteEntity.fromPersistence(result[0]);
  }

  async findByInvoiceId(invoiceId: string, tenantId: string): Promise<CreditNoteEntity[]> {
    const result = await db
      .select()
      .from(creditNotes)
      .where(and(eq(creditNotes.invoiceId, invoiceId), eq(creditNotes.tenantId, tenantId)));

    return result.map(creditNote => CreditNoteEntity.fromPersistence(creditNote));
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: CreditNoteFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<CreditNoteEntity>> {
    const conditions = [
      eq(creditNotes.tenantId, tenantId),
      eq(creditNotes.customerId, customerId)
    ];

    if (filters.invoiceId) {
      conditions.push(eq(creditNotes.invoiceId, filters.invoiceId));
    }

    if (filters.status) {
      conditions.push(eq(creditNotes.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(creditNotes.creditNumber, `%${filters.search}%`));
    }

    const totalResult = await db
      .select({ count: creditNotes.id })
      .from(creditNotes)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy || 'createdAt';
    const sortOrder = pagination.sortOrder || 'desc';
    const orderBy = sortOrder === 'desc' ? desc(creditNotes[sortBy]) : asc(creditNotes[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(creditNotes)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(creditNote => CreditNoteEntity.fromPersistence(creditNote));

    return {
      data: entities,
      pagination: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        total: Number(total),
        totalPages: Math.ceil(Number(total) / pagination.pageSize)
      }
    };
  }

  async findAll(
    tenantId: string,
    filters: CreditNoteFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<CreditNoteEntity>> {
    const conditions = [eq(creditNotes.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(creditNotes.customerId, filters.customerId));
    }

    if (filters.invoiceId) {
      conditions.push(eq(creditNotes.invoiceId, filters.invoiceId));
    }

    if (filters.status) {
      conditions.push(eq(creditNotes.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(creditNotes.creditNumber, `%${filters.search}%`));
    }

    const totalResult = await db
      .select({ count: creditNotes.id })
      .from(creditNotes)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy || 'createdAt';
    const sortOrder = pagination.sortOrder || 'desc';
    const orderBy = sortOrder === 'desc' ? desc(creditNotes[sortBy]) : asc(creditNotes[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(creditNotes)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(creditNote => CreditNoteEntity.fromPersistence(creditNote));

    return {
      data: entities,
      pagination: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        total: Number(total),
        totalPages: Math.ceil(Number(total) / pagination.pageSize)
      }
    };
  }

  async create(input: CreateCreditNoteInput & { tenantId: string }): Promise<CreditNoteEntity> {
    const creditNote = CreditNoteEntity.create(input);
    const creditNoteData = creditNote.toPersistence();

    const result = await db
      .insert(creditNotes)
      .values(creditNoteData as any)
      .returning();

    return CreditNoteEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateCreditNoteInput): Promise<CreditNoteEntity | null> {
    const updateData: any = {
      ...input,
      notes: input.notes ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(creditNotes)
      .set(updateData)
      .where(and(eq(creditNotes.id, id), eq(creditNotes.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return CreditNoteEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(creditNotes)
      .where(and(eq(creditNotes.id, id), eq(creditNotes.tenantId, tenantId)))
      .returning({ id: creditNotes.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: creditNotes.id })
      .from(creditNotes)
      .where(and(eq(creditNotes.id, id), eq(creditNotes.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: CreditNoteStatusType): Promise<CreditNoteEntity | null> {
    const updateData: any = {
      status,
      updatedAt: new Date()
    };

    if (status === CreditNoteStatus.SETTLED) {
      updateData.settledAt = new Date();
    }

    const result = await db
      .update(creditNotes)
      .set(updateData)
      .where(and(eq(creditNotes.id, id), eq(creditNotes.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return CreditNoteEntity.fromPersistence(result[0]);
  }
}