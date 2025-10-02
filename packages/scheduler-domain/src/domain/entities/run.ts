import { v4 as uuidv4 } from 'uuid';

export type RunStatus = 'Pending' | 'Running' | 'Succeeded' | 'Failed' | 'Missed' | 'Dead';

export interface RunMetrics {
  latencyMs?: number; // Time from scheduled to started
  durationMs?: number; // Time from started to finished
}

export class RunEntity {
  public readonly id: string;
  public readonly tenantId: string;
  public readonly scheduleId?: string;
  public readonly jobId?: string;
  public readonly dedupeKey?: string;
  public readonly status: RunStatus;
  public readonly startedAt?: Date;
  public readonly finishedAt?: Date;
  public readonly attempt: number;
  public readonly error?: string;
  public readonly metrics?: RunMetrics;
  public readonly workerId?: string;
  public readonly payload?: Record<string, any>;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  constructor(props: {
    id?: string;
    tenantId: string;
    scheduleId?: string;
    jobId?: string;
    dedupeKey?: string;
    status?: RunStatus;
    startedAt?: Date;
    finishedAt?: Date;
    attempt?: number;
    error?: string;
    metrics?: RunMetrics;
    workerId?: string;
    payload?: Record<string, any>;
    createdAt?: Date;
    updatedAt?: Date;
  }) {
    this.id = props.id || uuidv4();
    this.tenantId = props.tenantId;
    this.scheduleId = props.scheduleId;
    this.jobId = props.jobId;
    this.dedupeKey = props.dedupeKey;
    this.status = props.status || 'Pending';
    this.startedAt = props.startedAt;
    this.finishedAt = props.finishedAt;
    this.attempt = Math.max(1, props.attempt || 1);
    this.error = props.error;
    this.metrics = props.metrics;
    this.workerId = props.workerId;
    this.payload = props.payload;
    this.createdAt = props.createdAt || new Date();
    this.updatedAt = props.updatedAt || new Date();

    this.validate();
  }

  private validate(): void {
    if (!this.tenantId) {
      throw new Error('tenantId is required');
    }
    if (!this.scheduleId && !this.jobId) {
      throw new Error('Either scheduleId or jobId must be provided');
    }
    if (this.scheduleId && this.jobId) {
      throw new Error('Cannot have both scheduleId and jobId');
    }
    if (this.attempt < 1) {
      throw new Error('attempt must be at least 1');
    }
  }

  public start(workerId?: string): RunEntity {
    if (this.status !== 'Pending') {
      throw new Error(`Cannot start run in status: ${this.status}`);
    }

    const now = new Date();
    const latencyMs = this.createdAt ? now.getTime() - this.createdAt.getTime() : undefined;

    return new RunEntity({
      ...this,
      status: 'Running',
      startedAt: now,
      workerId,
      metrics: {
        ...this.metrics,
        latencyMs,
      },
      updatedAt: now,
    });
  }

  public succeed(): RunEntity {
    if (this.status !== 'Running') {
      throw new Error(`Cannot succeed run in status: ${this.status}`);
    }

    const now = new Date();
    const durationMs = this.startedAt ? now.getTime() - this.startedAt.getTime() : undefined;

    return new RunEntity({
      ...this,
      status: 'Succeeded',
      finishedAt: now,
      metrics: {
        ...this.metrics,
        durationMs,
      },
      updatedAt: now,
    });
  }

  public fail(error: string): RunEntity {
    if (this.status !== 'Running') {
      throw new Error(`Cannot fail run in status: ${this.status}`);
    }

    const now = new Date();
    const durationMs = this.startedAt ? now.getTime() - this.startedAt.getTime() : undefined;

    return new RunEntity({
      ...this,
      status: 'Failed',
      finishedAt: now,
      error,
      metrics: {
        ...this.metrics,
        durationMs,
      },
      updatedAt: now,
    });
  }

  public markDead(error: string): RunEntity {
    const now = new Date();

    return new RunEntity({
      ...this,
      status: 'Dead',
      finishedAt: now,
      error,
      updatedAt: now,
    });
  }

  public markMissed(): RunEntity {
    if (this.status !== 'Pending') {
      throw new Error(`Cannot mark as missed in status: ${this.status}`);
    }

    return new RunEntity({
      ...this,
      status: 'Missed',
      finishedAt: new Date(),
      updatedAt: new Date(),
    });
  }

  public isTerminal(): boolean {
    return ['Succeeded', 'Failed', 'Dead', 'Missed'].includes(this.status);
  }

  public isActive(): boolean {
    return this.status === 'Running';
  }

  public isPending(): boolean {
    return this.status === 'Pending';
  }

  public canRetry(): boolean {
    return this.status === 'Failed' && this.error !== undefined;
  }

  public getDurationMs(): number | undefined {
    if (!this.startedAt || !this.finishedAt) return undefined;
    return this.finishedAt.getTime() - this.startedAt.getTime();
  }

  public getLatencyMs(): number | undefined {
    if (!this.createdAt || !this.startedAt) return undefined;
    return this.startedAt.getTime() - this.createdAt.getTime();
  }
}