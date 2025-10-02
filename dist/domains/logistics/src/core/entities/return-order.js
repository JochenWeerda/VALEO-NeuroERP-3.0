"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReturnOrder = void 0;
const address_1 = require("../value-objects/address");
class ReturnOrder {
    returnId;
    tenantId;
    originalShipmentId;
    pickupAddress;
    returnReason;
    requestedAt;
    _status;
    constructor(props) {
        this.returnId = props.returnId ?? RET - ;
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
