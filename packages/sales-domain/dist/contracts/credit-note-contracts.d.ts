import { z } from 'zod';
export declare const CreditNoteLineContractSchema: z.ZodObject<{
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
export declare const CreditNoteStatusContractSchema: z.ZodEnum<["Issued", "Settled"]>;
export declare const CreateCreditNoteContractSchema: z.ZodObject<{
    tenantId: z.ZodString;
    customerId: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    invoiceId: z.ZodString;
    creditNumber: z.ZodString;
    reason: z.ZodString;
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
    tenantId: string;
    customerId: string;
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
    invoiceId: string;
    creditNumber: string;
    reason: string;
    notes?: string | undefined;
}, {
    tenantId: string;
    customerId: string;
    lines: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    invoiceId: string;
    creditNumber: string;
    reason: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
}>;
export declare const UpdateCreditNoteContractSchema: z.ZodObject<{
    reason: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Settled"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Issued" | "Settled" | undefined;
    notes?: string | null | undefined;
    reason?: string | undefined;
}, {
    status?: "Issued" | "Settled" | undefined;
    notes?: string | null | undefined;
    reason?: string | undefined;
}>;
export declare const CreditNoteResponseContractSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    invoiceId: z.ZodString;
    creditNumber: z.ZodString;
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
    reason: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Issued", "Settled"]>;
    settledAt: z.ZodOptional<z.ZodDate>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Issued" | "Settled";
    customerId: string;
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
    createdAt: Date;
    updatedAt: Date;
    version: number;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    notes?: string | undefined;
    settledAt?: Date | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Issued" | "Settled";
    customerId: string;
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
    createdAt: Date;
    updatedAt: Date;
    version: number;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    settledAt?: Date | undefined;
}>;
export declare const CreditNoteQueryContractSchema: z.ZodObject<{
    customerId: z.ZodOptional<z.ZodString>;
    invoiceId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Settled"]>>;
    search: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
    pageSize: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Issued" | "Settled" | undefined;
    customerId?: string | undefined;
    invoiceId?: string | undefined;
    search?: string | undefined;
}, {
    status?: "Issued" | "Settled" | undefined;
    customerId?: string | undefined;
    invoiceId?: string | undefined;
    search?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
export declare const CreditNoteListResponseContractSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        tenantId: z.ZodString;
        customerId: z.ZodString;
        invoiceId: z.ZodString;
        creditNumber: z.ZodString;
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
        reason: z.ZodString;
        notes: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Issued", "Settled"]>;
        settledAt: z.ZodOptional<z.ZodDate>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Issued" | "Settled";
        customerId: string;
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
        createdAt: Date;
        updatedAt: Date;
        version: number;
        invoiceId: string;
        creditNumber: string;
        reason: string;
        notes?: string | undefined;
        settledAt?: Date | undefined;
    }, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Issued" | "Settled";
        customerId: string;
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
        createdAt: Date;
        updatedAt: Date;
        version: number;
        invoiceId: string;
        creditNumber: string;
        reason: string;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
        settledAt?: Date | undefined;
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
        status: "Issued" | "Settled";
        customerId: string;
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
        createdAt: Date;
        updatedAt: Date;
        version: number;
        invoiceId: string;
        creditNumber: string;
        reason: string;
        notes?: string | undefined;
        settledAt?: Date | undefined;
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
        status: "Issued" | "Settled";
        customerId: string;
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
        createdAt: Date;
        updatedAt: Date;
        version: number;
        invoiceId: string;
        creditNumber: string;
        reason: string;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
        settledAt?: Date | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=credit-note-contracts.d.ts.map