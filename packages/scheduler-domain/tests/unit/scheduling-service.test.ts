import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SchedulingService } from '../../src/domain/services/scheduling-service';
import { ScheduleEntity } from '../../src/domain/entities';
import { EventPublisher } from '../../src/infra/messaging/publisher';

// Mock the event publisher
const mockEventPublisher = {
  publish: vi.fn().mockResolvedValue(undefined),
  publishBatch: vi.fn().mockResolvedValue(undefined),
  isHealthy: vi.fn().mockReturnValue(true),
} as unknown as EventPublisher;

describe('SchedulingService', () => {
  let service: SchedulingService;
  let mockRepository: any;

  beforeEach(() => {
    mockRepository = {
      update: vi.fn().mockResolvedValue(undefined),
    };
    service = new SchedulingService(mockRepository, mockEventPublisher, {
      maxRetries: 3,
      defaultTimezone: 'Europe/Berlin',
      enableBackfill: false,
    });
    vi.clearAllMocks();
  });

  describe('calculateNextFireTime', () => {
    it('should calculate next fire time for CRON trigger', () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *', // Every day at 9 AM
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = service.calculateNextFireTime(schedule);
      expect(result).toBeInstanceOf(Date);
    });

    it('should calculate next fire time for RRULE trigger', () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'RRULE',
          rrule: 'FREQ=DAILY;BYHOUR=9',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = service.calculateNextFireTime(schedule);
      expect(result).toBeInstanceOf(Date);
    });

    it('should calculate next fire time for FIXED_DELAY trigger', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'FIXED_DELAY',
          delaySec: 3600, // 1 hour
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const before = new Date();
      const result = await service.calculateNextFireTime(schedule);
      const after = new Date();

      expect(result).toBeInstanceOf(Date);
      expect(result!.getTime()).toBeGreaterThanOrEqual(before.getTime() + 3600000);
      expect(result!.getTime()).toBeLessThanOrEqual(after.getTime() + 3600000);
    });

    it('should calculate next fire time for ONE_SHOT trigger', () => {
      const futureTime = new Date(Date.now() + 3600000); // 1 hour from now

      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'ONE_SHOT',
          startAt: futureTime,
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = service.calculateNextFireTime(schedule);
      expect(result).toBe(futureTime);
    });

    it('should return null for past ONE_SHOT trigger', () => {
      const pastTime = new Date(Date.now() - 3600000); // 1 hour ago

      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'ONE_SHOT',
          startAt: pastTime,
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = service.calculateNextFireTime(schedule);
      expect(result).toBeNull();
    });

    it('should return null for invalid trigger config', () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          // Missing cron expression
        } as any,
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = service.calculateNextFireTime(schedule);
      expect(result).toBeNull();
    });
  });

  describe('executeSchedule', () => {
    it('should execute EVENT target successfully', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const context = {
        tenantId: 'tenant-1',
        correlationId: 'corr-123',
        userId: 'user-123',
      };

      const result = await service.executeSchedule(schedule, context);

      expect(result.success).toBe(true);
      expect(result.runId).toBeDefined();
      expect(mockEventPublisher.publish).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'test.topic',
          tenantId: 'tenant-1',
          correlationId: 'corr-123',
          payload: expect.objectContaining({
            scheduleId: schedule.id,
            runId: result.runId,
          }),
        })
      );
      expect(mockRepository.update).toHaveBeenCalled();
    });

    it('should handle execution errors', async () => {
      // Mock event publisher to throw error
      (mockEventPublisher.publish as any).mockRejectedValueOnce(new Error('Publish failed'));

      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const context = {
        tenantId: 'tenant-1',
      };

      const result = await service.executeSchedule(schedule, context);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Publish failed');
      expect(result.runId).toBeUndefined();
    });
  });

  describe('validateSchedule', () => {
    it('should validate valid schedule', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = await service.validateSchedule(schedule);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect invalid CRON expression', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: 'invalid cron',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = await service.validateSchedule(schedule);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Invalid CRON expression');
    });

    it('should detect missing RRULE', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'RRULE',
          // Missing rrule
        } as any,
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = await service.validateSchedule(schedule);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('RRULE is required');
    });

    it('should detect invalid FIXED_DELAY', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'FIXED_DELAY',
          delaySec: 0,
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'test.topic',
        },
        enabled: true,
      });

      const result = await service.validateSchedule(schedule);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Delay must be positive');
    });

    it('should detect missing event topic', async () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Test Schedule',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *',
        },
        target: {
          kind: 'EVENT',
          // Missing eventTopic
        } as any,
        enabled: true,
      });

      const result = await service.validateSchedule(schedule);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Event topic is required');
    });
  });
});