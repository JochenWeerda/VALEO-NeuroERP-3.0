"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class OrderRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.id, id), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.OrderEntity.fromPersistence(result[0]);
    }
    async findByNumber(orderNumber, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.orderNumber, orderNumber), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.OrderEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.orders.customerId, customerId)
        ];
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.orders.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.orders.orderNumber, `%${filters.search}%`));
        }
        if (filters.expectedDeliveryDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.orders.expectedDeliveryDate, filters.expectedDeliveryDateFrom));
        }
        if (filters.expectedDeliveryDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.orders.expectedDeliveryDate, filters.expectedDeliveryDateTo));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.orders.id })
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.orders[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.orders[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(order => entities_1.OrderEntity.fromPersistence(order));
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
    async findAll(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.orders.customerId, filters.customerId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.orders.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.orders.orderNumber, `%${filters.search}%`));
        }
        if (filters.expectedDeliveryDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.orders.expectedDeliveryDate, filters.expectedDeliveryDateFrom));
        }
        if (filters.expectedDeliveryDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.orders.expectedDeliveryDate, filters.expectedDeliveryDateTo));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.orders.id })
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.orders[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.orders[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(order => entities_1.OrderEntity.fromPersistence(order));
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
    async create(input) {
        const order = entities_1.OrderEntity.create(input);
        const orderData = order.toPersistence();
        const result = await connection_1.db
            .insert(schema_1.orders)
            .values(orderData)
            .returning();
        return entities_1.OrderEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            notes: input.notes ?? undefined,
            expectedDeliveryDate: input.expectedDeliveryDate ?? undefined,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.orders)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.id, id), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.OrderEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.orders)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.id, id), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .returning({ id: schema_1.orders.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.orders.id })
            .from(schema_1.orders)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.id, id), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStatus(id, tenantId, status) {
        const result = await connection_1.db
            .update(schema_1.orders)
            .set({
            status,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.orders.id, id), (0, drizzle_orm_1.eq)(schema_1.orders.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.OrderEntity.fromPersistence(result[0]);
    }
}
exports.OrderRepository = OrderRepository;
//# sourceMappingURL=order-repository.js.map