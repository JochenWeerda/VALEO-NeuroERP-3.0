import { eq, and, ilike, inArray, desc, asc } from 'drizzle-orm';
import { db } from '../db/connection';
import { customers } from '../db/schema';
import { CustomerEntity, Customer, CreateCustomerInput, UpdateCustomerInput, CustomerStatus, CustomerStatusType } from '../../domain/entities';
import { v4 as uuidv4 } from 'uuid';

export interface CustomerFilters {
  search?: string;
  status?: CustomerStatusType;
  tags?: string[];
  ownerUserId?: string;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'name' | 'createdAt' | 'updatedAt';
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

export class CustomerRepository {
  async findById(id: string, tenantId: string): Promise<CustomerEntity | null> {
    const result = await db
      .select()
      .from(customers)
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async findByNumber(number: string, tenantId: string): Promise<CustomerEntity | null> {
    const result = await db
      .select()
      .from(customers)
      .where(and(eq(customers.number, number), eq(customers.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async findAll(
    tenantId: string,
    filters: CustomerFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<CustomerEntity>> {
    const conditions = [eq(customers.tenantId, tenantId)];

    if (filters.search) {
      conditions.push(ilike(customers.name, `%${filters.search}%`));
    }

    if (filters.status) {
      conditions.push(eq(customers.status, filters.status));
    }

    if (filters.ownerUserId) {
      conditions.push(eq(customers.ownerUserId, filters.ownerUserId));
    }

    if (filters.tags && filters.tags.length > 0) {
      // This is a simplified approach - in production you might want to use JSON operators
      // For exact tag matching, you might need to adjust based on your needs
    }

    // Get total count
    const totalResult = await db
      .select({ count: customers.id })
      .from(customers)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(customers[sortBy])
      : asc(customers[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(customers)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(customer => CustomerEntity.fromPersistence(customer as any));

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

  async create(input: CreateCustomerInput & { tenantId: string }): Promise<CustomerEntity> {
    const customerData: Customer = {
      ...input,
      id: uuidv4(),
      status: input.status || CustomerStatus.PROSPECT,
      tags: input.tags ?? [],
      shippingAddresses: input.shippingAddresses ?? [],
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    const result = await db
      .insert(customers)
      .values(customerData as any)
      .returning();

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async update(id: string, tenantId: string, input: UpdateCustomerInput): Promise<CustomerEntity | null> {
    const updateData: any = {
      ...input,
      email: input.email ?? undefined,
      phone: input.phone ?? undefined,
      vatId: input.vatId ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(customers)
      .set(updateData)
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(customers)
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .returning({ id: customers.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: customers.id })
      .from(customers)
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: CustomerStatusType): Promise<CustomerEntity | null> {
    const result = await db
      .update(customers)
      .set({
        status,
        updatedAt: new Date()
      })
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async addTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity | null> {
    // First get current tags
    const current = await this.findById(id, tenantId);
    if (current === undefined || current === null) return null;

    const currentTags = current.tags;
    if (currentTags.includes(tag)) {
      return current; // Tag already exists
    }

    const updatedTags = [...currentTags, tag];
    const result = await db
      .update(customers)
      .set({
        tags: updatedTags,
        updatedAt: new Date()
      })
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .returning();

    return CustomerEntity.fromPersistence(result[0] as any);
  }

  async removeTag(id: string, tenantId: string, tag: string): Promise<CustomerEntity | null> {
    // First get current tags
    const current = await this.findById(id, tenantId);
    if (current === undefined || current === null) return null;

    const currentTags = current.tags;
    const tagIndex = currentTags.indexOf(tag);
    if (tagIndex === -1) {
      return current; // Tag doesn't exist
    }

    const updatedTags = currentTags.filter(t => t !== tag);
    const result = await db
      .update(customers)
      .set({
        tags: updatedTags,
        updatedAt: new Date()
      })
      .where(and(eq(customers.id, id), eq(customers.tenantId, tenantId)))
      .returning();

    return CustomerEntity.fromPersistence(result[0] as any);
  }
}
