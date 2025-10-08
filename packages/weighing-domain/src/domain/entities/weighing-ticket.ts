import { z } from 'zod';

// Enums
export const WeighingType = {
  VEHICLE: 'Vehicle',
  CONTAINER: 'Container',
  SILO: 'Silo',
  MANUAL: 'Manual',
} as const;

export const WeighingStatus = {
  DRAFT: 'Draft',
  IN_PROGRESS: 'InProgress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
  ERROR: 'Error',
} as const;

export const CommodityType = {
  WHEAT: 'WHEAT',
  BARLEY: 'BARLEY',
  RAPESEED: 'RAPESEED',
  SOYMEAL: 'SOYMEAL',
  COMPOUND_FEED: 'COMPOUND_FEED',
  FERTILIZER: 'FERTILIZER',
  OTHER: 'OTHER',
} as const;

export const WeighingMode = {
  GROSS: 'Gross',
  TARE: 'Tare',
  NET: 'Net',
} as const;

// Types
export type WeighingTypeValue = typeof WeighingType[keyof typeof WeighingType];
export type WeighingStatusValue = typeof WeighingStatus[keyof typeof WeighingStatus];
export type CommodityTypeValue = typeof CommodityType[keyof typeof CommodityType];
export type WeighingModeValue = typeof WeighingMode[keyof typeof WeighingMode];

// Schemas
export const WeighingDataSchema = z.object({
  weight: z.number().positive(),
  unit: z.enum(['kg', 't']),
  timestamp: z.string().datetime(),
  scaleId: z.string(),
  operatorId: z.string().optional(),
  notes: z.string().optional(),
});

export const WeighingTicketSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string(),
  ticketNumber: z.string(),
  type: z.enum([WeighingType.VEHICLE, WeighingType.CONTAINER, WeighingType.SILO, WeighingType.MANUAL]),
  status: z.enum([WeighingStatus.DRAFT, WeighingStatus.IN_PROGRESS, WeighingStatus.COMPLETED, WeighingStatus.CANCELLED, WeighingStatus.ERROR]).default(WeighingStatus.DRAFT),

  // Vehicle/Container Information
  licensePlate: z.string().optional(),
  containerNumber: z.string().optional(),
  siloId: z.string().optional(),

  // Commodity Information
  commodity: z.enum([CommodityType.WHEAT, CommodityType.BARLEY, CommodityType.RAPESEED, CommodityType.SOYMEAL, CommodityType.COMPOUND_FEED, CommodityType.FERTILIZER, CommodityType.OTHER]),
  commodityDescription: z.string().optional(),

  // Weights
  grossWeight: WeighingDataSchema.optional(),
  tareWeight: WeighingDataSchema.optional(),
  netWeight: z.number().optional(),
  netWeightUnit: z.enum(['kg', 't']).optional(),

  // Quality & Tolerances
  expectedWeight: z.number().optional(),
  tolerancePercent: z.number().min(0).max(20).default(2),
  isWithinTolerance: z.boolean().optional(),

  // References
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  deliveryNoteId: z.string().uuid().optional(),

  // ANPR & Automation
  anprRecordId: z.string().uuid().optional(),
  autoAssigned: z.boolean().default(false),

  // Gate & Logistics
  gateId: z.string().optional(),
  slotId: z.string().uuid().optional(),

  // Metadata
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  completedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interfaces
export interface WeighingData {
  weight: number;
  unit: 'kg' | 't';
  timestamp: Date;
  scaleId: string;
  operatorId?: string;
  notes?: string;
}

export interface WeighingTicketEntity {
  id: string;
  tenantId: string;
  ticketNumber: string;
  type: WeighingTypeValue;
  status: WeighingStatusValue;

  // Vehicle/Container Information
  licensePlate?: string;
  containerNumber?: string;
  siloId?: string;

  // Commodity Information
  commodity: CommodityTypeValue;
  commodityDescription?: string;

  // Weights
  grossWeight?: WeighingData;
  tareWeight?: WeighingData;
  netWeight?: number;
  netWeightUnit?: 'kg' | 't';

  // Quality & Tolerances
  expectedWeight?: number;
  tolerancePercent: number;
  isWithinTolerance?: boolean;

  // References
  contractId?: string;
  orderId?: string;
  deliveryNoteId?: string;

  // ANPR & Automation
  anprRecordId?: string;
  autoAssigned: boolean;

  // Gate & Logistics
  gateId?: string;
  slotId?: string;

  // Metadata
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  version: number;
}

// Entity implementation
export class WeighingTicket implements WeighingTicketEntity {
  public id: string;
  public tenantId: string;
  public ticketNumber: string;
  public type: WeighingTypeValue;
  public status: WeighingStatusValue;

  // Vehicle/Container Information
  public licensePlate?: string;
  public containerNumber?: string;
  public siloId?: string;

  // Commodity Information
  public commodity: CommodityTypeValue;
  public commodityDescription?: string;

  // Weights
  public grossWeight?: WeighingData;
  public tareWeight?: WeighingData;
  public netWeight?: number;
  public netWeightUnit?: 'kg' | 't';

  // Quality & Tolerances
  public expectedWeight?: number;
  public tolerancePercent: number;
  public isWithinTolerance?: boolean;

  // References
  public contractId?: string;
  public orderId?: string;
  public deliveryNoteId?: string;

