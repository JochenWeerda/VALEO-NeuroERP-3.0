"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FreightRate = void 0;
const nanoid_1 = require("nanoid");
class FreightRate {
    constructor(props) {
        this.rateId = props.rateId ?? `RATE-${(0, nanoid_1.nanoid)(10)}`;
        this.tenantId = props.tenantId;
        this.shipmentId = props.shipmentId;
        this.currency = props.currency;
        this.baseAmount = props.baseAmount;
        this.surcharges = props.surcharges ?? [];
        this.totalAmount = this.surcharges.reduce((acc, item) => acc + item.amount, props.baseAmount);
        this.explain = props.explain;
        this.calculatedAt = props.calculatedAt ?? new Date();
    }
    static create(props) {
        if (props.baseAmount < 0) {
            throw new Error('Freight base amount cannot be negative');
        }
        return new FreightRate(props);
    }
}
exports.FreightRate = FreightRate;
//# sourceMappingURL=freight-rate.js.map