import { z } from 'zod';

// Schema
export const WaitLogSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string(),
  ticketId: z.string().uuid(),
  licensePlate: z.string().optional(),

  // Timing
  arrivalAt: z.string().datetime(),
  serviceStartAt: z.string().datetime().optional(),
  serviceEndAt: z.string().datetime().optional(),

  // Calculated fields
  waitTimeMinutes: z.number().optional(),
  serviceTimeMinutes: z.number().optional(),
  totalTimeMinutes: z.number().optional(),

  // Gate & logistics
  gateId: z.string(),
  gateType: z.enum(['Inbound', 'Outbound', 'Weighing', 'Inspection']),
  slotId: z.string().uuid().optional(),

  // Priority & categorization
  priority: z.number().min(1).max(10).default(5),
  isHighPriority: z.boolean().optional(),
  isOvertime: z.boolean().optional(),

  // Context
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  commodity: z.string().optional(),
  expectedWeight: z.number().optional(),

  // Status
  status: z.enum(['Waiting', 'InService', 'Completed', 'Cancelled']).default('Waiting'),

  // Notes & metadata
  notes: z.string().optional(),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interface
export interface WaitLogEntity {
  id: string;
  tenantId: string;
  ticketId: string;
  licensePlate?: string;

  // Timing
  arrivalAt: Date;
  serviceStartAt?: Date;
  serviceEndAt?: Date;

  // Calculated fields
  waitTimeMinutes?: number;
  serviceTimeMinutes?: number;
  totalTimeMinutes?: number;

  // Gate & logistics
  gateId: string;
  gateType: 'Inbound' | 'Outbound' | 'Weighing' | 'Inspection';
  slotId?: string;

  // Priority & categorization
  priority: number;
  isHighPriority?: boolean;
  isOvertime?: boolean;

  // Context
  contractId?: string;
  orderId?: string;
  commodity?: string;
  expectedWeight?: number;

  // Status
  status: 'Waiting' | 'InService' | 'Completed' | 'Cancelled';

  // Notes & metadata
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class WaitLog implements WaitLogEntity {
  public id: string;
  public tenantId: string;
  public ticketId: string;
  public licensePlate?: string;

  // Timing
  public arrivalAt: Date;
  public serviceStartAt?: Date;
  public serviceEndAt?: Date;

  // Calculated fields
  public waitTimeMinutes?: number;
  public serviceTimeMinutes?: number;
  public totalTimeMinutes?: number;

  // Gate & logistics
  public gateId: string;
  public gateType: 'Inbound' | 'Outbound' | 'Weighing' | 'Inspection';
  public slotId?: string;

  // Priority & categorization
  public priority: number;
  public isHighPriority?: boolean;
  public isOvertime?: boolean;

  // Context
  public contractId?: string;
  public orderId?: string;
  public commodity?: string;
  public expectedWeight?: number;

  // Status
  public status: 'Waiting' | 'InService' | 'Completed' | 'Cancelled';

  // Notes & metadata
  public notes?: string;
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: WaitLogEntity) {
    this.id = props.id;
    this.tenantId = props.tenantId;
    this.ticketId = props.ticketId;
    if (props.licensePlate) this.licensePlate = props.licensePlate;

    this.arrivalAt = props.arrivalAt;
    if (props.serviceStartAt) this.serviceStartAt = props.serviceStartAt;
    if (props.serviceEndAt) this.serviceEndAt = props.serviceEndAt;

    if (props.waitTimeMinutes !== undefined) this.waitTimeMinutes = props.waitTimeMinutes;
    if (props.serviceTimeMinutes !== undefined) this.serviceTimeMinutes = props.serviceTimeMinutes;
    if (props.totalTimeMinutes !== undefined) this.totalTimeMinutes = props.totalTimeMinutes;

    this.gateId = props.gateId;
    this.gateType = props.gateType;
    if (props.slotId) this.slotId = props.slotId;

    this.priority = props.priority;
    if (props.isHighPriority !== undefined) this.isHighPriority = props.isHighPriority;
    if (props.isOvertime !== undefined) this.isOvertime = props.isOvertime;

    if (props.contractId) this.contractId = props.contractId;
    if (props.orderId) this.orderId = props.orderId;
    if (props.commodity) this.commodity = props.commodity;
    if (props.expectedWeight) this.expectedWeight = props.expectedWeight;

    this.status = props.status;

    if (props.notes) this.notes = props.notes;
    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;

    // Auto-calculate derived fields
    this.calculateTimes();
    this.isHighPriority = this.priority <= 3;
  }

