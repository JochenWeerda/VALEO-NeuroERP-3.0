/**
 * Mobile Run Entity for VALEO NeuroERP 3.0 Production Domain
 * Mobile production unit management with calibration and cleaning
 */
import { z } from 'zod';
declare const CalibrationCheckSchema: z.ZodObject<{
    scaleOk: z.ZodBoolean;
    moistureOk: z.ZodBoolean;
    temperatureOk: z.ZodBoolean;
    date: z.ZodString;
    validatedBy: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    date: string;
    scaleOk: boolean;
    moistureOk: boolean;
    temperatureOk: boolean;
    validatedBy: string;
    notes?: string | undefined;
}, {
    date: string;
    scaleOk: boolean;
    moistureOk: boolean;
    temperatureOk: boolean;
    validatedBy: string;
    notes?: string | undefined;
}>;
declare const CleaningSequenceSchema: z.ZodObject<{
    id: z.ZodString;
    type: z.ZodEnum<["DryClean", "Vacuum", "Flush", "WetClean"]>;
    startedAt: z.ZodString;
    endedAt: z.ZodOptional<z.ZodString>;
    usedMaterialSku: z.ZodOptional<z.ZodString>;
    flushMassKg: z.ZodOptional<z.ZodNumber>;
    validatedBy: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
    startedAt: string;
    validatedBy: string;
    notes?: string | undefined;
    endedAt?: string | undefined;
    usedMaterialSku?: string | undefined;
    flushMassKg?: number | undefined;
}, {
    id: string;
    type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
    startedAt: string;
    validatedBy: string;
    notes?: string | undefined;
    endedAt?: string | undefined;
    usedMaterialSku?: string | undefined;
    flushMassKg?: number | undefined;
}>;
export declare const MobileRunSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    mobileUnitId: z.ZodString;
    vehicleId: z.ZodOptional<z.ZodString>;
    operatorId: z.ZodString;
    site: z.ZodObject<{
        customerId: z.ZodString;
        location: z.ZodObject<{
            lat: z.ZodNumber;
            lng: z.ZodNumber;
            address: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lng: number;
            address?: string | undefined;
        }, {
            lat: number;
            lng: number;
            address?: string | undefined;
        }>;
    }, "strip", z.ZodTypeAny, {
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
    }, {
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
    }>;
    powerSource: z.ZodDefault<z.ZodEnum<["Generator", "Grid", "Battery"]>>;
    calibrationCheck: z.ZodObject<{
        scaleOk: z.ZodBoolean;
        moistureOk: z.ZodBoolean;
        temperatureOk: z.ZodBoolean;
        date: z.ZodString;
        validatedBy: z.ZodString;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        date: string;
        scaleOk: boolean;
        moistureOk: boolean;
        temperatureOk: boolean;
        validatedBy: string;
        notes?: string | undefined;
    }, {
        date: string;
        scaleOk: boolean;
        moistureOk: boolean;
        temperatureOk: boolean;
        validatedBy: string;
        notes?: string | undefined;
    }>;
    startAt: z.ZodString;
    endAt: z.ZodOptional<z.ZodString>;
    cleaningSequenceId: z.ZodOptional<z.ZodString>;
    cleaningSequences: z.ZodDefault<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        type: z.ZodEnum<["DryClean", "Vacuum", "Flush", "WetClean"]>;
        startedAt: z.ZodString;
        endedAt: z.ZodOptional<z.ZodString>;
        usedMaterialSku: z.ZodOptional<z.ZodString>;
        flushMassKg: z.ZodOptional<z.ZodNumber>;
        validatedBy: z.ZodString;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        startedAt: string;
        validatedBy: string;
        notes?: string | undefined;
        endedAt?: string | undefined;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
    }, {
        id: string;
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        startedAt: string;
        validatedBy: string;
        notes?: string | undefined;
        endedAt?: string | undefined;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
    }>, "many">>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    startAt: string;
    createdAt: string;
    updatedAt: string;
    mobileUnitId: string;
    operatorId: string;
    site: {
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
    };
    powerSource: "Generator" | "Grid" | "Battery";
    calibrationCheck: {
        date: string;
        scaleOk: boolean;
        moistureOk: boolean;
        temperatureOk: boolean;
        validatedBy: string;
        notes?: string | undefined;
    };
    cleaningSequences: {
        id: string;
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        startedAt: string;
        validatedBy: string;
        notes?: string | undefined;
        endedAt?: string | undefined;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
    }[];
    endAt?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    vehicleId?: string | undefined;
    cleaningSequenceId?: string | undefined;
}, {
    id: string;
    tenantId: string;
    startAt: string;
    createdAt: string;
    updatedAt: string;
    mobileUnitId: string;
    operatorId: string;
    site: {
        location: {
            lat: number;
            lng: number;
            address?: string | undefined;
        };
        customerId: string;
    };
    calibrationCheck: {
        date: string;
        scaleOk: boolean;
        moistureOk: boolean;
        temperatureOk: boolean;
        validatedBy: string;
        notes?: string | undefined;
    };
    endAt?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    vehicleId?: string | undefined;
    powerSource?: "Generator" | "Grid" | "Battery" | undefined;
    cleaningSequenceId?: string | undefined;
    cleaningSequences?: {
        id: string;
        type: "DryClean" | "Vacuum" | "Flush" | "WetClean";
        startedAt: string;
        validatedBy: string;
        notes?: string | undefined;
        endedAt?: string | undefined;
        usedMaterialSku?: string | undefined;
        flushMassKg?: number | undefined;
    }[] | undefined;
}>;
export type MobileRun = z.infer<typeof MobileRunSchema>;
export type CalibrationCheck = z.infer<typeof CalibrationCheckSchema>;
export type CleaningSequence = z.infer<typeof CleaningSequenceSchema>;
export declare class MobileRunEntity {
    private data;
    constructor(data: MobileRun);
    get id(): string;
    get tenantId(): string;
    get mobileUnitId(): string;
    get vehicleId(): string | undefined;
    get operatorId(): string;
    get site(): MobileRun['site'];
    get powerSource(): string;
    get calibrationCheck(): CalibrationCheck;
    get startAt(): string;
    get endAt(): string | undefined;
    get cleaningSequenceId(): string | undefined;
    get cleaningSequences(): CleaningSequence[];
    get createdAt(): string;
    get updatedAt(): string;
    isActive(): boolean;
    isCompleted(): boolean;
    canStart(): boolean;
    canFinish(): boolean;
    isCalibrationValid(): boolean;
    isCalibrationExpired(maxDays?: number): boolean;
    getDurationHours(): number;
    getActiveCleaningSequence(): CleaningSequence | undefined;
    getCompletedCleaningSequences(): CleaningSequence[];
    getTotalFlushMass(): number;
    getCleaningHistory(): CleaningSequence[];
    private validateBusinessRules;
    finish(endAt: string, updatedBy?: string): MobileRunEntity;
    updateCalibrationCheck(check: CalibrationCheck, updatedBy?: string): MobileRunEntity;
    addCleaningSequence(sequence: Omit<CleaningSequence, 'id'>, updatedBy?: string): MobileRunEntity;
    endCleaningSequence(sequenceId: string, endedAt: string, notes?: string, updatedBy?: string): MobileRunEntity;
    validateCleaningRequired(previousRecipeMedicated: boolean, currentRecipeMedicated: boolean): boolean;
    getRequiredCleaningType(previousRecipeMedicated: boolean, currentRecipeMedicated: boolean): CleaningSequence['type'];
    toJSON(): MobileRun;
    static create(data: Omit<MobileRun, 'id' | 'createdAt' | 'updatedAt'>): MobileRunEntity;
    static fromJSON(data: MobileRun): MobileRunEntity;
}
export {};
//# sourceMappingURL=mobile-run.d.ts.map