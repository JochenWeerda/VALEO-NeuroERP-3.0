/**
 * Mobile Run Entity for VALEO NeuroERP 3.0 Production Domain
 * Mobile production unit management with calibration and cleaning
 */

import { z } from 'zod';

// Calibration Check Schema
const CalibrationCheckSchema = z.object({
  scaleOk: z.boolean(),
  moistureOk: z.boolean(),
  temperatureOk: z.boolean(),
  date: z.string().datetime(),
  validatedBy: z.string(),
  notes: z.string().optional()
});

// Cleaning Sequence Schema
const CleaningSequenceSchema = z.object({
  id: z.string().uuid(),
  type: z.enum(['DryClean', 'Vacuum', 'Flush', 'WetClean']),
  startedAt: z.string().datetime(),
  endedAt: z.string().datetime().optional(),
  usedMaterialSku: z.string().optional(),
  flushMassKg: z.number().min(0).optional(),
  validatedBy: z.string(),
  notes: z.string().optional()
});

// Main Mobile Run Schema
export const MobileRunSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  mobileUnitId: z.string().uuid(),
  vehicleId: z.string().uuid().optional(),
  operatorId: z.string().uuid(),
  site: z.object({
    customerId: z.string().uuid(),
    location: z.object({
      lat: z.number().min(-90).max(90),
      lng: z.number().min(-180).max(180),
      address: z.string().optional()
    })
  }),
  powerSource: z.enum(['Generator', 'Grid', 'Battery']).default('Generator'),
  calibrationCheck: CalibrationCheckSchema,
  startAt: z.string().datetime(),
  endAt: z.string().datetime().optional(),
  cleaningSequenceId: z.string().uuid().optional(),
  cleaningSequences: z.array(CleaningSequenceSchema).default([]),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type MobileRun = z.infer<typeof MobileRunSchema>;
export type CalibrationCheck = z.infer<typeof CalibrationCheckSchema>;
export type CleaningSequence = z.infer<typeof CleaningSequenceSchema>;

export class MobileRunEntity {
  private readonly data: MobileRun;

