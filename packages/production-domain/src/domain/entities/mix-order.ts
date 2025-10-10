/**
 * Mix Order Entity for VALEO NeuroERP 3.0 Production Domain
 * Mix order management for both plant and mobile production
 */

import { z } from 'zod';

// Location Schema
const LocationSchema = z.object({
  lat: z.number().min(-90).max(90),
  lng: z.number().min(-180).max(180),
  address: z.string().optional()
});

// Mix Step Schema (runtime data)
const MixStepSchema = z.object({
  type: z.enum(['weigh', 'dose', 'grind', 'mix', 'flushing', 'transfer']),
  startedAt: z.string().datetime(),
  endedAt: z.string().datetime().optional(),
  equipmentId: z.string().optional(),
  actuals: z.object({
    massKg: z.number().min(0).optional(),
    timeSec: z.number().min(0).optional(),
    energyKWh: z.number().min(0).optional(),
    moisturePercent: z.number().min(0).max(100).optional()
  }).optional()
});

// Main Mix Order Schema
export const MixOrderSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  orderNumber: z.string().min(1).max(100),
  type: z.enum(['Plant', 'Mobile']),
  recipeId: z.string().uuid(),
  targetQtyKg: z.number().positive(),
  plannedAt: z.string().datetime(),
  location: LocationSchema.optional(),
  customerId: z.string().uuid().optional(),
  mobileUnitId: z.string().uuid().optional(),
  status: z.enum(['Draft', 'Staged', 'Running', 'Hold', 'Completed', 'Aborted']).default('Draft'),
  notes: z.string().optional(),
  steps: z.array(MixStepSchema).default([]),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type MixOrder = z.infer<typeof MixOrderSchema>;
export type Location = z.infer<typeof LocationSchema>;
export type MixStep = z.infer<typeof MixStepSchema>;

export class MixOrderEntity {
  private readonly data: MixOrder;

