import { ScheduleEntity } from '../entities';
import { ScheduleRepository } from '../../infra/repo/schedule-repository';
import { EventPublisher } from '../../infra/messaging/publisher';
export interface SchedulingServiceConfig {
    maxRetries: number;
    defaultTimezone: string;
    enableBackfill: boolean;
}
export interface ScheduleExecutionContext {
    tenantId: string;
    correlationId?: string;
    causationId?: string;
    userId?: string;
}
export interface ScheduleExecutionResult {
    success: boolean;
    runId?: string;
    error?: string;
    nextFireAt?: Date;
}
export declare class SchedulingService {
    private scheduleRepository;
    private eventPublisher;
    private config;
    constructor(scheduleRepository: ScheduleRepository, eventPublisher: EventPublisher, config: SchedulingServiceConfig);
    calculateNextFireTime(schedule: ScheduleEntity): Promise<Date | null>;
    executeSchedule(schedule: ScheduleEntity, context: ScheduleExecutionContext): Promise<ScheduleExecutionResult>;
    getSchedulesReadyForExecution(limit?: number): Promise<any[]>;
    setScheduleEnabled(scheduleId: string, enabled: boolean): Promise<void>;
    validateSchedule(schedule: ScheduleEntity): Promise<{
        valid: boolean;
        errors: string[];
    }>;
    private calculateNextCronFireTime;
    private calculateNextRRuleFireTime;
    private executeEventTarget;
    private executeHttpTarget;
    private executeQueueTarget;
    private isValidCronExpression;
}
//# sourceMappingURL=scheduling-service.d.ts.map