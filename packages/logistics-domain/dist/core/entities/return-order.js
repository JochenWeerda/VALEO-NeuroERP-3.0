"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReturnOrder = void 0;
const nanoid_1 = require("nanoid");
const address_1 = require("../value-objects/address");
class ReturnOrder {
    constructor(props) {
        this.returnId = props.returnId ?? `RET-${(0, nanoid_1.nanoid)(10)}`;
        this.tenantId = props.tenantId;
        this.originalShipmentId = props.originalShipmentId;
        this.pickupAddress = address_1.Address.create(props.pickupAddress);
        this.returnReason = props.returnReason;
        this.requestedAt = props.requestedAt ?? new Date();
        this._status = props.status ?? 'requested';
    }
    static create(props) {
        return new ReturnOrder(props);
    }
    get status() {
        return this._status;
    }
    updateStatus(status) {
        this._status = status;
    }
}
exports.ReturnOrder = ReturnOrder;
//# sourceMappingURL=return-order.js.map