import { z } from 'zod';
export declare const PriceListStatusEnum: z.ZodEnum<["Draft", "Active", "Archived"]>;
export type PriceListStatus = z.infer<typeof PriceListStatusEnum>;
export declare const TierBreakSchema: z.ZodObject<{
    minQty: z.ZodNumber;
    maxQty: z.ZodOptional<z.ZodNumber>;
    price: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    minQty: number;
    price: number;
    maxQty?: number | undefined;
}, {
    minQty: number;
    price: number;
    maxQty?: number | undefined;
}>;
export type TierBreak = z.infer<typeof TierBreakSchema>;
export declare const PriceListLineSchema: z.ZodObject<{
    sku: z.ZodString;
    commodity: z.ZodOptional<z.ZodString>;
    basePrice: z.ZodNumber;
    uom: z.ZodDefault<z.ZodString>;
    currency: z.ZodDefault<z.ZodString>;
    tierBreaks: z.ZodOptional<z.ZodArray<z.ZodObject<{
        minQty: z.ZodNumber;
        maxQty: z.ZodOptional<z.ZodNumber>;
        price: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        minQty: number;
        price: number;
        maxQty?: number | undefined;
    }, {
        minQty: number;
        price: number;
        maxQty?: number | undefined;
    }>, "many">>;
    minQty: z.ZodOptional<z.ZodNumber>;
    description: z.ZodOptional<z.ZodString>;
    active: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    sku: string;
    basePrice: number;
    uom: string;
    currency: string;
    active: boolean;
    minQty?: number | undefined;
    commodity?: string | undefined;
    tierBreaks?: {
        minQty: number;
        price: number;
        maxQty?: number | undefined;
    }[] | undefined;
    description?: string | undefined;
}, {
    sku: string;
    basePrice: number;
    minQty?: number | undefined;
    commodity?: string | undefined;
    uom?: string | undefined;
    currency?: string | undefined;
    tierBreaks?: {
        minQty: number;
        price: number;
        maxQty?: number | undefined;
    }[] | undefined;
    description?: string | undefined;
    active?: boolean | undefined;
}>;
export type PriceListLine = z.infer<typeof PriceListLineSchema>;
export declare const PriceListSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    code: z.ZodOptional<z.ZodString>;
    currency: z.ZodDefault<z.ZodString>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    lines: z.ZodArray<z.ZodObject<{
        sku: z.ZodString;
        commodity: z.ZodOptional<z.ZodString>;
        basePrice: z.ZodNumber;
        uom: z.ZodDefault<z.ZodString>;
        currency: z.ZodDefault<z.ZodString>;
        tierBreaks: z.ZodOptional<z.ZodArray<z.ZodObject<{
            minQty: z.ZodNumber;
            maxQty: z.ZodOptional<z.ZodNumber>;
            price: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }>, "many">>;
        minQty: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
        active: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }, {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }>, "many">;
    status: z.ZodDefault<z.ZodEnum<["Draft", "Active", "Archived"]>>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
    activatedAt: z.ZodOptional<z.ZodString>;
    activatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "Draft" | "Active" | "Archived";
    currency: string;
    tenantId: string;
    name: string;
    validFrom: string;
    lines: {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }[];
    code?: string | undefined;
    description?: string | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    activatedAt?: string | undefined;
    activatedBy?: string | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    lines: {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }[];
    code?: string | undefined;
    status?: "Draft" | "Active" | "Archived" | undefined;
    currency?: string | undefined;
    description?: string | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    activatedAt?: string | undefined;
    activatedBy?: string | undefined;
}>;
export type PriceList = z.infer<typeof PriceListSchema>;
export declare const CreatePriceListSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    code: z.ZodOptional<z.ZodString>;
    currency: z.ZodDefault<z.ZodString>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    lines: z.ZodArray<z.ZodObject<{
        sku: z.ZodString;
        commodity: z.ZodOptional<z.ZodString>;
        basePrice: z.ZodNumber;
        uom: z.ZodDefault<z.ZodString>;
        currency: z.ZodDefault<z.ZodString>;
        tierBreaks: z.ZodOptional<z.ZodArray<z.ZodObject<{
            minQty: z.ZodNumber;
            maxQty: z.ZodOptional<z.ZodNumber>;
            price: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }>, "many">>;
        minQty: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
        active: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }, {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }>, "many">;
    status: z.ZodDefault<z.ZodEnum<["Draft", "Active", "Archived"]>>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
    activatedAt: z.ZodOptional<z.ZodString>;
    activatedBy: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt" | "activatedAt">, "strip", z.ZodTypeAny, {
    status: "Draft" | "Active" | "Archived";
    currency: string;
    tenantId: string;
    name: string;
    validFrom: string;
    lines: {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }[];
    code?: string | undefined;
    description?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    activatedBy?: string | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    lines: {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }[];
    code?: string | undefined;
    status?: "Draft" | "Active" | "Archived" | undefined;
    currency?: string | undefined;
    description?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    activatedBy?: string | undefined;
}>;
export type CreatePriceList = z.infer<typeof CreatePriceListSchema>;
export declare const UpdatePriceListSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    tenantId: z.ZodOptional<z.ZodString>;
    name: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    code: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    currency: z.ZodOptional<z.ZodDefault<z.ZodString>>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    lines: z.ZodOptional<z.ZodArray<z.ZodObject<{
        sku: z.ZodString;
        commodity: z.ZodOptional<z.ZodString>;
        basePrice: z.ZodNumber;
        uom: z.ZodDefault<z.ZodString>;
        currency: z.ZodDefault<z.ZodString>;
        tierBreaks: z.ZodOptional<z.ZodArray<z.ZodObject<{
            minQty: z.ZodNumber;
            maxQty: z.ZodOptional<z.ZodNumber>;
            price: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }, {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }>, "many">>;
        minQty: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
        active: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }, {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }>, "many">>;
    status: z.ZodOptional<z.ZodDefault<z.ZodEnum<["Draft", "Active", "Archived"]>>>;
    createdAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    createdBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    activatedAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    activatedBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
}, "id" | "tenantId" | "createdAt" | "createdBy">, "strip", z.ZodTypeAny, {
    code?: string | undefined;
    status?: "Draft" | "Active" | "Archived" | undefined;
    currency?: string | undefined;
    description?: string | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    lines?: {
        sku: string;
        basePrice: number;
        uom: string;
        currency: string;
        active: boolean;
        minQty?: number | undefined;
        commodity?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
    }[] | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    activatedAt?: string | undefined;
    activatedBy?: string | undefined;
}, {
    code?: string | undefined;
    status?: "Draft" | "Active" | "Archived" | undefined;
    currency?: string | undefined;
    description?: string | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    lines?: {
        sku: string;
        basePrice: number;
        minQty?: number | undefined;
        commodity?: string | undefined;
        uom?: string | undefined;
        currency?: string | undefined;
        tierBreaks?: {
            minQty: number;
            price: number;
            maxQty?: number | undefined;
        }[] | undefined;
        description?: string | undefined;
        active?: boolean | undefined;
    }[] | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    activatedAt?: string | undefined;
    activatedBy?: string | undefined;
}>;
export type UpdatePriceList = z.infer<typeof UpdatePriceListSchema>;
//# sourceMappingURL=price-list.d.ts.map