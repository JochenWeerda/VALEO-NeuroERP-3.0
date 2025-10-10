/**
 * Quality Entities for VALEO NeuroERP 3.0 Production Domain
 * Quality management with sampling, testing, and non-conformity handling
 */

import { z } from 'zod';

// Sampling Plan Schema
export const SamplingPlanSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  name: z.string().min(1).max(200),
  for: z.enum(['mobile', 'plant']),
  frequency: z.enum(['perBatch', 'perN']),
  frequencyValue: z.number().int().positive().optional(), // For perN frequency
  retainedSamples: z.boolean().default(false),
  targetAnalytes: z.array(z.string()).min(1),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

// Sampling Result Schema
export const SamplingResultSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  batchId: z.string().uuid(),
  sampleCode: z.string().min(1).max(100),
  takenAt: z.string().datetime(),
  labId: z.string().uuid().optional(),
  analyte: z.string().min(1).max(100),
  value: z.number(),
  unit: z.string().min(1).max(20),
  limitType: z.enum(['Action', 'Reject']),
  decision: z.enum(['Pass', 'Investigate', 'Reject']),
  docUri: z.string().url().optional(),
  notes: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

// Retained Sample Schema
export const RetainedSampleSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  batchId: z.string().uuid(),
  sampleCode: z.string().min(1).max(100),
  storageLoc: z.string().min(1).max(200),
  expiryAt: z.string().datetime(),
  disposedAt: z.string().datetime().optional(),
  notes: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

// Non-Conformity Schema
export const NonConformitySchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  refType: z.enum(['batchId', 'mixOrderId', 'mobileRunId']),
  refId: z.string().uuid(),
  type: z.enum(['Contamination', 'SpecOut', 'Equipment', 'Process']),
  severity: z.enum(['Low', 'Medium', 'High', 'Critical']),
  description: z.string().min(1).max(1000),
  action: z.enum(['Block', 'Rework', 'Dispose']),
  capaId: z.string().uuid().optional(),
  status: z.enum(['Open', 'InProgress', 'Closed']).default('Open'),
  discoveredAt: z.string().datetime(),
  closedAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

// CAPA Schema
export const CAPASchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  ncId: z.string().uuid().optional(),
  title: z.string().min(1).max(200),
  description: z.string().min(1).max(2000),
  type: z.enum(['Correction', 'CorrectiveAction', 'PreventiveAction']),
  priority: z.enum(['Low', 'Medium', 'High', 'Critical']),
  status: z.enum(['Open', 'InProgress', 'Closed']).default('Open'),
  assignedTo: z.string().uuid().optional(),
  dueDate: z.string().datetime().optional(),
  closedAt: z.string().datetime().optional(),
  effectiveness: z.enum(['Effective', 'NotEffective', 'NotEvaluated']).optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type SamplingPlan = z.infer<typeof SamplingPlanSchema>;
export type SamplingResult = z.infer<typeof SamplingResultSchema>;
export type RetainedSample = z.infer<typeof RetainedSampleSchema>;
export type NonConformity = z.infer<typeof NonConformitySchema>;
export type CAPA = z.infer<typeof CAPASchema>;

// Sampling Plan Entity
export class SamplingPlanEntity {
  private readonly data: SamplingPlan;

