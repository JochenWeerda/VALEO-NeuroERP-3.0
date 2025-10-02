"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContactRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const uuid_1 = require("uuid");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class ContactRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.id, id), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.ContactEntity.fromPersistence(result[0]);
    }
    async findByEmail(email, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.email, email), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.ContactEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.contacts.customerId, customerId)
        ];
        if (filters.isPrimary !== undefined) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.contacts.isPrimary, filters.isPrimary));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.contacts.id })
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'createdAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.contacts[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.contacts[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(contact => entities_1.ContactEntity.fromPersistence(contact));
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
    async findAll(tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.contacts.customerId, filters.customerId));
        }
        if (filters.isPrimary !== undefined) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.contacts.isPrimary, filters.isPrimary));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.contacts.id })
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'createdAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.contacts[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.contacts[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(contact => entities_1.ContactEntity.fromPersistence(contact));
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
        const contactData = {
            ...input,
            id: (0, uuid_1.v4)(),
            isPrimary: input.isPrimary || false,
            createdAt: new Date(),
            updatedAt: new Date(),
            version: 1
        };
        const result = await connection_1.db
            .insert(schema_1.contacts)
            .values(contactData)
            .returning();
        return entities_1.ContactEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.contacts)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.id, id), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.ContactEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.contacts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.id, id), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)))
            .returning({ id: schema_1.contacts.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.contacts.id })
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.id, id), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async setPrimaryContact(customerId, contactId, tenantId) {
        // First, set all contacts for this customer to non-primary
        await connection_1.db
            .update(schema_1.contacts)
            .set({ isPrimary: false, updatedAt: new Date() })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.customerId, customerId), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)));
        // Then set the specified contact as primary
        await connection_1.db
            .update(schema_1.contacts)
            .set({ isPrimary: true, updatedAt: new Date() })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.id, contactId), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId)));
    }
    async getPrimaryContact(customerId, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.contacts)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.contacts.customerId, customerId), (0, drizzle_orm_1.eq)(schema_1.contacts.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.contacts.isPrimary, true)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.ContactEntity.fromPersistence(result[0]);
    }
}
exports.ContactRepository = ContactRepository;
//# sourceMappingURL=contact-repository.js.map