"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmissionRecord = void 0;
class EmissionRecord {
    emissionId;
    tenantId;
    shipmentId;
    co2eKg;
    method;
    factors;
    calculatedAt;
    constructor(props) {
        if (props.co2eKg < 0) {
            throw new Error('Emission value cannot be negative');
        }
        this.emissionId = props.emissionId ?? EM - ;
        this.tenantId = props.tenantId;
        this.shipmentId = props.shipmentId;
        this.co2eKg = props.co2eKg;
        this.method = props.method;
        this.factors = props.factors ?? [];
        this.calculatedAt = props.calculatedAt ?? new Date();
    }
    static create(props) {
        return new EmissionRecord(props);
    }
}
exports.EmissionRecord = EmissionRecord;
