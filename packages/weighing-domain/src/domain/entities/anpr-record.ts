import { z } from 'zod';

// Enums
export const ANPRConfidence = {
  LOW: 'Low',       // < 70%
  MEDIUM: 'Medium', // 70-90%
  HIGH: 'High',     // > 90%
} as const;

export const ANPRStatus = {
  DETECTED: 'Detected',
  PROCESSED: 'Processed',
  ASSIGNED: 'Assigned',
  REJECTED: 'Rejected',
  ERROR: 'Error',
} as const;

// Types
export type ANPRConfidenceValue = typeof ANPRConfidence[keyof typeof ANPRConfidence];
export type ANPRStatusValue = typeof ANPRStatus[keyof typeof ANPRStatus];

// Schema
export const ANPRRecordSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string(),
  licensePlate: z.string(),
  confidence: z.number().min(0).max(100),
  confidenceLevel: z.enum([ANPRConfidence.LOW, ANPRConfidence.MEDIUM, ANPRConfidence.HIGH]),
  capturedAt: z.string().datetime(),
  imageUri: z.string().url().optional(),
  cameraId: z.string(),
  gateId: z.string().optional(),

  // Processing
  status: z.enum([ANPRStatus.DETECTED, ANPRStatus.PROCESSED, ANPRStatus.ASSIGNED, ANPRStatus.REJECTED, ANPRStatus.ERROR]).default(ANPRStatus.DETECTED),
  processedAt: z.string().datetime().optional(),
  ticketSuggestionId: z.string().uuid().optional(),
  assignedTicketId: z.string().uuid().optional(),

  // Vehicle data (from lookup)
  vehicleId: z.string().uuid().optional(),
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  commodity: z.string().optional(),

  // Error handling
  errorMessage: z.string().optional(),
  retryCount: z.number().default(0),

  // Metadata
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  version: z.number().default(1),
});

// Entity interface
export interface ANPRRecordEntity {
  id: string;
  tenantId: string;
  licensePlate: string;
  confidence: number;
  confidenceLevel: ANPRConfidenceValue;
  capturedAt: Date;
  imageUri?: string;
  cameraId: string;
  gateId?: string;

  // Processing
  status: ANPRStatusValue;
  processedAt?: Date;
  ticketSuggestionId?: string;
  assignedTicketId?: string;

  // Vehicle data
  vehicleId?: string;
  contractId?: string;
  orderId?: string;
  commodity?: string;

  // Error handling
  errorMessage?: string;
  retryCount: number;

  // Metadata
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

// Entity implementation
export class ANPRRecord implements ANPRRecordEntity {
  public id: string;
  public tenantId: string;
  public licensePlate: string;
  public confidence: number;
  public confidenceLevel: ANPRConfidenceValue;
  public capturedAt: Date;
  public imageUri?: string;
  public cameraId: string;
  public gateId?: string;

  // Processing
  public status: ANPRStatusValue;
  public processedAt?: Date;
  public ticketSuggestionId?: string;
  public assignedTicketId?: string;

  // Vehicle data
  public vehicleId?: string;
  public contractId?: string;
  public orderId?: string;
  public commodity?: string;

  // Error handling
  public errorMessage?: string;
  public retryCount: number;

  // Metadata
  public createdAt: Date;
  public updatedAt: Date;
  public version: number;

  constructor(props: ANPRRecordEntity) {
    this.id = props.id;
    this.tenantId = props.tenantId;
    this.licensePlate = props.licensePlate;
    this.confidence = props.confidence;
    this.confidenceLevel = props.confidenceLevel;
    this.capturedAt = props.capturedAt;
    if (props.imageUri) this.imageUri = props.imageUri;
    this.cameraId = props.cameraId;
    if (props.gateId) this.gateId = props.gateId;

    this.status = props.status;
    if (props.processedAt) this.processedAt = props.processedAt;
    if (props.ticketSuggestionId) this.ticketSuggestionId = props.ticketSuggestionId;
    if (props.assignedTicketId) this.assignedTicketId = props.assignedTicketId;

    if (props.vehicleId) this.vehicleId = props.vehicleId;
    if (props.contractId) this.contractId = props.contractId;
    if (props.orderId) this.orderId = props.orderId;
    if (props.commodity) this.commodity = props.commodity;

    if (props.errorMessage) this.errorMessage = props.errorMessage;
    this.retryCount = props.retryCount;

    this.createdAt = props.createdAt;
    this.updatedAt = props.updatedAt;
    this.version = props.version;
  }

