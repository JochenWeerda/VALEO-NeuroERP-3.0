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
export declare const InvoiceStatusContractSchema: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
export declare const CreateInvoiceContractSchema: z.ZodObject<{
    currency: z.ZodDefault<z.ZodString>;
    taxRate: z.ZodDefault<z.ZodNumber>;
    notes: z.ZodOptional<z.ZodString>;
    customerId: z.ZodString;
    tenantId: z.ZodString;
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
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[];
    invoiceNumber: string;
    dueDate: Date;
    notes?: string | undefined;
    orderId?: string | undefined;
}, {
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
    invoiceNumber: string;
    dueDate: Date;
    currency?: string | undefined;
    taxRate?: number | undefined;
    notes?: string | undefined;
    orderId?: string | undefined;
}>;
export declare const UpdateInvoiceContractSchema: z.ZodObject<{
    dueDate: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>>;
}, "strip", z.ZodTypeAny, {
    notes?: string | null | undefined;
    status?: "Issued" | "Cancelled" | "Paid" | "Overdue" | undefined;
    dueDate?: Date | undefined;
}, {
    notes?: string | null | undefined;
    status?: "Issued" | "Cancelled" | "Paid" | "Overdue" | undefined;
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
    dueDate: z.ZodDate;
    paidAt: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    currency: string;
    taxRate: number;
    status: "Issued" | "Cancelled" | "Paid" | "Overdue";
    version: number;
    createdAt: Date;
    updatedAt: Date;
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
    invoiceNumber: string;
    dueDate: Date;
    notes?: string | undefined;
    orderId?: string | undefined;
    paidAt?: Date | undefined;
}, {
    id: string;
    status: "Issued" | "Cancelled" | "Paid" | "Overdue";
    version: number;
    createdAt: Date;
    updatedAt: Date;
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
    invoiceNumber: string;
    dueDate: Date;
    currency?: string | undefined;
    taxRate?: number | undefined;
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
    status?: "Issued" | "Cancelled" | "Paid" | "Overdue" | undefined;
    search?: string | undefined;
    customerId?: string | undefined;
    orderId?: string | undefined;
    dueDateFrom?: string | undefined;
    dueDateTo?: string | undefined;
}, {
    status?: "Issued" | "Cancelled" | "Paid" | "Overdue" | undefined;
    search?: string | undefined;
    customerId?: string | undefined;
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
        dueDate: z.ZodDate;
        paidAt: z.ZodOptional<z.ZodDate>;
        notes: z.ZodOptional<z.ZodString>;
        status: z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        currency: string;
        taxRate: number;
        status: "Issued" | "Cancelled" | "Paid" | "Overdue";
        version: number;
        createdAt: Date;
        updatedAt: Date;
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
        invoiceNumber: string;
        dueDate: Date;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
    }, {
        id: string;
        status: "Issued" | "Cancelled" | "Paid" | "Overdue";
        version: number;
        createdAt: Date;
        updatedAt: Date;
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
        invoiceNumber: string;
        dueDate: Date;
        currency?: string | undefined;
        taxRate?: number | undefined;
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
        status: "Issued" | "Cancelled" | "Paid" | "Overdue";
        version: number;
        createdAt: Date;
        updatedAt: Date;
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
        invoiceNumber: string;
        dueDate: Date;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
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
        status: "Issued" | "Cancelled" | "Paid" | "Overdue";
        version: number;
        createdAt: Date;
        updatedAt: Date;
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
        invoiceNumber: string;
        dueDate: Date;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
        orderId?: string | undefined;
        paidAt?: Date | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=invoice-contracts.d.ts.map