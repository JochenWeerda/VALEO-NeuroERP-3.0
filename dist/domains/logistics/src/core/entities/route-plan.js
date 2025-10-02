"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutePlan = exports.RouteLeg = void 0;
const time_window_1 = require("../value-objects/time-window");
class RouteLeg {
    legId;
    fromStopId;
    toStopId;
    distanceKm;
    eta;
    constructor(props) {
        if (props.distanceKm <= 0) {
            throw new Error('Route leg distance must be positive');
        }
        this.legId = props.legId ?? LEG - ;
        this.fromStopId = props.fromStopId;
        this.toStopId = props.toStopId;
        this.distanceKm = props.distanceKm;
        this.eta = time_window_1.TimeWindow.create({ from: props.etaFrom, to: props.etaTo });
    }
}
exports.RouteLeg = RouteLeg;
class RoutePlan {
    routeId;
    tenantId;
    shipmentId;
    vehicleId;
    driverId;
    legs;
    stops;
    distanceKm;
    plannedAt;
    _status;
    constructor(props) {
        if (props.distanceKm <= 0) {
            throw new Error('Route distance must be positive');
        }
        this.routeId = props.routeId ?? ROUTE - ;
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
