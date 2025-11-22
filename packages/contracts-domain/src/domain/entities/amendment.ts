import { z } from 'zod';

// Enums
export const AmendmentType = {
  QTY_CHANGE: 'QtyChange',
  WINDOW_CHANGE: 'WindowChange',
  PRICE_RULE_CHANGE: 'PriceRuleChange',
  COUNTERPARTY_CHANGE: 'CounterpartyChange',
  DELIVERY_TERMS_CHANGE: 'DeliveryTermsChange',
  OTHER: 'Other',
} as const;

export const AmendmentStatus = {
  PENDING: 'Pending',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
  CANCELLED: 'Cancelled',
} as const;

export type AmendmentTypeValue = typeof AmendmentType[keyof typeof AmendmentType];
export type AmendmentStatusValue = typeof AmendmentStatus[keyof typeof AmendmentStatus];

// Schema
export const AmendmentSchema = z.object({
  id: z.string().uuid().optional(),
  contractId: z.string().uuid(),
  tenantId: z.string(),
  type: z.enum([
    AmendmentType.QTY_CHANGE,
    AmendmentType.WINDOW_CHANGE,
    AmendmentType.PRICE_RULE_CHANGE,
    AmendmentType.COUNTERPARTY_CHANGE,
    AmendmentType.DELIVERY_TERMS_CHANGE,
    AmendmentType.OTHER,
  ]),
  reason: z.string(),
  changes: z.record(z.any()), // Flexible structure for different amendment types
  approvedBy: z.string().optional(),
  approvedAt: z.string().datetime().optional(),
  status: z.enum([
    AmendmentStatus.PENDING,
    AmendmentStatus.APPROVED,
    AmendmentStatus.REJECTED,
    AmendmentStatus.CANCELLED,
  ]).default(AmendmentStatus.PENDING),
  effectiveAt: z.string().datetime().optional(),
  notes: z.string().optional(),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interface
export interface AmendmentEntity {
  id: string;
  contractId: string;
  tenantId: string;
  type: AmendmentTypeValue;
  reason: string;
  changes: Record<string, any>;
  approvedBy?: string | undefined;
  approvedAt?: Date | undefined;
  status: AmendmentStatusValue;
  effectiveAt?: Date | undefined;
  notes?: string | undefined;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class Amendment implements AmendmentEntity {
  public id: string;
  public contractId: string;
  public tenantId: string;
  public type: AmendmentTypeValue;
  public reason: string;
  public changes: Record<string, any>;
  public approvedBy?: string;
  public approvedAt?: Date;
  public status: AmendmentStatusValue;
  public effectiveAt?: Date;
  public notes?: string;
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: AmendmentEntity) {
    this.id = props.id;
    this.contractId = props.contractId;
    this.tenantId = props.tenantId;
    this.type = props.type;
    this.reason = props.reason;
    this.changes = props.changes;
    if (props.approvedBy) this.approvedBy = props.approvedBy;
    if (props.approvedAt) this.approvedAt = props.approvedAt;
    this.status = props.status;
    if (props.effectiveAt) this.effectiveAt = props.effectiveAt;
    if (props.notes) this.notes = props.notes;
    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;
  }

  approve(approvedBy: string): void {
    if (this.status !== AmendmentStatus.PENDING) {
      throw new Error('Only pending amendments can be approved');
    }
    this.status = AmendmentStatus.APPROVED;
    this.approvedBy = approvedBy;
    this.approvedAt = new Date();
    this.effectiveAt = new Date();
    this.updatedAt = new Date();
    this.version++;
  }

  reject(): void {
    if (this.status !== AmendmentStatus.PENDING) {
      throw new Error('Only pending amendments can be rejected');
    }
    this.status = AmendmentStatus.REJECTED;
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(): void {
    if (this.status === AmendmentStatus.APPROVED) {
      throw new Error('Approved amendments cannot be cancelled');
    }
    this.status = AmendmentStatus.CANCELLED;
    this.updatedAt = new Date();
    this.version++;
  }

  canBeModified(): boolean {
    return this.status === AmendmentStatus.PENDING;
  }

  isEffective(): boolean {
    return this.status === AmendmentStatus.APPROVED &&
           this.effectiveAt !== undefined &&
           this.effectiveAt <= new Date();
  }
}