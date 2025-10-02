"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CallOff = exports.CallOffSchema = exports.CallOffStatus = void 0;
const zod_1 = require("zod");
exports.CallOffStatus = {
    PLANNED: 'Planned',
    SCHEDULED: 'Scheduled',
    DELIVERED: 'Delivered',
    INVOICED: 'Invoiced',
    CANCELLED: 'Cancelled',
};
exports.CallOffSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    qty: zod_1.z.number().positive(),
    window: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    site: zod_1.z.string().optional(),
    silo: zod_1.z.string().optional(),
    customerYard: zod_1.z.string().optional(),
    status: zod_1.z.enum([exports.CallOffStatus.PLANNED, exports.CallOffStatus.SCHEDULED, exports.CallOffStatus.DELIVERED, exports.CallOffStatus.INVOICED, exports.CallOffStatus.CANCELLED]).default(exports.CallOffStatus.PLANNED),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class CallOff {
    id;
    contractId;
    tenantId;
    qty;
    window;
    site;
    silo;
    customerYard;
    status;
    notes;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.contractId = props.contractId;
        this.tenantId = props.tenantId;
        this.qty = props.qty;
        this.window = props.window;
        if (props.site)
            this.site = props.site;
        if (props.silo)
            this.silo = props.silo;
        if (props.customerYard)
            this.customerYard = props.customerYard;
        this.status = props.status;
        if (props.notes)
            this.notes = props.notes;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
    }
    schedule() {
        if (this.status !== exports.CallOffStatus.PLANNED) {
            throw new Error('Only planned call-offs can be scheduled');
        }
        this.status = exports.CallOffStatus.SCHEDULED;
        this.updatedAt = new Date();
        this.version++;
    }
    markDelivered() {
        if (this.status !== exports.CallOffStatus.SCHEDULED) {
            throw new Error('Only scheduled call-offs can be marked as delivered');
        }
        this.status = exports.CallOffStatus.DELIVERED;
        this.updatedAt = new Date();
        this.version++;
    }
    cancel() {
        if (this.status === exports.CallOffStatus.DELIVERED || this.status === exports.CallOffStatus.INVOICED) {
            throw new Error('Delivered or invoiced call-offs cannot be cancelled');
        }
        this.status = exports.CallOffStatus.CANCELLED;
        this.updatedAt = new Date();
        this.version++;
    }
    canBeModified() {
        const modifiableStatuses = [exports.CallOffStatus.PLANNED, exports.CallOffStatus.SCHEDULED];
        return modifiableStatuses.includes(this.status);
    }
}
exports.CallOff = CallOff;
//# sourceMappingURL=call-off.js.map