  // ANPR & Automation
  public anprRecordId?: string;
  public autoAssigned: boolean;

  // Gate & Logistics
  public gateId?: string;
  public slotId?: string;

  // Metadata
  public createdAt: Date;
  public updatedAt: Date;
  public completedAt?: Date;
  public version: number;

  constructor(props: WeighingTicketEntity) {
    this.id = props.id;
    this.tenantId = props.tenantId;
    this.ticketNumber = props.ticketNumber;
    this.type = props.type;
    this.status = props.status;

    if (props.licensePlate) this.licensePlate = props.licensePlate;
    if (props.containerNumber) this.containerNumber = props.containerNumber;
    if (props.siloId) this.siloId = props.siloId;

    this.commodity = props.commodity;
    if (props.commodityDescription) this.commodityDescription = props.commodityDescription;

    if (props.grossWeight) this.grossWeight = props.grossWeight;
    if (props.tareWeight) this.tareWeight = props.tareWeight;
    if (props.netWeight !== undefined) this.netWeight = props.netWeight;
    if (props.netWeightUnit) this.netWeightUnit = props.netWeightUnit;

    if (props.expectedWeight) this.expectedWeight = props.expectedWeight;
    this.tolerancePercent = props.tolerancePercent;
    if (props.isWithinTolerance !== undefined) this.isWithinTolerance = props.isWithinTolerance;

    if (props.contractId) this.contractId = props.contractId;
    if (props.orderId) this.orderId = props.orderId;
    if (props.deliveryNoteId) this.deliveryNoteId = props.deliveryNoteId;

    if (props.anprRecordId) this.anprRecordId = props.anprRecordId;
    this.autoAssigned = props.autoAssigned;

    if (props.gateId) this.gateId = props.gateId;
    if (props.slotId) this.slotId = props.slotId;

    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    if (props.completedAt) this.completedAt = props.completedAt;
    this.version = props.version;
  }

  // Business methods
  addGrossWeight(weight: number, unit: 'kg' | 't', scaleId: string, operatorId?: string, notes?: string): void {
    if (this.status === WeighingStatus.COMPLETED) {
      throw new Error('Cannot modify completed ticket');
    }

    const weighingData: WeighingData = {
      weight,
      unit,
      timestamp: new Date(),
      scaleId,
    };

    if (operatorId) weighingData.operatorId = operatorId;
    if (notes) weighingData.notes = notes;

    this.grossWeight = weighingData;

    this.calculateNetWeight();
    this.updatedAt = new Date();
    this.version++;
  }

  addTareWeight(weight: number, unit: 'kg' | 't', scaleId: string, operatorId?: string, notes?: string): void {
    if (this.status === WeighingStatus.COMPLETED) {
      throw new Error('Cannot modify completed ticket');
    }

    const weighingData: WeighingData = {
      weight,
      unit,
      timestamp: new Date(),
      scaleId,
    };

    if (operatorId) weighingData.operatorId = operatorId;
    if (notes) weighingData.notes = notes;

    this.tareWeight = weighingData;

    this.calculateNetWeight();
    this.updatedAt = new Date();
    this.version++;
  }

  private calculateNetWeight(): void {
    if (this.grossWeight && this.tareWeight) {
      // Convert to same unit for calculation
      const grossKg = this.grossWeight.unit === 't' ? this.grossWeight.weight * 1000 : this.grossWeight.weight;
      const tareKg = this.tareWeight.unit === 't' ? this.tareWeight.weight * 1000 : this.tareWeight.weight;

      this.netWeight = grossKg - tareKg;
      this.netWeightUnit = 'kg';

      // Check tolerance
      if (this.expectedWeight) {
        const tolerance = (this.expectedWeight * this.tolerancePercent) / 100;
        this.isWithinTolerance = Math.abs(this.netWeight - this.expectedWeight) <= tolerance;
      }
    }
  }

  complete(): void {
    if (this.status === WeighingStatus.COMPLETED) {
      throw new Error('Ticket is already completed');
    }

    if (this.netWeight === undefined || this.netWeight === null) {
      throw new Error('Cannot complete ticket without net weight');
    }

    this.status = WeighingStatus.COMPLETED;
    this.completedAt = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(): void {
    if (this.status === WeighingStatus.COMPLETED) {
      throw new Error('Cannot cancel completed ticket');
    }

    this.status = WeighingStatus.CANCELLED;
    this.updatedAt = new Date();
    this.version++;
  }

  canBeModified(): boolean {
    const modifiableStatuses: WeighingStatusValue[] = [WeighingStatus.DRAFT, WeighingStatus.IN_PROGRESS];
    return modifiableStatuses.includes(this.status);
  }

  isValid(): boolean {
    return this.netWeight !== undefined && this.netWeight > 0;
  }

  getWeightSummary(): {
    gross?: number;
    tare?: number;
    net?: number;
    unit: 'kg' | 't';
    isWithinTolerance?: boolean;
  } {
    const summary: any = {
      unit: this.netWeightUnit ?? 'kg',
    };

    if (this.grossWeight?.weight) summary.gross = this.grossWeight.weight;
    if (this.tareWeight?.weight) summary.tare = this.tareWeight.weight;
    if (this.netWeight !== undefined) summary.net = this.netWeight;
    if (this.isWithinTolerance !== undefined) summary.isWithinTolerance = this.isWithinTolerance;

    return summary;
  }
}

