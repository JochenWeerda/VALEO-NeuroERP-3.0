"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpportunityRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const uuid_1 = require("uuid");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const entities_1 = require("../../domain/entities");
class OpportunityRepository {
    async findById(id, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.id, id), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)))
            .limit(1);
        if (result.length === 0) {
            return null;
        }
        return entities_1.OpportunityEntity.fromPersistence(result[0]);
    }
    async findByCustomerId(customerId, tenantId, filters = {}, pagination = { page: 1, pageSize: 20 }) {
        const conditions = [
            (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId),
            (0, drizzle_orm_1.eq)(schema_1.opportunities.customerId, customerId)
        ];
        if (filters.stage) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.opportunities.stage, filters.stage));
        }
        if (filters.ownerUserId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.opportunities.ownerUserId, filters.ownerUserId));
        }
        if (filters.amountMin !== undefined) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.opportunities.amountNet, filters.amountMin.toString()));
        }
        if (filters.amountMax !== undefined) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.opportunities.amountNet, filters.amountMax.toString()));
        }
        if (filters.expectedCloseDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.opportunities.expectedCloseDate, filters.expectedCloseDateFrom));
        }
        if (filters.expectedCloseDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.opportunities.expectedCloseDate, filters.expectedCloseDateTo));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.opportunities.id })
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'createdAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.opportunities[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.opportunities[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(opportunity => entities_1.OpportunityEntity.fromPersistence(opportunity));
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
        const conditions = [(0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)];
        if (filters.customerId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.opportunities.customerId, filters.customerId));
        }
        if (filters.stage) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.opportunities.stage, filters.stage));
        }
        if (filters.ownerUserId) {
            conditions.push((0, drizzle_orm_1.eq)(schema_1.opportunities.ownerUserId, filters.ownerUserId));
        }
        if (filters.amountMin !== undefined) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.opportunities.amountNet, filters.amountMin.toString()));
        }
        if (filters.amountMax !== undefined) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.opportunities.amountNet, filters.amountMax.toString()));
        }
        if (filters.expectedCloseDateFrom) {
            conditions.push((0, drizzle_orm_1.gte)(schema_1.opportunities.expectedCloseDate, filters.expectedCloseDateFrom));
        }
        if (filters.expectedCloseDateTo) {
            conditions.push((0, drizzle_orm_1.lte)(schema_1.opportunities.expectedCloseDate, filters.expectedCloseDateTo));
        }
        // Get total count
        const totalResult = await connection_1.db
            .select({ count: schema_1.opportunities.id })
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)(...conditions));
        const total = totalResult[0]?.count || 0;
        // Apply sorting
        const sortBy = pagination.sortBy || 'createdAt';
        const sortOrder = pagination.sortOrder || 'desc';
        const orderBy = sortOrder === 'desc'
            ? (0, drizzle_orm_1.desc)(schema_1.opportunities[sortBy])
            : (0, drizzle_orm_1.asc)(schema_1.opportunities[sortBy]);
        // Get paginated results
        const offset = (pagination.page - 1) * pagination.pageSize;
        const result = await connection_1.db
            .select()
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)(...conditions))
            .orderBy(orderBy)
            .limit(pagination.pageSize)
            .offset(offset);
        const entities = result.map(opportunity => entities_1.OpportunityEntity.fromPersistence(opportunity));
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
        const opportunityData = {
            ...input,
            id: (0, uuid_1.v4)(),
            stage: input.stage || entities_1.OpportunityStage.LEAD,
            probability: input.probability !== undefined ? input.probability : 0.1,
            createdAt: new Date(),
            updatedAt: new Date(),
            version: 1
        };
        const result = await connection_1.db
            .insert(schema_1.opportunities)
            .values(opportunityData)
            .returning();
        return entities_1.OpportunityEntity.fromPersistence(result[0]);
    }
    async update(id, tenantId, input) {
        const updateData = {
            ...input,
            updatedAt: new Date()
        };
        const result = await connection_1.db
            .update(schema_1.opportunities)
            .set(updateData)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.id, id), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.OpportunityEntity.fromPersistence(result[0]);
    }
    async delete(id, tenantId) {
        const result = await connection_1.db
            .delete(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.id, id), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)))
            .returning({ id: schema_1.opportunities.id });
        return result.length > 0;
    }
    async exists(id, tenantId) {
        const result = await connection_1.db
            .select({ id: schema_1.opportunities.id })
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.id, id), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)))
            .limit(1);
        return result.length > 0;
    }
    async updateStage(id, tenantId, stage) {
        const result = await connection_1.db
            .update(schema_1.opportunities)
            .set({
            stage,
            updatedAt: new Date()
        })
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.id, id), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)))
            .returning();
        if (result.length === 0) {
            return null;
        }
        return entities_1.OpportunityEntity.fromPersistence(result[0]);
    }
    async markAsWon(id, tenantId) {
        return this.updateStage(id, tenantId, entities_1.OpportunityStage.WON);
    }
    async markAsLost(id, tenantId) {
        return this.updateStage(id, tenantId, entities_1.OpportunityStage.LOST);
    }
    async getByStage(stage, tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.stage, stage), (0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId)));
        return result.map(opportunity => entities_1.OpportunityEntity.fromPersistence(opportunity));
    }
    async getOpenOpportunities(tenantId) {
        const result = await connection_1.db
            .select()
            .from(schema_1.opportunities)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.opportunities.tenantId, tenantId), (0, drizzle_orm_1.and)((0, drizzle_orm_1.ne)(schema_1.opportunities.stage, entities_1.OpportunityStage.WON), (0, drizzle_orm_1.ne)(schema_1.opportunities.stage, entities_1.OpportunityStage.LOST))));
        return result.map(opportunity => entities_1.OpportunityEntity.fromPersistence(opportunity));
    }
}
exports.OpportunityRepository = OpportunityRepository;
//# sourceMappingURL=opportunity-repository.js.map