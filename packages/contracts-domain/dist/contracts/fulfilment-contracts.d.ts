import { z } from 'zod';
export declare const FulfilmentResponseSchema: z.ZodObject<{
    contractId: z.ZodString;
    tenantId: z.ZodString;
    deliveredQty: z.ZodNumber;
    pricedQty: z.ZodNumber;
    invoicedQty: z.ZodNumber;
    openQty: z.ZodNumber;
    avgPrice: z.ZodOptional<z.ZodNumber>;
    timeline: z.ZodArray<z.ZodObject<{
        event: z.ZodString;
        timestamp: z.ZodString;
        qty: z.ZodOptional<z.ZodNumber>;
        price: z.ZodOptional<z.ZodNumber>;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
    }, {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
    }>, "many">;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    contractId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    timeline: {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
    }[];
    lastUpdated: string;
    avgPrice?: number | undefined;
}, {
    tenantId: string;
    contractId: string;
    deliveredQty: number;
    pricedQty: number;
    invoicedQty: number;
    openQty: number;
    timeline: {
        event: string;
        timestamp: string;
        qty?: number | undefined;
        notes?: string | undefined;
        price?: number | undefined;
    }[];
    lastUpdated: string;
    avgPrice?: number | undefined;
}>;
export declare const PricingFixingSchema: z.ZodObject<{
    kind: z.ZodEnum<["BASIS", "FUTURES", "MIN_PRICE_DECISION"]>;
    value: z.ZodNumber;
    futuresMonth: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    value: number;
    kind: "BASIS" | "FUTURES" | "MIN_PRICE_DECISION";
    futuresMonth?: string | undefined;
    notes?: string | undefined;
}, {
    value: number;
    kind: "BASIS" | "FUTURES" | "MIN_PRICE_DECISION";
    futuresMonth?: string | undefined;
    notes?: string | undefined;
}>;
export type FulfilmentResponse = z.infer<typeof FulfilmentResponseSchema>;
export type PricingFixing = z.infer<typeof PricingFixingSchema>;
//# sourceMappingURL=fulfilment-contracts.d.ts.map