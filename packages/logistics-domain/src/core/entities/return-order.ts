import { nanoid } from 'nanoid';
import { Address, AddressProps } from '../value-objects/address';

export type ReturnStatus = 'requested' | 'scheduled' | 'picked_up' | 'received' | 'closed';

export interface ReturnOrderProps {
  readonly returnId?: string;
  readonly tenantId: string;
  readonly originalShipmentId: string;
  readonly pickupAddress: AddressProps;
  readonly returnReason: string;
  readonly status?: ReturnStatus;
  readonly requestedAt?: Date;
}

export class ReturnOrder {
  readonly returnId: string;
  readonly tenantId: string;
  readonly originalShipmentId: string;
  readonly pickupAddress: Address;
  readonly returnReason: string;
  readonly requestedAt: Date;
  private _status: ReturnStatus;

  private constructor(props: ReturnOrderProps) {
    this.returnId = props.returnId ?? `RET-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.originalShipmentId = props.originalShipmentId;
    this.pickupAddress = Address.create(props.pickupAddress);
    this.returnReason = props.returnReason;
    this.requestedAt = props.requestedAt ?? new Date();
    this._status = props.status ?? 'requested';
  }

  static create(props: ReturnOrderProps): ReturnOrder {
    return new ReturnOrder(props);
  }

  get status(): ReturnStatus {
    return this._status;
  }

  updateStatus(status: ReturnStatus): void {
    this._status = status;
  }
}

