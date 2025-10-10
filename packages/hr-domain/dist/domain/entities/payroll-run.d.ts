/**
 * Payroll Run Entity for VALEO NeuroERP 3.0 HR Domain
 * Payroll preparation and export (no accounting entries)
 */
import { z } from 'zod';
declare const payrollStatusSchema: z.ZodEnum<["Draft", "Locked", "Exported"]>;
declare const PayrollItemSchema: z.ZodObject<{
    employeeId: z.ZodString;
    hours: z.ZodNumber;
    allowances: z.ZodOptional<z.ZodNumber>;
    deductions: z.ZodOptional<z.ZodNumber>;
    grossAmount: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    employeeId: string;
    hours: number;
    grossAmount?: number | undefined;
    allowances?: number | undefined;
    deductions?: number | undefined;
}, {
    employeeId: string;
    hours: number;
    grossAmount?: number | undefined;
    allowances?: number | undefined;
    deductions?: number | undefined;
}>;
declare const PayrollPeriodSchema: z.ZodObject<{
    from: z.ZodString;
    to: z.ZodString;
}, "strip", z.ZodTypeAny, {
    from: string;
    to: string;
}, {
    from: string;
    to: string;
}>;
export declare const PayrollRunSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    period: z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>;
    status: z.ZodEnum<["Draft", "Locked", "Exported"]>;
    items: z.ZodArray<z.ZodObject<{
        employeeId: z.ZodString;
        hours: z.ZodNumber;
        allowances: z.ZodOptional<z.ZodNumber>;
        deductions: z.ZodOptional<z.ZodNumber>;
        grossAmount: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        employeeId: string;
        hours: number;
        grossAmount?: number | undefined;
        allowances?: number | undefined;
        deductions?: number | undefined;
    }, {
        employeeId: string;
        hours: number;
        grossAmount?: number | undefined;
        allowances?: number | undefined;
        deductions?: number | undefined;
    }>, "many">;
    exportedAt: z.ZodOptional<z.ZodString>;
    exportedBy: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "Draft" | "Locked" | "Exported";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    period: {
        from: string;
        to: string;
    };
    items: {
        employeeId: string;
        hours: number;
        grossAmount?: number | undefined;
        allowances?: number | undefined;
        deductions?: number | undefined;
    }[];
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    exportedBy?: string | undefined;
    exportedAt?: string | undefined;
}, {
    status: "Draft" | "Locked" | "Exported";
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    period: {
        from: string;
        to: string;
    };
    items: {
        employeeId: string;
        hours: number;
        grossAmount?: number | undefined;
        allowances?: number | undefined;
        deductions?: number | undefined;
    }[];
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    exportedBy?: string | undefined;
    exportedAt?: string | undefined;
}>;
export type PayrollRun = z.infer<typeof PayrollRunSchema>;
export type PayrollItem = z.infer<typeof PayrollItemSchema>;
export type PayrollPeriod = z.infer<typeof PayrollPeriodSchema>;
export type PayrollRunStatus = z.infer<typeof payrollStatusSchema>;
export declare class PayrollRunEntity {
    private readonly data;
    constructor(data: PayrollRun);
    get id(): string;
    get tenantId(): string;
    get period(): PayrollPeriod;
    get status(): PayrollRunStatus;
    get items(): PayrollItem[];
    get exportedAt(): string | undefined;
    get exportedBy(): string | undefined;
    get createdAt(): string;
    get updatedAt(): string;
    isDraft(): boolean;
    isLocked(): boolean;
    isExported(): boolean;
    canEdit(): boolean;
    canLock(): boolean;
    canExport(): boolean;
    getEmployeeCount(): number;
    getTotalHours(): number;
    getTotalGrossAmount(): number;
    getTotalAllowances(): number;
    getTotalDeductions(): number;
    getPeriodDurationInDays(): number;
    hasEmployee(employeeId: string): boolean;
    getEmployeeItem(employeeId: string): PayrollItem | undefined;
    private validateBusinessRules;
    lock(updatedBy?: string): PayrollRunEntity;
    export(exportedBy: string): PayrollRunEntity;
    addEmployeeItem(item: PayrollItem, updatedBy?: string): PayrollRunEntity;
    updateEmployeeItem(employeeId: string, updates: Partial<PayrollItem>, updatedBy?: string): PayrollRunEntity;
    removeEmployeeItem(employeeId: string, updatedBy?: string): PayrollRunEntity;
    toJSON(): PayrollRun;
    private clone;
    static create(data: Omit<PayrollRun, 'id' | 'createdAt' | 'updatedAt'>): PayrollRunEntity;
    static fromJSON(data: PayrollRun): PayrollRunEntity;
}
export {};
//# sourceMappingURL=payroll-run.d.ts.map