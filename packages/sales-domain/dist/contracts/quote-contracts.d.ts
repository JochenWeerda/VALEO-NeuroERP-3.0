import { z } from 'zod';
export declare const QuoteLineContractSchema: z.ZodObject<{
    id: z.ZodString;
    sku: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    quantity: z.ZodNumber;
    unitPrice: z.ZodNumber;
    discount: z.ZodDefault<z.ZodNumber>;
    totalNet: z.ZodNumber;
    totalGross: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    name: string;
    sku: string;
    quantity: number;
    unitPrice: number;
    discount: number;
    totalNet: number;
    totalGross: number;
    description?: string | undefined;
}, {
    id: string;
    name: string;
    sku: string;
    quantity: number;
    unitPrice: number;
    totalNet: number;
    totalGross: number;
    description?: string | undefined;
    discount?: number | undefined;
}>;
export declare const QuoteStatusContractSchema: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
export declare const CreateQuoteContractSchema: z.ZodObject<{
    currency: z.ZodDefault<z.ZodString>;
    taxRate: z.ZodDefault<z.ZodNumber>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
    validUntil: z.ZodDate;
    customerId: z.ZodString;
    tenantId: z.ZodString;
    quoteNumber: z.ZodString;
} & {
    lines: z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        sku: z.ZodString;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        quantity: z.ZodNumber;
        unitPrice: z.ZodNumber;
        discount: z.ZodDefault<z.ZodNumber>;
        totalNet: z.ZodNumber;
        totalGross: z.ZodNumber;
    }, "id" | "totalNet" | "totalGross">, "strip", z.ZodTypeAny, {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }, {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    currency: string;
    taxRate: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    validUntil: Date;
    customerId: string;
    tenantId: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[];
    quoteNumber: string;
    notes?: string | undefined;
}, {
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    validUntil: Date;
    customerId: string;
    tenantId: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    quoteNumber: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
    notes?: string | undefined;
}>;
export declare const UpdateQuoteContractSchema: z.ZodObject<{
    lines: z.ZodOptional<z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        sku: z.ZodString;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        quantity: z.ZodNumber;
        unitPrice: z.ZodNumber;
        discount: z.ZodDefault<z.ZodNumber>;
        totalNet: z.ZodNumber;
        totalGross: z.ZodNumber;
    }, "id" | "totalNet" | "totalGross">, "strip", z.ZodTypeAny, {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }, {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }>, "many">>;
    validUntil: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>>;
}, "strip", z.ZodTypeAny, {
    notes?: string | null | undefined;
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    validUntil?: Date | undefined;
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[] | undefined;
}, {
    notes?: string | null | undefined;
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    validUntil?: Date | undefined;
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[] | undefined;
}>;
export declare const QuoteResponseContractSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    quoteNumber: z.ZodString;
    lines: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        sku: z.ZodString;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        quantity: z.ZodNumber;
        unitPrice: z.ZodNumber;
        discount: z.ZodDefault<z.ZodNumber>;
        totalNet: z.ZodNumber;
        totalGross: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
    }, {
        id: string;
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
        discount?: number | undefined;
    }>, "many">;
    subtotalNet: z.ZodNumber;
    totalDiscount: z.ZodNumber;
    totalNet: z.ZodNumber;
    totalGross: z.ZodNumber;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    validUntil: z.ZodDate;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    currency: string;
    taxRate: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    version: number;
    createdAt: Date;
    updatedAt: Date;
    validUntil: Date;
    customerId: string;
    totalNet: number;
    totalGross: number;
    lines: {
        id: string;
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
    }[];
    subtotalNet: number;
    totalDiscount: number;
    quoteNumber: string;
    notes?: string | undefined;
}, {
    id: string;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    version: number;
    createdAt: Date;
    updatedAt: Date;
    validUntil: Date;
    customerId: string;
    totalNet: number;
    totalGross: number;
    lines: {
        id: string;
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    subtotalNet: number;
    totalDiscount: number;
    quoteNumber: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
    notes?: string | undefined;
}>;
export declare const QuoteQueryContractSchema: z.ZodObject<{
    customerId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>>;
    search: z.ZodOptional<z.ZodString>;
    validUntilFrom: z.ZodOptional<z.ZodString>;
    validUntilTo: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
    pageSize: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    search?: string | undefined;
    customerId?: string | undefined;
    validUntilFrom?: string | undefined;
    validUntilTo?: string | undefined;
}, {
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    search?: string | undefined;
    customerId?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    validUntilFrom?: string | undefined;
    validUntilTo?: string | undefined;
}>;
export declare const QuoteListResponseContractSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        tenantId: z.ZodString;
        customerId: z.ZodString;
        quoteNumber: z.ZodString;
        lines: z.ZodArray<z.ZodObject<{
            id: z.ZodString;
            sku: z.ZodString;
            name: z.ZodString;
            description: z.ZodOptional<z.ZodString>;
            quantity: z.ZodNumber;
            unitPrice: z.ZodNumber;
            discount: z.ZodDefault<z.ZodNumber>;
            totalNet: z.ZodNumber;
            totalGross: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }, {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
            discount?: number | undefined;
        }>, "many">;
        subtotalNet: z.ZodNumber;
        totalDiscount: z.ZodNumber;
        totalNet: z.ZodNumber;
        totalGross: z.ZodNumber;
        taxRate: z.ZodDefault<z.ZodNumber>;
        currency: z.ZodDefault<z.ZodString>;
        validUntil: z.ZodDate;
        notes: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        currency: string;
        taxRate: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        validUntil: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        lines: {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        quoteNumber: string;
        notes?: string | undefined;
    }, {
        id: string;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        validUntil: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        lines: {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
            discount?: number | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        quoteNumber: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        pageSize: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    }, {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        id: string;
        currency: string;
        taxRate: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        validUntil: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        lines: {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        quoteNumber: string;
        notes?: string | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}, {
    data: {
        id: string;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        validUntil: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        lines: {
            id: string;
            name: string;
            sku: string;
            quantity: number;
            unitPrice: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
            discount?: number | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        quoteNumber: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=quote-contracts.d.ts.map