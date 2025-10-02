import { z } from 'zod';

// Enums
export const CallOffStatus = {
  PLANNED: 'Planned',
  SCHEDULED: 'Scheduled',
  DELIVERED: 'Delivered',
  INVOICED: 'Invoiced',
  CANCELLED: 'Cancelled',
} as const;

export type CallOffStatusValue = typeof CallOffStatus[keyof typeof CallOffStatus];

// Schema
export const CallOffSchema = z.object({
  id: z.string().uuid().optional(),
  contractId: z.string().uuid(),
  tenantId: z.string(),
  qty: z.number().positive(),
  window: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  site: z.string().optional(),
  silo: z.string().optional(),
  customerYard: z.string().optional(),
  status: z.enum([CallOffStatus.PLANNED, CallOffStatus.SCHEDULED, CallOffStatus.DELIVERED, CallOffStatus.INVOICED, CallOffStatus.CANCELLED]).default(CallOffStatus.PLANNED),
  notes: z.string().optional(),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interface
export interface CallOffEntity {
  id: string;
  contractId: string;
  tenantId: string;
  qty: number;
  window: {
    from: Date;
    to: Date;
  };
  site?: string;
  silo?: string;
  customerYard?: string;
  status: CallOffStatusValue;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class CallOff implements CallOffEntity {
  public id: string;
  public contractId: string;
  public tenantId: string;
  public qty: number;
  public window: { from: Date; to: Date; };
  public site?: string;
  public silo?: string;
  public customerYard?: string;
  public status: CallOffStatusValue;
  public notes?: string;
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: CallOffEntity) {
    this.id = props.id;
    this.contractId = props.contractId;
    this.tenantId = props.tenantId;
    this.qty = props.qty;
    this.window = props.window;
    if (props.site) this.site = props.site;
    if (props.silo) this.silo = props.silo;
    if (props.customerYard) this.customerYard = props.customerYard;
    this.status = props.status;
    if (props.notes) this.notes = props.notes;
    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;
  }

  schedule(): void {
    if (this.status !== CallOffStatus.PLANNED) {
      throw new Error('Only planned call-offs can be scheduled');
    }
    this.status = CallOffStatus.SCHEDULED;
    this.updatedAt = new Date();
    this.version++;
  }

  markDelivered(): void {
    if (this.status !== CallOffStatus.SCHEDULED) {
      throw new Error('Only scheduled call-offs can be marked as delivered');
    }
    this.status = CallOffStatus.DELIVERED;
    this.updatedAt = new Date();
    this.version++;
  }

  cancel(): void {
    if (this.status === CallOffStatus.DELIVERED || this.status === CallOffStatus.INVOICED) {
      throw new Error('Delivered or invoiced call-offs cannot be cancelled');
    }
    this.status = CallOffStatus.CANCELLED;
    this.updatedAt = new Date();
    this.version++;
  }

  canBeModified(): boolean {
    const modifiableStatuses: CallOffStatusValue[] = [CallOffStatus.PLANNED, CallOffStatus.SCHEDULED];
    return modifiableStatuses.includes(this.status);
  }
}