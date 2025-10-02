"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
const uuid_1 = require("uuid");
class CustomerRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.customers)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async findByNumber(number, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.customers)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.number, number), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async findAll(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)];
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.customers.name, `%${filters.search}%`));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.customers.status, filters.status));
        }
        if (filters.ownerUserId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.customers.ownerUserId, filters.ownerUserId));
        }
        if (filters.tags && filters.tags.length > 0) {
            // This is a simplified approach - in production you might want to use JSON operators
            // For exact tag matching, you might need to adjust based on your needs
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.customers.id })
            .from(schema_1.customers)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'createdAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.customers[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.customers[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.customers)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(customer => entities_1.CustomerEntity.fromPersistence(customer));
        return {
            data: entities,
            pagination: {
                page: pagination.page,
                pageSize: pagination.pageSize,
                total,
                totalPages: Math.ceil(total / pagination.pageSize)
            }
        };
    }
    async create(input) {
        const customerData = {
            ...input,
            id: (0, uuid_1.v4)(),
            status: input.status || entities_1.CustomerStatus.PROSPECT,
            tags: input.tags || [],
            shippingAddresses: input.shippingAddresses || [],
            createdAt: new Date(),
            updatedAt: new Date(),
            version: 1
        };
        const result = await connection_1.db
            .insert(schema_1.customers)
            .values(customerData)
            .returning();
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.customers)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.customers)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .returning({ id: schema_1.customers.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.customers.id })
            .from(schema_1.customers)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStatus(id, tenantId, status) {
        const result = await connection_1.db
            .update(schema_1.customers)
            .set({
            status,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async addTag(id, tenantId, tag) {
        // First get current tags
        const current = await this.findById(id, tenantId);
        if (!current)
            return null;
        const currentTags = current.tags;
        if (currentTags.includes(tag)) {
            return current; // Tag already exists
        }
        const updatedTags = [...currentTags, tag];
        const result = await connection_1.db
            .update(schema_1.customers)
            .set({
            tags: updatedTags,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .returning();
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
    async removeTag(id, tenantId, tag) {
        // First get current tags
        const current = await this.findById(id, tenantId);
        if (!current)
            return null;
        const currentTags = current.tags;
        const tagIndex = currentTags.indexOf(tag);
        if (tagIndex === -1) {
            return current; // Tag doesn't exist
        }
        const updatedTags = currentTags.filter(t => t !== tag);
        const result = await connection_1.db
            .update(schema_1.customers)
            .set({
            tags: updatedTags,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.customers.id, id), (0, drizzle_orm_1.eq)(schema_1.customers.tenantId, tenantId)))
            .returning();
        return entities_1.CustomerEntity.fromPersistence(result[0]);
    }
}
exports.CustomerRepository = CustomerRepository;
//# sourceMappingURL=customer-repository.js.map