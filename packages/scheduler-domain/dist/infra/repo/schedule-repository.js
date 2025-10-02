"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.scheduleRepository = exports.ScheduleRepository = void 0;
const drizzle_orm_1 = require("drizzle-orm");
const connection_1 = require("../db/connection");
const schema_1 = require("../db/schema");
const schedule_1 = require("../../domain/entities/schedule");
class ScheduleRepository {
    async create(scheduleData) {
        const [schedule] = await connection_1.db.insert(schema_1.schedules).values(scheduleData).returning();
        if (!schedule) {
            throw new Error('Failed to create schedule');
        }
        return schedule;
    }
    async findById(id) {
        const result = await connection_1.db
            .select()
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.eq)(schema_1.schedules.id, id))
            .limit(1);
        return (result.length > 0 ? result[0] : null);
    }
    async findByTenantAndName(tenantId, name) {
        const result = await connection_1.db
            .select()
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.schedules.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.schedules.name, name)))
            .limit(1);
        return result.length > 0 ? result[0] : null;
    }
    async findDue(now = new Date()) {
        return await connection_1.db
            .select()
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.schedules.enabled, true), (0, drizzle_orm_1.gte)(schema_1.schedules.nextFireAt, now)))
            .orderBy((0, drizzle_orm_1.asc)(schema_1.schedules.nextFireAt));
    }
    async findByTenant(tenantId, query = {}) {
        const { enabled, name, tz, page = 1, pageSize = 20, } = query;
        const whereConditions = [(0, drizzle_orm_1.eq)(schema_1.schedules.tenantId, tenantId)];
        if (enabled !== undefined) {
            whereConditions.push((0, drizzle_orm_1.eq)(schema_1.schedules.enabled, enabled));
        }
        if (name) {
            whereConditions.push((0, drizzle_orm_1.like)(schema_1.schedules.name, `%${name}%`));
        }
        if (tz) {
            whereConditions.push((0, drizzle_orm_1.eq)(schema_1.schedules.tz, tz));
        }
        const countResult = await connection_1.db
            .select({ count: (0, drizzle_orm_1.sql) `count(*)` })
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.and)(...whereConditions));
        const total = countResult[0]?.count || 0;
        const offset = (page - 1) * pageSize;
        const data = await connection_1.db
            .select()
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.and)(...whereConditions))
            .orderBy((0, drizzle_orm_1.desc)(schema_1.schedules.createdAt))
            .limit(pageSize)
            .offset(offset);
        return {
            data,
            pagination: {
                page,
                pageSize,
                total,
                totalPages: Math.ceil(total / pageSize),
            },
        };
    }
    async update(id, updates) {
        const [schedule] = await connection_1.db
            .update(schema_1.schedules)
            .set({
            ...updates,
            updatedAt: new Date(),
            version: (0, drizzle_orm_1.sql) `${schema_1.schedules.version} + 1`,
        })
            .where((0, drizzle_orm_1.eq)(schema_1.schedules.id, id))
            .returning();
        return schedule || null;
    }
    async updateNextFire(id, nextFireAt) {
        const [schedule] = await connection_1.db
            .update(schema_1.schedules)
            .set({
            nextFireAt,
            lastFireAt: new Date(),
            updatedAt: new Date(),
            version: (0, drizzle_orm_1.sql) `${schema_1.schedules.version} + 1`,
        })
            .where((0, drizzle_orm_1.eq)(schema_1.schedules.id, id))
            .returning();
        return schedule || null;
    }
    async enable(id) {
        return this.update(id, { enabled: true });
    }
    async disable(id) {
        return this.update(id, { enabled: false });
    }
    async delete(id) {
        const result = await connection_1.db
            .delete(schema_1.schedules)
            .where((0, drizzle_orm_1.eq)(schema_1.schedules.id, id));
        return result.rowCount > 0;
    }
    async countByTenant(tenantId) {
        const result = await connection_1.db
            .select({ count: (0, drizzle_orm_1.sql) `count(*)` })
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.eq)(schema_1.schedules.tenantId, tenantId));
        return result[0]?.count || 0;
    }
    async countEnabledByTenant(tenantId) {
        const result = await connection_1.db
            .select({ count: (0, drizzle_orm_1.sql) `count(*)` })
            .from(schema_1.schedules)
            .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.schedules.tenantId, tenantId), (0, drizzle_orm_1.eq)(schema_1.schedules.enabled, true)));
        return result[0]?.count || 0;
    }
    toDomainEntity(schedule) {
        return new schedule_1.ScheduleEntity({
            id: schedule.id,
            tenantId: schedule.tenantId,
            name: schedule.name,
            description: schedule.description || undefined,
            tz: schedule.tz,
            trigger: schedule.triggerConfig,
            target: schedule.targetConfig,
            payload: schedule.payload || undefined,
            calendar: schedule.calendarConfig || undefined,
            enabled: schedule.enabled,
            nextFireAt: schedule.nextFireAt || undefined,
            lastFireAt: schedule.lastFireAt || undefined,
            createdAt: schedule.createdAt,
            updatedAt: schedule.updatedAt,
            version: schedule.version,
        });
    }
    toDatabaseRecord(entity) {
        return {
            id: entity.id,
            tenantId: entity.tenantId,
            name: entity.name,
            description: entity.description,
            tz: entity.tz,
            triggerType: entity.trigger.type,
            triggerConfig: entity.trigger,
            targetType: entity.target.kind,
            targetConfig: entity.target,
            payload: entity.payload,
            calendarConfig: entity.calendar,
            enabled: entity.enabled,
            nextFireAt: entity.nextFireAt,
            lastFireAt: entity.lastFireAt,
            createdAt: entity.createdAt,
            updatedAt: entity.updatedAt,
            version: entity.version,
        };
    }
}
exports.ScheduleRepository = ScheduleRepository;
exports.scheduleRepository = new ScheduleRepository();
//# sourceMappingURL=schedule-repository.js.map