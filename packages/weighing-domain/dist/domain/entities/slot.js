"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Slot = exports.SlotSchema = exports.GateType = exports.SlotStatus = void 0;
const zod_1 = require("zod");
exports.SlotStatus = {
    SCHEDULED: 'Scheduled',
    ENTERED: 'Entered',
    EXITED: 'Exited',
    CANCELLED: 'Cancelled',
    NO_SHOW: 'NoShow',
};
exports.GateType = {
    INBOUND: 'Inbound',
    OUTBOUND: 'Outbound',
    WEIGHING: 'Weighing',
    INSPECTION: 'Inspection',
};
exports.SlotSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string(),
    gateId: zod_1.z.string(),
    gateType: zod_1.z.enum([exports.GateType.INBOUND, exports.GateType.OUTBOUND, exports.GateType.WEIGHING, exports.GateType.INSPECTION]),
    windowFrom: zod_1.z.string().datetime(),
    windowTo: zod_1.z.string().datetime(),
    assignedVehicleId: zod_1.z.string().uuid().optional(),
    licensePlate: zod_1.z.string().optional(),
    priority: zod_1.z.number().min(1).max(10).default(5),
    status: zod_1.z.enum([exports.SlotStatus.SCHEDULED, exports.SlotStatus.ENTERED, exports.SlotStatus.EXITED, exports.SlotStatus.CANCELLED, exports.SlotStatus.NO_SHOW]).default(exports.SlotStatus.SCHEDULED),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    commodity: zod_1.z.string().optional(),
    expectedWeight: zod_1.z.number().optional(),
    enteredAt: zod_1.z.string().datetime().optional(),
    exitedAt: zod_1.z.string().datetime().optional(),
    actualServiceStart: zod_1.z.string().datetime().optional(),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class Slot {
    id;
    tenantId;
    gateId;
    gateType;
    windowFrom;
    windowTo;
    assignedVehicleId;
    licensePlate;
    priority;
    status;
    contractId;
    orderId;
    commodity;
    expectedWeight;
    enteredAt;
    exitedAt;
    actualServiceStart;
    notes;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.tenantId = props.tenantId;
        this.gateId = props.gateId;
        this.gateType = props.gateType;
        this.windowFrom = props.windowFrom;
        this.windowTo = props.windowTo;
        if (props.assignedVehicleId)
            this.assignedVehicleId = props.assignedVehicleId;
        if (props.licensePlate)
            this.licensePlate = props.licensePlate;
        this.priority = props.priority;
        this.status = props.status;
        if (props.contractId)
            this.contractId = props.contractId;
        if (props.orderId)
            this.orderId = props.orderId;
        if (props.commodity)
            this.commodity = props.commodity;
        if (props.expectedWeight)
            this.expectedWeight = props.expectedWeight;
        if (props.enteredAt)
            this.enteredAt = props.enteredAt;
        if (props.exitedAt)
            this.exitedAt = props.exitedAt;
        if (props.actualServiceStart)
            this.actualServiceStart = props.actualServiceStart;
        if (props.notes)
            this.notes = props.notes;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
    }
    assignVehicle(vehicleId, licensePlate) {
        if (this.status !== exports.SlotStatus.SCHEDULED) {
            throw new Error('Can only assign vehicle to scheduled slots');
        }
        this.assignedVehicleId = vehicleId;
        if (licensePlate)
            this.licensePlate = licensePlate;
        this.updatedAt = new Date();
        this.version++;
    }
    markEntered() {
        if (this.status !== exports.SlotStatus.SCHEDULED) {
            throw new Error('Can only mark scheduled slots as entered');
        }
        this.status = exports.SlotStatus.ENTERED;
        this.enteredAt = new Date();
        this.actualServiceStart = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    markExited() {
        if (this.status !== exports.SlotStatus.ENTERED) {
            throw new Error('Can only mark entered slots as exited');
        }
        this.status = exports.SlotStatus.EXITED;
        this.exitedAt = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    cancel(reason) {
        const nonCancellableStatuses = [exports.SlotStatus.EXITED, exports.SlotStatus.CANCELLED];
        if (nonCancellableStatuses.includes(this.status)) {
            throw new Error('Cannot cancel completed or already cancelled slots');
        }
        this.status = exports.SlotStatus.CANCELLED;
        if (reason)
            this.notes = (this.notes ? this.notes + '; ' : '') + `Cancelled: ${reason}`;
        this.updatedAt = new Date();
        this.version++;
    }
    markNoShow() {
        if (this.status !== exports.SlotStatus.SCHEDULED) {
            throw new Error('Can only mark scheduled slots as no-show');
        }
        this.status = exports.SlotStatus.NO_SHOW;
        this.updatedAt = new Date();
        this.version++;
    }
    isActive() {
        const activeStatuses = [exports.SlotStatus.SCHEDULED, exports.SlotStatus.ENTERED];
        return activeStatuses.includes(this.status);
    }
    isCompleted() {
        return this.status === exports.SlotStatus.EXITED;
    }
    isOverdue() {
        const now = new Date();
        return this.status === exports.SlotStatus.SCHEDULED && now > this.windowTo;
    }
    getWaitTimeMinutes() {
        if (!this.enteredAt || !this.actualServiceStart)
            return null;
        return Math.round((this.actualServiceStart.getTime() - this.enteredAt.getTime()) / (1000 * 60));
    }
    getServiceTimeMinutes() {
        if (!this.actualServiceStart || !this.exitedAt)
            return null;
        return Math.round((this.exitedAt.getTime() - this.actualServiceStart.getTime()) / (1000 * 60));
    }
    getTotalTimeMinutes() {
        if (!this.enteredAt || !this.exitedAt)
            return null;
        return Math.round((this.exitedAt.getTime() - this.enteredAt.getTime()) / (1000 * 60));
    }
    isHighPriority() {
        return this.priority <= 3;
    }
    isLowPriority() {
        return this.priority >= 8;
    }
    isWithinWindow(now) {
        const currentTime = now || new Date();
        return currentTime >= this.windowFrom && currentTime <= this.windowTo;
    }
    getWindowDurationMinutes() {
        return Math.round((this.windowTo.getTime() - this.windowFrom.getTime()) / (1000 * 60));
    }
}
exports.Slot = Slot;
//# sourceMappingURL=slot.js.map