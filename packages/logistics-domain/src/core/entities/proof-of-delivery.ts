import { nanoid } from 'nanoid';

export interface ProofOfDeliveryProps {
  readonly podId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly stopId: string;
  readonly signedBy: string;
  readonly capturedAt?: Date;
  readonly signatureRef?: string;
  readonly photoRefs?: string[];
  readonly scans?: string[];
  readonly exceptions?: string[];
}

export class ProofOfDelivery {
  readonly podId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly stopId: string;
  readonly signedBy: string;
  readonly capturedAt: Date;
  readonly signatureRef?: string;
  readonly photoRefs?: string[];
  readonly scans?: string[];
  readonly exceptions?: string[];

  private constructor(props: ProofOfDeliveryProps) {
    this.podId = props.podId ?? `POD-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.stopId = props.stopId;
    this.signedBy = props.signedBy;
    this.capturedAt = props.capturedAt ?? new Date();
    this.signatureRef = props.signatureRef;
    this.photoRefs = props.photoRefs;
    this.scans = props.scans;
    this.exceptions = props.exceptions;
  }

  static create(props: ProofOfDeliveryProps): ProofOfDelivery {
    return new ProofOfDelivery(props);
  }
}

