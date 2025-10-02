/**
 * Leave Request Entity for VALEO NeuroERP 3.0 HR Domain
 * Vacation, sick leave, and other absence management
 */
import { z } from 'zod';
export declare const LeaveRequestSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    employeeId: z.ZodString;
    type: z.ZodEnum<["Vacation", "Sick", "Unpaid", "Other"]>;
    from: z.ZodString;
    to: z.ZodString;
    days: z.ZodNumber;
    status: z.ZodEnum<["Pending", "Approved", "Rejected"]>;
    approvedBy: z.ZodOptional<z.ZodString>;
    note: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    type: "Vacation" | "Sick" | "Unpaid" | "Other";
    status: "Approved" | "Rejected" | "Pending";
    createdAt: string;
    updatedAt: string;
    version: number;
    employeeId: string;
    from: string;
    to: string;
    days: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    approvedBy?: string | undefined;
    note?: string | undefined;
}, {
    id: string;
    tenantId: string;
    type: "Vacation" | "Sick" | "Unpaid" | "Other";
    status: "Approved" | "Rejected" | "Pending";
    createdAt: string;
    updatedAt: string;
    version: number;
    employeeId: string;
    from: string;
    to: string;
    days: number;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    approvedBy?: string | undefined;
    note?: string | undefined;
}>;
export type LeaveRequest = z.infer<typeof LeaveRequestSchema>;
export declare class LeaveRequestEntity {
    private data;
    constructor(data: LeaveRequest);
    get id(): string;
    get tenantId(): string;
    get employeeId(): string;
    get type(): string;
    get from(): string;
    get to(): string;
    get days(): number;
    get status(): string;
    get approvedBy(): string | undefined;
    get note(): string | undefined;
    get createdAt(): string;
    get updatedAt(): string;
    get version(): number;
    isPending(): boolean;
    isApproved(): boolean;
    isRejected(): boolean;
    canEdit(): boolean;
    canApprove(): boolean;
    canReject(): boolean;
    isVacation(): boolean;
    isSickLeave(): boolean;
    isUnpaid(): boolean;
    getDurationInDays(): number;
    isInPeriod(date: string): boolean;
    overlapsWith(other: LeaveRequestEntity): boolean;
    private validateBusinessRules;
    approve(approvedBy: string, note?: string): LeaveRequestEntity;
    reject(approvedBy: string, note?: string): LeaveRequestEntity;
    updateNote(note: string | undefined, updatedBy?: string): LeaveRequestEntity;
    updateDates(from: string, to: string, days: number, updatedBy?: string): LeaveRequestEntity;
    toJSON(): LeaveRequest;
    static create(data: Omit<LeaveRequest, 'id' | 'createdAt' | 'updatedAt' | 'version'>): LeaveRequestEntity;
    static fromJSON(data: LeaveRequest): LeaveRequestEntity;
}
//# sourceMappingURL=leave-request.d.ts.map