/**
 * Time Entry Entity for VALEO NeuroERP 3.0 HR Domain
 * Time tracking with validation and business rules
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const MAX_BREAK_MINUTES = 480;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MILLISECONDS_PER_MINUTE = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE;
const MINUTES_PER_DAY = HOURS_PER_DAY * MINUTES_PER_HOUR;
const DEFAULT_MAX_DAILY_HOURS = 8;
const INITIAL_VERSION = 1;

const timeEntrySourceSchema = z.enum(['Manual', 'Terminal', 'Mobile']);
const timeEntryStatusSchema = z.enum(['Draft', 'Approved', 'Rejected']);

export const TimeEntrySchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  employeeId: z.string().uuid(),
  date: z.string().date(),
  start: z.string().datetime(),
  end: z.string().datetime(),
  breakMinutes: z.number().int().min(0).max(MAX_BREAK_MINUTES), // Max 8 hours break
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional(),
  source: timeEntrySourceSchema,
  status: timeEntryStatusSchema,
  approvedBy: z.string().uuid().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number().int().min(INITIAL_VERSION),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type TimeEntry = z.infer<typeof TimeEntrySchema>;
export type TimeEntrySource = z.infer<typeof timeEntrySourceSchema>;
export type TimeEntryStatus = z.infer<typeof timeEntryStatusSchema>;

export class TimeEntryEntity {
  private readonly data: TimeEntry;

  constructor(data: TimeEntry) {
    this.data = TimeEntrySchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get employeeId(): string { return this.data.employeeId; }
  get date(): string { return this.data.date; }
  get start(): string { return this.data.start; }
  get end(): string { return this.data.end; }
  get breakMinutes(): number { return this.data.breakMinutes; }
  get projectId(): string | undefined { return this.data.projectId; }
  get costCenter(): string | undefined { return this.data.costCenter; }
  get source(): TimeEntrySource { return this.data.source; }
  get status(): TimeEntryStatus { return this.data.status; }
  get approvedBy(): string | undefined { return this.data.approvedBy; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }
  get version(): number { return this.data.version; }

  // Business Methods
  isDraft(): boolean {
    return this.data.status === 'Draft';
  }

  isApproved(): boolean {
    return this.data.status === 'Approved';
  }

  isRejected(): boolean {
    return this.data.status === 'Rejected';
  }

  canEdit(): boolean {
    return this.isDraft();
  }

  canApprove(): boolean {
    return this.isDraft();
  }

  canReject(): boolean {
    return this.isDraft();
  }

  getWorkingMinutes(): number {
    const startTime = new Date(this.data.start);
    const endTime = new Date(this.data.end);
    const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_MINUTE);
    return Math.max(0, totalMinutes - this.data.breakMinutes);
  }

  getWorkingHours(): number {
    return this.getWorkingMinutes() / MINUTES_PER_HOUR;
  }

  getOvertimeMinutes(maxDailyHours = DEFAULT_MAX_DAILY_HOURS): number {
    const maxMinutes = maxDailyHours * MINUTES_PER_HOUR;
    const workingMinutes = this.getWorkingMinutes();
    return Math.max(0, workingMinutes - maxMinutes);
  }

  // Validation
  private validateBusinessRules(): void {
    const startTime = new Date(this.data.start);
    const endTime = new Date(this.data.end);

    if (endTime <= startTime) {
      throw new Error('End time must be after start time');
    }

    const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_MINUTE);
    if (this.data.breakMinutes > totalMinutes) {
      throw new Error('Break time cannot exceed total time');
    }

    // Check for reasonable working hours (max 24 hours)
    if (totalMinutes > MINUTES_PER_DAY) {
      throw new Error('Working time cannot exceed 24 hours');
    }
  }

  // State Changes
  approve(approvedBy: string): TimeEntryEntity {
    if (!this.canApprove()) {
      throw new Error('Time entry cannot be approved in current status');
    }

    return this.clone({
      status: 'Approved',
      approvedBy,
      updatedBy: approvedBy
    });
  }

  reject(approvedBy: string): TimeEntryEntity {
    if (!this.canReject()) {
      throw new Error('Time entry cannot be rejected in current status');
    }

    return this.clone({
      status: 'Rejected',
      approvedBy,
      updatedBy: approvedBy
    });
  }

  updateTimes(start: string, end: string, breakMinutes: number, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return this.clone({
      start,
      end,
      breakMinutes,
      updatedBy
    });
  }

  updateProject(projectId: string | undefined, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return this.clone({ projectId, updatedBy });
  }

  updateCostCenter(costCenter: string | undefined, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return this.clone({ costCenter, updatedBy });
  }

  // Export for persistence
  toJSON(): TimeEntry {
    return { ...this.data };
  }

  private clone(overrides: Partial<TimeEntry>): TimeEntryEntity {
    const now = new Date().toISOString();
    return new TimeEntryEntity({
      ...this.data,
      ...overrides,
      updatedAt: now,
      version: this.data.version + 1
    });
  }

  // Factory methods
  static create(data: Omit<TimeEntry, 'id' | 'createdAt' | 'updatedAt' | 'version'>): TimeEntryEntity {
    const now = new Date().toISOString();
    return new TimeEntryEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now,
      version: INITIAL_VERSION
    });
  }

  static fromJSON(data: TimeEntry): TimeEntryEntity {
    return new TimeEntryEntity(data);
  }
}

