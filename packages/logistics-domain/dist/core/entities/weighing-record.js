"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighingRecord = void 0;
const nanoid_1 = require("nanoid");
class WeighingRecord {
    constructor(props) {
        if (props.grossWeightKg <= props.tareWeightKg) {
            throw new Error('Gross weight must exceed tare weight');
        }
        this.weighingId = props.weighingId ?? `WEIGH-${(0, nanoid_1.nanoid)(10)}`;
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
//# sourceMappingURL=weighing-record.js.map