import { v4 as uuidv4 } from 'uuid';

export type ScheduleStatus = 'Active' | 'Paused' | 'Disabled';
export type TriggerType = 'CRON' | 'RRULE' | 'FIXED_DELAY' | 'ONE_SHOT';
export type TargetType = 'EVENT' | 'HTTP' | 'QUEUE';

export interface Trigger {
  type: TriggerType;
  cron?: string; // CRON expression
  rrule?: string; // iCal RRULE
  delaySec?: number; // FIXED_DELAY
  startAt?: Date; // ONE_SHOT
}

export interface Target {
  kind: TargetType;
  eventTopic?: string; // EVENT
  http?: {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    headers?: Record<string, string>;
    hmacKeyRef?: string;
  }; // HTTP
  queue?: {
    topic: string;
  }; // QUEUE
}

export interface CalendarConfig {
  holidaysCode?: string; // e.g., "DE-BY-AGRI"
  businessDaysOnly?: boolean;
}

export class ScheduleEntity {
  public readonly id: string;
  public readonly tenantId: string;
  public readonly name: string;
  public readonly description?: string;
  public readonly tz: string;
  public readonly trigger: Trigger;
  public readonly target: Target;
  public readonly payload?: Record<string, any>;
  public readonly calendar?: CalendarConfig;
  public readonly enabled: boolean;
  public readonly nextFireAt?: Date;
  public readonly lastFireAt?: Date;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  constructor(props: {
    id?: string;
    tenantId: string;
    name: string;
    description?: string;
    tz: string;
    trigger: Trigger;
    target: Target;
    payload?: Record<string, any>;
    calendar?: CalendarConfig;
    enabled?: boolean;
    nextFireAt?: Date;
    lastFireAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    version?: number;
  }) {
    this.id = props.id || uuidv4();
    this.tenantId = props.tenantId;
    this.name = props.name;
    this.description = props.description;
    this.tz = props.tz;
    this.trigger = props.trigger;
    this.target = props.target;
    this.payload = props.payload;
    this.calendar = props.calendar;
    this.enabled = props.enabled ?? true;
    this.nextFireAt = props.nextFireAt;
    this.lastFireAt = props.lastFireAt;
    this.createdAt = props.createdAt || new Date();
    this.updatedAt = props.updatedAt || new Date();
    this.version = props.version || 1;

    this.validate();
  }

  private validate(): void {
    if (!this.tenantId) {
      throw new Error('tenantId is required');
    }
    if (!this.name) {
      throw new Error('name is required');
    }
    if (!this.tz) {
      throw new Error('tz is required');
    }
    this.validateTrigger();
    this.validateTarget();
  }

  private validateTrigger(): void {
    switch (this.trigger.type) {
      case 'CRON':
        if (!this.trigger.cron) {
          throw new Error('cron expression is required for CRON trigger');
        }
        break;
      case 'RRULE':
        if (!this.trigger.rrule) {
          throw new Error('rrule is required for RRULE trigger');
        }
        break;
      case 'FIXED_DELAY':
        if (!this.trigger.delaySec || this.trigger.delaySec <= 0) {
          throw new Error('delaySec must be positive for FIXED_DELAY trigger');
        }
        break;
      case 'ONE_SHOT':
        if (!this.trigger.startAt) {
          throw new Error('startAt is required for ONE_SHOT trigger');
        }
        break;
      default:
        throw new Error(`Unknown trigger type: ${this.trigger.type}`);
    }
  }

  private validateTarget(): void {
    switch (this.target.kind) {
      case 'EVENT':
        if (!this.target.eventTopic) {
          throw new Error('eventTopic is required for EVENT target');
        }
        break;
      case 'HTTP':
        if (!this.target.http?.url) {
          throw new Error('url is required for HTTP target');
        }
        break;
      case 'QUEUE':
        if (!this.target.queue?.topic) {
          throw new Error('topic is required for QUEUE target');
        }
        break;
      default:
        throw new Error(`Unknown target kind: ${this.target.kind}`);
    }
  }

  public enable(): ScheduleEntity {
    return new ScheduleEntity({
      ...this,
      enabled: true,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public disable(): ScheduleEntity {
    return new ScheduleEntity({
      ...this,
      enabled: false,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public updateNextFire(nextFireAt: Date): ScheduleEntity {
    return new ScheduleEntity({
      ...this,
      nextFireAt,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public updateLastFire(lastFireAt: Date): ScheduleEntity {
    return new ScheduleEntity({
      ...this,
      lastFireAt,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public isDue(now: Date = new Date()): boolean {
    if (!this.enabled || !this.nextFireAt) {
      return false;
    }
    return this.nextFireAt <= now;
  }

  public shouldFire(now: Date = new Date()): boolean {
    return this.enabled && this.isDue(now);
  }

  public getDedupeKey(fireTime: Date): string {
    return `${this.id}@${fireTime.toISOString()}`;
  }
}