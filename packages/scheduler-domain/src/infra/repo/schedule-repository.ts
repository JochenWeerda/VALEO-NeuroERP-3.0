/* eslint-disable @typescript-eslint/no-unnecessary-type-assertion */
import { and, asc, desc, eq, gte, isNull, like, lte, or, sql } from 'drizzle-orm';
import { db } from '../db/connection';
import { NewSchedule, Schedule, schedules } from '../db/schema';
import { ScheduleEntity } from '../../domain/entities/schedule';

export interface ScheduleQuery {
  tenantId?: string;
  enabled?: boolean;
  name?: string;
  tz?: string;
  page?: number;
  pageSize?: number;
}

export interface ScheduleListResult {
  data: Schedule[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

export class ScheduleRepository {
  async create(scheduleData: NewSchedule): Promise<Schedule> {
    const [schedule] = await db.insert(schedules).values(scheduleData).returning();
    if (!schedule) {
      throw new Error('Failed to create schedule');
    }
    return schedule;
  }

  async findById(id: string): Promise<any> {
    const result = await db
      .select()
      .from(schedules)
      .where(eq(schedules.id, id))
      .limit(1);

    return (result.length > 0 ? result[0] : null) as any;
  }

  async findByTenantAndName(tenantId: string, name: string): Promise<Schedule | null> {
    const result = await db
      .select()
      .from(schedules)
      .where(and(
        eq(schedules.tenantId, tenantId),
        eq(schedules.name, name)
      ))
      .limit(1);

    return result.length > 0 ? (result[0] as Schedule) : null;
  }

  async findDue(now: Date = new Date()): Promise<Schedule[]> {
    return await db
      .select()
      .from(schedules)
      .where(and(
        eq(schedules.enabled, true),
        gte(schedules.nextFireAt, now)
      ))
      .orderBy(asc(schedules.nextFireAt));
  }

  async findByTenant(tenantId: string, query: ScheduleQuery = {}): Promise<ScheduleListResult> {
    const {
      enabled,
      name,
      tz,
      page = 1,
      pageSize = 20,
    } = query;

    // Build where conditions
    const whereConditions = [eq(schedules.tenantId, tenantId)];

    if (enabled !== undefined) {
      whereConditions.push(eq(schedules.enabled, enabled));
    }

    if (name) {
      whereConditions.push(like(schedules.name, `%${name}%`));
    }

    if (tz) {
      whereConditions.push(eq(schedules.tz, tz));
    }

    // Get total count
    const countResult = await db
      .select({ count: sql<number>`count(*)` })
      .from(schedules)
      .where(and(...whereConditions));

    const total = countResult[0]?.count || 0;

    // Get paginated results
    const offset = (page - 1) * pageSize;
    const data = await db
      .select()
      .from(schedules)
      .where(and(...whereConditions))
      .orderBy(desc(schedules.createdAt))
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

  async update(id: string, updates: Partial<NewSchedule>): Promise<Schedule | null> {
    const [schedule] = await db
      .update(schedules)
      .set({
        ...updates,
        updatedAt: new Date(),
        version: sql`${schedules.version} + 1`,
      })
      .where(eq(schedules.id, id))
      .returning();

    return schedule || null;
  }

  async updateNextFire(id: string, nextFireAt: Date): Promise<Schedule | null> {
    const [schedule] = await db
      .update(schedules)
      .set({
        nextFireAt,
        lastFireAt: new Date(),
        updatedAt: new Date(),
        version: sql`${schedules.version} + 1`,
      })
      .where(eq(schedules.id, id))
      .returning();

    return schedule || null;
  }

  async enable(id: string): Promise<Schedule | null> {
    return this.update(id, { enabled: true });
  }

  async disable(id: string): Promise<Schedule | null> {
    return this.update(id, { enabled: false });
  }

  async delete(id: string): Promise<boolean> {
    const result = await db
      .delete(schedules)
      .where(eq(schedules.id, id));

    return (result as any).rowCount > 0;
  }

  async countByTenant(tenantId: string): Promise<number> {
    const result = await db
      .select({ count: sql<number>`count(*)` })
      .from(schedules)
      .where(eq(schedules.tenantId, tenantId));

    return result[0]?.count || 0;
  }

  async countEnabledByTenant(tenantId: string): Promise<number> {
    const result = await db
      .select({ count: sql<number>`count(*)` })
      .from(schedules)
      .where(and(
        eq(schedules.tenantId, tenantId),
        eq(schedules.enabled, true)
      ));

    return result[0]?.count || 0;
  }

  async findEnabledSchedulesBeforeDate(beforeDate: Date, limit = 100): Promise<Schedule[]> {
    const result = await db
      .select()
      .from(schedules)
      .where(and(
        eq(schedules.enabled, true),
        lte(schedules.nextFireAt, beforeDate)
      ))
      .orderBy(asc(schedules.nextFireAt))
      .limit(limit);

    return result as Schedule[];
  }

  // Convert database record to domain entity
  toDomainEntity(schedule: Schedule): ScheduleEntity {
    return new ScheduleEntity({
      id: schedule.id,
      tenantId: schedule.tenantId,
      name: schedule.name,
      description: schedule.description || undefined,
      tz: schedule.tz,
      trigger: schedule.triggerConfig as any, // Type assertion needed
      target: schedule.targetConfig as any, // Type assertion needed
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

  // Convert domain entity to database record
  toDatabaseRecord(entity: ScheduleEntity): NewSchedule {
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

// Export singleton instance
export const scheduleRepository = new ScheduleRepository();