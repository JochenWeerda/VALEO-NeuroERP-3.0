import { nanoid } from 'nanoid';

export interface FreightSurcharge {
  readonly type: string;
  readonly amount: number;
}

export interface FreightRateProps {
  readonly rateId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly currency: string;
  readonly baseAmount: number;
  readonly surcharges?: FreightSurcharge[];
  readonly explain?: string;
  readonly calculatedAt?: Date;
}

export class FreightRate {
  readonly rateId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly currency: string;
  readonly baseAmount: number;
  readonly surcharges: FreightSurcharge[];
  readonly totalAmount: number;
  readonly explain?: string;
  readonly calculatedAt: Date;

  private constructor(props: FreightRateProps) {
    this.rateId = props.rateId ?? `RATE-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.currency = props.currency;
    this.baseAmount = props.baseAmount;
    this.surcharges = props.surcharges ?? [];
    this.totalAmount = this.surcharges.reduce((acc, item) => acc + item.amount, props.baseAmount);
    this.explain = props.explain;
    this.calculatedAt = props.calculatedAt ?? new Date();
  }

  static create(props: FreightRateProps): FreightRate {
    if (props.baseAmount < 0) {
      throw new Error('Freight base amount cannot be negative');
    }
    return new FreightRate(props);
  }
}

