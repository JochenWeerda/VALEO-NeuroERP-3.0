"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DispatchAssignment = void 0;
class DispatchAssignment {
    assignmentId;
    tenantId;
    routeId;
    driverId;
    vehicleId;
    trailerId;
    assignedAt;
    _status;
    constructor(props) {
        this.assignmentId = props.assignmentId ?? ASSIGN - ;
        this.tenantId = props.tenantId;
        this.routeId = props.routeId;
        this.driverId = props.driverId;
        this.vehicleId = props.vehicleId;
        this.trailerId = props.trailerId;
        this.assignedAt = props.assignedAt ?? new Date();
        this._status = props.status ?? 'assigned';
    }
    static create(props) {
        return new DispatchAssignment(props);
    }
    get status() {
        return this._status;
    }
    updateStatus(status) {
        this._status = status;
    }
}
exports.DispatchAssignment = DispatchAssignment;