  // Business methods
  startService(): void {
    if (this.status !== 'Waiting') {
      throw new Error('Can only start service for waiting entries');
    }

    this.status = 'InService';
    this.serviceStartAt = new Date();
    this.calculateTimes();
    this.updatedAt = new Date();
    this.version++;
  }

  completeService(): void {
    if (this.status !== 'InService') {
      throw new Error('Can only complete service for entries in service');
    }

    this.status = 'Completed';
    this.serviceEndAt = new Date();
    this.calculateTimes();
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(reason?: string): void {
    if (this.status === 'Completed') {
      throw new Error('Cannot cancel completed entries');
    }

    this.status = 'Cancelled';
    if (reason) this.notes = (this.notes ? this.notes + '; ' : '') + `Cancelled: ${reason}`;
    this.calculateTimes();
    this.updatedAt = new Date();
    this.version++;
  }

  private calculateTimes(): void {
    const now = new Date();

    // Calculate wait time (arrival to service start)
    if (this.serviceStartAt) {
      this.waitTimeMinutes = Math.round((this.serviceStartAt.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
    }

    // Calculate service time (service start to end)
    if (this.serviceStartAt && this.serviceEndAt) {
      this.serviceTimeMinutes = Math.round((this.serviceEndAt.getTime() - this.serviceStartAt.getTime()) / (1000 * 60));
    }

    // Calculate total time (arrival to end)
    const endTime = this.serviceEndAt || (this.status === 'InService' ? now : this.serviceStartAt);
    if (endTime) {
      this.totalTimeMinutes = Math.round((endTime.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
    }

    // Check for overtime (more than 2 hours wait)
    this.isOvertime = (this.waitTimeMinutes || 0) > 120;
  }

  // Status checks
  isWaiting(): boolean {
    return this.status === 'Waiting';
  }

  isInService(): boolean {
    return this.status === 'InService';
  }

  isCompleted(): boolean {
    return this.status === 'Completed';
  }

  isActive(): boolean {
    return ['Waiting', 'InService'].includes(this.status);
  }

  // Time helpers
  getCurrentWaitTimeMinutes(): number {
    if (this.serviceStartAt) return this.waitTimeMinutes || 0;

    const now = new Date();
    return Math.round((now.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
  }

  getAgeMinutes(): number {
    const now = new Date();
    return Math.round((now.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
  }

  isLongWait(thresholdMinutes: number = 60): boolean {
    return this.getCurrentWaitTimeMinutes() > thresholdMinutes;
  }

  // Priority helpers
  isHighPriorityCheck(): boolean {
    return this.priority <= 3;
  }

  isLowPriority(): boolean {
    return this.priority >= 8;
  }

  // KPI helpers
  getServiceEfficiency(): number | null {
    if (!this.expectedWeight || !this.serviceTimeMinutes) return null;

    // Simple efficiency metric: expected weight / service time
    // Higher values indicate better efficiency
    return this.expectedWeight / this.serviceTimeMinutes;
  }

  // Reporting helpers
  toReportRow(): {
    ticketId: string;
    licensePlate?: string;
    gateId: string;
    gateType: string;
    priority: number;
    arrivalAt: string;
    serviceStartAt?: string;
    serviceEndAt?: string;
    waitTimeMinutes?: number;
    serviceTimeMinutes?: number;
    totalTimeMinutes?: number;
    status: string;
    commodity?: string;
    isOvertime?: boolean;
  } {
    const row: any = {
      ticketId: this.ticketId,
      gateId: this.gateId,
      gateType: this.gateType,
      priority: this.priority,
      arrivalAt: this.arrivalAt.toISOString(),
      status: this.status,
    };

    if (this.licensePlate) row.licensePlate = this.licensePlate;
    if (this.serviceStartAt) row.serviceStartAt = this.serviceStartAt.toISOString();
    if (this.serviceEndAt) row.serviceEndAt = this.serviceEndAt.toISOString();
    if (this.waitTimeMinutes !== undefined) row.waitTimeMinutes = this.waitTimeMinutes;
    if (this.serviceTimeMinutes !== undefined) row.serviceTimeMinutes = this.serviceTimeMinutes;
    if (this.totalTimeMinutes !== undefined) row.totalTimeMinutes = this.totalTimeMinutes;
    if (this.commodity) row.commodity = this.commodity;
    if (this.isOvertime !== undefined) row.isOvertime = this.isOvertime;

    return row;
  }
}