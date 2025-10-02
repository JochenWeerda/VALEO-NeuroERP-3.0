"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CarrierDocument = void 0;
class CarrierDocument {
    documentId;
    tenantId;
    carrierId;
    type;
    reference;
    payload;
    createdAt;
    constructor(props) {
        this.documentId = props.documentId ?? CARR - ;
        this.tenantId = props.tenantId;
        this.carrierId = props.carrierId;
        this.type = props.type;
        this.reference = props.reference;
        this.payload = props.payload;
        this.createdAt = props.createdAt ?? new Date();
    }
    static create(props) {
        return new CarrierDocument(props);
    }
}
exports.CarrierDocument = CarrierDocument;
