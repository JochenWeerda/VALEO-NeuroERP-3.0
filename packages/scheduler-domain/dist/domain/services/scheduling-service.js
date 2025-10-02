"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SchedulingService = void 0;
const uuid_1 = require("uuid");
class SchedulingService {
    scheduleRepository;
    eventPublisher;
    config;
    constructor(scheduleRepository, eventPublisher, config) {
        this.scheduleRepository = scheduleRepository;
        this.eventPublisher = eventPublisher;
        this.config = config;
    }
    async calculateNextFireTime(schedule) {
        const now = new Date();
        switch (schedule.trigger.type) {
            case 'CRON':
                return schedule.trigger.cron
                    ? this.calculateNextCronFireTime(schedule.trigger.cron, schedule.tz, now)
                    : null;
            case 'RRULE':
                return schedule.trigger.rrule
                    ? this.calculateNextRRuleFireTime(schedule.trigger.rrule, schedule.tz, now)
                    : null;
            case 'FIXED_DELAY':
                return schedule.trigger.delaySec
                    ? new Date(now.getTime() + (schedule.trigger.delaySec * 1000))
                    : null;
            case 'ONE_SHOT':
                return schedule.trigger.startAt && schedule.trigger.startAt > now
                    ? schedule.trigger.startAt
                    : null;
            default:
                return null;
        }
    }
    async executeSchedule(schedule, context) {
        try {
            const runId = (0, uuid_1.v4)();
            const correlationId = context.correlationId || (0, uuid_1.v4)();
            let success = false;
            let error;
            switch (schedule.target.kind) {
                case 'EVENT':
                    success = await this.executeEventTarget(schedule, runId, correlationId, context);
                    break;
                case 'HTTP':
                    success = await this.executeHttpTarget(schedule, runId, correlationId, context);
                    break;
                case 'QUEUE':
                    success = await this.executeQueueTarget(schedule, runId, correlationId, context);
                    break;
                default:
                    error = `Unsupported target type: ${schedule.target.kind}`;
            }
            const nextFireAt = success ? await this.calculateNextFireTime(schedule) : undefined;
            await this.scheduleRepository.update(schedule.id, {
                nextFireAt: nextFireAt || undefined,
                lastFireAt: new Date(),
            });
            return {
                success,
                runId: success ? runId : undefined,
                error,
                nextFireAt,
            };
        }
        catch (err) {
            return {
                success: false,
                error: err instanceof Error ? err.message : 'Unknown execution error',
            };
        }
    }
    async getSchedulesReadyForExecution(limit = 100) {
        const now = new Date();
        return await this.scheduleRepository.findEnabledSchedulesBeforeDate(now, limit);
    }
    async setScheduleEnabled(scheduleId, enabled) {
        const schedule = await this.scheduleRepository.findById(scheduleId);
        if (!schedule) {
            throw new Error(`Schedule ${scheduleId} not found`);
        }
        const nextFireAt = enabled ? await this.calculateNextFireTime(schedule) : null;
        await this.scheduleRepository.update(scheduleId, {
            enabled,
            nextFireAt,
        });
    }
    async validateSchedule(schedule) {
        const errors = [];
        switch (schedule.trigger.type) {
            case 'CRON':
                if (!schedule.trigger.cron) {
                    errors.push('CRON expression is required');
                }
                else if (!this.isValidCronExpression(schedule.trigger.cron)) {
                    errors.push('Invalid CRON expression');
                }
                break;
            case 'RRULE':
                if (!schedule.trigger.rrule) {
                    errors.push('RRULE is required');
                }
                break;
            case 'FIXED_DELAY':
                if (!schedule.trigger.delaySec || schedule.trigger.delaySec <= 0) {
                    errors.push('Delay must be positive');
                }
                break;
            case 'ONE_SHOT':
                if (!schedule.trigger.startAt) {
                    errors.push('Start time is required for one-shot schedules');
                }
                break;
        }
        switch (schedule.target.kind) {
            case 'EVENT':
                if (!schedule.target.eventTopic) {
                    errors.push('Event topic is required');
                }
                break;
            case 'HTTP':
                if (!schedule.target.http?.url) {
                    errors.push('HTTP URL is required');
                }
                break;
            case 'QUEUE':
                if (!schedule.target.queue?.topic) {
                    errors.push('Queue topic is required');
                }
                break;
        }
        return {
            valid: errors.length === 0,
            errors,
        };
    }
    calculateNextCronFireTime(cronExpression, timezone, from) {
        return new Date(from.getTime() + (60 * 1000));
    }
    calculateNextRRuleFireTime(rrule, timezone, from) {
        return new Date(from.getTime() + (24 * 60 * 60 * 1000));
    }
    async executeEventTarget(schedule, runId, correlationId, context) {
        try {
            const event = {
                eventId: (0, uuid_1.v4)(),
                eventType: schedule.target.eventTopic,
                eventVersion: 1,
                occurredAt: new Date().toISOString(),
                tenantId: schedule.tenantId,
                correlationId,
                payload: {
                    scheduleId: schedule.id,
                    runId,
                    firedAt: new Date().toISOString(),
                },
            };
            await this.eventPublisher.publish(event);
            return true;
        }
        catch (error) {
            console.error('Failed to publish event:', error);
            return false;
        }
    }
    async executeHttpTarget(schedule, runId, correlationId, context) {
        console.log(`Executing HTTP target for schedule ${schedule.id}`);
        return true;
    }
    async executeQueueTarget(schedule, runId, correlationId, context) {
        console.log(`Executing queue target for schedule ${schedule.id}`);
        return true;
    }
    isValidCronExpression(cron) {
        const parts = cron.split(' ');
        return parts.length >= 5;
    }
}
exports.SchedulingService = SchedulingService;
//# sourceMappingURL=scheduling-service.js.map