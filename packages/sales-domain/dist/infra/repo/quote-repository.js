"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QuoteRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class QuoteRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.id, id), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.QuoteEntity.fromPersistence(result[0]);
    }
    async findByNumber(quoteNumber, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.quoteNumber, quoteNumber), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.QuoteEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.quotes.customerId, customerId)
        ];
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.quotes.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.quotes.quoteNumber, `%${filters.search}%`));
        }
        if (filters.validUntilFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.quotes.validUntil, filters.validUntilFrom));
        }
        if (filters.validUntilTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.quotes.validUntil, filters.validUntilTo));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.quotes.id })
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.quotes[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.quotes[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(quote => entities_1.QuoteEntity.fromPersistence(quote));
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
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.quotes.customerId, filters.customerId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.quotes.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.quotes.quoteNumber, `%${filters.search}%`));
        }
        if (filters.validUntilFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.quotes.validUntil, filters.validUntilFrom));
        }
        if (filters.validUntilTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.quotes.validUntil, filters.validUntilTo));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.quotes.id })
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.quotes[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.quotes[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(quote => entities_1.QuoteEntity.fromPersistence(quote));
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
        const quote = entities_1.QuoteEntity.create(input);
        const quoteData = quote.toPersistence();
        const result = await connection_1.db
            .insert(schema_1.quotes)
            .values(quoteData)
            .returning();
        return entities_1.QuoteEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            notes: input.notes ?? undefined,
            validUntil: input.validUntil ?? undefined,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.quotes)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.id, id), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.QuoteEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.id, id), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .returning({ id: schema_1.quotes.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.quotes.id })
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.id, id), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStatus(id, tenantId, status) {
        const result = await connection_1.db
            .update(schema_1.quotes)
            .set({
            status,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.id, id), (0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.QuoteEntity.fromPersistence(result[0]);
    }
    async getExpiringSoon(tenantId, daysAhead = 7) {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + daysAhead);
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.quotes.status, entities_1.QuoteStatus.SENT), (0, drizzle_orm_1.lte)(schema_1.quotes.validUntil, futureDate)));
        return result.map(quote => entities_1.QuoteEntity.fromPersistence(quote));
    }
    async getExpired(tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.quotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.quotes.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.quotes.status, entities_1.QuoteStatus.SENT), (0, drizzle_orm_1.lte)(schema_1.quotes.validUntil, new Date())));
        return result.map(quote => entities_1.QuoteEntity.fromPersistence(quote));
    }
}
exports.QuoteRepository = QuoteRepository;
//# sourceMappingURL=quote-repository.js.map