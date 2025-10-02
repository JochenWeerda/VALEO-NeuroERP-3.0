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
    sku: string;
    name: string;
    quantity: number;
    unitPrice: number;
    discount: number;
    totalNet: number;
    totalGross: number;
    description?: string | undefined;
}, {
    id: string;
    sku: string;
    name: string;
    quantity: number;
    unitPrice: number;
    totalNet: number;
    totalGross: number;
    description?: string | undefined;
    discount?: number | undefined;
}>;
export declare const QuoteStatusContractSchema: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
export declare const CreateQuoteContractSchema: z.ZodObject<{
    status: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    quoteNumber: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    validUntil: z.ZodDate;
    notes: z.ZodOptional<z.ZodString>;
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
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }, {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    tenantId: string;
    customerId: string;
    quoteNumber: string;
    lines: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[];
    taxRate: number;
    currency: string;
    validUntil: Date;
    notes?: string | undefined;
}, {
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    tenantId: string;
    customerId: string;
    quoteNumber: string;
    lines: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    validUntil: Date;
    taxRate?: number | undefined;
    currency?: string | undefined;
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
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }, {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }>, "many">>;
    validUntil: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    lines?: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[] | undefined;
    validUntil?: Date | undefined;
    notes?: string | null | undefined;
}, {
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    lines?: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[] | undefined;
    validUntil?: Date | undefined;
    notes?: string | null | undefined;
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
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
    }, {
        id: string;
        sku: string;
        name: string;
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
    totalNet: number;
    totalGross: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    customerId: string;
    quoteNumber: string;
    lines: {
        id: string;
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
    }[];
    subtotalNet: number;
    totalDiscount: number;
    taxRate: number;
    currency: string;
    validUntil: Date;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    notes?: string | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    customerId: string;
    quoteNumber: string;
    lines: {
        id: string;
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        totalNet: number;
        totalGross: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    subtotalNet: number;
    totalDiscount: number;
    validUntil: Date;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    taxRate?: number | undefined;
    currency?: string | undefined;
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
    customerId?: string | undefined;
    search?: string | undefined;
    validUntilFrom?: string | undefined;
    validUntilTo?: string | undefined;
}, {
    status?: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired" | undefined;
    customerId?: string | undefined;
    search?: string | undefined;
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
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }, {
            id: string;
            sku: string;
            name: string;
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
        totalNet: number;
        totalGross: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        customerId: string;
        quoteNumber: string;
        lines: {
            id: string;
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        taxRate: number;
        currency: string;
        validUntil: Date;
        createdAt: Date;
        updatedAt: Date;
        version: number;
        notes?: string | undefined;
    }, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        customerId: string;
        quoteNumber: string;
        lines: {
            id: string;
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
            discount?: number | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        validUntil: Date;
        createdAt: Date;
        updatedAt: Date;
        version: number;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
    }>, "many">;
    pagination: z.ZodObject<{
        page: z.ZodNumber;
        pageSize: z.ZodNumber;
        total: z.ZodNumber;
        totalPages: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }, {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    }>;
}, "strip", z.ZodTypeAny, {
    data: {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        customerId: string;
        quoteNumber: string;
        lines: {
            id: string;
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            discount: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        taxRate: number;
        currency: string;
        validUntil: Date;
        createdAt: Date;
        updatedAt: Date;
        version: number;
        notes?: string | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
        customerId: string;
        quoteNumber: string;
        lines: {
            id: string;
            sku: string;
            name: string;
            quantity: number;
            unitPrice: number;
            totalNet: number;
            totalGross: number;
            description?: string | undefined;
            discount?: number | undefined;
        }[];
        subtotalNet: number;
        totalDiscount: number;
        validUntil: Date;
        createdAt: Date;
        updatedAt: Date;
        version: number;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=quote-contracts.d.ts.map