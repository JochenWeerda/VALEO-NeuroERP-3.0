/**
 * Time Entry Entity for VALEO NeuroERP 3.0 HR Domain
 * Time tracking with validation and business rules
 */

import { z } from 'zod';

export const TimeEntrySchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  employeeId: z.string().uuid(),
  date: z.string().date(),
  start: z.string().datetime(),
  end: z.string().datetime(),
  breakMinutes: z.number().int().min(0).max(480), // Max 8 hours break
  projectId: z.string().uuid().optional(),
  costCenter: z.string().optional(),
  source: z.enum(['Manual', 'Terminal', 'Mobile']),
  status: z.enum(['Draft', 'Approved', 'Rejected']),
  approvedBy: z.string().uuid().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number().int().min(1),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type TimeEntry = z.infer<typeof TimeEntrySchema>;

export class TimeEntryEntity {
  private data: TimeEntry;

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
  get source(): string { return this.data.source; }
  get status(): string { return this.data.status; }
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
    const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
    return Math.max(0, totalMinutes - this.data.breakMinutes);
  }

  getWorkingHours(): number {
    return this.getWorkingMinutes() / 60;
  }

  getOvertimeMinutes(maxDailyHours: number = 8): number {
    const maxMinutes = maxDailyHours * 60;
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

    const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
    if (this.data.breakMinutes > totalMinutes) {
      throw new Error('Break time cannot exceed total time');
    }

    // Check for reasonable working hours (max 24 hours)
    if (totalMinutes > 24 * 60) {
      throw new Error('Working time cannot exceed 24 hours');
    }
  }

  // State Changes
  approve(approvedBy: string): TimeEntryEntity {
    if (!this.canApprove()) {
      throw new Error('Time entry cannot be approved in current status');
    }

    return new TimeEntryEntity({
      ...this.data,
      status: 'Approved',
      approvedBy,
      updatedAt: new Date().toISOString(),
      updatedBy: approvedBy,
      version: this.data.version + 1
    });
  }

  reject(approvedBy: string): TimeEntryEntity {
    if (!this.canReject()) {
      throw new Error('Time entry cannot be rejected in current status');
    }

    return new TimeEntryEntity({
      ...this.data,
      status: 'Rejected',
      approvedBy,
      updatedAt: new Date().toISOString(),
      updatedBy: approvedBy,
      version: this.data.version + 1
    });
  }

  updateTimes(start: string, end: string, breakMinutes: number, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return new TimeEntryEntity({
      ...this.data,
      start,
      end,
      breakMinutes,
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  updateProject(projectId: string | undefined, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return new TimeEntryEntity({
      ...this.data,
      projectId,
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  updateCostCenter(costCenter: string | undefined, updatedBy?: string): TimeEntryEntity {
    if (!this.canEdit()) {
      throw new Error('Time entry cannot be edited in current status');
    }

    return new TimeEntryEntity({
      ...this.data,
      costCenter,
      updatedAt: new Date().toISOString(),
      updatedBy,
      version: this.data.version + 1
    });
  }

  // Export for persistence
  toJSON(): TimeEntry {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<TimeEntry, 'id' | 'createdAt' | 'updatedAt' | 'version'>): TimeEntryEntity {
    const now = new Date().toISOString();
    return new TimeEntryEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now,
      version: 1
    });
  }

  static fromJSON(data: TimeEntry): TimeEntryEntity {
    return new TimeEntryEntity(data);
  }
}

