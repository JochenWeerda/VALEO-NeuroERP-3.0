/**
 * Batch Entity for VALEO NeuroERP 3.0 Production Domain
 * Batch management with traceability and quality control
 */

import { z } from 'zod';

// Batch Input Schema
const BatchInputSchema = z.object({
  batchId: z.string().uuid(),
  ingredientLotId: z.string().uuid(),
  plannedKg: z.number().positive(),
  actualKg: z.number().positive()
});

// Batch Output Lot Schema
const BatchOutputLotSchema = z.object({
  id: z.string().uuid(),
  batchId: z.string().uuid(),
  lotNumber: z.string().min(1).max(100),
  qtyKg: z.number().positive(),
  packing: z.object({
    form: z.enum(['Bulk', 'Bag', 'Silo']),
    size: z.number().optional(),
    unit: z.string().optional()
  }),
  destination: z.enum(['Inventory', 'DirectFarm']),
  gmpPlusMarkings: z.array(z.string()).optional()
});

// Main Batch Schema
export const BatchSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  batchNumber: z.string().min(1).max(100),
  mixOrderId: z.string().uuid(),
  producedQtyKg: z.number().positive(),
  startAt: z.string().datetime(),
  endAt: z.string().datetime().optional(),
  status: z.enum(['Released', 'Quarantine', 'Rejected']).default('Quarantine'),
  parentBatches: z.array(z.string().uuid()).default([]),
  labels: z.array(z.string()).default([]),
  inputs: z.array(BatchInputSchema).default([]),
  outputs: z.array(BatchOutputLotSchema).default([]),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type Batch = z.infer<typeof BatchSchema>;
export type BatchInput = z.infer<typeof BatchInputSchema>;
export type BatchOutputLot = z.infer<typeof BatchOutputLotSchema>;

export class BatchEntity {
  private readonly data: Batch;

