import { z } from 'zod';
export declare const InvoiceStatus: {
    readonly ISSUED: "Issued";
    readonly PAID: "Paid";
    readonly OVERDUE: "Overdue";
    readonly CANCELLED: "Cancelled";
};
export type InvoiceStatusType = typeof InvoiceStatus[keyof typeof InvoiceStatus];
export declare const InvoiceLineSchema: z.ZodObject<{
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
export type InvoiceLine = z.infer<typeof InvoiceLineSchema>;
export declare const InvoiceSchema: z.ZodObject<{
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
}, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Issued" | "Paid" | "Overdue" | "Cancelled";
    tenantId: string;
    customerId: string;
    invoiceNumber: string;
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
    dueDate: Date;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    orderId?: string | undefined;
    paidAt?: Date | undefined;
    notes?: string | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Issued" | "Paid" | "Overdue" | "Cancelled";
    tenantId: string;
    customerId: string;
    invoiceNumber: string;
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
    dueDate: Date;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    orderId?: string | undefined;
    taxRate?: number | undefined;
    currency?: string | undefined;
    paidAt?: Date | undefined;
    notes?: string | undefined;
}>;
export type Invoice = z.infer<typeof InvoiceSchema>;
export declare const CreateInvoiceInputSchema: z.ZodObject<{
    tenantId: z.ZodString;
    customerId: z.ZodString;
    orderId: z.ZodOptional<z.ZodString>;
    invoiceNumber: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    dueDate: z.ZodDate;
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
    tenantId: string;
    customerId: string;
    invoiceNumber: string;
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
    dueDate: Date;
    orderId?: string | undefined;
    notes?: string | undefined;
}, {
    tenantId: string;
    customerId: string;
    invoiceNumber: string;
    lines: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    dueDate: Date;
    orderId?: string | undefined;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
}>;
export type CreateInvoiceInput = z.infer<typeof CreateInvoiceInputSchema>;
export declare const UpdateInvoiceInputSchema: z.ZodObject<{
    dueDate: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Issued", "Paid", "Overdue", "Cancelled"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Issued" | "Paid" | "Overdue" | "Cancelled" | undefined;
    dueDate?: Date | undefined;
    notes?: string | null | undefined;
}, {
    status?: "Issued" | "Paid" | "Overdue" | "Cancelled" | undefined;
    dueDate?: Date | undefined;
    notes?: string | null | undefined;
}>;
export type UpdateInvoiceInput = z.infer<typeof UpdateInvoiceInputSchema>;
export declare class InvoiceEntity {
    private props;
    private constructor();
    static create(props: CreateInvoiceInput & {
        tenantId: string;
    }): InvoiceEntity;
    static fromPersistence(props: any): InvoiceEntity;
    update(props: UpdateInvoiceInput): void;
    markAsPaid(): void;
    markAsOverdue(): void;
    cancel(): void;
    isOverdue(): boolean;
    canBePaid(): boolean;
    canBeCancelled(): boolean;
    private validateStatusTransition;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get orderId(): string | undefined;
    get invoiceNumber(): string;
    get lines(): InvoiceLine[];
    get subtotalNet(): number;
    get totalDiscount(): number;
    get totalNet(): number;
    get totalGross(): number;
    get taxRate(): number;
    get currency(): string;
    get dueDate(): Date;
    get paidAt(): Date | undefined;
    get notes(): string | undefined;
    get status(): InvoiceStatusType;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Invoice;
    toJSON(): Omit<Invoice, 'tenantId'>;
}
//# sourceMappingURL=invoice.d.ts.map