  constructor(data: MobileRun) {
    this.data = MobileRunSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get mobileUnitId(): string { return this.data.mobileUnitId; }
  get vehicleId(): string | undefined { return this.data.vehicleId; }
  get operatorId(): string { return this.data.operatorId; }
  get site(): MobileRun['site'] { return this.data.site; }
  get powerSource(): string { return this.data.powerSource; }
  get calibrationCheck(): CalibrationCheck { return this.data.calibrationCheck; }
  get startAt(): string { return this.data.startAt; }
  get endAt(): string | undefined { return this.data.endAt; }
  get cleaningSequenceId(): string | undefined { return this.data.cleaningSequenceId; }
  get cleaningSequences(): CleaningSequence[] { return [...this.data.cleaningSequences]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  isActive(): boolean {
    return !this.data.endAt;
  }

  isCompleted(): boolean {
    return !!this.data.endAt;
  }

  canStart(): boolean {
    return this.isCalibrationValid() && !this.isActive();
  }

  canFinish(): boolean {
    return this.isActive();
  }

  isCalibrationValid(): boolean {
    const check = this.data.calibrationCheck;
    return check.scaleOk && check.moistureOk && check.temperatureOk;
  }

  isCalibrationExpired(maxDays = 30): boolean {
    const checkDate = new Date(this.data.calibrationCheck.date);
    const now = new Date();
    const diffDays = (now.getTime() - checkDate.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > maxDays;
  }

  getDurationHours(): number {
    if (!this.data.endAt) return 0;
    
    const startTime = new Date(this.data.startAt);
    const endTime = new Date(this.data.endAt);
    
    return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
  }

  getActiveCleaningSequence(): CleaningSequence | undefined {
    return this.data.cleaningSequences.find(seq => !seq.endedAt);
  }

  getCompletedCleaningSequences(): CleaningSequence[] {
    return this.data.cleaningSequences.filter(seq => seq.endedAt);
  }

  getTotalFlushMass(): number {
    return this.data.cleaningSequences
      .filter(seq => seq.type === 'Flush' && seq.flushMassKg)
      .reduce((total, seq) => total + (seq.flushMassKg ?? 0), 0);
  }

  getCleaningHistory(): CleaningSequence[] {
    return [...this.data.cleaningSequences].sort((a, b) => 
      new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime()
    );
  }

  // Validation
  private validateBusinessRules(): void {
    // Validate calibration check date is not in the future
    const checkDate = new Date(this.data.calibrationCheck.date);
    const now = new Date();
    if (checkDate > now) {
      throw new Error('Calibration check date cannot be in the future');
    }

    // Validate time sequence
    if (this.data.endAt) {
      const startTime = new Date(this.data.startAt);
      const endTime = new Date(this.data.endAt);
      
      if (endTime <= startTime) {
        throw new Error('End time must be after start time');
      }
    }

    // Validate cleaning sequences
    for (const seq of this.data.cleaningSequences) {
      if (seq.endedAt) {
        const startTime = new Date(seq.startedAt);
        const endTime = new Date(seq.endedAt);
        
        if (endTime <= startTime) {
          throw new Error(`Cleaning sequence ${seq.type} has invalid time range`);
        }
      }
    }

    // Validate location coordinates
    const { lat, lng } = this.data.site.location;
    if (lat < -90 || lat > 90) {
      throw new Error('Invalid latitude');
    }
    if (lng < -180 || lng > 180) {
      throw new Error('Invalid longitude');
    }
  }

  // State Changes
  finish(endAt: string, updatedBy?: string): MobileRunEntity {
    if (!this.canFinish()) {
      throw new Error('Mobile run cannot be finished in current status');
    }

    return new MobileRunEntity({
      ...this.data,
      endAt,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  updateCalibrationCheck(check: CalibrationCheck, updatedBy?: string): MobileRunEntity {
    return new MobileRunEntity({
      ...this.data,
      calibrationCheck: check,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addCleaningSequence(sequence: Omit<CleaningSequence, 'id'>, updatedBy?: string): MobileRunEntity {
    const newSequence: CleaningSequence = {
      ...sequence,
      id: require('uuid').v4()
    };

    // Check for overlapping cleaning sequences
    const hasActiveSequence = this.getActiveCleaningSequence();
    if (hasActiveSequence) {
      throw new Error('Cannot start new cleaning sequence while another is active');
    }

    return new MobileRunEntity({
      ...this.data,
      cleaningSequences: [...this.data.cleaningSequences, newSequence],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  endCleaningSequence(sequenceId: string, endedAt: string, notes?: string, updatedBy?: string): MobileRunEntity {
    const sequenceIndex = this.data.cleaningSequences.findIndex(seq => seq.id === sequenceId);
    
    if (sequenceIndex === -1) {
      throw new Error('Cleaning sequence not found');
    }

    const sequence = this.data.cleaningSequences[sequenceIndex];
    if (sequence.endedAt) {
      throw new Error('Cleaning sequence is already ended');
    }

    const updatedSequence: CleaningSequence = {
      ...sequence,
      endedAt,
      notes: notes ? `${sequence.notes ?? ''}\n${notes}`.trim() : sequence.notes
    };

    const updatedSequences = [...this.data.cleaningSequences];
    updatedSequences[sequenceIndex] = updatedSequence;

    return new MobileRunEntity({
      ...this.data,
      cleaningSequences: updatedSequences,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  // Cleaning sequence validation
  validateCleaningRequired(previousRecipeMedicated: boolean, currentRecipeMedicated: boolean): boolean {
    // Medicated to non-medicated requires cleaning
    if (previousRecipeMedicated && !currentRecipeMedicated) {
      return true;
    }

    // Check if any cleaning was performed recently
    const recentCleaning = this.data.cleaningSequences.find(seq => {
      const endTime = seq.endedAt ? new Date(seq.endedAt) : new Date();
      const now = new Date();
      const diffHours = (now.getTime() - endTime.getTime()) / (1000 * 60 * 60);
      return diffHours < 24; // Cleaning within last 24 hours
    });

    return !recentCleaning;
  }

  getRequiredCleaningType(previousRecipeMedicated: boolean, currentRecipeMedicated: boolean): CleaningSequence['type'] {
    if (previousRecipeMedicated && !currentRecipeMedicated) {
      return 'WetClean'; // Full cleaning for medicated to non-medicated
    }
    
    return 'Flush'; // Basic flush for other transitions
  }

  // Export for persistence
  toJSON(): MobileRun {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<MobileRun, 'id' | 'createdAt' | 'updatedAt'>): MobileRunEntity {
    const now = new Date().toISOString();
    return new MobileRunEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: MobileRun): MobileRunEntity {
    return new MobileRunEntity(data);
  }
}

