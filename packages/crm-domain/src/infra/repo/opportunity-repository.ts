import { eq, and, ne, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { opportunities } from '../db/schema';
import { OpportunityEntity, Opportunity, CreateOpportunityInput, UpdateOpportunityInput, OpportunityStage, OpportunityStageType } from '../../domain/entities';

export interface OpportunityFilters {
  customerId?: string;
  stage?: OpportunityStageType;
  ownerUserId?: string;
  amountMin?: number;
  amountMax?: number;
  expectedCloseDateFrom?: Date;
  expectedCloseDateTo?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'title' | 'stage' | 'amountNet' | 'expectedCloseDate' | 'createdAt' | 'updatedAt';
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

export class OpportunityRepository {
  async findById(id: string, tenantId: string): Promise<OpportunityEntity | null> {
    const result = await db
      .select()
      .from(opportunities)
      .where(and(eq(opportunities.id, id), eq(opportunities.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return OpportunityEntity.fromPersistence(result[0]);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: OpportunityFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<OpportunityEntity>> {
    const conditions = [
      eq(opportunities.tenantId, tenantId),
      eq(opportunities.customerId, customerId)
    ];

    if (filters.stage) {
      conditions.push(eq(opportunities.stage, filters.stage));
    }

    if (filters.ownerUserId) {
      conditions.push(eq(opportunities.ownerUserId, filters.ownerUserId));
    }

    if (filters.amountMin !== undefined) {
      conditions.push(gte(opportunities.amountNet, filters.amountMin.toString()));
    }

    if (filters.amountMax !== undefined) {
      conditions.push(lte(opportunities.amountNet, filters.amountMax.toString()));
    }

    if (filters.expectedCloseDateFrom) {
      conditions.push(gte(opportunities.expectedCloseDate, filters.expectedCloseDateFrom));
    }

    if (filters.expectedCloseDateTo) {
      conditions.push(lte(opportunities.expectedCloseDate, filters.expectedCloseDateTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: opportunities.id })
      .from(opportunities)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(opportunities[sortBy])
      : asc(opportunities[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(opportunities)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(opportunity => OpportunityEntity.fromPersistence(opportunity));

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
    filters: OpportunityFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<OpportunityEntity>> {
    const conditions = [eq(opportunities.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(opportunities.customerId, filters.customerId));
    }

    if (filters.stage) {
      conditions.push(eq(opportunities.stage, filters.stage));
    }

    if (filters.ownerUserId) {
      conditions.push(eq(opportunities.ownerUserId, filters.ownerUserId));
    }

    if (filters.amountMin !== undefined) {
      conditions.push(gte(opportunities.amountNet, filters.amountMin.toString()));
    }

    if (filters.amountMax !== undefined) {
      conditions.push(lte(opportunities.amountNet, filters.amountMax.toString()));
    }

    if (filters.expectedCloseDateFrom) {
      conditions.push(gte(opportunities.expectedCloseDate, filters.expectedCloseDateFrom));
    }

    if (filters.expectedCloseDateTo) {
      conditions.push(lte(opportunities.expectedCloseDate, filters.expectedCloseDateTo));
    }

    // Get total count
    const totalResult = await db
      .select({ count: opportunities.id })
      .from(opportunities)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(opportunities[sortBy])
      : asc(opportunities[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(opportunities)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(opportunity => OpportunityEntity.fromPersistence(opportunity));

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

  async create(input: CreateOpportunityInput & { tenantId: string }): Promise<OpportunityEntity> {
    const opportunityData: Opportunity = {
      ...input,
      id: uuidv4(),
      stage: input.stage || OpportunityStage.LEAD,
      probability: input.probability !== undefined ? input.probability : 0.1,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    const result = await db
      .insert(opportunities)
      .values(opportunityData as any)
      .returning();

    return OpportunityEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateOpportunityInput): Promise<OpportunityEntity | null> {
    const updateData: any = {
      ...input,
      ownerUserId: input.ownerUserId ?? undefined,
      expectedCloseDate: input.expectedCloseDate ?? undefined,
      amountNet: input.amountNet ?? undefined,
      currency: input.currency ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(opportunities)
      .set(updateData)
      .where(and(eq(opportunities.id, id), eq(opportunities.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return OpportunityEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(opportunities)
      .where(and(eq(opportunities.id, id), eq(opportunities.tenantId, tenantId)))
      .returning({ id: opportunities.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: opportunities.id })
      .from(opportunities)
      .where(and(eq(opportunities.id, id), eq(opportunities.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStage(id: string, tenantId: string, stage: OpportunityStageType): Promise<OpportunityEntity | null> {
    const result = await db
      .update(opportunities)
      .set({
        stage,
        updatedAt: new Date()
      })
      .where(and(eq(opportunities.id, id), eq(opportunities.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return OpportunityEntity.fromPersistence(result[0]);
  }

  async markAsWon(id: string, tenantId: string): Promise<OpportunityEntity | null> {
    return this.updateStage(id, tenantId, OpportunityStage.WON);
  }

  async markAsLost(id: string, tenantId: string): Promise<OpportunityEntity | null> {
    return this.updateStage(id, tenantId, OpportunityStage.LOST);
  }

  async getByStage(stage: OpportunityStageType, tenantId: string): Promise<OpportunityEntity[]> {
    const result = await db
      .select()
      .from(opportunities)
      .where(and(eq(opportunities.stage, stage), eq(opportunities.tenantId, tenantId)));

    return result.map(opportunity => OpportunityEntity.fromPersistence(opportunity));
  }

  async getOpenOpportunities(tenantId: string): Promise<OpportunityEntity[]> {
    const result = await db
      .select()
      .from(opportunities)
      .where(and(
        eq(opportunities.tenantId, tenantId),
        and(
          ne(opportunities.stage, OpportunityStage.WON),
          ne(opportunities.stage, OpportunityStage.LOST)
        )
      ));

    return result.map(opportunity => OpportunityEntity.fromPersistence(opportunity));
  }
}
