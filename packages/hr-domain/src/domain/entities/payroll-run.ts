/**
 * Payroll Run Entity for VALEO NeuroERP 3.0 HR Domain
 * Payroll preparation and export (no accounting entries)
 */

import { v4 as uuidv4 } from 'uuid';
import { z } from 'zod';

const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MILLISECONDS_PER_DAY = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;
const INCLUSIVE_DAY_OFFSET = 1;
const MAX_PAYROLL_PERIOD_DAYS = 365;
const ZERO = 0;

const payrollStatusSchema = z.enum(['Draft', 'Locked', 'Exported']);

const PayrollItemSchema = z.object({
  employeeId: z.string().uuid(),
  hours: z.number().positive(),
  allowances: z.number().min(0).optional(),
  deductions: z.number().min(0).optional(),
  grossAmount: z.number().min(0).optional() // Optional preview calculation
});

const PayrollPeriodSchema = z.object({
  from: z.string().date(),
  to: z.string().date()
});

export const PayrollRunSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string().uuid(),
  period: PayrollPeriodSchema,
  status: payrollStatusSchema,
  items: z.array(PayrollItemSchema),
  exportedAt: z.string().datetime().optional(),
  exportedBy: z.string().uuid().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  createdBy: z.string().optional(),
  updatedBy: z.string().optional()
});

export type PayrollRun = z.infer<typeof PayrollRunSchema>;
export type PayrollItem = z.infer<typeof PayrollItemSchema>;
export type PayrollPeriod = z.infer<typeof PayrollPeriodSchema>;
export type PayrollRunStatus = z.infer<typeof payrollStatusSchema>;

export class PayrollRunEntity {
  private readonly data: PayrollRun;

  constructor(data: PayrollRun) {
    this.data = PayrollRunSchema.parse(data);
    this.validateBusinessRules();
  }

  // Getters
  get id(): string { return this.data.id; }
  get tenantId(): string { return this.data.tenantId; }
  get period(): PayrollPeriod { return this.data.period; }
  get status(): PayrollRunStatus { return this.data.status; }
  get items(): PayrollItem[] { return [...this.data.items]; }
  get exportedAt(): string | undefined { return this.data.exportedAt; }
  get exportedBy(): string | undefined { return this.data.exportedBy; }
  get createdAt(): string { return this.data.createdAt; }
  get updatedAt(): string { return this.data.updatedAt; }

  // Business Methods
  isDraft(): boolean {
    return this.data.status === 'Draft';
  }

  isLocked(): boolean {
    return this.data.status === 'Locked';
  }

  isExported(): boolean {
    return this.data.status === 'Exported';
  }

  canEdit(): boolean {
    return this.isDraft();
  }

  canLock(): boolean {
    return this.isDraft() && this.data.items.length > 0;
  }

  canExport(): boolean {
    return this.isLocked();
  }

  getEmployeeCount(): number {
    return this.data.items.length;
  }

  getTotalHours(): number {
    return this.data.items.reduce((sum, item) => sum + item.hours, ZERO);
  }

  getTotalGrossAmount(): number {
    return this.data.items.reduce((sum, item) => sum + (item.grossAmount ?? ZERO), ZERO);
  }

  getTotalAllowances(): number {
    return this.data.items.reduce((sum, item) => sum + (item.allowances ?? ZERO), ZERO);
  }

  getTotalDeductions(): number {
    return this.data.items.reduce((sum, item) => sum + (item.deductions ?? ZERO), ZERO);
  }

  getPeriodDurationInDays(): number {
    const fromDate = new Date(this.data.period.from);
    const toDate = new Date(this.data.period.to);
    const diffTime = Math.abs(toDate.getTime() - fromDate.getTime());
    return Math.ceil(diffTime / MILLISECONDS_PER_DAY) + INCLUSIVE_DAY_OFFSET;
  }

  hasEmployee(employeeId: string): boolean {
    return this.data.items.some(item => item.employeeId === employeeId);
  }

