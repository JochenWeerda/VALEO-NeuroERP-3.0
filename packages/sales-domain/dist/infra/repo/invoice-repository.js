"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class InvoiceRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.id, id), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async findByNumber(invoiceNumber, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.invoiceNumber, invoiceNumber), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async findByOrderId(orderId, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.orderId, orderId), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.invoices.customerId, customerId)
        ];
        if (filters.orderId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.invoices.orderId, filters.orderId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.invoices.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.invoices.invoiceNumber, `%${filters.search}%`));
        }
        if (filters.dueDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.invoices.dueDate, filters.dueDateFrom));
        }
        if (filters.dueDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.invoices.dueDate, filters.dueDateTo));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.invoices.id })
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.invoices[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.invoices[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(invoice => entities_1.InvoiceEntity.fromPersistence(invoice));
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
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.invoices.customerId, filters.customerId));
        }
        if (filters.orderId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.invoices.orderId, filters.orderId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.invoices.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.invoices.invoiceNumber, `%${filters.search}%`));
        }
        if (filters.dueDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.invoices.dueDate, filters.dueDateFrom));
        }
        if (filters.dueDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.invoices.dueDate, filters.dueDateTo));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.invoices.id })
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.invoices[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.invoices[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(invoice => entities_1.InvoiceEntity.fromPersistence(invoice));
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
        const invoice = entities_1.InvoiceEntity.create(input);
        const invoiceData = invoice.toPersistence();
        const result = await connection_1.db
            .insert(schema_1.invoices)
            .values(invoiceData)
            .returning();
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            notes: input.notes ?? undefined,
            dueDate: input.dueDate ?? undefined,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.invoices)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.id, id), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.id, id), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .returning({ id: schema_1.invoices.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.invoices.id })
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.id, id), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStatus(id, tenantId, status) {
        const updateData = {
            status,
            updatedAt: new Date()
        };
        if (status === entities_1.InvoiceStatus.PAID) {
            updateData.paidAt = new Date();
        }
        const result = await connection_1.db
            .update(schema_1.invoices)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.id, id), (0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.InvoiceEntity.fromPersistence(result[0]);
    }
    async getOverdueInvoices(tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.invoices)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.invoices.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.invoices.status, entities_1.InvoiceStatus.ISSUED), (0, drizzle_orm_1.lte)(schema_1.invoices.dueDate, new Date())));
        return result.map(invoice => entities_1.InvoiceEntity.fromPersistence(invoice));
    }
}
exports.InvoiceRepository = InvoiceRepository;
//# sourceMappingURL=invoice-repository.js.map