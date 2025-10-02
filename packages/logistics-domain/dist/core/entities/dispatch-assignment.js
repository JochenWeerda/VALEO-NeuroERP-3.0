"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DispatchAssignment = void 0;
const nanoid_1 = require("nanoid");
class DispatchAssignment {
    constructor(props) {
        this.assignmentId = props.assignmentId ?? `ASSIGN-${(0, nanoid_1.nanoid)(10)}`;
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
//# sourceMappingURL=dispatch-assignment.js.map