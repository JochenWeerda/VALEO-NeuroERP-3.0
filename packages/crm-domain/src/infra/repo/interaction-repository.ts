import { eq, and, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { interactions } from '../db/schema';
import { InteractionEntity, Interaction, CreateInteractionInput, UpdateInteractionInput, InteractionType, InteractionTypeType } from '../../domain/entities';

export interface InteractionFilters {
  customerId: string;
  contactId?: string;
  type?: InteractionTypeType;
  from?: Date;
  to?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'subject' | 'type' | 'occurredAt' | 'createdAt' | 'updatedAt';
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

export class InteractionRepository {
  async findById(id: string, tenantId: string): Promise<InteractionEntity | null> {
    const result = await db
      .select()
      .from(interactions)
      .where(and(eq(interactions.id, id), eq(interactions.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return InteractionEntity.fromPersistence(result[0]);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: Omit<InteractionFilters, 'customerId'> = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<InteractionEntity>> {
    const conditions = [
      eq(interactions.tenantId, tenantId),
      eq(interactions.customerId, customerId)
    ];

    if (filters.contactId) {
      conditions.push(eq(interactions.contactId, filters.contactId));
    }

    if (filters.type) {
      conditions.push(eq(interactions.type, filters.type));
    }

    if (filters.from) {
      conditions.push(gte(interactions.occurredAt, filters.from));
    }

    if (filters.to) {
      conditions.push(lte(interactions.occurredAt, filters.to));
    }

    // Get total count
    const totalResult = await db
      .select({ count: interactions.id })
      .from(interactions)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'occurredAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(interactions[sortBy])
      : asc(interactions[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(interactions)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(interaction => InteractionEntity.fromPersistence(interaction));

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
    filters: InteractionFilters,
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<InteractionEntity>> {
    const conditions = [eq(interactions.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(interactions.customerId, filters.customerId));
    }

    if (filters.contactId) {
      conditions.push(eq(interactions.contactId, filters.contactId));
    }

    if (filters.type) {
      conditions.push(eq(interactions.type, filters.type));
    }

    if (filters.from) {
      conditions.push(gte(interactions.occurredAt, filters.from));
    }

    if (filters.to) {
      conditions.push(lte(interactions.occurredAt, filters.to));
    }

    // Get total count
    const totalResult = await db
      .select({ count: interactions.id })
      .from(interactions)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'occurredAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(interactions[sortBy])
      : asc(interactions[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(interactions)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(interaction => InteractionEntity.fromPersistence(interaction));

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

  async create(input: CreateInteractionInput & { tenantId: string }): Promise<InteractionEntity> {
    const interactionData: Interaction = {
      ...input,
      id: uuidv4(),
      attachments: input.attachments ?? [],
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    const result = await db
      .insert(interactions)
      .values(interactionData as any)
      .returning();

    return InteractionEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateInteractionInput): Promise<InteractionEntity | null> {
    const updateData: any = {
      ...input,
      updatedAt: new Date()
    };

    const result = await db
      .update(interactions)
      .set(updateData)
      .where(and(eq(interactions.id, id), eq(interactions.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return InteractionEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(interactions)
      .where(and(eq(interactions.id, id), eq(interactions.tenantId, tenantId)))
      .returning({ id: interactions.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: interactions.id })
      .from(interactions)
      .where(and(eq(interactions.id, id), eq(interactions.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async getByType(type: InteractionTypeType, tenantId: string): Promise<InteractionEntity[]> {
    const result = await db
      .select()
      .from(interactions)
      .where(and(eq(interactions.type, type), eq(interactions.tenantId, tenantId)));

    return result.map(interaction => InteractionEntity.fromPersistence(interaction));
  }

  async getUpcomingInteractions(tenantId: string, from?: Date): Promise<InteractionEntity[]> {
    const fromDate = from || new Date();
    const result = await db
      .select()
      .from(interactions)
      .where(and(
        eq(interactions.tenantId, tenantId),
        gte(interactions.occurredAt, fromDate)
      ))
      .orderBy(asc(interactions.occurredAt));

    return result.map(interaction => InteractionEntity.fromPersistence(interaction));
  }

  async getOverdueInteractions(tenantId: string): Promise<InteractionEntity[]> {
    const now = new Date();
    const result = await db
      .select()
      .from(interactions)
      .where(and(
        eq(interactions.tenantId, tenantId),
        lte(interactions.occurredAt, now)
      ))
      .orderBy(asc(interactions.occurredAt));

    return result.map(interaction => InteractionEntity.fromPersistence(interaction));
  }

  async getTodaysInteractions(tenantId: string): Promise<InteractionEntity[]> {
    const today = new Date();
    const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);

    const result = await db
      .select()
      .from(interactions)
      .where(and(
        eq(interactions.tenantId, tenantId),
        gte(interactions.occurredAt, startOfDay),
        lte(interactions.occurredAt, endOfDay)
      ))
      .orderBy(asc(interactions.occurredAt));

    return result.map(interaction => InteractionEntity.fromPersistence(interaction));
  }
}
