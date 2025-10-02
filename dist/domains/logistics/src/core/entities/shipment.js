"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Shipment = exports.ShipmentPayloadItem = exports.ShipmentStop = void 0;
const address_1 = require("../value-objects/address");
const time_window_1 = require("../value-objects/time-window");
const temperature_range_1 = require("../value-objects/temperature-range");
class ShipmentStop {
    stopId;
    sequence;
    type;
    address;
    window;
    constructor(props) {
        this.stopId = props.stopId ?? STOP - ;
        this.sequence = props.sequence;
        this.type = props.type;
        this.address = address_1.Address.create(props.address);
        this.window = props.window ? time_window_1.TimeWindow.create(props.window) : undefined;
    }
}
exports.ShipmentStop = ShipmentStop;
class ShipmentPayloadItem {
    sscc;
    description;
    weightKg;
    volumeM3;
    tempRange;
    constructor(props) {
        if (props.weightKg <= 0) {
            throw new Error('Payload weight must be positive');
        }
        this.sscc = props.sscc;
        this.description = props.description;
        this.weightKg = props.weightKg;
        this.volumeM3 = props.volumeM3;
        this.tempRange = props.tempRange ? temperature_range_1.TemperatureRange.create(props.tempRange) : undefined;
    }
}
exports.ShipmentPayloadItem = ShipmentPayloadItem;
class Shipment {
    shipmentId;
    tenantId;
    reference;
    origin;
    destination;
    priority;
    incoterm;
    createdAt;
    _status;
    stops;
    payload;
    constructor(props) {
        this.shipmentId = props.shipmentId ?? SHP - ;
        this.tenantId = props.tenantId;
        this.reference = props.reference;
        this.origin = address_1.Address.create(props.origin);
        this.destination = address_1.Address.create(props.destination);
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
    static create(props) {
        return new Shipment(props);
    }
    get status() {
        return this._status;
    }
    updateStatus(status) {
        this._status = status;
    }
    getStops() {
        return this.stops.map((stop) => ({ ...stop }));
    }
    getPayload() {
        return this.payload.map((item) => ({ ...item }));
    }
    toJSON() {
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
exports.Shipment = Shipment;
