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
export declare const CreditNoteStatusContractSchema: z.ZodEnum<["Issued", "Settled"]>;
export declare const CreateCreditNoteContractSchema: z.ZodObject<{
    currency: z.ZodDefault<z.ZodString>;
    taxRate: z.ZodDefault<z.ZodNumber>;
    notes: z.ZodOptional<z.ZodString>;
    customerId: z.ZodString;
    tenantId: z.ZodString;
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
    customerId: string;
    tenantId: string;
    invoiceId: string;
    creditNumber: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[];
    reason: string;
    notes?: string | undefined;
}, {
    customerId: string;
    tenantId: string;
    invoiceId: string;
    creditNumber: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    reason: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
    notes?: string | undefined;
}>;
export declare const UpdateCreditNoteContractSchema: z.ZodObject<{
    reason: z.ZodOptional<z.ZodString>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Settled"]>>;
}, "strip", z.ZodTypeAny, {
    notes?: string | null | undefined;
    status?: "Issued" | "Settled" | undefined;
    reason?: string | undefined;
}, {
    notes?: string | null | undefined;
    status?: "Issued" | "Settled" | undefined;
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
    reason: z.ZodString;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Issued", "Settled"]>;
    settledAt: z.ZodOptional<z.ZodDate>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    currency: string;
    taxRate: number;
    status: "Issued" | "Settled";
    version: number;
    createdAt: Date;
    updatedAt: Date;
    customerId: string;
    totalNet: number;
    totalGross: number;
    invoiceId: string;
    creditNumber: string;
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
    reason: string;
    notes?: string | undefined;
    settledAt?: Date | undefined;
}, {
    id: string;
    status: "Issued" | "Settled";
    version: number;
    createdAt: Date;
    updatedAt: Date;
    customerId: string;
    totalNet: number;
    totalGross: number;
    invoiceId: string;
    creditNumber: string;
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
    reason: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
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
    search?: string | undefined;
    customerId?: string | undefined;
    invoiceId?: string | undefined;
}, {
    status?: "Issued" | "Settled" | undefined;
    search?: string | undefined;
    customerId?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    invoiceId?: string | undefined;
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
        reason: z.ZodString;
        notes: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Issued", "Settled"]>;
        settledAt: z.ZodOptional<z.ZodDate>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        currency: string;
        taxRate: number;
        status: "Issued" | "Settled";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        invoiceId: string;
        creditNumber: string;
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
        reason: string;
        notes?: string | undefined;
        settledAt?: Date | undefined;
    }, {
        id: string;
        status: "Issued" | "Settled";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        invoiceId: string;
        creditNumber: string;
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
        reason: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
        settledAt?: Date | undefined;
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
        status: "Issued" | "Settled";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        invoiceId: string;
        creditNumber: string;
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
        reason: string;
        notes?: string | undefined;
        settledAt?: Date | undefined;
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
        status: "Issued" | "Settled";
        version: number;
        createdAt: Date;
        updatedAt: Date;
        customerId: string;
        totalNet: number;
        totalGross: number;
        invoiceId: string;
        creditNumber: string;
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
        reason: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
        settledAt?: Date | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=credit-note-contracts.d.ts.map