  constructor(data: MixOrder) {
    this.data = MixOrderSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get orderNumber(): string { return this.data.orderNumber; }
  get type(): string { return this.data.type; }
  get recipeId(): string { return this.data.recipeId; }
  get targetQtyKg(): number { return this.data.targetQtyKg; }
  get plannedAt(): string { return this.data.plannedAt; }
  get location(): Location | undefined { return this.data.location; }
  get customerId(): string | undefined { return this.data.customerId; }
  get mobileUnitId(): string | undefined { return this.data.mobileUnitId; }
  get status(): string { return this.data.status; }
  get notes(): string | undefined { return this.data.notes; }
  get steps(): MixStep[] { return [...this.data.steps]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  isDraft(): boolean {
    return this.data.status === 'Draft';
  }

  isStaged(): boolean {
    return this.data.status === 'Staged';
  }

  isRunning(): boolean {
    return this.data.status === 'Running';
  }

  isOnHold(): boolean {
    return this.data.status === 'Hold';
  }

  isCompleted(): boolean {
    return this.data.status === 'Completed';
  }

  isAborted(): boolean {
    return this.data.status === 'Aborted';
  }

  isMobile(): boolean {
    return this.data.type === 'Mobile';
  }

  isPlant(): boolean {
    return this.data.type === 'Plant';
  }

  canStart(): boolean {
    return this.isStaged();
  }

  canStage(): boolean {
    return this.isDraft();
  }

  canHold(): boolean {
    return this.isRunning() || this.isStaged();
  }

  canComplete(): boolean {
    return this.isRunning();
  }

  canAbort(): boolean {
    return !this.isCompleted() && !this.isAborted();
  }

  getDurationMinutes(): number {
    if (this.data.steps.length === 0) return 0;
    
    const startTime = new Date(this.data.steps[0].startedAt);
    const lastStep = this.data.steps[this.data.steps.length - 1];
    const endTime = lastStep.endedAt ? new Date(lastStep.endedAt) : new Date();
    
    return Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
  }

  getTotalMassProcessed(): number {
    return this.data.steps.reduce((total, step) => {
      return total + (step.actuals?.massKg ?? 0);
    }, 0);
  }

  getTotalEnergyConsumed(): number {
    return this.data.steps.reduce((total, step) => {
      return total + (step.actuals?.energyKWh ?? 0);
    }, 0);
  }

  getActiveSteps(): MixStep[] {
    return this.data.steps.filter(step => !step.endedAt);
  }

  getCompletedSteps(): MixStep[] {
    return this.data.steps.filter(step => step.endedAt);
  }

  // Validation
  private validateBusinessRules(): void {
    // Mobile orders must have location
    if (this.isMobile() && !this.data.location) {
      throw new Error('Mobile mix orders must have location');
    }

    // Mobile orders must have mobileUnitId
    if (this.isMobile() && !this.data.mobileUnitId) {
      throw new Error('Mobile mix orders must have mobileUnitId');
    }

    // Customer orders should have customerId
    if (this.data.customerId && !this.data.customerId.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
      throw new Error('Invalid customerId format');
    }

    // Validate step sequence
    const stepsWithEndTime = this.data.steps.filter(step => step.endedAt);
    for (const step of stepsWithEndTime) {
      const startTime = new Date(step.startedAt);
      if (step.endedAt === undefined || step.endedAt === null) continue;
      const endTime = new Date(step.endedAt);
      
      if (endTime <= startTime) {
        throw new Error(`Step ${step.type} has invalid time range`);
      }
    }
  }

  // State Changes
  stage(updatedBy?: string): MixOrderEntity {
    if (!this.canStage()) {
      throw new Error('Mix order cannot be staged in current status');
    }

    return new MixOrderEntity({
      ...this.data,
      status: 'Staged',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  start(updatedBy?: string): MixOrderEntity {
    if (!this.canStart()) {
      throw new Error('Mix order cannot be started in current status');
    }

    return new MixOrderEntity({
      ...this.data,
      status: 'Running',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  hold(reason?: string, updatedBy?: string): MixOrderEntity {
    if (!this.canHold()) {
      throw new Error('Mix order cannot be put on hold in current status');
    }

    const notes = reason ? `${this.data.notes ?? ''}\n[HOLD] ${reason}`.trim() : this.data.notes;

    return new MixOrderEntity({
      ...this.data,
      status: 'Hold',
      notes,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  complete(updatedBy?: string): MixOrderEntity {
    if (!this.canComplete()) {
      throw new Error('Mix order cannot be completed in current status');
    }

    return new MixOrderEntity({
      ...this.data,
      status: 'Completed',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  abort(reason?: string, updatedBy?: string): MixOrderEntity {
    if (!this.canAbort()) {
      throw new Error('Mix order cannot be aborted in current status');
    }

    const notes = reason ? `${this.data.notes ?? ''}\n[ABORTED] ${reason}`.trim() : this.data.notes;

    return new MixOrderEntity({
      ...this.data,
      status: 'Aborted',
      notes,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addStep(step: MixStep, updatedBy?: string): MixOrderEntity {
    // Validate step sequence
    if (this.data.steps.length > 0) {
      const lastStep = this.data.steps[this.data.steps.length - 1];
      if (!lastStep.endedAt) {
        throw new Error('Cannot add new step while previous step is still running');
      }
    }

    return new MixOrderEntity({
      ...this.data,
      steps: [...this.data.steps, step],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  updateStep(stepIndex: number, updates: Partial<MixStep>, updatedBy?: string): MixOrderEntity {
    if (stepIndex < 0 || stepIndex >= this.data.steps.length) {
      throw new Error('Invalid step index');
    }

    const updatedSteps = [...this.data.steps];
    updatedSteps[stepIndex] = { ...updatedSteps[stepIndex], ...updates };

    return new MixOrderEntity({
      ...this.data,
      steps: updatedSteps,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  endStep(stepIndex: number, endedAt: string, actuals?: MixStep['actuals'], updatedBy?: string): MixOrderEntity {
    if (stepIndex < 0 || stepIndex >= this.data.steps.length) {
      throw new Error('Invalid step index');
    }

    const step = this.data.steps[stepIndex];
    if (step.endedAt) {
      throw new Error('Step is already ended');
    }

    const updatedStep: MixStep = {
      ...step,
      endedAt,
      actuals: actuals ? { ...step.actuals, ...actuals } : step.actuals
    };

    return this.updateStep(stepIndex, updatedStep, updatedBy);
  }

  // Export for persistence
  toJSON(): MixOrder {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<MixOrder, 'id' | 'createdAt' | 'updatedAt'>): MixOrderEntity {
    const now = new Date().toISOString();
    return new MixOrderEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: MixOrder): MixOrderEntity {
    return new MixOrderEntity(data);
  }
}

