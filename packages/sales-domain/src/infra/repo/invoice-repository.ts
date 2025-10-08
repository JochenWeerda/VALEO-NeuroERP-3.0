import { eq, and, ilike, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { invoices } from '../db/schema';
import { InvoiceEntity, Invoice, CreateInvoiceInput, UpdateInvoiceInput, InvoiceStatus, InvoiceStatusType } from '../../domain/entities';

export interface InvoiceFilters {
  customerId?: string;
  orderId?: string;
  status?: InvoiceStatusType;
  search?: string;
  dueDateFrom?: Date;
  dueDateTo?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'invoiceNumber' | 'dueDate' | 'totalNet' | 'createdAt' | 'updatedAt';
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

export class InvoiceRepository {
  async findById(id: string, tenantId: string): Promise<InvoiceEntity | null> {
    const result = await db
      .select()
      .from(invoices)
      .where(and(eq(invoices.id, id), eq(invoices.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async findByNumber(invoiceNumber: string, tenantId: string): Promise<InvoiceEntity | null> {
    const result = await db
      .select()
      .from(invoices)
      .where(and(eq(invoices.invoiceNumber, invoiceNumber), eq(invoices.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async findByOrderId(orderId: string, tenantId: string): Promise<InvoiceEntity | null> {
    const result = await db
      .select()
      .from(invoices)
      .where(and(eq(invoices.orderId, orderId), eq(invoices.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: InvoiceFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<InvoiceEntity>> {
    const conditions = [
      eq(invoices.tenantId, tenantId),
      eq(invoices.customerId, customerId)
    ];

    if (filters.orderId) {
      conditions.push(eq(invoices.orderId, filters.orderId));
    }

    if (filters.status) {
      conditions.push(eq(invoices.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(invoices.invoiceNumber, `%${filters.search}%`));
    }

    if (filters.dueDateFrom) {
      conditions.push(gte(invoices.dueDate, filters.dueDateFrom));
    }

    if (filters.dueDateTo) {
      conditions.push(lte(invoices.dueDate, filters.dueDateTo));
    }

    const totalResult = await db
      .select({ count: invoices.id })
      .from(invoices)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';
    const orderBy = sortOrder === 'desc' ? desc(invoices[sortBy]) : asc(invoices[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(invoices)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(invoice => InvoiceEntity.fromPersistence(invoice));

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
    filters: InvoiceFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<InvoiceEntity>> {
    const conditions = [eq(invoices.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(invoices.customerId, filters.customerId));
    }

    if (filters.orderId) {
      conditions.push(eq(invoices.orderId, filters.orderId));
    }

    if (filters.status) {
      conditions.push(eq(invoices.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(invoices.invoiceNumber, `%${filters.search}%`));
    }

    if (filters.dueDateFrom) {
      conditions.push(gte(invoices.dueDate, filters.dueDateFrom));
    }

    if (filters.dueDateTo) {
      conditions.push(lte(invoices.dueDate, filters.dueDateTo));
    }

    const totalResult = await db
      .select({ count: invoices.id })
      .from(invoices)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';
    const orderBy = sortOrder === 'desc' ? desc(invoices[sortBy]) : asc(invoices[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(invoices)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(invoice => InvoiceEntity.fromPersistence(invoice));

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

  async create(input: CreateInvoiceInput & { tenantId: string }): Promise<InvoiceEntity> {
    const invoice = InvoiceEntity.create(input);
    const invoiceData = invoice.toPersistence();

    const result = await db
      .insert(invoices)
      .values(invoiceData as any)
      .returning();

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateInvoiceInput): Promise<InvoiceEntity | null> {
    const updateData: any = {
      ...input,
      notes: input.notes ?? undefined,
      dueDate: input.dueDate ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(invoices)
      .set(updateData)
      .where(and(eq(invoices.id, id), eq(invoices.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(invoices)
      .where(and(eq(invoices.id, id), eq(invoices.tenantId, tenantId)))
      .returning({ id: invoices.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: invoices.id })
      .from(invoices)
      .where(and(eq(invoices.id, id), eq(invoices.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: InvoiceStatusType): Promise<InvoiceEntity | null> {
    const updateData: any = {
      status,
      updatedAt: new Date()
    };

    if (status === InvoiceStatus.PAID) {
      updateData.paidAt = new Date();
    }

    const result = await db
      .update(invoices)
      .set(updateData)
      .where(and(eq(invoices.id, id), eq(invoices.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return InvoiceEntity.fromPersistence(result[0]);
  }

  async getOverdueInvoices(tenantId: string): Promise<InvoiceEntity[]> {
    const result = await db
      .select()
      .from(invoices)
      .where(and(
        eq(invoices.tenantId, tenantId),
        eq(invoices.status, InvoiceStatus.ISSUED),
        lte(invoices.dueDate, new Date())
      ));

    return result.map(invoice => InvoiceEntity.fromPersistence(invoice));
  }
}
