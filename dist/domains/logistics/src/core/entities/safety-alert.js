"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SafetyAlert = void 0;
class SafetyAlert {
    alertId;
    tenantId;
    referenceId;
    shipmentId;
    type;
    severity;
    message;
    detectedAt;
    acknowledgedBy;
    acknowledgedAt;
    constructor(props) {
        this.alertId = props.alertId ?? ALERT - ;
        this.tenantId = props.tenantId;
        this.referenceId = props.referenceId;
        this.shipmentId = props.shipmentId;
        this.type = props.type;
        this.severity = props.severity;
        this.message = props.message;
        this.detectedAt = props.detectedAt ?? new Date();
        this.acknowledgedBy = props.acknowledgedBy;
        this.acknowledgedAt = props.acknowledgedAt;
    }
    static create(props) {
        return new SafetyAlert(props);
    }
    acknowledge(userId) {
        return SafetyAlert.create({
            ...this,
            alertId: this.alertId,
            detectedAt: this.detectedAt,
            acknowledgedBy: userId,
            acknowledgedAt: new Date(),
        });
    }
}
exports.SafetyAlert = SafetyAlert;
