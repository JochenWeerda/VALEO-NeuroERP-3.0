/**
 * Mix Order Entity for VALEO NeuroERP 3.0 Production Domain
 * Mix order management for both plant and mobile production
 */
import { z } from 'zod';
declare const LocationSchema: z.ZodObject<{
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
declare const MixStepSchema: z.ZodObject<{
    type: z.ZodEnum<["weigh", "dose", "grind", "mix", "flushing", "transfer"]>;
    startedAt: z.ZodString;
    endedAt: z.ZodOptional<z.ZodString>;
    equipmentId: z.ZodOptional<z.ZodString>;
    actuals: z.ZodOptional<z.ZodObject<{
        massKg: z.ZodOptional<z.ZodNumber>;
        timeSec: z.ZodOptional<z.ZodNumber>;
        energyKWh: z.ZodOptional<z.ZodNumber>;
        moisturePercent: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        massKg?: number | undefined;
        timeSec?: number | undefined;
        energyKWh?: number | undefined;
        moisturePercent?: number | undefined;
    }, {
        massKg?: number | undefined;
        timeSec?: number | undefined;
        energyKWh?: number | undefined;
        moisturePercent?: number | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
    startedAt: string;
    endedAt?: string | undefined;
    equipmentId?: string | undefined;
    actuals?: {
        massKg?: number | undefined;
        timeSec?: number | undefined;
        energyKWh?: number | undefined;
        moisturePercent?: number | undefined;
    } | undefined;
}, {
    type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
    startedAt: string;
    endedAt?: string | undefined;
    equipmentId?: string | undefined;
    actuals?: {
        massKg?: number | undefined;
        timeSec?: number | undefined;
        energyKWh?: number | undefined;
        moisturePercent?: number | undefined;
    } | undefined;
}>;
export declare const MixOrderSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    orderNumber: z.ZodString;
    type: z.ZodEnum<["Plant", "Mobile"]>;
    recipeId: z.ZodString;
    targetQtyKg: z.ZodNumber;
    plannedAt: z.ZodString;
    location: z.ZodOptional<z.ZodObject<{
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
    }>>;
    customerId: z.ZodOptional<z.ZodString>;
    mobileUnitId: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Draft", "Staged", "Running", "Hold", "Completed", "Aborted"]>>;
    notes: z.ZodOptional<z.ZodString>;
    steps: z.ZodDefault<z.ZodArray<z.ZodObject<{
        type: z.ZodEnum<["weigh", "dose", "grind", "mix", "flushing", "transfer"]>;
        startedAt: z.ZodString;
        endedAt: z.ZodOptional<z.ZodString>;
        equipmentId: z.ZodOptional<z.ZodString>;
        actuals: z.ZodOptional<z.ZodObject<{
            massKg: z.ZodOptional<z.ZodNumber>;
            timeSec: z.ZodOptional<z.ZodNumber>;
            energyKWh: z.ZodOptional<z.ZodNumber>;
            moisturePercent: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        }, {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
        startedAt: string;
        endedAt?: string | undefined;
        equipmentId?: string | undefined;
        actuals?: {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        } | undefined;
    }, {
        type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
        startedAt: string;
        endedAt?: string | undefined;
        equipmentId?: string | undefined;
        actuals?: {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        } | undefined;
    }>, "many">>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    status: "Draft" | "Staged" | "Running" | "Hold" | "Completed" | "Aborted";
    type: "Plant" | "Mobile";
    createdAt: string;
    updatedAt: string;
    orderNumber: string;
    recipeId: string;
    targetQtyKg: number;
    plannedAt: string;
    steps: {
        type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
        startedAt: string;
        endedAt?: string | undefined;
        equipmentId?: string | undefined;
        actuals?: {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        } | undefined;
    }[];
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    location?: {
        lat: number;
        lng: number;
        address?: string | undefined;
    } | undefined;
    customerId?: string | undefined;
    mobileUnitId?: string | undefined;
    notes?: string | undefined;
}, {
    id: string;
    tenantId: string;
    type: "Plant" | "Mobile";
    createdAt: string;
    updatedAt: string;
    orderNumber: string;
    recipeId: string;
    targetQtyKg: number;
    plannedAt: string;
    status?: "Draft" | "Staged" | "Running" | "Hold" | "Completed" | "Aborted" | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    location?: {
        lat: number;
        lng: number;
        address?: string | undefined;
    } | undefined;
    customerId?: string | undefined;
    mobileUnitId?: string | undefined;
    notes?: string | undefined;
    steps?: {
        type: "weigh" | "dose" | "grind" | "mix" | "flushing" | "transfer";
        startedAt: string;
        endedAt?: string | undefined;
        equipmentId?: string | undefined;
        actuals?: {
            massKg?: number | undefined;
            timeSec?: number | undefined;
            energyKWh?: number | undefined;
            moisturePercent?: number | undefined;
        } | undefined;
    }[] | undefined;
}>;
export type MixOrder = z.infer<typeof MixOrderSchema>;
export type Location = z.infer<typeof LocationSchema>;
export type MixStep = z.infer<typeof MixStepSchema>;
export declare class MixOrderEntity {
    private data;
    constructor(data: MixOrder);
    get id(): string;
    get tenantId(): string;
    get orderNumber(): string;
    get type(): string;
    get recipeId(): string;
    get targetQtyKg(): number;
    get plannedAt(): string;
    get location(): Location | undefined;
    get customerId(): string | undefined;
    get mobileUnitId(): string | undefined;
    get status(): string;
    get notes(): string | undefined;
    get steps(): MixStep[];
    get createdAt(): string;
    get updatedAt(): string;
    isDraft(): boolean;
    isStaged(): boolean;
    isRunning(): boolean;
    isOnHold(): boolean;
    isCompleted(): boolean;
    isAborted(): boolean;
    isMobile(): boolean;
    isPlant(): boolean;
    canStart(): boolean;
    canStage(): boolean;
    canHold(): boolean;
    canComplete(): boolean;
    canAbort(): boolean;
    getDurationMinutes(): number;
    getTotalMassProcessed(): number;
    getTotalEnergyConsumed(): number;
    getActiveSteps(): MixStep[];
    getCompletedSteps(): MixStep[];
    private validateBusinessRules;
    stage(updatedBy?: string): MixOrderEntity;
    start(updatedBy?: string): MixOrderEntity;
    hold(reason?: string, updatedBy?: string): MixOrderEntity;
    complete(updatedBy?: string): MixOrderEntity;
    abort(reason?: string, updatedBy?: string): MixOrderEntity;
    addStep(step: MixStep, updatedBy?: string): MixOrderEntity;
    updateStep(stepIndex: number, updates: Partial<MixStep>, updatedBy?: string): MixOrderEntity;
    endStep(stepIndex: number, endedAt: string, actuals?: MixStep['actuals'], updatedBy?: string): MixOrderEntity;
    toJSON(): MixOrder;
    static create(data: Omit<MixOrder, 'id' | 'createdAt' | 'updatedAt'>): MixOrderEntity;
    static fromJSON(data: MixOrder): MixOrderEntity;
}
export {};
//# sourceMappingURL=mix-order.d.ts.map