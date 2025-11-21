"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreditNoteRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class CreditNoteRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.id, id), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.CreditNoteEntity.fromPersistence(result[0]);
    }
    async findByNumber(creditNumber, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.creditNumber, creditNumber), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.CreditNoteEntity.fromPersistence(result[0]);
    }
    async findByInvoiceId(invoiceId, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.invoiceId, invoiceId), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)));
        return result.map(creditNote => entities_1.CreditNoteEntity.fromPersistence(creditNote));
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.creditNotes.customerId, customerId)
        ];
        if (filters.invoiceId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.creditNotes.invoiceId, filters.invoiceId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.creditNotes.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.creditNotes.creditNumber, `%${filters.search}%`));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.creditNotes.id })
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.creditNotes[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.creditNotes[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(creditNote => entities_1.CreditNoteEntity.fromPersistence(creditNote));
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
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.creditNotes.customerId, filters.customerId));
        }
        if (filters.invoiceId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.creditNotes.invoiceId, filters.invoiceId));
        }
        if (filters.status) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.creditNotes.status, filters.status));
        }
        if (filters.search) {
            conditions.push((0, drizzle_orm_1.ilike)(schema_1.creditNotes.creditNumber, `%${filters.search}%`));
        }
        const totalResult = await connection_1.db
            .select({ count: schema_1.creditNotes.id })
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        const sortBy = pagination.sortBy ?? 'createdAt';
        const sortOrder = pagination.sortOrder ?? 'desc';
        const orderBy = sortOrder === 'desc' ? (0, drizzle_orm_1.desc)(schema_1.creditNotes[sortBy]) : (0, drizzle_orm_1.asc)(schema_1.creditNotes[sortBy]);
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(creditNote => entities_1.CreditNoteEntity.fromPersistence(creditNote));
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
        const creditNote = entities_1.CreditNoteEntity.create(input);
        const creditNoteData = creditNote.toPersistence();
        const result = await connection_1.db
            .insert(schema_1.creditNotes)
            .values(creditNoteData)
            .returning();
        return entities_1.CreditNoteEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            notes: input.notes ?? undefined,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.creditNotes)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.id, id), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.CreditNoteEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.id, id), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .returning({ id: schema_1.creditNotes.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.creditNotes.id })
            .from(schema_1.creditNotes)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.id, id), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStatus(id, tenantId, status) {
        const updateData = {
            status,
            updatedAt: new Date()
        };
        if (status === entities_1.CreditNoteStatus.SETTLED) {
            updateData.settledAt = new Date();
        }
        const result = await connection_1.db
            .update(schema_1.creditNotes)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.creditNotes.id, id), (0, drizzle_orm_1.eq)(schema_1.creditNotes.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.CreditNoteEntity.fromPersistence(result[0]);
    }
}
exports.CreditNoteRepository = CreditNoteRepository;
//# sourceMappingURL=credit-note-repository.js.map