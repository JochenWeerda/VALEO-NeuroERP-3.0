"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighingRecord = void 0;
class WeighingRecord {
    weighingId;
    tenantId;
    shipmentId;
    grossWeightKg;
    tareWeightKg;
    netWeightKg;
    source;
    capturedAt;
    constructor(props) {
        if (props.grossWeightKg <= props.tareWeightKg) {
            throw new Error('Gross weight must exceed tare weight');
        }
        this.weighingId = props.weighingId ?? WEIGH - ;
        this.tenantId = props.tenantId;
        this.shipmentId = props.shipmentId;
        this.grossWeightKg = props.grossWeightKg;
        this.tareWeightKg = props.tareWeightKg;
        this.netWeightKg = props.grossWeightKg - props.tareWeightKg;
        this.source = props.source;
        this.capturedAt = props.capturedAt ?? new Date();
    }
    static create(props) {
        return new WeighingRecord(props);
    }
}
exports.WeighingRecord = WeighingRecord;
