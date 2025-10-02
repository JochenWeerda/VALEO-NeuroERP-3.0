"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutePlan = exports.RouteLeg = void 0;
const time_window_1 = require("../value-objects/time-window");
const nanoid_1 = require("nanoid");
class RouteLeg {
    constructor(props) {
        if (props.distanceKm <= 0) {
            throw new Error('Route leg distance must be positive');
        }
        this.legId = props.legId ?? `LEG-${(0, nanoid_1.nanoid)(8)}`;
        this.fromStopId = props.fromStopId;
        this.toStopId = props.toStopId;
        this.distanceKm = props.distanceKm;
        this.eta = time_window_1.TimeWindow.create({ from: props.etaFrom, to: props.etaTo });
    }
}
exports.RouteLeg = RouteLeg;
class RoutePlan {
    constructor(props) {
        if (props.distanceKm <= 0) {
            throw new Error('Route distance must be positive');
        }
        this.routeId = props.routeId ?? `ROUTE-${(0, nanoid_1.nanoid)(10)}`;
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
    static create(props) {
        return new RoutePlan(props);
    }
    get status() {
        return this._status;
    }
    updateStatus(status) {
        this._status = status;
    }
}
exports.RoutePlan = RoutePlan;
//# sourceMappingURL=route-plan.js.map