  // Business methods
  process(vehicleData?: {
    vehicleId?: string;
    contractId?: string;
    orderId?: string;
    commodity?: string;
  }): void {
    if (this.status !== ANPRStatus.DETECTED) {
      throw new Error('Can only process detected ANPR records');
    }

    this.status = ANPRStatus.PROCESSED;
    this.processedAt = new Date();

    if (vehicleData) {
      if (vehicleData.vehicleId) this.vehicleId = vehicleData.vehicleId;
      if (vehicleData.contractId) this.contractId = vehicleData.contractId;
      if (vehicleData.orderId) this.orderId = vehicleData.orderId;
      if (vehicleData.commodity) this.commodity = vehicleData.commodity;
    }

    this.updatedAt = new Date();
    this.version++;
  }

  assignTicket(ticketId: string): void {
    if (this.status !== ANPRStatus.PROCESSED) {
      throw new Error('Can only assign tickets to processed ANPR records');
    }

    this.status = ANPRStatus.ASSIGNED;
    this.assignedTicketId = ticketId;
    this.updatedAt = new Date();
    this.version++;
  }

  reject(reason?: string): void {
    const nonRejectableStatuses: ANPRStatusValue[] = [ANPRStatus.ASSIGNED, ANPRStatus.ERROR];
    if (nonRejectableStatuses.includes(this.status)) {
      throw new Error('Cannot reject assigned or errored ANPR records');
    }

    this.status = ANPRStatus.REJECTED;
    if (reason) this.errorMessage = reason;
    this.updatedAt = new Date();
    this.version++;
  }

  markError(errorMessage: string): void {
    this.status = ANPRStatus.ERROR;
    this.errorMessage = errorMessage;
    this.retryCount++;
    this.updatedAt = new Date();
    this.version++;
  }

  retry(): void {
    if (this.retryCount >= 3) {
      throw new Error('Maximum retry attempts exceeded');
    }

    this.status = ANPRStatus.DETECTED;
    if (this.errorMessage) delete this.errorMessage;
    this.retryCount++;
    this.updatedAt = new Date();
    this.version++;
  }

  // Status checks
  isProcessed(): boolean {
    return this.status === ANPRStatus.PROCESSED;
  }

  isAssigned(): boolean {
    return this.status === ANPRStatus.ASSIGNED;
  }

  isHighConfidence(): boolean {
    return this.confidenceLevel === ANPRConfidence.HIGH;
  }

  isMediumConfidence(): boolean {
    return this.confidenceLevel === ANPRConfidence.MEDIUM;
  }

  isLowConfidence(): boolean {
    return this.confidenceLevel === ANPRConfidence.LOW;
  }

  canBeRetried(): boolean {
    const retryableStatuses: ANPRStatusValue[] = [ANPRStatus.ERROR, ANPRStatus.REJECTED];
    return this.retryCount < 3 && retryableStatuses.includes(this.status);
  }

  // Confidence helpers
  getConfidencePercentage(): number {
    return this.confidence;
  }

  getConfidenceLevel(): ANPRConfidenceValue {
    if (this.confidence >= 90) return ANPRConfidence.HIGH;
    if (this.confidence >= 70) return ANPRConfidence.MEDIUM;
    return ANPRConfidence.LOW;
  }

  // Age helpers
  getAgeMinutes(): number {
    const now = new Date();
    return Math.round((now.getTime() - this.capturedAt.getTime()) / (1000 * 60));
  }

  isStale(maxAgeMinutes: number = 30): boolean {
    return this.getAgeMinutes() > maxAgeMinutes;
  }

  // Processing time
  getProcessingTimeSeconds(): number | null {
    if (!this.processedAt) return null;
    return Math.round((this.processedAt.getTime() - this.capturedAt.getTime()) / 1000);
  }
}