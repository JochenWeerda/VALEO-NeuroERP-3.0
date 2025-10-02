"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WaitLog = exports.WaitLogSchema = void 0;
const zod_1 = require("zod");
exports.WaitLogSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string(),
    ticketId: zod_1.z.string().uuid(),
    licensePlate: zod_1.z.string().optional(),
    arrivalAt: zod_1.z.string().datetime(),
    serviceStartAt: zod_1.z.string().datetime().optional(),
    serviceEndAt: zod_1.z.string().datetime().optional(),
    waitTimeMinutes: zod_1.z.number().optional(),
    serviceTimeMinutes: zod_1.z.number().optional(),
    totalTimeMinutes: zod_1.z.number().optional(),
    gateId: zod_1.z.string(),
    gateType: zod_1.z.enum(['Inbound', 'Outbound', 'Weighing', 'Inspection']),
    slotId: zod_1.z.string().uuid().optional(),
    priority: zod_1.z.number().min(1).max(10).default(5),
    isHighPriority: zod_1.z.boolean().optional(),
    isOvertime: zod_1.z.boolean().optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    commodity: zod_1.z.string().optional(),
    expectedWeight: zod_1.z.number().optional(),
    status: zod_1.z.enum(['Waiting', 'InService', 'Completed', 'Cancelled']).default('Waiting'),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class WaitLog {
    id;
    tenantId;
    ticketId;
    licensePlate;
    arrivalAt;
    serviceStartAt;
    serviceEndAt;
    waitTimeMinutes;
    serviceTimeMinutes;
    totalTimeMinutes;
    gateId;
    gateType;
    slotId;
    priority;
    isHighPriority;
    isOvertime;
    contractId;
    orderId;
    commodity;
    expectedWeight;
    status;
    notes;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.tenantId = props.tenantId;
        this.ticketId = props.ticketId;
        if (props.licensePlate)
            this.licensePlate = props.licensePlate;
        this.arrivalAt = props.arrivalAt;
        if (props.serviceStartAt)
            this.serviceStartAt = props.serviceStartAt;
        if (props.serviceEndAt)
            this.serviceEndAt = props.serviceEndAt;
        if (props.waitTimeMinutes !== undefined)
            this.waitTimeMinutes = props.waitTimeMinutes;
        if (props.serviceTimeMinutes !== undefined)
            this.serviceTimeMinutes = props.serviceTimeMinutes;
        if (props.totalTimeMinutes !== undefined)
            this.totalTimeMinutes = props.totalTimeMinutes;
        this.gateId = props.gateId;
        this.gateType = props.gateType;
        if (props.slotId)
            this.slotId = props.slotId;
        this.priority = props.priority;
        if (props.isHighPriority !== undefined)
            this.isHighPriority = props.isHighPriority;
        if (props.isOvertime !== undefined)
            this.isOvertime = props.isOvertime;
        if (props.contractId)
            this.contractId = props.contractId;
        if (props.orderId)
            this.orderId = props.orderId;
        if (props.commodity)
            this.commodity = props.commodity;
        if (props.expectedWeight)
            this.expectedWeight = props.expectedWeight;
        this.status = props.status;
        if (props.notes)
            this.notes = props.notes;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
        this.calculateTimes();
        this.isHighPriority = this.priority <= 3;
    }
    startService() {
        if (this.status !== 'Waiting') {
            throw new Error('Can only start service for waiting entries');
        }
        this.status = 'InService';
        this.serviceStartAt = new Date();
        this.calculateTimes();
        this.updatedAt = new Date();
        this.version++;
    }
    completeService() {
        if (this.status !== 'InService') {
            throw new Error('Can only complete service for entries in service');
        }
        this.status = 'Completed';
        this.serviceEndAt = new Date();
        this.calculateTimes();
        this.updatedAt = new Date();
        this.version++;
    }
    cancel(reason) {
        if (this.status === 'Completed') {
            throw new Error('Cannot cancel completed entries');
        }
        this.status = 'Cancelled';
        if (reason)
            this.notes = (this.notes ? this.notes + '; ' : '') + `Cancelled: ${reason}`;
        this.calculateTimes();
        this.updatedAt = new Date();
        this.version++;
    }
    calculateTimes() {
        const now = new Date();
        if (this.serviceStartAt) {
            this.waitTimeMinutes = Math.round((this.serviceStartAt.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
        }
        if (this.serviceStartAt && this.serviceEndAt) {
            this.serviceTimeMinutes = Math.round((this.serviceEndAt.getTime() - this.serviceStartAt.getTime()) / (1000 * 60));
        }
        const endTime = this.serviceEndAt || (this.status === 'InService' ? now : this.serviceStartAt);
        if (endTime) {
            this.totalTimeMinutes = Math.round((endTime.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
        }
        this.isOvertime = (this.waitTimeMinutes || 0) > 120;
    }
    isWaiting() {
        return this.status === 'Waiting';
    }
    isInService() {
        return this.status === 'InService';
    }
    isCompleted() {
        return this.status === 'Completed';
    }
    isActive() {
        return ['Waiting', 'InService'].includes(this.status);
    }
    getCurrentWaitTimeMinutes() {
        if (this.serviceStartAt)
            return this.waitTimeMinutes || 0;
        const now = new Date();
        return Math.round((now.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
    }
    getAgeMinutes() {
        const now = new Date();
        return Math.round((now.getTime() - this.arrivalAt.getTime()) / (1000 * 60));
    }
    isLongWait(thresholdMinutes = 60) {
        return this.getCurrentWaitTimeMinutes() > thresholdMinutes;
    }
    isHighPriorityCheck() {
        return this.priority <= 3;
    }
    isLowPriority() {
        return this.priority >= 8;
    }
    getServiceEfficiency() {
        if (!this.expectedWeight || !this.serviceTimeMinutes)
            return null;
        return this.expectedWeight / this.serviceTimeMinutes;
    }
    toReportRow() {
        const row = {
            ticketId: this.ticketId,
            gateId: this.gateId,
            gateType: this.gateType,
            priority: this.priority,
            arrivalAt: this.arrivalAt.toISOString(),
            status: this.status,
        };
        if (this.licensePlate)
            row.licensePlate = this.licensePlate;
        if (this.serviceStartAt)
            row.serviceStartAt = this.serviceStartAt.toISOString();
        if (this.serviceEndAt)
            row.serviceEndAt = this.serviceEndAt.toISOString();
        if (this.waitTimeMinutes !== undefined)
            row.waitTimeMinutes = this.waitTimeMinutes;
        if (this.serviceTimeMinutes !== undefined)
            row.serviceTimeMinutes = this.serviceTimeMinutes;
        if (this.totalTimeMinutes !== undefined)
            row.totalTimeMinutes = this.totalTimeMinutes;
        if (this.commodity)
            row.commodity = this.commodity;
        if (this.isOvertime !== undefined)
            row.isOvertime = this.isOvertime;
        return row;
    }
}
exports.WaitLog = WaitLog;
//# sourceMappingURL=wait-log.js.map