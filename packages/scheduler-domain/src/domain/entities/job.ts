import { v4 as uuidv4 } from 'uuid';

export type JobStatus = 'Active' | 'Paused' | 'Disabled';
export type BackoffStrategy = 'FIXED' | 'EXPONENTIAL';

export interface BackoffConfig {
  strategy: BackoffStrategy;
  baseSec: number; // Base delay in seconds
  maxSec?: number; // Maximum delay (optional)
}

export class JobEntity {
  public readonly id: string;
  public readonly tenantId: string;
  public readonly key: string; // Unique identifier within tenant
  public readonly queue: string; // "default", "high", "low", etc.
  public readonly priority: number; // 1-9, higher = more priority
  public readonly maxAttempts: number;
  public readonly backoff: BackoffConfig;
  public readonly timeoutSec: number;
  public readonly concurrencyLimit?: number; // Max concurrent runs
  public readonly slaSec?: number; // SLA in seconds
  public readonly enabled: boolean;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly version: number;

  constructor(props: {
    id?: string;
    tenantId: string;
    key: string;
    queue?: string;
    priority?: number;
    maxAttempts?: number;
    backoff?: BackoffConfig;
    timeoutSec?: number;
    concurrencyLimit?: number;
    slaSec?: number;
    enabled?: boolean;
    createdAt?: Date;
    updatedAt?: Date;
    version?: number;
  }) {
    this.id = props.id || uuidv4();
    this.tenantId = props.tenantId;
    this.key = props.key;
    this.queue = props.queue || 'default';
    this.priority = Math.max(1, Math.min(9, props.priority || 5));
    this.maxAttempts = Math.max(1, props.maxAttempts || 3);
    this.backoff = props.backoff || { strategy: 'EXPONENTIAL', baseSec: 60 };
    this.timeoutSec = Math.max(1, props.timeoutSec || 300); // 5 minutes default
    this.concurrencyLimit = props.concurrencyLimit;
    this.slaSec = props.slaSec;
    this.enabled = props.enabled ?? true;
    this.createdAt = props.createdAt || new Date();
    this.updatedAt = props.updatedAt || new Date();
    this.version = props.version || 1;

    this.validate();
  }

  private validate(): void {
    if (!this.tenantId) {
      throw new Error('tenantId is required');
    }
    if (!this.key) {
      throw new Error('key is required');
    }
    if (this.priority < 1 || this.priority > 9) {
      throw new Error('priority must be between 1 and 9');
    }
    if (this.maxAttempts < 1) {
      throw new Error('maxAttempts must be at least 1');
    }
    if (this.timeoutSec < 1) {
      throw new Error('timeoutSec must be at least 1');
    }
    if (this.concurrencyLimit !== undefined && this.concurrencyLimit < 1) {
      throw new Error('concurrencyLimit must be at least 1');
    }
    if (this.slaSec !== undefined && this.slaSec < 1) {
      throw new Error('slaSec must be at least 1');
    }
  }

  public enable(): JobEntity {
    return new JobEntity({
      ...this,
      enabled: true,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public disable(): JobEntity {
    return new JobEntity({
      ...this,
      enabled: false,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public calculateBackoffDelay(attempt: number): number {
    if (attempt <= 1) return 0;

    const attemptNum = attempt - 1; // First retry is attempt 2

    switch (this.backoff.strategy) {
      case 'FIXED':
        return Math.min(this.backoff.baseSec, this.backoff.maxSec || this.backoff.baseSec);

      case 'EXPONENTIAL':
        const delay = this.backoff.baseSec * Math.pow(2, attemptNum - 1);
        return this.backoff.maxSec ? Math.min(delay, this.backoff.maxSec) : delay;

      default:
        return this.backoff.baseSec;
    }
  }

  public isSlaViolated(startedAt: Date, finishedAt?: Date): boolean {
    if (!this.slaSec) return false;

    const endTime = finishedAt || new Date();
    const durationSec = (endTime.getTime() - startedAt.getTime()) / 1000;

    return durationSec > this.slaSec;
  }

  public getQueueKey(): string {
    return `${this.tenantId}:${this.queue}`;
  }

  public getJobKey(): string {
    return `${this.tenantId}:${this.key}`;
  }
}