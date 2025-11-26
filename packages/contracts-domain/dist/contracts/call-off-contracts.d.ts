import { z } from 'zod';
export declare const CallOffStatusEnum: z.ZodEnum<["Planned", "Scheduled", "Delivered", "Invoiced", "Cancelled"]>;
export declare const CreateCallOffSchema: z.ZodObject<{
    qty: z.ZodNumber;
    window: z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>;
    site: z.ZodOptional<z.ZodString>;
    silo: z.ZodOptional<z.ZodString>;
    customerYard: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    qty: number;
    window: {
        from: string;
        to: string;
    };
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}, {
    qty: number;
    window: {
        from: string;
        to: string;
    };
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}>;
export declare const UpdateCallOffSchema: z.ZodObject<{
    qty: z.ZodOptional<z.ZodNumber>;
    window: z.ZodOptional<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>>;
    site: z.ZodOptional<z.ZodString>;
    silo: z.ZodOptional<z.ZodString>;
    customerYard: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    qty?: number | undefined;
    notes?: string | undefined;
    window?: {
        from: string;
        to: string;
    } | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}, {
    qty?: number | undefined;
    notes?: string | undefined;
    window?: {
        from: string;
        to: string;
    } | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}>;
export declare const CallOffResponseSchema: z.ZodObject<{
    id: z.ZodString;
    contractId: z.ZodString;
    tenantId: z.ZodString;
    qty: z.ZodNumber;
    window: z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>;
    site: z.ZodOptional<z.ZodString>;
    silo: z.ZodOptional<z.ZodString>;
    customerYard: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Planned", "Scheduled", "Delivered", "Invoiced", "Cancelled"]>;
    notes: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    status: "Cancelled" | "Planned" | "Scheduled" | "Delivered" | "Invoiced";
    id: string;
    tenantId: string;
    qty: number;
    createdAt: string;
    updatedAt: string;
    version: number;
    contractId: string;
    window: {
        from: string;
        to: string;
    };
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}, {
    status: "Cancelled" | "Planned" | "Scheduled" | "Delivered" | "Invoiced";
    id: string;
    tenantId: string;
    qty: number;
    createdAt: string;
    updatedAt: string;
    version: number;
    contractId: string;
    window: {
        from: string;
        to: string;
    };
    notes?: string | undefined;
    site?: string | undefined;
    silo?: string | undefined;
    customerYard?: string | undefined;
}>;
export declare const MarkDeliveredSchema: z.ZodObject<{
    actualQty: z.ZodOptional<z.ZodNumber>;
    notes: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    notes?: string | undefined;
    actualQty?: number | undefined;
}, {
    notes?: string | undefined;
    actualQty?: number | undefined;
}>;
export type CreateCallOff = z.infer<typeof CreateCallOffSchema>;
export type UpdateCallOff = z.infer<typeof UpdateCallOffSchema>;
export type CallOffResponse = z.infer<typeof CallOffResponseSchema>;
export type MarkDelivered = z.infer<typeof MarkDeliveredSchema>;
//# sourceMappingURL=call-off-contracts.d.ts.map