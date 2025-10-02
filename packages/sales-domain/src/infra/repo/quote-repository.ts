import { eq, and, ilike, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { quotes } from '../db/schema';
import { QuoteEntity, Quote, CreateQuoteInput, UpdateQuoteInput, QuoteStatus, QuoteStatusType } from '../../domain/entities';

export interface QuoteFilters {
  customerId?: string;
  status?: QuoteStatusType;
  search?: string;
  validUntilFrom?: Date;
  validUntilTo?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'quoteNumber' | 'validUntil' | 'totalNet' | 'createdAt' | 'updatedAt';
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

export class QuoteRepository {
  async findById(id: string, tenantId: string): Promise<QuoteEntity | null> {
    const result = await db
      .select()
      .from(quotes)
      .where(and(eq(quotes.id, id), eq(quotes.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return QuoteEntity.fromPersistence(result[0]);
  }

  async findByNumber(quoteNumber: string, tenantId: string): Promise<QuoteEntity | null> {
    const result = await db
      .select()
      .from(quotes)
      .where(and(eq(quotes.quoteNumber, quoteNumber), eq(quotes.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return QuoteEntity.fromPersistence(result[0]);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: QuoteFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<QuoteEntity>> {
    const conditions = [
      eq(quotes.tenantId, tenantId),
      eq(quotes.customerId, customerId)
    ];

    if (filters.status) {
      conditions.push(eq(quotes.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(quotes.quoteNumber, `%${filters.search}%`));
    }

    if (filters.validUntilFrom) {
      conditions.push(gte(quotes.validUntil, filters.validUntilFrom));
    }

    if (filters.validUntilTo) {
      conditions.push(lte(quotes.validUntil, filters.validUntilTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: quotes.id })
      .from(quotes)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy || 'createdAt';
    const sortOrder = pagination.sortOrder || 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(quotes[sortBy])
      : asc(quotes[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(quotes)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(quote => QuoteEntity.fromPersistence(quote));

    return {
      data: entities,
      pagination: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        total,
        totalPages: Math.ceil(total / pagination.pageSize)
      }
    };
  }

  async findAll(
    tenantId: string,
    filters: QuoteFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<QuoteEntity>> {
    const conditions = [eq(quotes.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(quotes.customerId, filters.customerId));
    }

    if (filters.status) {
      conditions.push(eq(quotes.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(quotes.quoteNumber, `%${filters.search}%`));
    }

    if (filters.validUntilFrom) {
      conditions.push(gte(quotes.validUntil, filters.validUntilFrom));
    }

    if (filters.validUntilTo) {
      conditions.push(lte(quotes.validUntil, filters.validUntilTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: quotes.id })
      .from(quotes)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy || 'createdAt';
    const sortOrder = pagination.sortOrder || 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(quotes[sortBy])
      : asc(quotes[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(quotes)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(quote => QuoteEntity.fromPersistence(quote));

    return {
      data: entities,
      pagination: {
        page: pagination.page,
        pageSize: pagination.pageSize,
        total,
        totalPages: Math.ceil(total / pagination.pageSize)
      }
    };
  }

  async create(input: CreateQuoteInput & { tenantId: string }): Promise<QuoteEntity> {
    const quoteData: Quote = {
      ...input,
      id: uuidv4(),
      status: input.status || QuoteStatus.DRAFT,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    const result = await db
      .insert(quotes)
      .values(quoteData)
      .returning();

    return QuoteEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateQuoteInput): Promise<QuoteEntity | null> {
    const updateData: Partial<Quote> = {
      ...input,
      updatedAt: new Date()
    };

    const result = await db
      .update(quotes)
      .set(updateData)
      .where(and(eq(quotes.id, id), eq(quotes.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return QuoteEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(quotes)
      .where(and(eq(quotes.id, id), eq(quotes.tenantId, tenantId)))
      .returning({ id: quotes.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: quotes.id })
      .from(quotes)
      .where(and(eq(quotes.id, id), eq(quotes.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: QuoteStatusType): Promise<QuoteEntity | null> {
    const result = await db
      .update(quotes)
      .set({
        status,
        updatedAt: new Date()
      })
      .where(and(eq(quotes.id, id), eq(quotes.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return QuoteEntity.fromPersistence(result[0]);
  }

  async getExpiringSoon(tenantId: string, daysAhead: number = 7): Promise<QuoteEntity[]> {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + daysAhead);

    const result = await db
      .select()
      .from(quotes)
      .where(and(
        eq(quotes.tenantId, tenantId),
        eq(quotes.status, QuoteStatus.SENT),
        lte(quotes.validUntil, futureDate)
      ));

    return result.map(quote => QuoteEntity.fromPersistence(quote));
  }

  async getExpired(tenantId: string): Promise<QuoteEntity[]> {
    const result = await db
      .select()
      .from(quotes)
      .where(and(
        eq(quotes.tenantId, tenantId),
        eq(quotes.status, QuoteStatus.SENT),
        lte(quotes.validUntil, new Date())
      ));

    return result.map(quote => QuoteEntity.fromPersistence(quote));
  }
}