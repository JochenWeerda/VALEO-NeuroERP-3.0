import { z } from 'zod';

// Enums
export const SlotStatus = {
  SCHEDULED: 'Scheduled',
  ENTERED: 'Entered',
  EXITED: 'Exited',
  CANCELLED: 'Cancelled',
  NO_SHOW: 'NoShow',
} as const;

export const GateType = {
  INBOUND: 'Inbound',
  OUTBOUND: 'Outbound',
  WEIGHING: 'Weighing',
  INSPECTION: 'Inspection',
} as const;

// Types
export type SlotStatusValue = typeof SlotStatus[keyof typeof SlotStatus];
export type GateTypeValue = typeof GateType[keyof typeof GateType];

// Schema
export const SlotSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string(),
  gateId: z.string(),
  gateType: z.enum([GateType.INBOUND, GateType.OUTBOUND, GateType.WEIGHING, GateType.INSPECTION]),
  windowFrom: z.string().datetime(),
  windowTo: z.string().datetime(),
  assignedVehicleId: z.string().uuid().optional(),
  licensePlate: z.string().optional(),
  priority: z.number().min(1).max(10).default(5), // 1 = highest priority
  status: z.enum([SlotStatus.SCHEDULED, SlotStatus.ENTERED, SlotStatus.EXITED, SlotStatus.CANCELLED, SlotStatus.NO_SHOW]).default(SlotStatus.SCHEDULED),

  // Logistics
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  commodity: z.string().optional(),
  expectedWeight: z.number().optional(),

  // Actual times
  enteredAt: z.string().datetime().optional(),
  exitedAt: z.string().datetime().optional(),
  actualServiceStart: z.string().datetime().optional(),

  // Metadata
  notes: z.string().optional(),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interface
export interface SlotEntity {
  id: string;
  tenantId: string;
  gateId: string;
  gateType: GateTypeValue;
  windowFrom: Date;
  windowTo: Date;
  assignedVehicleId?: string;
  licensePlate?: string;
  priority: number;
  status: SlotStatusValue;

  // Logistics
  contractId?: string;
  orderId?: string;
  commodity?: string;
  expectedWeight?: number;

  // Actual times
  enteredAt?: Date;
  exitedAt?: Date;
  actualServiceStart?: Date;

  // Metadata
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class Slot implements SlotEntity {
  public id: string;
  public tenantId: string;
  public gateId: string;
  public gateType: GateTypeValue;
  public windowFrom: Date;
  public windowTo: Date;
  public assignedVehicleId?: string;
  public licensePlate?: string;
  public priority: number;
  public status: SlotStatusValue;

  // Logistics
  public contractId?: string;
  public orderId?: string;
  public commodity?: string;
  public expectedWeight?: number;

  // Actual times
  public enteredAt?: Date;
  public exitedAt?: Date;
  public actualServiceStart?: Date;

  // Metadata
  public notes?: string;
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: SlotEntity) {
    this.id = props.id;
    this.tenantId = props.tenantId;
    this.gateId = props.gateId;
    this.gateType = props.gateType;
    this.windowFrom = props.windowFrom;
    this.windowTo = props.windowTo;
    if (props.assignedVehicleId) this.assignedVehicleId = props.assignedVehicleId;
    if (props.licensePlate) this.licensePlate = props.licensePlate;
    this.priority = props.priority;
    this.status = props.status;

    if (props.contractId) this.contractId = props.contractId;
    if (props.orderId) this.orderId = props.orderId;
    if (props.commodity) this.commodity = props.commodity;
    if (props.expectedWeight) this.expectedWeight = props.expectedWeight;

    if (props.enteredAt) this.enteredAt = props.enteredAt;
    if (props.exitedAt) this.exitedAt = props.exitedAt;
    if (props.actualServiceStart) this.actualServiceStart = props.actualServiceStart;

    if (props.notes) this.notes = props.notes;
    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;
  }

  // Business methods
  assignVehicle(vehicleId: string, licensePlate?: string): void {
    if (this.status !== SlotStatus.SCHEDULED) {
      throw new Error('Can only assign vehicle to scheduled slots');
    }

    this.assignedVehicleId = vehicleId;
    if (licensePlate) this.licensePlate = licensePlate;
    this.updatedAt = new Date();
    this.version++;
  }

  markEntered(): void {
    if (this.status !== SlotStatus.SCHEDULED) {
      throw new Error('Can only mark scheduled slots as entered');
    }

    this.status = SlotStatus.ENTERED;
    this.enteredAt = new Date();
    this.actualServiceStart = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  markExited(): void {
    if (this.status !== SlotStatus.ENTERED) {
      throw new Error('Can only mark entered slots as exited');
    }

    this.status = SlotStatus.EXITED;
    this.exitedAt = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(reason?: string): void {
    const nonCancellableStatuses: SlotStatusValue[] = [SlotStatus.EXITED, SlotStatus.CANCELLED];
    if (nonCancellableStatuses.includes(this.status)) {
      throw new Error('Cannot cancel completed or already cancelled slots');
    }

    this.status = SlotStatus.CANCELLED;
    if (reason) this.notes = (this.notes ? this.notes + '; ' : '') + `Cancelled: ${reason}`;
    this.updatedAt = new Date();
    this.version++;
  }

  markNoShow(): void {
    if (this.status !== SlotStatus.SCHEDULED) {
      throw new Error('Can only mark scheduled slots as no-show');
    }

    this.status = SlotStatus.NO_SHOW;
    this.updatedAt = new Date();
    this.version++;
  }

  // Status checks
  isActive(): boolean {
    const activeStatuses: SlotStatusValue[] = [SlotStatus.SCHEDULED, SlotStatus.ENTERED];
    return activeStatuses.includes(this.status);
  }

  isCompleted(): boolean {
    return this.status === SlotStatus.EXITED;
  }

  isOverdue(): boolean {
    const now = new Date();
    return this.status === SlotStatus.SCHEDULED && now > this.windowTo;
  }

  getWaitTimeMinutes(): number | null {
    if (!this.enteredAt || !this.actualServiceStart) return null;
    return Math.round((this.actualServiceStart.getTime() - this.enteredAt.getTime()) / (1000 * 60));
  }

  getServiceTimeMinutes(): number | null {
    if (!this.actualServiceStart || !this.exitedAt) return null;
    return Math.round((this.exitedAt.getTime() - this.actualServiceStart.getTime()) / (1000 * 60));
  }

  getTotalTimeMinutes(): number | null {
    if (!this.enteredAt || !this.exitedAt) return null;
    return Math.round((this.exitedAt.getTime() - this.enteredAt.getTime()) / (1000 * 60));
  }

  // Priority helpers
  isHighPriority(): boolean {
    return this.priority <= 3;
  }

  isLowPriority(): boolean {
    return this.priority >= 8;
  }

  // Window helpers
  isWithinWindow(now?: Date): boolean {
    const currentTime = now || new Date();
    return currentTime >= this.windowFrom && currentTime <= this.windowTo;
  }

  getWindowDurationMinutes(): number {
    return Math.round((this.windowTo.getTime() - this.windowFrom.getTime()) / (1000 * 60));
  }
}