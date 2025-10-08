"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const uuid_1 = require("uuid");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class InteractionRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.id, id), (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.InteractionEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.interactions.customerId, customerId)
        ];
        if (filters.contactId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.interactions.contactId, filters.contactId));
        }
        if (filters.type) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.interactions.type, filters.type));
        }
        if (filters.from) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.interactions.occurredAt, filters.from));
        }
        if (filters.to) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.interactions.occurredAt, filters.to));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.interactions.id })
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'occurredAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.interactions[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.interactions[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
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
    async findAll(tenantId, filters, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.interactions.customerId, filters.customerId));
        }
        if (filters.contactId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.interactions.contactId, filters.contactId));
        }
        if (filters.type) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.interactions.type, filters.type));
        }
        if (filters.from) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.interactions.occurredAt, filters.from));
        }
        if (filters.to) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.interactions.occurredAt, filters.to));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.interactions.id })
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'occurredAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.interactions[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.interactions[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
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
        const interactionData = {
            ...input,
            id: (0, uuid_1.v4)(),
            attachments: input.attachments || [],
            createdAt: new Date(),
            updatedAt: new Date(),
            version: 1
        };
        const result = await connection_1.db
            .insert(schema_1.interactions)
            .values(interactionData)
            .returning();
        return entities_1.InteractionEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.interactions)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.id, id), (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.InteractionEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.id, id), (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)))
            .returning({ id: schema_1.interactions.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.interactions.id })
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.id, id), (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async getByType(type, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.type, type), (0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId)));
        return result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
    }
    async getUpcomingInteractions(tenantId, from) {
        const fromDate = from || new Date();
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId), (0, drizzle_orm_1.gte)(schema_1.interactions.occurredAt, fromDate)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.interactions.occurredAt));
        return result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
    }
    async getOverdueInteractions(tenantId) {
        const now = new Date();
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId), (0, drizzle_orm_1.lte)(schema_1.interactions.occurredAt, now)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.interactions.occurredAt));
        return result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
    }
    async getTodaysInteractions(tenantId) {
        const today = new Date();
        const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
        const result = await connection_1.db
            .select()
            .from(schema_1.interactions)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.interactions.tenantId, tenantId), (0, drizzle_orm_1.gte)(schema_1.interactions.occurredAt, startOfDay), (0, drizzle_orm_1.lte)(schema_1.interactions.occurredAt, endOfDay)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.interactions.occurredAt));
        return result.map(interaction => entities_1.InteractionEntity.fromPersistence(interaction));
    }
}
exports.InteractionRepository = InteractionRepository;
//# sourceMappingURL=interaction-repository.js.map