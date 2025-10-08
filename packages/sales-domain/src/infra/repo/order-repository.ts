import { eq, and, ilike, gte, lte, desc, asc } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import { db } from '../db/connection';
import { orders } from '../db/schema';
import { OrderEntity, Order, CreateOrderInput, UpdateOrderInput, OrderStatus, OrderStatusType } from '../../domain/entities';

export interface OrderFilters {
  customerId?: string;
  status?: OrderStatusType;
  search?: string;
  expectedDeliveryDateFrom?: Date;
  expectedDeliveryDateTo?: Date;
}

export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: 'orderNumber' | 'expectedDeliveryDate' | 'totalNet' | 'createdAt' | 'updatedAt';
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

export class OrderRepository {
  async findById(id: string, tenantId: string): Promise<OrderEntity | null> {
    const result = await db
      .select()
      .from(orders)
      .where(and(eq(orders.id, id), eq(orders.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return OrderEntity.fromPersistence(result[0]);
  }

  async findByNumber(orderNumber: string, tenantId: string): Promise<OrderEntity | null> {
    const result = await db
      .select()
      .from(orders)
      .where(and(eq(orders.orderNumber, orderNumber), eq(orders.tenantId, tenantId)))
      .limit(1);

    if (result.length === 0) {
      return null;
    }

    return OrderEntity.fromPersistence(result[0]);
  }

  async findByCustomerId(
    customerId: string,
    tenantId: string,
    filters: OrderFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<OrderEntity>> {
    const conditions = [
      eq(orders.tenantId, tenantId),
      eq(orders.customerId, customerId)
    ];

    if (filters.status) {
      conditions.push(eq(orders.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(orders.orderNumber, `%${filters.search}%`));
    }

    if (filters.expectedDeliveryDateFrom) {
      conditions.push(gte(orders.expectedDeliveryDate, filters.expectedDeliveryDateFrom));
    }

    if (filters.expectedDeliveryDateTo) {
      conditions.push(lte(orders.expectedDeliveryDate, filters.expectedDeliveryDateTo));
    }

    const totalResult = await db
      .select({ count: orders.id })
      .from(orders)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';
    const orderBy = sortOrder === 'desc' ? desc(orders[sortBy]) : asc(orders[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(orders)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(order => OrderEntity.fromPersistence(order));

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
    filters: OrderFilters = {},
    pagination: PaginationOptions = { page: 1, pageSize: 20 }
  ): Promise<PaginatedResult<OrderEntity>> {
    const conditions = [eq(orders.tenantId, tenantId)];

    if (filters.customerId) {
      conditions.push(eq(orders.customerId, filters.customerId));
    }

    if (filters.status) {
      conditions.push(eq(orders.status, filters.status));
    }

    if (filters.search) {
      conditions.push(ilike(orders.orderNumber, `%${filters.search}%`));
    }

    if (filters.expectedDeliveryDateFrom) {
      conditions.push(gte(orders.expectedDeliveryDate, filters.expectedDeliveryDateFrom));
    }

    if (filters.expectedDeliveryDateTo) {
      conditions.push(lte(orders.expectedDeliveryDate, filters.expectedDeliveryDateTo));
    }

    const totalResult = await db
      .select({ count: orders.id })
      .from(orders)
      .where(and(...conditions));

    const total = totalResult[0]?.count || 0;

    const sortBy = pagination.sortBy ?? 'createdAt';
    const sortOrder = pagination.sortOrder ?? 'desc';
    const orderBy = sortOrder === 'desc' ? desc(orders[sortBy]) : asc(orders[sortBy]);

    const offset = (pagination.page - 1) * pagination.pageSize;
    const result = await db
      .select()
      .from(orders)
      .where(and(...conditions))
      .orderBy(orderBy)
      .limit(pagination.pageSize)
      .offset(offset);

    const entities = result.map(order => OrderEntity.fromPersistence(order));

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

  async create(input: CreateOrderInput & { tenantId: string }): Promise<OrderEntity> {
    const order = OrderEntity.create(input);
    const orderData = order.toPersistence();

    const result = await db
      .insert(orders)
      .values(orderData as any)
      .returning();

    return OrderEntity.fromPersistence(result[0]);
  }

  async update(id: string, tenantId: string, input: UpdateOrderInput): Promise<OrderEntity | null> {
    const updateData: any = {
      ...input,
      notes: input.notes ?? undefined,
      expectedDeliveryDate: input.expectedDeliveryDate ?? undefined,
      updatedAt: new Date()
    };

    const result = await db
      .update(orders)
      .set(updateData)
      .where(and(eq(orders.id, id), eq(orders.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return OrderEntity.fromPersistence(result[0]);
  }

  async delete(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .delete(orders)
      .where(and(eq(orders.id, id), eq(orders.tenantId, tenantId)))
      .returning({ id: orders.id });

    return result.length > 0;
  }

  async exists(id: string, tenantId: string): Promise<boolean> {
    const result = await db
      .select({ id: orders.id })
      .from(orders)
      .where(and(eq(orders.id, id), eq(orders.tenantId, tenantId)))
      .limit(1);

    return result.length > 0;
  }

  async updateStatus(id: string, tenantId: string, status: OrderStatusType): Promise<OrderEntity | null> {
    const result = await db
      .update(orders)
      .set({
        status,
        updatedAt: new Date()
      })
      .where(and(eq(orders.id, id), eq(orders.tenantId, tenantId)))
      .returning();

    if (result.length === 0) {
      return null;
    }

    return OrderEntity.fromPersistence(result[0]);
  }
}
