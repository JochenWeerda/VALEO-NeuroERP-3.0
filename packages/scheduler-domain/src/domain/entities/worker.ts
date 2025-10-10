import { v4 as uuidv4 } from 'uuid';

export type WorkerStatus = 'Online' | 'Offline' | 'Maintenance';

export interface WorkerCapabilities {
  queues: string[]; // ["default", "high", "low"]
  jobKeys: string[]; // Specific job keys this worker can handle
}

export class WorkerEntity {
  public readonly id: string;
  public readonly tenantId?: string; // null for shared workers
  public readonly name: string;
  public readonly capabilities: WorkerCapabilities;
  public readonly heartbeatAt: Date;
  public readonly status: WorkerStatus;
  public readonly maxParallel: number;
  public readonly currentJobs: number;
  public readonly version: number;
  public readonly createdAt: Date;
  public readonly updatedAt: Date;

  constructor(props: {
    id?: string;
    tenantId?: string;
    name: string;
    capabilities: WorkerCapabilities;
    heartbeatAt?: Date;
    status?: WorkerStatus;
    maxParallel?: number;
    currentJobs?: number;
    version?: number;
    createdAt?: Date;
    updatedAt?: Date;
  }) {
    this.id = props.id || uuidv4();
    this.tenantId = props.tenantId;
    this.name = props.name;
    this.capabilities = props.capabilities;
    this.heartbeatAt = props.heartbeatAt || new Date();
    this.status = props.status || 'Online';
    this.maxParallel = Math.max(1, props.maxParallel || 10);
    this.currentJobs = Math.max(0, props.currentJobs || 0);
    this.version = props.version || 1;
    this.createdAt = props.createdAt || new Date();
    this.updatedAt = props.updatedAt || new Date();

    this.validate();
  }

  private validate(): void {
    if (!this.name) {
      throw new Error('name is required');
    }
    if (!this.capabilities) {
      throw new Error('capabilities is required');
    }
    if (!Array.isArray(this.capabilities.queues)) {
      throw new Error('capabilities.queues must be an array');
    }
    if (!Array.isArray(this.capabilities.jobKeys)) {
      throw new Error('capabilities.jobKeys must be an array');
    }
    if (this.maxParallel < 1) {
      throw new Error('maxParallel must be at least 1');
    }
    if (this.currentJobs < 0) {
      throw new Error('currentJobs cannot be negative');
    }
    if (this.currentJobs > this.maxParallel) {
      throw new Error('currentJobs cannot exceed maxParallel');
    }
  }

  public heartbeat(): WorkerEntity {
    const now = new Date();
    return new WorkerEntity({
      ...this,
      heartbeatAt: now,
      status: 'Online',
      updatedAt: now,
      version: this.version + 1,
    });
  }

  public goOffline(): WorkerEntity {
    return new WorkerEntity({
      ...this,
      status: 'Offline',
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public goOnline(): WorkerEntity {
    return new WorkerEntity({
      ...this,
      status: 'Online',
      heartbeatAt: new Date(),
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public startJob(): WorkerEntity {
    if (this.currentJobs >= this.maxParallel) {
      throw new Error('Worker at maximum capacity');
    }

    return new WorkerEntity({
      ...this,
      currentJobs: this.currentJobs + 1,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public finishJob(): WorkerEntity {
    if (this.currentJobs <= 0) {
      throw new Error('No jobs currently running');
    }

    return new WorkerEntity({
      ...this,
      currentJobs: this.currentJobs - 1,
      updatedAt: new Date(),
      version: this.version + 1,
    });
  }

  public canHandleQueue(queue: string): boolean {
    return this.capabilities.queues.includes(queue) || this.capabilities.queues.includes('*');
  }

  public canHandleJob(jobKey: string): boolean {
    return this.capabilities.jobKeys.includes(jobKey) || this.capabilities.jobKeys.includes('*');
  }

  public canAcceptJob(queue: string, jobKey?: string): boolean {
    if (this.status !== 'Online') return false;
    if (this.currentJobs >= this.maxParallel) return false;
    if (!this.canHandleQueue(queue)) return false;
    if (jobKey && !this.canHandleJob(jobKey)) return false;

    return true;
  }

  public isHealthy(heartbeatTimeoutSec = 300): boolean {
    // Consider unhealthy if no heartbeat for more than timeout
    const now = new Date();
    const timeSinceHeartbeat = (now.getTime() - this.heartbeatAt.getTime()) / 1000;
    return timeSinceHeartbeat <= heartbeatTimeoutSec;
  }

  public getAvailableSlots(): number {
    return Math.max(0, this.maxParallel - this.currentJobs);
  }

  public getUtilizationPercentage(): number {
    return this.maxParallel > 0 ? (this.currentJobs / this.maxParallel) * 100 : 0;
  }
}