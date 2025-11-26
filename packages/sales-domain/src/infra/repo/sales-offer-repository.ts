import { eq, and, ilike, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { salesOffers } from '../db/schema';
import { SalesOffer, CreateSalesOfferInput, UpdateSalesOfferInput, SalesOfferStatus } from '../../domain/entities';

export interface SalesOfferFilters {
  customerId?: string;
  status?: SalesOfferStatusType;
  search?: string;
  validUntilFrom?: Date;
  validUntilTo?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'offerNumber' | 'validUntil' | 'totalAmount' | 'createdAt' | 'updatedAt';
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

export class SalesOfferRepository {
  async findById(id: string, tenantId: string): Promise<SalesOfferEntity | null> {
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(eq(salesOffers.id, id), eq(salesOffers.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return SalesOfferEntity.fromPersistence(result[0]);
  }

  async findByNumber(offerNumber: string, tenantId: string): Promise<SalesOfferEntity | null> {
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(eq(salesOffers.offerNumber, offerNumber), eq(salesOffers.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return SalesOfferEntity.fromPersistence(result[0]);
  }

  async findByCustomerInquiryId(customerInquiryId: string, tenantId: string): Promise<SalesOfferEntity[]> {
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(eq(salesOffers.customerInquiryId, customerInquiryId), eq(salesOffers.tenantId, tenantId)))
      .orderBy(desc(salesOffers.createdAt));

    return result.map(offer => SalesOfferEntity.fromPersistence(offer));
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: SalesOfferFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<SalesOfferEntity>> {
    const conditions = [
      eq(salesOffers.tenantId, tenantId),
      eq(salesOffers.customerId, customerId)
    ];

    if (filters.status) {
      conditions.push(eq(salesOffers.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(salesOffers.offerNumber, `%${filters.search}%`));
    }

    if (filters.validUntilFrom) {
      conditions.push(gte(salesOffers.validUntil, filters.validUntilFrom));
    }

    if (filters.validUntilTo) {
      conditions.push(lte(salesOffers.validUntil, filters.validUntilTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: salesOffers.id })
      .from(salesOffers)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(salesOffers[sortBy])
      : asc(salesOffers[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(offer => SalesOfferEntity.fromPersistence(offer));

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
    filters: SalesOfferFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<SalesOfferEntity>> {
    const conditions = [eq(salesOffers.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(salesOffers.customerId, filters.customerId));
    }

    if (filters.status) {
      conditions.push(eq(salesOffers.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(salesOffers.offerNumber, `%${filters.search}%`));
    }

    if (filters.validUntilFrom) {
      conditions.push(gte(salesOffers.validUntil, filters.validUntilFrom));
    }

    if (filters.validUntilTo) {
      conditions.push(lte(salesOffers.validUntil, filters.validUntilTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: salesOffers.id })
      .from(salesOffers)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(salesOffers[sortBy])
      : asc(salesOffers[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(offer => SalesOfferEntity.fromPersistence(offer));

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

  async create(input: CreateSalesOfferInput & { tenantId: string }): Promise<SalesOfferEntity> {
    const offer = SalesOfferEntity.create(input);
    const offerData = offer.toPersistence();

    const result = await db
      .insert(salesOffers)
      .values(offerData as any)
      .returning();

    return SalesOfferEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateSalesOfferInput): Promise<SalesOfferEntity | null> {
    const updateData: any = {
      ...input,
      contactPerson: input.contactPerson ?? undefined,
      deliveryDate: input.deliveryDate ?? undefined,
      paymentTerms: input.paymentTerms ?? undefined,
      notes: input.notes ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(salesOffers)
      .set(updateData)
      .where(and(eq(salesOffers.id, id), eq(salesOffers.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return SalesOfferEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(salesOffers)
      .where(and(eq(salesOffers.id, id), eq(salesOffers.tenantId, tenantId)))
      .returning({ id: salesOffers.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: salesOffers.id })
      .from(salesOffers)
      .where(and(eq(salesOffers.id, id), eq(salesOffers.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: SalesOfferStatusType): Promise<SalesOfferEntity | null> {
    const result = await db
      .update(salesOffers)
      .set({
        status,
        updatedAt: new Date()
      })
      .where(and(eq(salesOffers.id, id), eq(salesOffers.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return SalesOfferEntity.fromPersistence(result[0]);
  }

  async getExpiringSoon(tenantId: string, daysAhead: number = 7): Promise<SalesOfferEntity[]> {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + daysAhead);

    const result = await db
      .select()
      .from(salesOffers)
      .where(and(
        eq(salesOffers.tenantId, tenantId),
        eq(salesOffers.status, SalesOfferStatus.VERSENDET),
        lte(salesOffers.validUntil, futureDate)
      ));

    return result.map(offer => SalesOfferEntity.fromPersistence(offer));
  }

  async getExpired(tenantId: string): Promise<SalesOfferEntity[]> {
    const result = await db
      .select()
      .from(salesOffers)
      .where(and(
        eq(salesOffers.tenantId, tenantId),
        eq(salesOffers.status, SalesOfferStatus.VERSENDET),
        lte(salesOffers.validUntil, new Date())
      ));

    return result.map(offer => SalesOfferEntity.fromPersistence(offer));
  }
}