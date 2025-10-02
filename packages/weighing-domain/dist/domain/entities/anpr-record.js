"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ANPRRecord = exports.ANPRRecordSchema = exports.ANPRStatus = exports.ANPRConfidence = void 0;
const zod_1 = require("zod");
exports.ANPRConfidence = {
    LOW: 'Low',
    MEDIUM: 'Medium',
    HIGH: 'High',
};
exports.ANPRStatus = {
    DETECTED: 'Detected',
    PROCESSED: 'Processed',
    ASSIGNED: 'Assigned',
    REJECTED: 'Rejected',
    ERROR: 'Error',
};
exports.ANPRRecordSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string(),
    licensePlate: zod_1.z.string(),
    confidence: zod_1.z.number().min(0).max(100),
    confidenceLevel: zod_1.z.enum([exports.ANPRConfidence.LOW, exports.ANPRConfidence.MEDIUM, exports.ANPRConfidence.HIGH]),
    capturedAt: zod_1.z.string().datetime(),
    imageUri: zod_1.z.string().url().optional(),
    cameraId: zod_1.z.string(),
    gateId: zod_1.z.string().optional(),
    status: zod_1.z.enum([exports.ANPRStatus.DETECTED, exports.ANPRStatus.PROCESSED, exports.ANPRStatus.ASSIGNED, exports.ANPRStatus.REJECTED, exports.ANPRStatus.ERROR]).default(exports.ANPRStatus.DETECTED),
    processedAt: zod_1.z.string().datetime().optional(),
    ticketSuggestionId: zod_1.z.string().uuid().optional(),
    assignedTicketId: zod_1.z.string().uuid().optional(),
    vehicleId: zod_1.z.string().uuid().optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    commodity: zod_1.z.string().optional(),
    errorMessage: zod_1.z.string().optional(),
    retryCount: zod_1.z.number().default(0),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class ANPRRecord {
    id;
    tenantId;
    licensePlate;
    confidence;
    confidenceLevel;
    capturedAt;
    imageUri;
    cameraId;
    gateId;
    status;
    processedAt;
    ticketSuggestionId;
    assignedTicketId;
    vehicleId;
    contractId;
    orderId;
    commodity;
    errorMessage;
    retryCount;
    createdAt;
    updatedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.tenantId = props.tenantId;
        this.licensePlate = props.licensePlate;
        this.confidence = props.confidence;
        this.confidenceLevel = props.confidenceLevel;
        this.capturedAt = props.capturedAt;
        if (props.imageUri)
            this.imageUri = props.imageUri;
        this.cameraId = props.cameraId;
        if (props.gateId)
            this.gateId = props.gateId;
        this.status = props.status;
        if (props.processedAt)
            this.processedAt = props.processedAt;
        if (props.ticketSuggestionId)
            this.ticketSuggestionId = props.ticketSuggestionId;
        if (props.assignedTicketId)
            this.assignedTicketId = props.assignedTicketId;
        if (props.vehicleId)
            this.vehicleId = props.vehicleId;
        if (props.contractId)
            this.contractId = props.contractId;
        if (props.orderId)
            this.orderId = props.orderId;
        if (props.commodity)
            this.commodity = props.commodity;
        if (props.errorMessage)
            this.errorMessage = props.errorMessage;
        this.retryCount = props.retryCount;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        this.version = props.version;
    }
    process(vehicleData) {
        if (this.status !== exports.ANPRStatus.DETECTED) {
            throw new Error('Can only process detected ANPR records');
        }
        this.status = exports.ANPRStatus.PROCESSED;
        this.processedAt = new Date();
        if (vehicleData) {
            if (vehicleData.vehicleId)
                this.vehicleId = vehicleData.vehicleId;
            if (vehicleData.contractId)
                this.contractId = vehicleData.contractId;
            if (vehicleData.orderId)
                this.orderId = vehicleData.orderId;
            if (vehicleData.commodity)
                this.commodity = vehicleData.commodity;
        }
        this.updatedAt = new Date();
        this.version++;
    }
    assignTicket(ticketId) {
        if (this.status !== exports.ANPRStatus.PROCESSED) {
            throw new Error('Can only assign tickets to processed ANPR records');
        }
        this.status = exports.ANPRStatus.ASSIGNED;
        this.assignedTicketId = ticketId;
        this.updatedAt = new Date();
        this.version++;
    }
    reject(reason) {
        const nonRejectableStatuses = [exports.ANPRStatus.ASSIGNED, exports.ANPRStatus.ERROR];
        if (nonRejectableStatuses.includes(this.status)) {
            throw new Error('Cannot reject assigned or errored ANPR records');
        }
        this.status = exports.ANPRStatus.REJECTED;
        if (reason)
            this.errorMessage = reason;
        this.updatedAt = new Date();
        this.version++;
    }
    markError(errorMessage) {
        this.status = exports.ANPRStatus.ERROR;
        this.errorMessage = errorMessage;
        this.retryCount++;
        this.updatedAt = new Date();
        this.version++;
    }
    retry() {
        if (this.retryCount >= 3) {
            throw new Error('Maximum retry attempts exceeded');
        }
        this.status = exports.ANPRStatus.DETECTED;
        if (this.errorMessage)
            delete this.errorMessage;
        this.retryCount++;
        this.updatedAt = new Date();
        this.version++;
    }
    isProcessed() {
        return this.status === exports.ANPRStatus.PROCESSED;
    }
    isAssigned() {
        return this.status === exports.ANPRStatus.ASSIGNED;
    }
    isHighConfidence() {
        return this.confidenceLevel === exports.ANPRConfidence.HIGH;
    }
    isMediumConfidence() {
        return this.confidenceLevel === exports.ANPRConfidence.MEDIUM;
    }
    isLowConfidence() {
        return this.confidenceLevel === exports.ANPRConfidence.LOW;
    }
    canBeRetried() {
        const retryableStatuses = [exports.ANPRStatus.ERROR, exports.ANPRStatus.REJECTED];
        return this.retryCount < 3 && retryableStatuses.includes(this.status);
    }
    getConfidencePercentage() {
        return this.confidence;
    }
    getConfidenceLevel() {
        if (this.confidence >= 90)
            return exports.ANPRConfidence.HIGH;
        if (this.confidence >= 70)
            return exports.ANPRConfidence.MEDIUM;
        return exports.ANPRConfidence.LOW;
    }
    getAgeMinutes() {
        const now = new Date();
        return Math.round((now.getTime() - this.capturedAt.getTime()) / (1000 * 60));
    }
    isStale(maxAgeMinutes = 30) {
        return this.getAgeMinutes() > maxAgeMinutes;
    }
    getProcessingTimeSeconds() {
        if (!this.processedAt)
            return null;
        return Math.round((this.processedAt.getTime() - this.capturedAt.getTime()) / 1000);
    }
}
exports.ANPRRecord = ANPRRecord;
//# sourceMappingURL=anpr-record.js.map