  getEmployeeItem(employeeId: string): PayrollItem | undefined {
    return this.data.items.find(item => item.employeeId === employeeId);
  }

  // Validation
  private validateBusinessRules(): void {
    const fromDate = new Date(this.data.period.from);
    const toDate = new Date(this.data.period.to);

    if (toDate < fromDate) {
      throw new Error('End date must be after or equal to start date');
    }

    // Check for reasonable period duration (max 1 year)
    const durationDays = this.getPeriodDurationInDays();
    if (durationDays > MAX_PAYROLL_PERIOD_DAYS) {
      throw new Error('Payroll period cannot exceed 365 days');
    }

    // Validate items
    for (const item of this.data.items) {
      if (item.hours <= 0) {
        throw new Error('Employee hours must be positive');
      }
      if (typeof item.allowances === 'number' && item.allowances < 0) {
        throw new Error('Allowances cannot be negative');
      }
      if (typeof item.deductions === 'number' && item.deductions < 0) {
        throw new Error('Deductions cannot be negative');
      }
    }

    // Check for duplicate employees
    const employeeIds = this.data.items.map(item => item.employeeId);
    const uniqueEmployeeIds = new Set(employeeIds);
    if (employeeIds.length !== uniqueEmployeeIds.size) {
      throw new Error('Duplicate employees found in payroll run');
    }
  }

  // State Changes
  lock(updatedBy?: string): PayrollRunEntity {
    if (!this.canLock()) {
      throw new Error('Payroll run cannot be locked in current status');
    }

    return this.clone({ status: 'Locked', updatedBy });
  }

  export(exportedBy: string): PayrollRunEntity {
    if (!this.canExport()) {
      throw new Error('Payroll run cannot be exported in current status');
    }

    const timestamp = new Date().toISOString();
    return this.clone({
      status: 'Exported',
      exportedAt: timestamp,
      exportedBy,
      updatedBy: exportedBy
    });
  }

  addEmployeeItem(item: PayrollItem, updatedBy?: string): PayrollRunEntity {
    if (!this.canEdit()) {
      throw new Error('Payroll run cannot be edited in current status');
    }

    if (this.hasEmployee(item.employeeId)) {
      throw new Error('Employee already exists in payroll run');
    }

    return this.clone({
      items: [...this.data.items, item],
      updatedBy
    });
  }

  updateEmployeeItem(employeeId: string, updates: Partial<PayrollItem>, updatedBy?: string): PayrollRunEntity {
    if (!this.canEdit()) {
      throw new Error('Payroll run cannot be edited in current status');
    }

    const updatedItems = this.data.items.map(item => 
      item.employeeId === employeeId ? { ...item, ...updates } : item
    );

    return this.clone({
      items: updatedItems,
      updatedBy
    });
  }

  removeEmployeeItem(employeeId: string, updatedBy?: string): PayrollRunEntity {
    if (!this.canEdit()) {
      throw new Error('Payroll run cannot be edited in current status');
    }

    return this.clone({
      items: this.data.items.filter(item => item.employeeId !== employeeId),
      updatedBy
    });
  }

  // Export for persistence
  toJSON(): PayrollRun {
    return { ...this.data };
  }

  private clone(overrides: Partial<PayrollRun>): PayrollRunEntity {
    const now = new Date().toISOString();
    return new PayrollRunEntity({
      ...this.data,
      ...overrides,
      updatedAt: now
    });
  }

  // Factory methods
  static create(data: Omit<PayrollRun, 'id' | 'createdAt' | 'updatedAt'>): PayrollRunEntity {
    const now = new Date().toISOString();
    return new PayrollRunEntity({
      ...data,
      id: uuidv4(),
      createdAt: now,
      updatedAt: now
    });
  }

  static fromJSON(data: PayrollRun): PayrollRunEntity {
    return new PayrollRunEntity(data);
  }
}

