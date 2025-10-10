import { ScheduleEntity, TargetType, TriggerType } from '../entities';
import { ScheduleRepository } from '../../infra/repo/schedule-repository';
import { EventPublisher } from '../../infra/messaging/publisher';
import { v4 as uuidv4 } from 'uuid';

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

export class SchedulingService {
  constructor(
    private readonly scheduleRepository: ScheduleRepository,
    private readonly eventPublisher: EventPublisher,
    private readonly config: SchedulingServiceConfig
  ) {}

  /**
   * Calculate next fire time for a schedule
   */
  async calculateNextFireTime(schedule: ScheduleEntity): Promise<Date | null> {
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

  /**
   * Execute a schedule
   */
  async executeSchedule(
    schedule: ScheduleEntity,
    context: ScheduleExecutionContext
  ): Promise<ScheduleExecutionResult> {
    try {
      // Create execution run
      const runId = uuidv4();
      const correlationId = context.correlationId || uuidv4();

      // Execute based on target type
      let success = false;
      let error: string | undefined;

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

      // Calculate next fire time
      const nextFireAt = success ? await this.calculateNextFireTime(schedule) : null;

      // Update schedule with next fire time
      const updateData: any = {
        lastFireAt: new Date(),
      };
      if (nextFireAt !== null) {
        updateData.nextFireAt = nextFireAt;
      }
      await this.scheduleRepository.update(schedule.id, updateData);

      return {
        success,
        runId: success ? runId : undefined,
        error,
        nextFireAt: nextFireAt || undefined,
      };

    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'Unknown execution error',
      };
    }
  }

  /**
   * Get schedules ready for execution
   */
  async getSchedulesReadyForExecution(limit = 100): Promise<any[]> {
    const now = new Date();
    return await this.scheduleRepository.findEnabledSchedulesBeforeDate(now, limit);
  }

  /**
   * Enable/disable schedule
   */
  async setScheduleEnabled(scheduleId: string, enabled: boolean): Promise<void> {
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

  /**
   * Validate schedule configuration
   */
  async validateSchedule(schedule: ScheduleEntity): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    // Validate trigger
    switch (schedule.trigger.type) {
      case 'CRON':
        if (!schedule.trigger.cron) {
          errors.push('CRON expression is required');
        } else if (!this.isValidCronExpression(schedule.trigger.cron)) {
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

    // Validate target
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

  private calculateNextCronFireTime(cronExpression: string, timezone: string, from: Date): Date | null {
    // This would use a cron parser library
    // For now, return a simple calculation
    return new Date(from.getTime() + (60 * 1000)); // Every minute for demo
  }

  private calculateNextRRuleFireTime(rrule: string, timezone: string, from: Date): Date | null {
    // This would use the rrule library
    // For now, return a simple calculation
    return new Date(from.getTime() + (24 * 60 * 60 * 1000)); // Daily for demo
  }

  private async executeEventTarget(
    schedule: ScheduleEntity,
    runId: string,
    correlationId: string,
    context: ScheduleExecutionContext
  ): Promise<boolean> {
    try {
      const event = {
        eventId: uuidv4(),
        eventType: schedule.target.eventTopic!,
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
    } catch (error) {
      console.error('Failed to publish event:', error);
      return false;
    }
  }

  private async executeHttpTarget(
    schedule: ScheduleEntity,
    runId: string,
    correlationId: string,
    context: ScheduleExecutionContext
  ): Promise<boolean> {
    // HTTP execution would be implemented here
    // For now, just return success
    console.log(`Executing HTTP target for schedule ${schedule.id}`);
    return true;
  }

  private async executeQueueTarget(
    schedule: ScheduleEntity,
    runId: string,
    correlationId: string,
    context: ScheduleExecutionContext
  ): Promise<boolean> {
    // Queue execution would be implemented here
    // For now, just return success
    console.log(`Executing queue target for schedule ${schedule.id}`);
    return true;
  }

  private isValidCronExpression(cron: string): boolean {
    // Basic validation - would use a proper cron parser
    const parts = cron.split(' ');
    return parts.length >= 5;
  }
}