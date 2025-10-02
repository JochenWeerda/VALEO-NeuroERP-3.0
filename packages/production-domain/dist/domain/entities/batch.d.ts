/**
 * Batch Entity for VALEO NeuroERP 3.0 Production Domain
 * Batch management with traceability and quality control
 */
import { z } from 'zod';
declare const BatchInputSchema: z.ZodObject<{
    batchId: z.ZodString;
    ingredientLotId: z.ZodString;
    plannedKg: z.ZodNumber;
    actualKg: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    batchId: string;
    ingredientLotId: string;
    plannedKg: number;
    actualKg: number;
}, {
    batchId: string;
    ingredientLotId: string;
    plannedKg: number;
    actualKg: number;
}>;
declare const BatchOutputLotSchema: z.ZodObject<{
    id: z.ZodString;
    batchId: z.ZodString;
    lotNumber: z.ZodString;
    qtyKg: z.ZodNumber;
    packing: z.ZodObject<{
        form: z.ZodEnum<["Bulk", "Bag", "Silo"]>;
        size: z.ZodOptional<z.ZodNumber>;
        unit: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        form: "Bulk" | "Bag" | "Silo";
        size?: number | undefined;
        unit?: string | undefined;
    }, {
        form: "Bulk" | "Bag" | "Silo";
        size?: number | undefined;
        unit?: string | undefined;
    }>;
    destination: z.ZodEnum<["Inventory", "DirectFarm"]>;
    gmpPlusMarkings: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    id: string;
    batchId: string;
    lotNumber: string;
    qtyKg: number;
    packing: {
        form: "Bulk" | "Bag" | "Silo";
        size?: number | undefined;
        unit?: string | undefined;
    };
    destination: "Inventory" | "DirectFarm";
    gmpPlusMarkings?: string[] | undefined;
}, {
    id: string;
    batchId: string;
    lotNumber: string;
    qtyKg: number;
    packing: {
        form: "Bulk" | "Bag" | "Silo";
        size?: number | undefined;
        unit?: string | undefined;
    };
    destination: "Inventory" | "DirectFarm";
    gmpPlusMarkings?: string[] | undefined;
}>;
export declare const BatchSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    batchNumber: z.ZodString;
    mixOrderId: z.ZodString;
    producedQtyKg: z.ZodNumber;
    startAt: z.ZodString;
    endAt: z.ZodOptional<z.ZodString>;
    status: z.ZodDefault<z.ZodEnum<["Released", "Quarantine", "Rejected"]>>;
    parentBatches: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    labels: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    inputs: z.ZodDefault<z.ZodArray<z.ZodObject<{
        batchId: z.ZodString;
        ingredientLotId: z.ZodString;
        plannedKg: z.ZodNumber;
        actualKg: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        batchId: string;
        ingredientLotId: string;
        plannedKg: number;
        actualKg: number;
    }, {
        batchId: string;
        ingredientLotId: string;
        plannedKg: number;
        actualKg: number;
    }>, "many">>;
    outputs: z.ZodDefault<z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        batchId: z.ZodString;
        lotNumber: z.ZodString;
        qtyKg: z.ZodNumber;
        packing: z.ZodObject<{
            form: z.ZodEnum<["Bulk", "Bag", "Silo"]>;
            size: z.ZodOptional<z.ZodNumber>;
            unit: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        }, {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        }>;
        destination: z.ZodEnum<["Inventory", "DirectFarm"]>;
        gmpPlusMarkings: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        batchId: string;
        lotNumber: string;
        qtyKg: number;
        packing: {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        };
        destination: "Inventory" | "DirectFarm";
        gmpPlusMarkings?: string[] | undefined;
    }, {
        id: string;
        batchId: string;
        lotNumber: string;
        qtyKg: number;
        packing: {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        };
        destination: "Inventory" | "DirectFarm";
        gmpPlusMarkings?: string[] | undefined;
    }>, "many">>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    batchNumber: string;
    mixOrderId: string;
    producedQtyKg: number;
    startAt: string;
    status: "Released" | "Quarantine" | "Rejected";
    parentBatches: string[];
    labels: string[];
    inputs: {
        batchId: string;
        ingredientLotId: string;
        plannedKg: number;
        actualKg: number;
    }[];
    outputs: {
        id: string;
        batchId: string;
        lotNumber: string;
        qtyKg: number;
        packing: {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        };
        destination: "Inventory" | "DirectFarm";
        gmpPlusMarkings?: string[] | undefined;
    }[];
    createdAt: string;
    updatedAt: string;
    endAt?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}, {
    id: string;
    tenantId: string;
    batchNumber: string;
    mixOrderId: string;
    producedQtyKg: number;
    startAt: string;
    createdAt: string;
    updatedAt: string;
    endAt?: string | undefined;
    status?: "Released" | "Quarantine" | "Rejected" | undefined;
    parentBatches?: string[] | undefined;
    labels?: string[] | undefined;
    inputs?: {
        batchId: string;
        ingredientLotId: string;
        plannedKg: number;
        actualKg: number;
    }[] | undefined;
    outputs?: {
        id: string;
        batchId: string;
        lotNumber: string;
        qtyKg: number;
        packing: {
            form: "Bulk" | "Bag" | "Silo";
            size?: number | undefined;
            unit?: string | undefined;
        };
        destination: "Inventory" | "DirectFarm";
        gmpPlusMarkings?: string[] | undefined;
    }[] | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}>;
export type Batch = z.infer<typeof BatchSchema>;
export type BatchInput = z.infer<typeof BatchInputSchema>;
export type BatchOutputLot = z.infer<typeof BatchOutputLotSchema>;
export declare class BatchEntity {
    private data;
    constructor(data: Batch);
    get id(): string;
    get tenantId(): string;
    get batchNumber(): string;
    get mixOrderId(): string;
    get producedQtyKg(): number;
    get startAt(): string;
    get endAt(): string | undefined;
    get status(): string;
    get parentBatches(): string[];
    get labels(): string[];
    get inputs(): BatchInput[];
    get outputs(): BatchOutputLot[];
    get createdAt(): string;
    get updatedAt(): string;
    isReleased(): boolean;
    isInQuarantine(): boolean;
    isRejected(): boolean;
    isCompleted(): boolean;
    isInProgress(): boolean;
    canRelease(): boolean;
    canReject(): boolean;
    canQuarantine(): boolean;
    isRework(): boolean;
    hasGMPPlusMarking(): boolean;
    getTotalInputKg(): number;
    getTotalOutputKg(): number;
    getYield(): number;
    getDurationHours(): number;
    getIngredientLotIds(): string[];
    getOutputLotNumbers(): string[];
    private validateBusinessRules;
    release(updatedBy?: string): BatchEntity;
    reject(reason?: string, updatedBy?: string): BatchEntity;
    quarantine(reason?: string, updatedBy?: string): BatchEntity;
    complete(endAt: string, updatedBy?: string): BatchEntity;
    addInput(input: BatchInput, updatedBy?: string): BatchEntity;
    addOutput(output: BatchOutputLot, updatedBy?: string): BatchEntity;
    addLabel(label: string, updatedBy?: string): BatchEntity;
    removeLabel(label: string, updatedBy?: string): BatchEntity;
    addParentBatch(parentBatchId: string, updatedBy?: string): BatchEntity;
    getTraceabilityData(): any;
    toJSON(): Batch;
    static create(data: Omit<Batch, 'id' | 'createdAt' | 'updatedAt'>): BatchEntity;
    static fromJSON(data: Batch): BatchEntity;
}
export {};
//# sourceMappingURL=batch.d.ts.map