import { z } from 'zod';
export declare const FulfilmentSchema: z.ZodObject<{
    contractId: z.ZodString;
    tenantId: z.ZodString;
    deliveredQty: z.ZodDefault<z.ZodNumber>;
    pricedQty: z.ZodDefault<z.ZodNumber>;
    invoicedQty: z.ZodDefault<z.ZodNumber>;
    openQty: z.ZodNumber;
    avgPrice: z.ZodOptional<z.ZodNumber>;
    timeline: z.ZodDefault<z.ZodArray<z.ZodObject<{
        event: z.ZodString;
        timestamp: z.ZodString;
        qty: z.ZodOptional<z.ZodNumber>;
        price: z.ZodOptional<z.ZodNumber>;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        event: string;
        timestamp: string;
        notes?: string | undefined;
        qty?: number | undefined;
        price?: number | undefined;
    }, {
        event: string;
        timestamp: string;
        notes?: string | undefined;
        qty?: number | undefined;
        price?: number | undefined;
    }>, "many">>;
    lastUpdated: z.ZodOptional<z.ZodDate>;
}, "strip", z.ZodTypeAny, {
    contractId: string;
    tenantId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    timeline: {
        event: string;
        timestamp: string;
        notes?: string | undefined;
        qty?: number | undefined;
        price?: number | undefined;
    }[];
    avgPrice?: number | undefined;
    lastUpdated?: Date | undefined;
}, {
    contractId: string;
    tenantId: string;
    openQty: number;
    deliveredQty?: number | undefined;
    pricedQty?: number | undefined;
    invoicedQty?: number | undefined;
    avgPrice?: number | undefined;
    timeline?: {
        event: string;
        timestamp: string;
        notes?: string | undefined;
        qty?: number | undefined;
        price?: number | undefined;
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
    timeline: Array<{
        event: string;
        timestamp: Date;
        qty?: number;
        price?: number;
        notes?: string;
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
    timeline: Array<{
        event: string;
        timestamp: Date;
        qty?: number;
        price?: number;
        notes?: string;
    }>;
    lastUpdated: Date;
    constructor(props: FulfilmentEntity);
    addDelivery(qty: number, notes?: string): void;
    addPricing(qty: number, price: number, notes?: string): void;
    addInvoicing(qty: number, notes?: string): void;
    private updateAveragePrice;
    getFulfilmentPercentage(): number;
    isFullyFulfilled(): boolean;
}
//# sourceMappingURL=fulfilment.d.ts.map