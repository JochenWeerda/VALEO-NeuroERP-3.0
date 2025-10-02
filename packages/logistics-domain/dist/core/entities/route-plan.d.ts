import { ShipmentStop } from './shipment';
import { TimeWindow } from '../value-objects/time-window';
export type RouteStatus = 'planned' | 'in_progress' | 'completed' | 'canceled';
export interface RouteLegProps {
    readonly legId?: string;
    readonly fromStopId: string;
    readonly toStopId: string;
    readonly distanceKm: number;
    readonly etaFrom: Date;
    readonly etaTo: Date;
}
export declare class RouteLeg {
    readonly legId: string;
    readonly fromStopId: string;
    readonly toStopId: string;
    readonly distanceKm: number;
    readonly eta: TimeWindow;
    constructor(props: RouteLegProps);
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
export declare class RoutePlan {
    readonly routeId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly vehicleId?: string;
    readonly driverId?: string;
    readonly legs: RouteLeg[];
    readonly stops: ShipmentStop[];
    readonly distanceKm: number;
    readonly plannedAt: Date;
    private _status;
    private constructor();
    static create(props: RoutePlanProps): RoutePlan;
    get status(): RouteStatus;
    updateStatus(status: RouteStatus): void;
}
//# sourceMappingURL=route-plan.d.ts.map