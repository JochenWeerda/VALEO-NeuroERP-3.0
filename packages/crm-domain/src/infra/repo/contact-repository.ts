import { eq, and, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { contacts } from '../db/schema';
import { ContactEntity, Contact, CreateContactInput, UpdateContactInput } from '../../domain/entities';

export interface ContactFilters {
  customerId?: string;
  isPrimary?: boolean;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'firstName' | 'lastName' | 'createdAt' | 'updatedAt';
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

export class ContactRepository {
  async findById(id: string, tenantId: string): Promise<ContactEntity | null> {
    const result = await db
      .select()
      .from(contacts)
      .where(and(eq(contacts.id, id), eq(contacts.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return ContactEntity.fromPersistence(result[0] as any);
  }

  async findByEmail(email: string, tenantId: string): Promise<ContactEntity | null> {
    const result = await db
      .select()
      .from(contacts)
      .where(and(eq(contacts.email, email), eq(contacts.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return ContactEntity.fromPersistence(result[0] as any);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: ContactFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<ContactEntity>> {
    const conditions = [
      eq(contacts.tenantId, tenantId),
      eq(contacts.customerId, customerId)
    ];

    if (filters.isPrimary !== undefined) {
      conditions.push(eq(contacts.isPrimary, filters.isPrimary));
    }

    // Get total count
    const totalResult = await db
      .select({ count: contacts.id })
      .from(contacts)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(contacts[sortBy])
      : asc(contacts[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(contacts)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(contact => ContactEntity.fromPersistence(contact as any));

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
    filters: ContactFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<ContactEntity>> {
    const conditions = [eq(contacts.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(contacts.customerId, filters.customerId));
    }

    if (filters.isPrimary !== undefined) {
      conditions.push(eq(contacts.isPrimary, filters.isPrimary));
    }

    // Get total count
    const totalResult = await db
      .select({ count: contacts.id })
      .from(contacts)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    // Apply sorting
    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';

    const orderBy = sortOrder === 'desc'
      ? desc(contacts[sortBy])
      : asc(contacts[sortBy]);

    // Get paginated results
    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(contacts)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(contact => ContactEntity.fromPersistence(contact as any));

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

  async create(input: CreateContactInput & { tenantId: string }): Promise<ContactEntity> {
    const contactData: Contact = {
      ...input,
      id: uuidv4(),
      isPrimary: input.isPrimary || false,
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    const result = await db
      .insert(contacts)
      .values(contactData as any)
      .returning();

    return ContactEntity.fromPersistence(result[0] as any);
  }

  async update(id: string, tenantId: string, input: UpdateContactInput): Promise<ContactEntity | null> {
    const updateData: any = {
      ...input,
      updatedAt: new Date()
    };

    const result = await db
      .update(contacts)
      .set(updateData as any)
      .where(and(eq(contacts.id, id), eq(contacts.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return ContactEntity.fromPersistence(result[0] as any);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(contacts)
      .where(and(eq(contacts.id, id), eq(contacts.tenantId, tenantId)))
      .returning({ id: contacts.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: contacts.id })
      .from(contacts)
      .where(and(eq(contacts.id, id), eq(contacts.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async setPrimaryContact(customerId: string, contactId: string, tenantId: string): Promise<void> {
    // First, set all contacts for this customer to non-primary
    await db
      .update(contacts)
      .set({ isPrimary: false, updatedAt: new Date() })
      .where(and(
        eq(contacts.customerId, customerId),
        eq(contacts.tenantId, tenantId)
      ));

    // Then set the specified contact as primary
    await db
      .update(contacts)
      .set({ isPrimary: true, updatedAt: new Date() })
      .where(and(
        eq(contacts.id, contactId),
        eq(contacts.tenantId, tenantId)
      ));
  }

  async getPrimaryContact(customerId: string, tenantId: string): Promise<ContactEntity | null> {
    const result = await db
      .select()
      .from(contacts)
      .where(and(
        eq(contacts.customerId, customerId),
        eq(contacts.tenantId, tenantId),
        eq(contacts.isPrimary, true)
      ))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return ContactEntity.fromPersistence(result[0] as any);
  }
}
