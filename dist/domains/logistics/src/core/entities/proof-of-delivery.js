"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProofOfDelivery = void 0;
class ProofOfDelivery {
    podId;
    tenantId;
    shipmentId;
    stopId;
    signedBy;
    capturedAt;
    signatureRef;
    photoRefs;
    scans;
    exceptions;
    constructor(props) {
        this.podId = props.podId ?? POD - ;
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
