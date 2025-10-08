/**
 * Shift Entity for VALEO NeuroERP 3.0 HR Domain
 * Shift planning and scheduling
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const SHIFT_NAME_MIN_LENGTH = 1;
const SHIFT_NAME_MAX_LENGTH = 200;
const MIN_REQUIRED_HEADCOUNT = 1;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const MILLISECONDS_PER_HOUR = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
const MAX_SHIFT_DURATION_HOURS = 24;
const MIN_SHIFT_DURATION_HOURS = 0.5;

export const ShiftSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  name: z.string().min(SHIFT_NAME_MIN_LENGTH).max(SHIFT_NAME_MAX_LENGTH),
  location: z.string().optional(),
  startsAt: z.string().datetime(),
  endsAt: z.string().datetime(),
  requiredHeadcount: z.number().int().min(MIN_REQUIRED_HEADCOUNT),
  assigned: z.array(z.string().uuid()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Shift = z.infer<typeof ShiftSchema>;

export class ShiftEntity {
  private readonly data: Shift;

  constructor(data: Shift) {
    this.data = ShiftSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get name(): string { return this.data.name; }
  get location(): string | undefined { return this.data.location; }
  get startsAt(): string { return this.data.startsAt; }
  get endsAt(): string { return this.data.endsAt; }
  get requiredHeadcount(): number { return this.data.requiredHeadcount; }
  get assigned(): string[] { return [...this.data.assigned]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  getDurationHours(): number {
    const startTime = new Date(this.data.startsAt);
    const endTime = new Date(this.data.endsAt);
    return (endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_HOUR;
  }

  getAssignedCount(): number {
    return this.data.assigned.length;
  }

  isFullyStaffed(): boolean {
    return this.getAssignedCount() >= this.data.requiredHeadcount;
  }

  isOverStaffed(): boolean {
    return this.getAssignedCount() > this.data.requiredHeadcount;
  }

  isUnderStaffed(): boolean {
    return this.getAssignedCount() < this.data.requiredHeadcount;
  }

  hasEmployee(employeeId: string): boolean {
    return this.data.assigned.includes(employeeId);
  }

  canAssignEmployee(employeeId: string): boolean {
    return !this.hasEmployee(employeeId);
  }

  getStaffingRatio(): number {
    return this.getAssignedCount() / this.data.requiredHeadcount;
  }

  // Validation
  private validateBusinessRules(): void {
    const startTime = new Date(this.data.startsAt);
    const endTime = new Date(this.data.endsAt);

    if (endTime <= startTime) {
      throw new Error('End time must be after start time');
    }

    if (this.data.requiredHeadcount < MIN_REQUIRED_HEADCOUNT) {
      throw new Error('Required headcount must be at least 1');
    }

    const durationHours = this.getDurationHours();
    if (durationHours > MAX_SHIFT_DURATION_HOURS) {
      throw new Error('Shift duration cannot exceed 24 hours');
    }

    if (durationHours < MIN_SHIFT_DURATION_HOURS) {
      throw new Error('Shift duration must be at least 30 minutes');
    }
  }

  // State Changes
  assignEmployee(employeeId: string, updatedBy?: string): ShiftEntity {
    if (!this.canAssignEmployee(employeeId)) {
      throw new Error('Employee is already assigned to this shift');
    }

    return this.clone({
      assigned: [...this.data.assigned, employeeId],
      updatedBy
    });
  }

  unassignEmployee(employeeId: string, updatedBy?: string): ShiftEntity {
    if (!this.hasEmployee(employeeId)) {
      throw new Error('Employee is not assigned to this shift');
    }

    return this.clone({
      assigned: this.data.assigned.filter(id => id !== employeeId),
      updatedBy
    });
  }

  updateRequiredHeadcount(headcount: number, updatedBy?: string): ShiftEntity {
    if (headcount < 1) {
      throw new Error('Required headcount must be at least 1');
    }

    return this.clone({
      requiredHeadcount: headcount,
      updatedBy
    });
  }

  updateLocation(location: string | undefined, updatedBy?: string): ShiftEntity {
    return this.clone({
      location,
      updatedBy
    });
  }

  updateTimes(startsAt: string, endsAt: string, updatedBy?: string): ShiftEntity {
    return this.clone({
      startsAt,
      endsAt,
      updatedBy
    });
  }

  // Export for persistence
  toJSON(): Shift {
    return { ...this.data };
  }

  private clone(overrides: Partial<Shift>): ShiftEntity {
    const now = new Date().toISOString();
    return new ShiftEntity({
      ...this.data,
      ...overrides,
      updatedAt: now
    });
  }

  // Factory methods
  static create(data: Omit<Shift, 'id' | 'createdAt' | 'updatedAt'>): ShiftEntity {
    const now = new Date().toISOString();
    return new ShiftEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: Shift): ShiftEntity {
    return new ShiftEntity(data);
  }
}
