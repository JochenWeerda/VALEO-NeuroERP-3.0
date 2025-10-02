"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CarrierDocument = void 0;
const nanoid_1 = require("nanoid");
class CarrierDocument {
    constructor(props) {
        this.documentId = props.documentId ?? `CARR-${(0, nanoid_1.nanoid)(10)}`;
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
//# sourceMappingURL=carrier-document.js.map