import { nanoid } from 'nanoid';

export interface EmissionFactorDetail {
  readonly factor: string;
  readonly value: number;
  readonly unit: string;
}

export interface EmissionRecordProps {
  readonly emissionId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly co2eKg: number;
  readonly method: string;
  readonly factors?: EmissionFactorDetail[];
  readonly calculatedAt?: Date;
}

export class EmissionRecord {
  readonly emissionId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly co2eKg: number;
  readonly method: string;
  readonly factors: EmissionFactorDetail[];
  readonly calculatedAt: Date;

  private constructor(props: EmissionRecordProps) {
    if (props.co2eKg < 0) {
      throw new Error('Emission value cannot be negative');
    }
    this.emissionId = props.emissionId ?? `EM-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.co2eKg = props.co2eKg;
    this.method = props.method;
    this.factors = props.factors ?? [];
    this.calculatedAt = props.calculatedAt ?? new Date();
  }

  static create(props: EmissionRecordProps): EmissionRecord {
    return new EmissionRecord(props);
  }
}

