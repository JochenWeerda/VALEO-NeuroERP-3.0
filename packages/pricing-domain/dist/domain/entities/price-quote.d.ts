import { z } from 'zod';
export declare const PriceComponentTypeEnum: z.ZodEnum<["Base", "Condition", "Dynamic", "Charge", "Tax"]>;
export type PriceComponentType = z.infer<typeof PriceComponentTypeEnum>;
export declare const PriceComponentSchema: z.ZodObject<{
    type: z.ZodEnum<["Base", "Condition", "Dynamic", "Charge", "Tax"]>;
    key: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    value: z.ZodNumber;
    basis: z.ZodOptional<z.ZodNumber>;
    calculatedFrom: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    value: number;
    type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
    key: string;
    description?: string | undefined;
    basis?: number | undefined;
    calculatedFrom?: string | undefined;
}, {
    value: number;
    type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
    key: string;
    description?: string | undefined;
    basis?: number | undefined;
    calculatedFrom?: string | undefined;
}>;
export type PriceComponent = z.infer<typeof PriceComponentSchema>;
export declare const CalcQuoteInputSchema: z.ZodObject<{
    customerId: z.ZodString;
    sku: z.ZodString;
    qty: z.ZodNumber;
    channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI"]>>;
    deliveryWindow: z.ZodOptional<z.ZodObject<{
        from: z.ZodString;
        to: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        from: string;
        to: string;
    }, {
        from: string;
        to: string;
    }>>;
    siteId: z.ZodOptional<z.ZodString>;
    contractRef: z.ZodOptional<z.ZodString>;
    context: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    sku: string;
    customerId: string;
    qty: number;
    channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    deliveryWindow?: {
        from: string;
        to: string;
    } | undefined;
    siteId?: string | undefined;
    contractRef?: string | undefined;
    context?: Record<string, any> | undefined;
}, {
    sku: string;
    customerId: string;
    qty: number;
    channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    deliveryWindow?: {
        from: string;
        to: string;
    } | undefined;
    siteId?: string | undefined;
    contractRef?: string | undefined;
    context?: Record<string, any> | undefined;
}>;
export type CalcQuoteInput = z.infer<typeof CalcQuoteInputSchema>;
export declare const PriceQuoteSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    inputs: z.ZodObject<{
        customerId: z.ZodString;
        sku: z.ZodString;
        qty: z.ZodNumber;
        channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI"]>>;
        deliveryWindow: z.ZodOptional<z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>>;
        siteId: z.ZodOptional<z.ZodString>;
        contractRef: z.ZodOptional<z.ZodString>;
        context: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    }, {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    }>;
    components: z.ZodArray<z.ZodObject<{
        type: z.ZodEnum<["Base", "Condition", "Dynamic", "Charge", "Tax"]>;
        key: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        value: z.ZodNumber;
        basis: z.ZodOptional<z.ZodNumber>;
        calculatedFrom: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }, {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }>, "many">;
    totalNet: z.ZodNumber;
    totalGross: z.ZodOptional<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    calculatedAt: z.ZodOptional<z.ZodString>;
    expiresAt: z.ZodString;
    signature: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    currency: string;
    tenantId: string;
    inputs: {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    };
    components: {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }[];
    totalNet: number;
    expiresAt: string;
    id?: string | undefined;
    createdBy?: string | undefined;
    calculatedAt?: string | undefined;
    totalGross?: number | undefined;
    signature?: string | undefined;
}, {
    tenantId: string;
    inputs: {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    };
    components: {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }[];
    totalNet: number;
    expiresAt: string;
    currency?: string | undefined;
    id?: string | undefined;
    createdBy?: string | undefined;
    calculatedAt?: string | undefined;
    totalGross?: number | undefined;
    signature?: string | undefined;
}>;
export type PriceQuote = z.infer<typeof PriceQuoteSchema>;
export declare const CreatePriceQuoteSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    inputs: z.ZodObject<{
        customerId: z.ZodString;
        sku: z.ZodString;
        qty: z.ZodNumber;
        channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI"]>>;
        deliveryWindow: z.ZodOptional<z.ZodObject<{
            from: z.ZodString;
            to: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            from: string;
            to: string;
        }, {
            from: string;
            to: string;
        }>>;
        siteId: z.ZodOptional<z.ZodString>;
        contractRef: z.ZodOptional<z.ZodString>;
        context: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    }, {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    }>;
    components: z.ZodArray<z.ZodObject<{
        type: z.ZodEnum<["Base", "Condition", "Dynamic", "Charge", "Tax"]>;
        key: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        value: z.ZodNumber;
        basis: z.ZodOptional<z.ZodNumber>;
        calculatedFrom: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }, {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }>, "many">;
    totalNet: z.ZodNumber;
    totalGross: z.ZodOptional<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    calculatedAt: z.ZodOptional<z.ZodString>;
    expiresAt: z.ZodString;
    signature: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
}, "id" | "calculatedAt" | "signature">, "strip", z.ZodTypeAny, {
    currency: string;
    tenantId: string;
    inputs: {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    };
    components: {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }[];
    totalNet: number;
    expiresAt: string;
    createdBy?: string | undefined;
    totalGross?: number | undefined;
}, {
    tenantId: string;
    inputs: {
        sku: string;
        customerId: string;
        qty: number;
        channel?: "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        deliveryWindow?: {
            from: string;
            to: string;
        } | undefined;
        siteId?: string | undefined;
        contractRef?: string | undefined;
        context?: Record<string, any> | undefined;
    };
    components: {
        value: number;
        type: "Tax" | "Base" | "Condition" | "Dynamic" | "Charge";
        key: string;
        description?: string | undefined;
        basis?: number | undefined;
        calculatedFrom?: string | undefined;
    }[];
    totalNet: number;
    expiresAt: string;
    currency?: string | undefined;
    createdBy?: string | undefined;
    totalGross?: number | undefined;
}>;
export type CreatePriceQuote = z.infer<typeof CreatePriceQuoteSchema>;
//# sourceMappingURL=price-quote.d.ts.map