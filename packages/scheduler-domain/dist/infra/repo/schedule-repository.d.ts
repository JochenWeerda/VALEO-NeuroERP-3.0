import { Schedule, NewSchedule } from '../db/schema';
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
export declare class ScheduleRepository {
    create(scheduleData: NewSchedule): Promise<Schedule>;
    findById(id: string): Promise<any>;
    findByTenantAndName(tenantId: string, name: string): Promise<Schedule | null>;
    findDue(now?: Date): Promise<Schedule[]>;
    findByTenant(tenantId: string, query?: ScheduleQuery): Promise<ScheduleListResult>;
    update(id: string, updates: Partial<NewSchedule>): Promise<Schedule | null>;
    updateNextFire(id: string, nextFireAt: Date): Promise<Schedule | null>;
    enable(id: string): Promise<Schedule | null>;
    disable(id: string): Promise<Schedule | null>;
    delete(id: string): Promise<boolean>;
    countByTenant(tenantId: string): Promise<number>;
    countEnabledByTenant(tenantId: string): Promise<number>;
    findEnabledSchedulesBeforeDate(beforeDate: Date, limit?: number): Promise<Schedule[]>;
    toDomainEntity(schedule: Schedule): ScheduleEntity;
    toDatabaseRecord(entity: ScheduleEntity): NewSchedule;
}
export declare const scheduleRepository: ScheduleRepository;
//# sourceMappingURL=schedule-repository.d.ts.map