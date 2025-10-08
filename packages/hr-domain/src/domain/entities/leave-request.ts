/**
 * Leave Request Entity for VALEO NeuroERP 3.0 HR Domain
 * Vacation, sick leave, and other absence management
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MILLISECONDS_PER_DAY = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;
const MAX_LEAVE_DURATION_DAYS = 365;
const INCLUSIVE_DAY_OFFSET = 1;
const DAY_TOLERANCE = 1;
const INITIAL_VERSION = 1;

const leaveTypeSchema = z.enum(['Vacation', 'Sick', 'Unpaid', 'Other']);
const leaveStatusSchema = z.enum(['Pending', 'Approved', 'Rejected']);

export const LeaveRequestSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  employeeId: z.string().uuid(),
  type: leaveTypeSchema,
  from: z.string().date(),
  to: z.string().date(),
  days: z.number().positive(),
  status: leaveStatusSchema,
  approvedBy: z.string().uuid().optional(),
  note: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number().int().min(1),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type LeaveRequest = z.infer<typeof LeaveRequestSchema>;
export type LeaveType = z.infer<typeof leaveTypeSchema>;
export type LeaveStatus = z.infer<typeof leaveStatusSchema>;

export class LeaveRequestEntity {
  private readonly data: LeaveRequest;

  constructor(data: LeaveRequest) {
    this.data = LeaveRequestSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get employeeId(): string { return this.data.employeeId; }
  get type(): LeaveType { return this.data.type; }
  get from(): string { return this.data.from; }
  get to(): string { return this.data.to; }
  get days(): number { return this.data.days; }
  get status(): LeaveStatus { return this.data.status; }
  get approvedBy(): string | undefined { return this.data.approvedBy; }
  get note(): string | undefined { return this.data.note; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }
  get version(): number { return this.data.version; }

  // Business Methods
  isPending(): boolean {
    return this.data.status === 'Pending';
  }

  isApproved(): boolean {
    return this.data.status === 'Approved';
  }

  isRejected(): boolean {
    return this.data.status === 'Rejected';
  }

  canEdit(): boolean {
    return this.isPending();
  }

  canApprove(): boolean {
    return this.isPending();
  }

  canReject(): boolean {
    return this.isPending();
  }

  isVacation(): boolean {
    return this.data.type === 'Vacation';
  }

  isSickLeave(): boolean {
    return this.data.type === 'Sick';
  }

  isUnpaid(): boolean {
    return this.data.type === 'Unpaid';
  }

  getDurationInDays(): number {
    const fromDate = new Date(this.data.from);
    const toDate = new Date(this.data.to);
    const diffTime = Math.abs(toDate.getTime() - fromDate.getTime());
    return Math.ceil(diffTime / MILLISECONDS_PER_DAY) + INCLUSIVE_DAY_OFFSET; // include start and end days
  }

  isInPeriod(date: string): boolean {
    return date >= this.data.from && date <= this.data.to;
  }

  overlapsWith(other: LeaveRequestEntity): boolean {
    return this.isInPeriod(other.from) || 
           this.isInPeriod(other.to) || 
           other.isInPeriod(this.from) || 
           other.isInPeriod(this.to);
  }

  // Validation
  private validateBusinessRules(): void {
    const fromDate = new Date(this.data.from);
    const toDate = new Date(this.data.to);

    if (toDate < fromDate) {
      throw new Error('End date must be after or equal to start date');
    }

    if (this.data.days <= 0) {
      throw new Error('Days must be positive');
    }

    if (this.data.days > MAX_LEAVE_DURATION_DAYS) {
      throw new Error('Leave duration cannot exceed 365 days');
    }

    const actualDays = this.getDurationInDays();
    if (Math.abs(this.data.days - actualDays) > DAY_TOLERANCE) {
      throw new Error('Declared days must match the date range');
    }
  }

  // State Changes
  approve(approvedBy: string, note?: string): LeaveRequestEntity {
    if (!this.canApprove()) {
      throw new Error('Leave request cannot be approved in current status');
    }

    return this.clone({
      status: 'Approved',
      approvedBy,
      note: note ?? this.data.note,
      updatedBy: approvedBy
    });
  }

  reject(approvedBy: string, note?: string): LeaveRequestEntity {
    if (!this.canReject()) {
      throw new Error('Leave request cannot be rejected in current status');
    }

    return this.clone({
      status: 'Rejected',
      approvedBy,
      note: note ?? this.data.note,
      updatedBy: approvedBy
    });
  }

  updateNote(note: string | undefined, updatedBy?: string): LeaveRequestEntity {
    if (!this.canEdit()) {
      throw new Error('Leave request cannot be edited in current status');
    }

    return this.clone({ note, updatedBy });
  }

  updateDates(from: string, to: string, days: number, updatedBy?: string): LeaveRequestEntity {
    if (!this.canEdit()) {
      throw new Error('Leave request cannot be edited in current status');
    }

    return this.clone({
      from,
      to,
      days,
      updatedBy
    });
  }

  // Export for persistence
  toJSON(): LeaveRequest {
    return { ...this.data };
  }

  private clone(overrides: Partial<LeaveRequest>): LeaveRequestEntity {
    const now = new Date().toISOString();
    return new LeaveRequestEntity({
      ...this.data,
      ...overrides,
      updatedAt: now,
      version: this.data.version + 1
    });
  }

  // Factory methods
  static create(data: Omit<LeaveRequest, 'id' | 'createdAt' | 'updatedAt' | 'version'>): LeaveRequestEntity {
    const now = new Date().toISOString();
    return new LeaveRequestEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now,
      version: INITIAL_VERSION
    });
  }

  static fromJSON(data: LeaveRequest): LeaveRequestEntity {
    return new LeaveRequestEntity(data);
  }
}

