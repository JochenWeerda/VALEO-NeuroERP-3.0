"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DriverTimeEventEntity = exports.REST_DRIVER_EVENT_TYPES = exports.PRODUCTIVE_DRIVER_EVENT_TYPES = exports.DriverTimeEventSchema = exports.DriverTimeCorrectionStatusSchema = exports.DriverTimeEventSourceSchema = exports.DriverTimeEventTypeSchema = void 0;
const zod_1 = require("zod");
const MAX_EVENT_DURATION_HOURS = 48;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MILLISECONDS_PER_MINUTE = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE;
const MINUTES_PER_HOUR = 60;
exports.DriverTimeEventTypeSchema = zod_1.z.enum([
    'DRIVING',
    'LOADING',
    'UNLOADING',
    'OTHER_WORK',
    'AVAILABILITY',
    'BREAK',
    'DAILY_REST',
    'WEEKLY_REST',
    'TOUR_START',
    'TOUR_END',
    'VEHICLE_CHANGE',
    'TACHO_IMPORT'
]);
exports.DriverTimeEventSourceSchema = zod_1.z.enum(['MANUAL', 'MOBILE', 'TACHO', 'TELEMATICS', 'DISPATCH']);
exports.DriverTimeCorrectionStatusSchema = zod_1.z.enum(['ORIGINAL', 'CORRECTED', 'REQUIRES_REASON']);
exports.DriverTimeEventSchema = zod_1.z.object({
    id: zod_1.z.string().min(1),
    tenantId: zod_1.z.string().min(1),
    employeeId: zod_1.z.string().min(1),
    eventType: exports.DriverTimeEventTypeSchema,
    start: zod_1.z.string().datetime(),
    end: zod_1.z.string().datetime(),
    tourId: zod_1.z.string().min(1).optional(),
    vehicleId: zod_1.z.string().min(1).optional(),
    locationRef: zod_1.z.string().min(1).optional(),
    source: exports.DriverTimeEventSourceSchema,
    correctionStatus: exports.DriverTimeCorrectionStatusSchema.default('ORIGINAL'),
    correctionReason: zod_1.z.string().min(1).optional(),
    auditRef: zod_1.z.string().min(1).optional()
});
exports.PRODUCTIVE_DRIVER_EVENT_TYPES = new Set([
    'DRIVING',
    'LOADING',
    'UNLOADING',
    'OTHER_WORK',
    'AVAILABILITY'
]);
exports.REST_DRIVER_EVENT_TYPES = new Set([
    'BREAK',
    'DAILY_REST',
    'WEEKLY_REST'
]);
class DriverTimeEventEntity {
    data;
    constructor(data) {
        this.data = exports.DriverTimeEventSchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get employeeId() { return this.data.employeeId; }
    get eventType() { return this.data.eventType; }
    get start() { return this.data.start; }
    get end() { return this.data.end; }
    get tourId() { return this.data.tourId; }
    get vehicleId() { return this.data.vehicleId; }
    get source() { return this.data.source; }
    get correctionStatus() { return this.data.correctionStatus; }
    get correctionReason() { return this.data.correctionReason; }
    getDurationMinutes() {
        const start = new Date(this.data.start);
        const end = new Date(this.data.end);
        return Math.floor((end.getTime() - start.getTime()) / MILLISECONDS_PER_MINUTE);
    }
    isProductiveWork() {
        return exports.PRODUCTIVE_DRIVER_EVENT_TYPES.has(this.data.eventType);
    }
    isRest() {
        return exports.REST_DRIVER_EVENT_TYPES.has(this.data.eventType);
    }
    requiresVehicle() {
        return this.data.eventType === 'DRIVING' || this.data.eventType === 'VEHICLE_CHANGE';
    }
    requiresTour() {
        return this.data.eventType !== 'DAILY_REST' && this.data.eventType !== 'WEEKLY_REST';
    }
    toJSON() {
        return { ...this.data };
    }
    validateBusinessRules() {
        const start = new Date(this.data.start);
        const end = new Date(this.data.end);
        if (end <= start) {
            throw new Error('Driver-time event end must be after start');
        }
        const durationHours = (end.getTime() - start.getTime()) / MILLISECONDS_PER_MINUTE / MINUTES_PER_HOUR;
        if (durationHours > MAX_EVENT_DURATION_HOURS) {
            throw new Error('Driver-time event duration exceeds 48 hours');
        }
    }
    static fromJSON(data) {
        return new DriverTimeEventEntity(data);
    }
}
exports.DriverTimeEventEntity = DriverTimeEventEntity;
//# sourceMappingURL=driver-time-event.js.map