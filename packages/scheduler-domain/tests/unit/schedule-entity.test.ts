import { describe, it, expect } from 'vitest';
import { ScheduleEntity } from '../../src/domain/entities';

describe('ScheduleEntity', () => {
  describe('creation', () => {
    it('should create a valid schedule entity', () => {
      const schedule = new ScheduleEntity({
        tenantId: 'tenant-1',
        name: 'Daily Report',
        tz: 'Europe/Berlin',
        trigger: {
          type: 'CRON',
          cron: '0 9 * * *',
        },
        target: {
          kind: 'EVENT',
          eventTopic: 'reports.daily.generate',
        },
        enabled: true,
      });

      expect(schedule.id).toBeDefined();
      expect(schedule.tenantId).toBe('tenant-1');
      expect(schedule.name).toBe('Daily Report');
      expect(schedule.trigger.type).toBe('CRON');
      expect(schedule.target.kind).toBe('EVENT');
      expect(schedule.enabled).toBe(true);
      expect(schedule.createdAt).toBeInstanceOf(Date);
      expect(schedule.updatedAt).toBeInstanceOf(Date);
    });

    it('should validate required fields', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: '',
          name: 'Test',
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
      }).toThrow('tenantId is required');
    });

    it('should validate CRON trigger', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
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
      }).toThrow('cron expression is required for CRON trigger');
    });

    it('should validate RRULE trigger', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
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
      }).toThrow('rrule is required for RRULE trigger');
    });

    it('should validate FIXED_DELAY trigger', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
          tz: 'Europe/Berlin',
          trigger: {
            type: 'FIXED_DELAY',
            delaySec: 0, // Invalid delay
          },
          target: {
            kind: 'EVENT',
            eventTopic: 'test.topic',
          },
          enabled: true,
        });
      }).toThrow('delaySec must be positive for FIXED_DELAY trigger');
    });

    it('should validate ONE_SHOT trigger', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
          tz: 'Europe/Berlin',
          trigger: {
            type: 'ONE_SHOT',
            // Missing startAt
          } as any,
          target: {
            kind: 'EVENT',
            eventTopic: 'test.topic',
          },
          enabled: true,
        });
      }).toThrow('startAt is required for ONE_SHOT trigger');
    });

    it('should validate EVENT target', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
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
      }).toThrow('eventTopic is required for EVENT target');
    });

    it('should validate HTTP target', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
          tz: 'Europe/Berlin',
          trigger: {
            type: 'CRON',
            cron: '0 9 * * *',
          },
          target: {
            kind: 'HTTP',
            // Missing http.url
          } as any,
          enabled: true,
        });
      }).toThrow('url is required for HTTP target');
    });

    it('should validate QUEUE target', () => {
      expect(() => {
        new ScheduleEntity({
          tenantId: 'tenant-1',
          name: 'Test',
          tz: 'Europe/Berlin',
          trigger: {
            type: 'CRON',
            cron: '0 9 * * *',
          },
          target: {
            kind: 'QUEUE',
            // Missing queue.topic
          } as any,
          enabled: true,
        });
      }).toThrow('topic is required for QUEUE target');
    });
  });

  describe('state management', () => {
    let schedule: ScheduleEntity;

    beforeEach(() => {
      schedule = new ScheduleEntity({
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
    });

    it('should enable schedule', () => {
      const disabledSchedule = schedule.disable();
      const enabledSchedule = disabledSchedule.enable();

      expect(enabledSchedule.enabled).toBe(true);
      expect(enabledSchedule.version).toBe(3); // Initial + disable + enable
    });

    it('should disable schedule', () => {
      const disabledSchedule = schedule.disable();

      expect(disabledSchedule.enabled).toBe(false);
      expect(disabledSchedule.version).toBe(2);
    });

    it('should update next fire time', () => {
      const nextFireAt = new Date(Date.now() + 3600000); // 1 hour from now
      const updatedSchedule = schedule.updateNextFire(nextFireAt);

      expect(updatedSchedule.nextFireAt).toBe(nextFireAt);
      expect(updatedSchedule.version).toBe(2);
    });

    it('should update last fire time', () => {
      const lastFireAt = new Date();
      const updatedSchedule = schedule.updateLastFire(lastFireAt);

      expect(updatedSchedule.lastFireAt).toBe(lastFireAt);
      expect(updatedSchedule.version).toBe(2);
    });
  });

  describe('execution logic', () => {
    it('should determine if schedule is due', () => {
      const pastTime = new Date(Date.now() - 3600000); // 1 hour ago
      const futureTime = new Date(Date.now() + 3600000); // 1 hour from now

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
        nextFireAt: pastTime,
      });

      expect(schedule.isDue()).toBe(true);

      const futureSchedule = schedule.updateNextFire(futureTime);
      expect(futureSchedule.isDue()).toBe(false);
    });

    it('should determine if schedule should fire', () => {
      const pastTime = new Date(Date.now() - 3600000); // 1 hour ago

      const enabledSchedule = new ScheduleEntity({
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
        nextFireAt: pastTime,
      });

      const disabledSchedule = new ScheduleEntity({
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
        enabled: false,
        nextFireAt: pastTime,
      });

      expect(enabledSchedule.shouldFire()).toBe(true);
      expect(disabledSchedule.shouldFire()).toBe(false);
    });

    it('should generate dedupe key', () => {
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

      const fireTime = new Date('2024-01-01T09:00:00Z');
      const dedupeKey = schedule.getDedupeKey(fireTime);

      expect(dedupeKey).toBe(`${schedule.id}@${fireTime.toISOString()}`);
    });
  });
});