  constructor(data: SamplingPlan) {
    this.data = SamplingPlanSchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get name(): string { return this.data.name; }
  get for(): string { return this.data.for; }
  get frequency(): string { return this.data.frequency; }
  get frequencyValue(): number | undefined { return this.data.frequencyValue; }
  get retainedSamples(): boolean { return this.data.retainedSamples; }
  get targetAnalytes(): string[] { return [...this.data.targetAnalytes]; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  private validateBusinessRules(): void {
    if (this.data.frequency === 'perN' && !this.data.frequencyValue) {
      throw new Error('Frequency value is required for perN frequency');
    }
  }

  isForMobile(): boolean {
    return this.data.for === 'mobile';
  }

  isForPlant(): boolean {
    return this.data.for === 'plant';
  }

  shouldSampleBatch(batchNumber: number): boolean {
    if (this.data.frequency === 'perBatch') {
      return true;
    }
    
    if (this.data.frequency === 'perN' && this.data.frequencyValue) {
      return batchNumber % this.data.frequencyValue === 0;
    }
    
    return false;
  }

  toJSON(): SamplingPlan {
    return { ...this.data };
  }

  static create(data: Omit<SamplingPlan, 'id' | 'createdAt' | 'updatedAt'>): SamplingPlanEntity {
    const now = new Date().toISOString();
    return new SamplingPlanEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }
}

// Sampling Result Entity
export class SamplingResultEntity {
  private readonly data: SamplingResult;

  constructor(data: SamplingResult) {
    this.data = SamplingResultSchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get batchId(): string { return this.data.batchId; }
  get sampleCode(): string { return this.data.sampleCode; }
  get takenAt(): string { return this.data.takenAt; }
  get labId(): string | undefined { return this.data.labId; }
  get analyte(): string { return this.data.analyte; }
  get value(): number { return this.data.value; }
  get unit(): string { return this.data.unit; }
  get limitType(): string { return this.data.limitType; }
  get decision(): string { return this.data.decision; }
  get docUri(): string | undefined { return this.data.docUri; }
  get notes(): string | undefined { return this.data.notes; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  private validateBusinessRules(): void {
    if (this.data.value < 0) {
      throw new Error('Sample value cannot be negative');
    }
  }

  isPass(): boolean {
    return this.data.decision === 'Pass';
  }

  isReject(): boolean {
    return this.data.decision === 'Reject';
  }

  requiresInvestigation(): boolean {
    return this.data.decision === 'Investigate';
  }

  isActionLimit(): boolean {
    return this.data.limitType === 'Action';
  }

  isRejectLimit(): boolean {
    return this.data.limitType === 'Reject';
  }

  updateDecision(decision: SamplingResult['decision'], updatedBy?: string): SamplingResultEntity {
    return new SamplingResultEntity({
      ...this.data,
      decision,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  toJSON(): SamplingResult {
    return { ...this.data };
  }

  static create(data: Omit<SamplingResult, 'id' | 'createdAt' | 'updatedAt'>): SamplingResultEntity {
    const now = new Date().toISOString();
    return new SamplingResultEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }
}

// Retained Sample Entity
export class RetainedSampleEntity {
  private readonly data: RetainedSample;

  constructor(data: RetainedSample) {
    this.data = RetainedSampleSchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get batchId(): string { return this.data.batchId; }
  get sampleCode(): string { return this.data.sampleCode; }
  get storageLoc(): string { return this.data.storageLoc; }
  get expiryAt(): string { return this.data.expiryAt; }
  get disposedAt(): string | undefined { return this.data.disposedAt; }
  get notes(): string | undefined { return this.data.notes; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  private validateBusinessRules(): void {
    const expiryDate = new Date(this.data.expiryAt);
    const now = new Date();
    if (expiryDate <= now) {
      throw new Error('Expiry date must be in the future');
    }
  }

  isExpired(): boolean {
    return new Date(this.data.expiryAt) <= new Date();
  }

  isDisposed(): boolean {
    return !!this.data.disposedAt;
  }

  dispose(disposedAt: string, notes?: string, updatedBy?: string): RetainedSampleEntity {
    if (this.isDisposed()) {
      throw new Error('Sample is already disposed');
    }

    return new RetainedSampleEntity({
      ...this.data,
      disposedAt,
      notes: notes ? `${this.data.notes ?? ''}\n[DISPOSED] ${notes}`.trim() : this.data.notes,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  toJSON(): RetainedSample {
    return { ...this.data };
  }

  static create(data: Omit<RetainedSample, 'id' | 'createdAt' | 'updatedAt'>): RetainedSampleEntity {
    const now = new Date().toISOString();
    return new RetainedSampleEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }
}

// Non-Conformity Entity
export class NonConformityEntity {
  private readonly data: NonConformity;

  constructor(data: NonConformity) {
    this.data = NonConformitySchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get refType(): string { return this.data.refType; }
  get refId(): string { return this.data.refId; }
  get type(): string { return this.data.type; }
  get severity(): string { return this.data.severity; }
  get description(): string { return this.data.description; }
  get action(): string { return this.data.action; }
  get capaId(): string | undefined { return this.data.capaId; }
  get status(): string { return this.data.status; }
  get discoveredAt(): string { return this.data.discoveredAt; }
  get closedAt(): string | undefined { return this.data.closedAt; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  private validateBusinessRules(): void {
    if (this.data.closedAt) {
      const discoveredDate = new Date(this.data.discoveredAt);
      const closedDate = new Date(this.data.closedAt);
      if (closedDate < discoveredDate) {
        throw new Error('Closed date cannot be before discovery date');
      }
    }
  }

  isOpen(): boolean {
    return this.data.status === 'Open';
  }

  isInProgress(): boolean {
    return this.data.status === 'InProgress';
  }

  isClosed(): boolean {
    return this.data.status === 'Closed';
  }

  isCritical(): boolean {
    return this.data.severity === 'Critical';
  }

  requiresImmediateAction(): boolean {
    return this.isCritical() || (this.data.severity === 'High' && this.data.action === 'Block');
  }

  assignCAPA(capaId: string, updatedBy?: string): NonConformityEntity {
    return new NonConformityEntity({
      ...this.data,
      capaId,
      status: 'InProgress',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  close(closedAt: string, updatedBy?: string): NonConformityEntity {
    if (this.isClosed()) {
      throw new Error('Non-conformity is already closed');
    }

    return new NonConformityEntity({
      ...this.data,
      status: 'Closed',
      closedAt,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  toJSON(): NonConformity {
    return { ...this.data };
  }

  static create(data: Omit<NonConformity, 'id' | 'createdAt' | 'updatedAt'>): NonConformityEntity {
    const now = new Date().toISOString();
    return new NonConformityEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }
}

// CAPA Entity
export class CAPAEntity {
  private readonly data: CAPA;

  constructor(data: CAPA) {
    this.data = CAPASchema.parse(data);
    this.validateBusinessRules();
  }

  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get ncId(): string | undefined { return this.data.ncId; }
  get title(): string { return this.data.title; }
  get description(): string { return this.data.description; }
  get type(): string { return this.data.type; }
  get priority(): string { return this.data.priority; }
  get status(): string { return this.data.status; }
  get assignedTo(): string | undefined { return this.data.assignedTo; }
  get dueDate(): string | undefined { return this.data.dueDate; }
  get closedAt(): string | undefined { return this.data.closedAt; }
  get effectiveness(): string | undefined { return this.data.effectiveness; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  private validateBusinessRules(): void {
    if (this.data.closedAt) {
      const createdDate = new Date(this.data.createdAt);
      const closedDate = new Date(this.data.closedAt);
      if (closedDate < createdDate) {
        throw new Error('Closed date cannot be before creation date');
      }
    }

    if (this.data.dueDate) {
      const dueDate = new Date(this.data.dueDate);
      const createdDate = new Date(this.data.createdAt);
      if (dueDate < createdDate) {
        throw new Error('Due date cannot be before creation date');
      }
    }
  }

  isOpen(): boolean {
    return this.data.status === 'Open';
  }

  isInProgress(): boolean {
    return this.data.status === 'InProgress';
  }

  isClosed(): boolean {
    return this.data.status === 'Closed';
  }

  isOverdue(): boolean {
    if (!this.data.dueDate || this.isClosed()) {
      return false;
    }
    return new Date(this.data.dueDate) < new Date();
  }

  isCritical(): boolean {
    return this.data.priority === 'Critical';
  }

  isCorrective(): boolean {
    return this.data.type === 'CorrectiveAction';
  }

  isPreventive(): boolean {
    return this.data.type === 'PreventiveAction';
  }

  assignTo(userId: string, updatedBy?: string): CAPAEntity {
    return new CAPAEntity({
      ...this.data,
      assignedTo: userId,
      status: 'InProgress',
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  close(effectiveness: CAPA['effectiveness'], closedAt: string, updatedBy?: string): CAPAEntity {
    if (this.isClosed()) {
      throw new Error('CAPA is already closed');
    }

    return new CAPAEntity({
      ...this.data,
      status: 'Closed',
      effectiveness,
      closedAt,
      updatedAt: new Date().toISOString(),
      updatedBy
    });
  }

  toJSON(): CAPA {
    return { ...this.data };
  }

  static create(data: Omit<CAPA, 'id' | 'createdAt' | 'updatedAt'>): CAPAEntity {
    const now = new Date().toISOString();
    return new CAPAEntity({
      ...data,
      id: require('uuid').v4(),
      createdAt: now,
      updatedAt: now
    });
  }
}

