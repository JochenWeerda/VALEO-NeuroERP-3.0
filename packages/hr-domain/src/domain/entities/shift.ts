/**
 * Shift Entity for VALEO NeuroERP 3.0 HR Domain
 * Shift planning and scheduling
 */

import { z } from 'zod';

export const ShiftSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  name: z.string().min(1).max(200),
  location: z.string().optional(),
  startsAt: z.string().datetime(),
  endsAt: z.string().datetime(),
  requiredHeadcount: z.number().int().min(1),
  assigned: z.array(z.string().uuid()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Shift = z.infer<typeof ShiftSchema>;

export class ShiftEntity {
  private data: Shift;

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
    return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
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

    if (this.data.requiredHeadcount < 1) {
      throw new Error('Required headcount must be at least 1');
    }

    // Check for reasonable shift duration (max 24 hours)
    const durationHours = this.getDurationHours();
    if (durationHours > 24) {
      throw new Error('Shift duration cannot exceed 24 hours');
    }

    if (durationHours < 0.5) {
      throw new Error('Shift duration must be at least 30 minutes');
    }
  }

  // State Changes
  assignEmployee(employeeId: string, updatedBy?: string): ShiftEntity {
    if (!this.canAssignEmployee(employeeId)) {
      throw new Error('Employee is already assigned to this shift');
    }

    return new ShiftEntity({
      ...this.data,
      assigned: [...this.data.assigned, employeeId],
      updatedAt: new Date().toISOString(),
      updatedBy,
      // version: (this.data as any).version ? (this.data as any).version + 1 : 1
    });
  }

  unassignEmployee(employeeId: string, updatedBy?: string): ShiftEntity {
    if (!this.hasEmployee(employeeId)) {
      throw new Error('Employee is not assigned to this shift');
    }

    return new ShiftEntity({
      ...this.data,
      assigned: this.data.assigned.filter(id => id !== employeeId),
      updatedAt: new Date().toISOString(),
      updatedBy,
      // version: (this.data as any).version ? (this.data as any).version + 1 : 1
    });
  }

  updateRequiredHeadcount(headcount: number, updatedBy?: string): ShiftEntity {
    if (headcount < 1) {
      throw new Error('Required headcount must be at least 1');
    }

    return new ShiftEntity({
      ...this.data,
      requiredHeadcount: headcount,
      updatedAt: new Date().toISOString(),
      updatedBy,
      // version: (this.data as any).version ? (this.data as any).version + 1 : 1
    });
  }

  updateLocation(location: string | undefined, updatedBy?: string): ShiftEntity {
    return new ShiftEntity({
      ...this.data,
      location,
      updatedAt: new Date().toISOString(),
      updatedBy,
      // version: (this.data as any).version ? (this.data as any).version + 1 : 1
    });
  }

  updateTimes(startsAt: string, endsAt: string, updatedBy?: string): ShiftEntity {
    return new ShiftEntity({
      ...this.data,
      startsAt,
      endsAt,
      updatedAt: new Date().toISOString(),
      updatedBy,
      // version: (this.data as any).version ? (this.data as any).version + 1 : 1
    });
  }

  // Export for persistence
  toJSON(): Shift {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<Shift, 'id' | 'createdAt' | 'updatedAt'>): ShiftEntity {
    const now = new Date().toISOString();
    return new ShiftEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: Shift): ShiftEntity {
    return new ShiftEntity(data);
  }
}
