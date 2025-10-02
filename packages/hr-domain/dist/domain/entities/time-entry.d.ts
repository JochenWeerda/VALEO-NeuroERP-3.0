/**
 * Time Entry Entity for VALEO NeuroERP 3.0 HR Domain
 * Time tracking with validation and business rules
 */
import { z } from 'zod';
export declare const TimeEntrySchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    employeeId: z.ZodString;
    date: z.ZodString;
    start: z.ZodString;
    end: z.ZodString;
    breakMinutes: z.ZodNumber;
    projectId: z.ZodOptional<z.ZodString>;
    costCenter: z.ZodOptional<z.ZodString>;
    source: z.ZodEnum<["Manual", "Terminal", "Mobile"]>;
    status: z.ZodEnum<["Draft", "Approved", "Rejected"]>;
    approvedBy: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    status: "Draft" | "Approved" | "Rejected";
    date: string;
    createdAt: string;
    updatedAt: string;
    version: number;
    employeeId: string;
    start: string;
    end: string;
    source: "Manual" | "Terminal" | "Mobile";
    breakMinutes: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    approvedBy?: string | undefined;
    projectId?: string | undefined;
    costCenter?: string | undefined;
}, {
    id: string;
    tenantId: string;
    status: "Draft" | "Approved" | "Rejected";
    date: string;
    createdAt: string;
    updatedAt: string;
    version: number;
    employeeId: string;
    start: string;
    end: string;
    source: "Manual" | "Terminal" | "Mobile";
    breakMinutes: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    approvedBy?: string | undefined;
    projectId?: string | undefined;
    costCenter?: string | undefined;
}>;
export type TimeEntry = z.infer<typeof TimeEntrySchema>;
export declare class TimeEntryEntity {
    private data;
    constructor(data: TimeEntry);
    get id(): string;
    get tenantId(): string;
    get employeeId(): string;
    get date(): string;
    get start(): string;
    get end(): string;
    get breakMinutes(): number;
    get projectId(): string | undefined;
    get costCenter(): string | undefined;
    get source(): string;
    get status(): string;
    get approvedBy(): string | undefined;
    get createdAt(): string;
    get updatedAt(): string;
    get version(): number;
    isDraft(): boolean;
    isApproved(): boolean;
    isRejected(): boolean;
    canEdit(): boolean;
    canApprove(): boolean;
    canReject(): boolean;
    getWorkingMinutes(): number;
    getWorkingHours(): number;
    getOvertimeMinutes(maxDailyHours?: number): number;
    private validateBusinessRules;
    approve(approvedBy: string): TimeEntryEntity;
    reject(approvedBy: string): TimeEntryEntity;
    updateTimes(start: string, end: string, breakMinutes: number, updatedBy?: string): TimeEntryEntity;
    updateProject(projectId: string | undefined, updatedBy?: string): TimeEntryEntity;
    updateCostCenter(costCenter: string | undefined, updatedBy?: string): TimeEntryEntity;
    toJSON(): TimeEntry;
    static create(data: Omit<TimeEntry, 'id' | 'createdAt' | 'updatedAt' | 'version'>): TimeEntryEntity;
    static fromJSON(data: TimeEntry): TimeEntryEntity;
}
//# sourceMappingURL=time-entry.d.ts.map