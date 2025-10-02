"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.YardVisit = void 0;
const time_window_1 = require("../value-objects/time-window");
class YardVisit {
    visitId;
    tenantId;
    shipmentId;
    gate;
    dock;
    scheduledWindow;
    checkinAt;
    checkoutAt;
    _status;
    constructor(props) {
        this.visitId = props.visitId ?? YARD - ;
        this.tenantId = props.tenantId;
        this.shipmentId = props.shipmentId;
        this.gate = props.gate;
        this.dock = props.dock;
        this.scheduledWindow = props.scheduledWindow
            ? time_window_1.TimeWindow.create({ from: props.scheduledWindow.from, to: props.scheduledWindow.to })
            : undefined;
        this.checkinAt = props.checkinAt;
        this.checkoutAt = props.checkoutAt;
        this._status = props.status ?? 'scheduled';
    }
    static create(props) {
        return new YardVisit(props);
    }
    get status() {
        return this._status;
    }
    updateStatus(status) {
        this._status = status;
    }
}
exports.YardVisit = YardVisit;