  constructor(data: Batch) {
    this.data = BatchSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get batchNumber(): string { return this.data.batchNumber; }
  get mixOrderId(): string { return this.data.mixOrderId; }
  get producedQtyKg(): number { return this.data.producedQtyKg; }
  get startAt(): string { return this.data.startAt; }
  get endAt(): string | undefined { return this.data.endAt; }
  get status(): string { return this.data.status; }
  get parentBatches(): string[] { return [...this.data.parentBatches]; }
  get labels(): string[] { return [...this.data.labels]; }
  get inputs(): BatchInput[] { return [...this.data.inputs]; }
  get outputs(): BatchOutputLot[] { return [...this.data.outputs]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  isReleased(): boolean {
    return this.data.status === 'Released';
  }

  isInQuarantine(): boolean {
    return this.data.status === 'Quarantine';
  }

  isRejected(): boolean {
    return this.data.status === 'Rejected';
  }

  isCompleted(): boolean {
    return !!this.data.endAt;
  }

  isInProgress(): boolean {
    return !this.data.endAt;
  }

  canRelease(): boolean {
    return this.isInQuarantine() && this.isCompleted();
  }

  canReject(): boolean {
    return !this.isRejected();
  }

  canQuarantine(): boolean {
    return this.isReleased();
  }

  isRework(): boolean {
    return this.data.parentBatches.length > 0;
  }

  hasGMPPlusMarking(): boolean {
    return this.data.outputs.some(output => output.gmpPlusMarkings && output.gmpPlusMarkings.length > 0);
  }

  getTotalInputKg(): number {
    return this.data.inputs.reduce((total, input) => total + input.actualKg, 0);
  }

  getTotalOutputKg(): number {
    return this.data.outputs.reduce((total, output) => total + output.qtyKg, 0);
  }

  getYield(): number {
    const inputKg = this.getTotalInputKg();
    const outputKg = this.getTotalOutputKg();
    return inputKg > 0 ? (outputKg / inputKg) * 100 : 0;
  }

  getDurationHours(): number {
    if (!this.data.endAt) return 0;
    
    const startTime = new Date(this.data.startAt);
    const endTime = new Date(this.data.endAt);
    
    return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
  }

  getIngredientLotIds(): string[] {
    return this.data.inputs.map(input => input.ingredientLotId);
  }

  getOutputLotNumbers(): string[] {
    return this.data.outputs.map(output => output.lotNumber);
  }

  // Validation
  private validateBusinessRules(): void {
    // Validate batch number format (should be unique within tenant)
    if (!this.data.batchNumber.match(/^[A-Z0-9-_]+$/)) {
      throw new Error('Batch number must contain only uppercase letters, numbers, hyphens and underscores');
    }

    // Validate time sequence
    if (this.data.endAt) {
      const startTime = new Date(this.data.startAt);
      const endTime = new Date(this.data.endAt);
      
      if (endTime <= startTime) {
        throw new Error('End time must be after start time');
      }
    }

    // Validate inputs
    for (const input of this.data.inputs) {
      if (input.actualKg <= 0) {
        throw new Error('Actual input quantity must be positive');
      }
    }

    // Validate outputs
    for (const output of this.data.outputs) {
      if (output.qtyKg <= 0) {
        throw new Error('Output quantity must be positive');
      }
    }

    // Validate mass balance (allow some tolerance)
    const inputKg = this.getTotalInputKg();
    const outputKg = this.getTotalOutputKg();
    const tolerance = 0.05; // 5% tolerance
    
    if (outputKg > inputKg * (1 + tolerance)) {
      throw new Error('Output quantity exceeds input quantity beyond acceptable tolerance');
    }
  }

  // State Changes
  release(updatedBy?: string): BatchEntity {
    if (!this.canRelease()) {
      throw new Error('Batch cannot be released in current status');
    }

    return new BatchEntity({
      ...this.data,
      status: 'Released',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  reject(reason?: string, updatedBy?: string): BatchEntity {
    if (!this.canReject()) {
      throw new Error('Batch cannot be rejected in current status');
    }

    const notes = reason ? `REJECTED: ${reason}` : 'REJECTED';
    const updatedLabels = [...this.data.labels, notes];

    return new BatchEntity({
      ...this.data,
      status: 'Rejected',
      labels: updatedLabels,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  quarantine(reason?: string, updatedBy?: string): BatchEntity {
    if (!this.canQuarantine()) {
      throw new Error('Batch cannot be quarantined in current status');
    }

    const notes = reason ? `QUARANTINED: ${reason}` : 'QUARANTINED';
    const updatedLabels = [...this.data.labels, notes];

    return new BatchEntity({
      ...this.data,
      status: 'Quarantine',
      labels: updatedLabels,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  complete(endAt: string, updatedBy?: string): BatchEntity {
    if (this.isCompleted()) {
      throw new Error('Batch is already completed');
    }

    return new BatchEntity({
      ...this.data,
      endAt,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addInput(input: BatchInput, updatedBy?: string): BatchEntity {
    // Check for duplicate ingredient lots
    const existingLotIds = this.data.inputs.map(i => i.ingredientLotId);
    if (existingLotIds.includes(input.ingredientLotId)) {
      throw new Error('Ingredient lot already added to batch');
    }

    return new BatchEntity({
      ...this.data,
      inputs: [...this.data.inputs, input],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addOutput(output: BatchOutputLot, updatedBy?: string): BatchEntity {
    // Check for duplicate lot numbers
    const existingLotNumbers = this.data.outputs.map(o => o.lotNumber);
    if (existingLotNumbers.includes(output.lotNumber)) {
      throw new Error('Lot number already exists in batch');
    }

    return new BatchEntity({
      ...this.data,
      outputs: [...this.data.outputs, output],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addLabel(label: string, updatedBy?: string): BatchEntity {
    if (this.data.labels.includes(label)) {
      return this; // Label already exists
    }

    return new BatchEntity({
      ...this.data,
      labels: [...this.data.labels, label],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  removeLabel(label: string, updatedBy?: string): BatchEntity {
    return new BatchEntity({
      ...this.data,
      labels: this.data.labels.filter(l => l !== label),
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  addParentBatch(parentBatchId: string, updatedBy?: string): BatchEntity {
    if (this.data.parentBatches.includes(parentBatchId)) {
      return this; // Parent batch already exists
    }

    return new BatchEntity({
      ...this.data,
      parentBatches: [...this.data.parentBatches, parentBatchId],
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  // Traceability methods
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  getTraceabilityData(): any {
    return {
      batchId: this.data.id,
      batchNumber: this.data.batchNumber,
      mixOrderId: this.data.mixOrderId,
      status: this.data.status,
      startAt: this.data.startAt,
      endAt: this.data.endAt,
      inputs: this.data.inputs.map(input => ({
        ingredientLotId: input.ingredientLotId,
        plannedKg: input.plannedKg,
        actualKg: input.actualKg
      })),
      outputs: this.data.outputs.map(output => ({
        lotNumber: output.lotNumber,
        qtyKg: output.qtyKg,
        destination: output.destination,
        packing: output.packing
      })),
      parentBatches: this.data.parentBatches,
      labels: this.data.labels
    };
  }

  // Export for persistence
  toJSON(): Batch {
    return { ...this.data };
  }

  // Factory methods
  static create(data: Omit<Batch, 'id' | 'createdAt' | 'updatedAt'>): BatchEntity {
    const now = new Date().toISOString();
    return new BatchEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: Batch): BatchEntity {
    return new BatchEntity(data);
  }
}

