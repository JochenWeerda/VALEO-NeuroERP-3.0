import { z } from 'zod';
export declare const FulfilmentSchema: z.ZodObject<{
    contractId: z.ZodString;
    tenantId: z.ZodString;
    deliveredQty: z.ZodDefault<z.ZodNumber>;
    pricedQty: z.ZodDefault<z.ZodNumber>;
    invoicedQty: z.ZodDefault<z.ZodNumber>;
    openQty: z.ZodNumber;
    avgPrice: z.ZodOptional<z.ZodNumber>;
    qualityScore: z.ZodOptional<z.ZodNumber>;
    onTimeDeliveryRate: z.ZodOptional<z.ZodNumber>;
    deliverySchedule: z.ZodDefault<z.ZodArray<z.ZodObject<{
        plannedDate: z.ZodString;
        actualDate: z.ZodOptional<z.ZodString>;
        qty: z.ZodNumber;
        status: z.ZodEnum<["PENDING", "DELIVERED", "DELAYED", "CANCELLED"]>;
        qualityCheck: z.ZodOptional<z.ZodObject<{
            passed: z.ZodBoolean;
            score: z.ZodOptional<z.ZodNumber>;
            notes: z.ZodOptional<z.ZodString>;
            inspector: z.ZodOptional<z.ZodString>;
            inspectionDate: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        }, {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        status: "CANCELLED" | "PENDING" | "DELIVERED" | "DELAYED";
        qty: number;
        plannedDate: string;
        actualDate?: string | undefined;
        qualityCheck?: {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        } | undefined;
    }, {
        status: "CANCELLED" | "PENDING" | "DELIVERED" | "DELAYED";
        qty: number;
        plannedDate: string;
        actualDate?: string | undefined;
        qualityCheck?: {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        } | undefined;
    }>, "many">>;
    timeline: z.ZodDefault<z.ZodArray<z.ZodObject<{
        event: z.ZodString;
        timestamp: z.ZodString;
        qty: z.ZodOptional<z.ZodNumber>;
        price: z.ZodOptional<z.ZodNumber>;
        notes: z.ZodOptional<z.ZodString>;
        qualityData: z.ZodOptional<z.ZodObject<{
            score: z.ZodOptional<z.ZodNumber>;
            issues: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        }, "strip", z.ZodTypeAny, {
            issues?: string[] | undefined;
            score?: number | undefined;
        }, {
            issues?: string[] | undefined;
            score?: number | undefined;
        }>>;
        deliveryData: z.ZodOptional<z.ZodObject<{
            deliveryNote: z.ZodOptional<z.ZodString>;
            batchNumbers: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
            storageLocation: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        }, {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
        qualityData?: {
            issues?: string[] | undefined;
            score?: number | undefined;
        } | undefined;
        deliveryData?: {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        } | undefined;
    }, {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
        qualityData?: {
            issues?: string[] | undefined;
            score?: number | undefined;
        } | undefined;
        deliveryData?: {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        } | undefined;
    }>, "many">>;
    lastUpdated: z.ZodOptional<z.ZodDate>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    contractId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    deliverySchedule: {
        status: "CANCELLED" | "PENDING" | "DELIVERED" | "DELAYED";
        qty: number;
        plannedDate: string;
        actualDate?: string | undefined;
        qualityCheck?: {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        } | undefined;
    }[];
    timeline: {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
        qualityData?: {
            issues?: string[] | undefined;
            score?: number | undefined;
        } | undefined;
        deliveryData?: {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        } | undefined;
    }[];
    avgPrice?: number | undefined;
    qualityScore?: number | undefined;
    onTimeDeliveryRate?: number | undefined;
    lastUpdated?: Date | undefined;
}, {
    tenantId: string;
    contractId: string;
    openQty: number;
    deliveredQty?: number | undefined;
    pricedQty?: number | undefined;
    invoicedQty?: number | undefined;
    avgPrice?: number | undefined;
    qualityScore?: number | undefined;
    onTimeDeliveryRate?: number | undefined;
    deliverySchedule?: {
        status: "CANCELLED" | "PENDING" | "DELIVERED" | "DELAYED";
        qty: number;
        plannedDate: string;
        actualDate?: string | undefined;
        qualityCheck?: {
            passed: boolean;
            notes?: string | undefined;
            score?: number | undefined;
            inspector?: string | undefined;
            inspectionDate?: string | undefined;
        } | undefined;
    }[] | undefined;
    timeline?: {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
        qualityData?: {
            issues?: string[] | undefined;
            score?: number | undefined;
        } | undefined;
        deliveryData?: {
            deliveryNote?: string | undefined;
            batchNumbers?: string[] | undefined;
            storageLocation?: string | undefined;
        } | undefined;
    }[] | undefined;
    lastUpdated?: Date | undefined;
}>;
export interface FulfilmentEntity {
    contractId: string;
    tenantId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    avgPrice?: number;
    qualityScore?: number;
    onTimeDeliveryRate?: number;
    deliverySchedule: Array<{
        plannedDate: Date;
        actualDate?: Date;
        qty: number;
        status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED';
        qualityCheck?: {
            passed: boolean;
            score?: number;
            notes?: string;
            inspector?: string;
            inspectionDate?: Date;
        };
    }>;
    timeline: Array<{
        event: string;
        timestamp: Date;
        qty?: number;
        price?: number;
        notes?: string;
        qualityData?: {
            score?: number;
            issues?: string[];
        };
        deliveryData?: {
            deliveryNote?: string;
            batchNumbers?: string[];
            storageLocation?: string;
        };
    }>;
    lastUpdated: Date;
}
export declare class Fulfilment implements FulfilmentEntity {
    contractId: string;
    tenantId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    avgPrice?: number;
    qualityScore?: number;
    onTimeDeliveryRate?: number;
    deliverySchedule: Array<{
        plannedDate: Date;
        actualDate?: Date;
        qty: number;
        status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED';
        qualityCheck?: {
            passed: boolean;
            score?: number;
            notes?: string;
            inspector?: string;
            inspectionDate?: Date;
        };
    }>;
    timeline: Array<{
        event: string;
        timestamp: Date;
        qty?: number;
        price?: number;
        notes?: string;
        qualityData?: {
            score?: number;
            issues?: string[];
        };
        deliveryData?: {
            deliveryNote?: string;
            batchNumbers?: string[];
            storageLocation?: string;
        };
    }>;
    lastUpdated: Date;
    constructor(props: FulfilmentEntity);
    addDelivery(qty: number, deliveryData?: {
        deliveryNote?: string;
        batchNumbers?: string[];
        storageLocation?: string;
        qualityData?: {
            score?: number;
            issues?: string[];
        };
    }, notes?: string): void;
    addPricing(qty: number, price: number, notes?: string): void;
    addInvoicing(qty: number, notes?: string): void;
    private updateAveragePrice;
    private updateQualityScore;
    private updateDeliveryMetrics;
    getFulfilmentPercentage(): number;
    isFullyFulfilled(): boolean;
    addDeliveryScheduleItem(plannedDate: Date, qty: number): void;
    updateDeliveryStatus(index: number, status: 'PENDING' | 'DELIVERED' | 'DELAYED' | 'CANCELLED', actualDate?: Date): void;
    addQualityCheck(deliveryIndex: number, qualityCheck: {
        passed: boolean;
        score?: number;
        notes?: string;
        inspector?: string;
    }): void;
    getDelayedDeliveries(): Array<{
        plannedDate: Date;
        delayDays: number;
    }>;
    getUpcomingDeliveries(daysAhead?: number): Array<{
        plannedDate: Date;
        qty: number;
    }>;
    getFulfilmentSummary(): {
        totalContracted: number;
        delivered: number;
        remaining: number;
        fulfilmentRate: number;
        qualityScore?: number | undefined;
        onTimeDeliveryRate?: number | undefined;
        nextDelivery?: Date | undefined;
    };
}
//# sourceMappingURL=fulfilment.d.ts.map