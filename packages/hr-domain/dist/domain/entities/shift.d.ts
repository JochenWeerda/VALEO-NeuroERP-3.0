/**
 * Shift Entity for VALEO NeuroERP 3.0 HR Domain
 * Shift planning and scheduling
 */
import { z } from 'zod';
export declare const ShiftSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    location: z.ZodOptional<z.ZodString>;
    startsAt: z.ZodString;
    endsAt: z.ZodString;
    requiredHeadcount: z.ZodNumber;
    assigned: z.ZodArray<z.ZodString, "many">;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    name: string;
    startsAt: string;
    endsAt: string;
    requiredHeadcount: number;
    assigned: string[];
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    location?: string | undefined;
}, {
    id: string;
    tenantId: string;
    createdAt: string;
    updatedAt: string;
    name: string;
    startsAt: string;
    endsAt: string;
    requiredHeadcount: number;
    assigned: string[];
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    location?: string | undefined;
}>;
export type Shift = z.infer<typeof ShiftSchema>;
export declare class ShiftEntity {
    private readonly data;
    constructor(data: Shift);
    get id(): string;
    get tenantId(): string;
    get name(): string;
    get location(): string | undefined;
    get startsAt(): string;
    get endsAt(): string;
    get requiredHeadcount(): number;
    get assigned(): string[];
    get createdAt(): string;
    get updatedAt(): string;
    getDurationHours(): number;
    getAssignedCount(): number;
    isFullyStaffed(): boolean;
    isOverStaffed(): boolean;
    isUnderStaffed(): boolean;
    hasEmployee(employeeId: string): boolean;
    canAssignEmployee(employeeId: string): boolean;
    getStaffingRatio(): number;
    private validateBusinessRules;
    assignEmployee(employeeId: string, updatedBy?: string): ShiftEntity;
    unassignEmployee(employeeId: string, updatedBy?: string): ShiftEntity;
    updateRequiredHeadcount(headcount: number, updatedBy?: string): ShiftEntity;
    updateLocation(location: string | undefined, updatedBy?: string): ShiftEntity;
    updateTimes(startsAt: string, endsAt: string, updatedBy?: string): ShiftEntity;
    toJSON(): Shift;
    private clone;
    static create(data: Omit<Shift, 'id' | 'createdAt' | 'updatedAt'>): ShiftEntity;
    static fromJSON(data: Shift): ShiftEntity;
}
//# sourceMappingURL=shift.d.ts.map