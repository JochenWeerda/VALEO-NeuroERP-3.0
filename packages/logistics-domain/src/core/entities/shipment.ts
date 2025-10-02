import { Address, AddressProps } from '../value-objects/address';
import { TimeWindow, TimeWindowProps } from '../value-objects/time-window';
import { TemperatureRange, TemperatureRangeProps } from '../value-objects/temperature-range';
import { nanoid } from 'nanoid';

type StopType = 'pickup' | 'delivery' | 'cross-dock' | 'drop-off' | 'return';

export interface ShipmentStopProps {
  readonly stopId?: string;
  readonly sequence: number;
  readonly type: StopType;
  readonly address: AddressProps;
  readonly window?: TimeWindowProps;
}

export interface ShipmentPayloadItemProps {
  readonly sscc?: string;
  readonly description?: string;
  readonly weightKg: number;
  readonly volumeM3?: number;
  readonly tempRange?: TemperatureRangeProps;
}

export type ShipmentStatus = 'draft' | 'planned' | 'in_transit' | 'completed' | 'canceled';

export interface ShipmentProps {
  readonly shipmentId?: string;
  readonly tenantId: string;
  readonly reference?: string;
  readonly origin: AddressProps;
  readonly destination: AddressProps;
  readonly priority?: 'standard' | 'express' | 'critical';
  readonly incoterm?: string;
  readonly stops: ShipmentStopProps[];
  readonly payload: ShipmentPayloadItemProps[];
  readonly status?: ShipmentStatus;
  readonly createdAt?: Date;
}

export class ShipmentStop {
  readonly stopId: string;
  readonly sequence: number;
  readonly type: StopType;
  readonly address: Address;
  readonly window?: TimeWindow;

  constructor(props: ShipmentStopProps) {
    this.stopId = props.stopId ?? `STOP-${nanoid(10)}`;
    this.sequence = props.sequence;
    this.type = props.type;
    this.address = Address.create(props.address);
    this.window = props.window ? TimeWindow.create(props.window) : undefined;
  }
}

export class ShipmentPayloadItem {
  readonly sscc?: string;
  readonly description?: string;
  readonly weightKg: number;
  readonly volumeM3?: number;
  readonly tempRange?: TemperatureRange;

  constructor(props: ShipmentPayloadItemProps) {
    if (props.weightKg <= 0) {
      throw new Error('Payload weight must be positive');
    }
    this.sscc = props.sscc;
    this.description = props.description;
    this.weightKg = props.weightKg;
    this.volumeM3 = props.volumeM3;
    this.tempRange = props.tempRange ? TemperatureRange.create(props.tempRange) : undefined;
  }
}

export class Shipment {
  readonly shipmentId: string;
  readonly tenantId: string;
  readonly reference?: string;
  readonly origin: Address;
  readonly destination: Address;
  readonly priority: 'standard' | 'express' | 'critical';
  readonly incoterm?: string;
  readonly createdAt: Date;
  private _status: ShipmentStatus;
  private readonly stops: ShipmentStop[];
  private readonly payload: ShipmentPayloadItem[];

  private constructor(props: ShipmentProps) {
    this.shipmentId = props.shipmentId ?? `SHP-${nanoid(12)}`;
    this.tenantId = props.tenantId;
    this.reference = props.reference;
    this.origin = Address.create(props.origin);
    this.destination = Address.create(props.destination);
    this.priority = props.priority ?? 'standard';
    this.incoterm = props.incoterm;
    this.createdAt = props.createdAt ?? new Date();
    this._status = props.status ?? 'planned';
    this.stops = props.stops.map((stop) => new ShipmentStop(stop));
    this.payload = props.payload.map((item) => new ShipmentPayloadItem(item));
    if (this.stops.length === 0) {
      throw new Error('Shipment requires at least one stop');
    }
  }

  static create(props: ShipmentProps): Shipment {
    return new Shipment(props);
  }

  get status(): ShipmentStatus {
    return this._status;
  }

  updateStatus(status: ShipmentStatus): void {
    this._status = status;
  }

  getStops(): ShipmentStop[] {
    return this.stops.map((stop) => ({ ...stop } as ShipmentStop));
  }

  getPayload(): ShipmentPayloadItem[] {
    return this.payload.map((item) => ({ ...item } as ShipmentPayloadItem));
  }

  toJSON(): Record<string, unknown> {
    return {
      shipmentId: this.shipmentId,
      tenantId: this.tenantId,
      reference: this.reference,
      origin: this.origin.toJSON(),
      destination: this.destination.toJSON(),
      priority: this.priority,
      incoterm: this.incoterm,
      status: this._status,
      createdAt: this.createdAt.toISOString(),
      stops: this.stops.map((stop) => ({
        stopId: stop.stopId,
        sequence: stop.sequence,
        type: stop.type,
        address: stop.address.toJSON(),
        window: stop.window?.toJSON(),
      })),
      payload: this.payload.map((item) => ({
        sscc: item.sscc,
        description: item.description,
        weightKg: item.weightKg,
        volumeM3: item.volumeM3,
        tempRange: item.tempRange?.toJSON(),
      })),
    };
  }
}

