import { ShipmentStop } from './shipment';
import { TimeWindow } from '../value-objects/time-window';
import { nanoid } from 'nanoid';

export type RouteStatus = 'planned' | 'in_progress' | 'completed' | 'canceled';

export interface RouteLegProps {
  readonly legId?: string;
  readonly fromStopId: string;
  readonly toStopId: string;
  readonly distanceKm: number;
  readonly etaFrom: Date;
  readonly etaTo: Date;
}

export class RouteLeg {
  readonly legId: string;
  readonly fromStopId: string;
  readonly toStopId: string;
  readonly distanceKm: number;
  readonly eta: TimeWindow;

  constructor(props: RouteLegProps) {
    if (props.distanceKm <= 0) {
      throw new Error('Route leg distance must be positive');
    }
    this.legId = props.legId ?? `LEG-${nanoid(8)}`;
    this.fromStopId = props.fromStopId;
    this.toStopId = props.toStopId;
    this.distanceKm = props.distanceKm;
    this.eta = TimeWindow.create({ from: props.etaFrom, to: props.etaTo });
  }
}

export interface RoutePlanProps {
  readonly routeId?: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly vehicleId?: string;
  readonly driverId?: string;
  readonly legs: RouteLegProps[];
  readonly stops: ShipmentStop[];
  readonly distanceKm: number;
  readonly status?: RouteStatus;
  readonly plannedAt?: Date;
}

export class RoutePlan {
  readonly routeId: string;
  readonly tenantId: string;
  readonly shipmentId: string;
  readonly vehicleId?: string;
  readonly driverId?: string;
  readonly legs: RouteLeg[];
  readonly stops: ShipmentStop[];
  readonly distanceKm: number;
  readonly plannedAt: Date;
  private _status: RouteStatus;

  private constructor(props: RoutePlanProps) {
    if (props.distanceKm <= 0) {
      throw new Error('Route distance must be positive');
    }
    this.routeId = props.routeId ?? `ROUTE-${nanoid(10)}`;
    this.tenantId = props.tenantId;
    this.shipmentId = props.shipmentId;
    this.vehicleId = props.vehicleId;
    this.driverId = props.driverId;
    this.legs = props.legs.map((leg) => new RouteLeg(leg));
    this.stops = props.stops.map((stop) => ({ ...stop }));
    this.distanceKm = props.distanceKm;
    this.plannedAt = props.plannedAt ?? new Date();
    this._status = props.status ?? 'planned';
    if (this.legs.length === 0) {
      throw new Error('Route requires at least one leg');
    }
  }

  static create(props: RoutePlanProps): RoutePlan {
    return new RoutePlan(props);
  }

  get status(): RouteStatus {
    return this._status;
  }

  updateStatus(status: RouteStatus): void {
    this._status = status;
  }
}

