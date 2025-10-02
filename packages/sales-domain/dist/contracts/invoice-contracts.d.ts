import { z } from 'zod';
export declare const InvoiceLineContractSchema: z.ZodObject<{
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
export declare const InvoiceStatusContractSchema: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
export declare const CreateInvoiceContractSchema: z.ZodObject<{
    tenantId: z.ZodString;
    customerId: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    orderId: z.ZodOptional<z.ZodString>;
    invoiceNumber: z.ZodString;
    dueDate: z.ZodDate;
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
    invoiceNumber: string;
    dueDate: Date;
    notes?: string | undefined;
    orderId?: string | undefined;
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
    invoiceNumber: string;
    dueDate: Date;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    orderId?: string | undefined;
}>;
export declare const UpdateInvoiceContractSchema: z.ZodObject<{
    dueDate: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Cancelled" | "Issued" | "Paid" | "Overdue" | undefined;
    notes?: string | null | undefined;
    dueDate?: Date | undefined;
}, {
    status?: "Cancelled" | "Issued" | "Paid" | "Overdue" | undefined;
    notes?: string | null | undefined;
    dueDate?: Date | undefined;
}>;
export declare const InvoiceResponseContractSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    orderId: z.ZodOptional<z.ZodString>;
    invoiceNumber: z.ZodString;
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
    dueDate: z.ZodDate;
    paidAt: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
    invoiceNumber: string;
    dueDate: Date;
    notes?: string | undefined;
    orderId?: string | undefined;
    paidAt?: Date | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
    invoiceNumber: string;
    dueDate: Date;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    orderId?: string | undefined;
    paidAt?: Date | undefined;
}>;
export declare const InvoiceQueryContractSchema: z.ZodObject<{
    customerId: z.ZodOptional<z.ZodString>;
    orderId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>>;
    search: z.ZodOptional<z.ZodString>;
    dueDateFrom: z.ZodOptional<z.ZodString>;
    dueDateTo: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
    pageSize: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Cancelled" | "Issued" | "Paid" | "Overdue" | undefined;
    customerId?: string | undefined;
    search?: string | undefined;
    orderId?: string | undefined;
    dueDateFrom?: string | undefined;
    dueDateTo?: string | undefined;
}, {
    status?: "Cancelled" | "Issued" | "Paid" | "Overdue" | undefined;
    customerId?: string | undefined;
    search?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    orderId?: string | undefined;
    dueDateFrom?: string | undefined;
    dueDateTo?: string | undefined;
}>;
export declare const InvoiceListResponseContractSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        tenantId: z.ZodString;
        customerId: z.ZodString;
        orderId: z.ZodOptional<z.ZodString>;
        invoiceNumber: z.ZodString;
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
        dueDate: z.ZodDate;
        paidAt: z.ZodOptional<z.ZodDate>;
        notes: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
        invoiceNumber: string;
        dueDate: Date;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
    }, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
        invoiceNumber: string;
        dueDate: Date;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
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
        status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
        invoiceNumber: string;
        dueDate: Date;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
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
        status: "Cancelled" | "Issued" | "Paid" | "Overdue";
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
        invoiceNumber: string;
        dueDate: Date;
        taxRate?: number | undefined;
        currency?: string | undefined;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=invoice-contracts.d.ts.map