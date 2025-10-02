import { nanoid } from 'nanoid';

export type CarrierDocumentType = 'label' | 'manifest' | 'invoice';

export interface CarrierDocumentProps {
  readonly documentId?: string;
  readonly tenantId: string;
  readonly carrierId: string;
  readonly type: CarrierDocumentType;
  readonly reference: string;
  readonly payload: Record<string, unknown>;
  readonly createdAt?: Date;
}

export class CarrierDocument {
  readonly documentId: string;
  readonly tenantId: string;
  readonly carrierId: string;
  readonly type: CarrierDocumentType;
  readonly reference: string;
  readonly payload: Record<string, unknown>;
  readonly createdAt: Date;

  private constructor(props: CarrierDocumentProps) {
    this.documentId = props.documentId ?? `CARR-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.carrierId = props.carrierId;
    this.type = props.type;
    this.reference = props.reference;
    this.payload = props.payload;
    this.createdAt = props.createdAt ?? new Date();
  }

  static create(props: CarrierDocumentProps): CarrierDocument {
    return new CarrierDocument(props);
  }
}

