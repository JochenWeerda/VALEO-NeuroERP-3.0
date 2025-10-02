"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProofOfDelivery = void 0;
const nanoid_1 = require("nanoid");
class ProofOfDelivery {
    constructor(props) {
        this.podId = props.podId ?? `POD-${(0, nanoid_1.nanoid)(10)}`;
        this.tenantId = props.tenantId;
        this.shipmentId = props.shipmentId;
        this.stopId = props.stopId;
        this.signedBy = props.signedBy;
        this.capturedAt = props.capturedAt ?? new Date();
        this.signatureRef = props.signatureRef;
        this.photoRefs = props.photoRefs;
        this.scans = props.scans;
        this.exceptions = props.exceptions;
    }
    static create(props) {
        return new ProofOfDelivery(props);
    }
}
exports.ProofOfDelivery = ProofOfDelivery;
//# sourceMappingURL=proof-of-delivery.js.map