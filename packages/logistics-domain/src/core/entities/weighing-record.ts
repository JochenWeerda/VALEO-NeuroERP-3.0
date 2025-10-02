import { nanoid } from 'nanoid';

export interface WeighingRecordProps {
  readonly weighingId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly grossWeightKg: number;
  readonly tareWeightKg: number;
  readonly source: 'bridge' | 'sensor';
  readonly capturedAt?: Date;
}

export class WeighingRecord {
  readonly weighingId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly grossWeightKg: number;
  readonly tareWeightKg: number;
  readonly netWeightKg: number;
  readonly source: 'bridge' | 'sensor';
  readonly capturedAt: Date;

  private constructor(props: WeighingRecordProps) {
    if (props.grossWeightKg <= props.tareWeightKg) {
      throw new Error('Gross weight must exceed tare weight');
    }
    this.weighingId = props.weighingId ?? `WEIGH-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.grossWeightKg = props.grossWeightKg;
    this.tareWeightKg = props.tareWeightKg;
    this.netWeightKg = props.grossWeightKg - props.tareWeightKg;
    this.source = props.source;
    this.capturedAt = props.capturedAt ?? new Date();
  }

  static create(props: WeighingRecordProps): WeighingRecord {
    return new WeighingRecord(props);
  }
}

