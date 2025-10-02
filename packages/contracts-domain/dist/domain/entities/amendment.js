"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Amendment = exports.AmendmentSchema = exports.AmendmentStatus = exports.AmendmentType = void 0;
const zod_1 = require("zod");
exports.AmendmentType = {
    QTY_CHANGE: 'QtyChange',
    WINDOW_CHANGE: 'WindowChange',
    PRICE_RULE_CHANGE: 'PriceRuleChange',
    COUNTERPARTY_CHANGE: 'CounterpartyChange',
    DELIVERY_TERMS_CHANGE: 'DeliveryTermsChange',
    OTHER: 'Other',
};
exports.AmendmentStatus = {
    PENDING: 'Pending',
    APPROVED: 'Approved',
    REJECTED: 'Rejected',
    CANCELLED: 'Cancelled',
};
exports.AmendmentSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    type: zod_1.z.enum([
        exports.AmendmentType.QTY_CHANGE,
        exports.AmendmentType.WINDOW_CHANGE,
        exports.AmendmentType.PRICE_RULE_CHANGE,
        exports.AmendmentType.COUNTERPARTY_CHANGE,
        exports.AmendmentType.DELIVERY_TERMS_CHANGE,
        exports.AmendmentType.OTHER,
    ]),
    reason: zod_1.z.string(),
    changes: zod_1.z.record(zod_1.z.any()),
    approvedBy: zod_1.z.string().optional(),
    approvedAt: zod_1.z.string().datetime().optional(),
    status: zod_1.z.enum([
        exports.AmendmentStatus.PENDING,
        exports.AmendmentStatus.APPROVED,
        exports.AmendmentStatus.REJECTED,
        exports.AmendmentStatus.CANCELLED,
    ]).default(exports.AmendmentStatus.PENDING),
    effectiveAt: zod_1.z.string().datetime().optional(),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class Amendment {
    id;
    contractId;
    tenantId;
    type;
    reason;
    changes;
    approvedBy;
    approvedAt;
    status;
    effectiveAt;
    notes;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.contractId = props.contractId;
        this.tenantId = props.tenantId;
        this.type = props.type;
        this.reason = props.reason;
        this.changes = props.changes;
        if (props.approvedBy)
            this.approvedBy = props.approvedBy;
        if (props.approvedAt)
            this.approvedAt = props.approvedAt;
        this.status = props.status;
        if (props.effectiveAt)
            this.effectiveAt = props.effectiveAt;
        if (props.notes)
            this.notes = props.notes;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
    }
    approve(approvedBy) {
        if (this.status !== exports.AmendmentStatus.PENDING) {
            throw new Error('Only pending amendments can be approved');
        }
        this.status = exports.AmendmentStatus.APPROVED;
        this.approvedBy = approvedBy;
        this.approvedAt = new Date();
        this.effectiveAt = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    reject() {
        if (this.status !== exports.AmendmentStatus.PENDING) {
            throw new Error('Only pending amendments can be rejected');
        }
        this.status = exports.AmendmentStatus.REJECTED;
        this.updatedAt = new Date();
        this.version++;
    }
    cancel() {
        if (this.status === exports.AmendmentStatus.APPROVED) {
            throw new Error('Approved amendments cannot be cancelled');
        }
        this.status = exports.AmendmentStatus.CANCELLED;
        this.updatedAt = new Date();
        this.version++;
    }
    canBeModified() {
        return this.status === exports.AmendmentStatus.PENDING;
    }
    isEffective() {
        return this.status === exports.AmendmentStatus.APPROVED &&
            this.effectiveAt !== undefined &&
            this.effectiveAt <= new Date();
    }
}
exports.Amendment = Amendment;
//# sourceMappingURL=amendment.js.map