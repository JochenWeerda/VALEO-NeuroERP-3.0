import { z } from 'zod';
export declare const CreditNoteStatus: {
    readonly ISSUED: "Issued";
    readonly SETTLED: "Settled";
};
export type CreditNoteStatusType = typeof CreditNoteStatus[keyof typeof CreditNoteStatus];
export declare const CreditNoteLineSchema: z.ZodObject<{
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
export type CreditNoteLine = z.infer<typeof CreditNoteLineSchema>;
export declare const CreditNoteSchema: z.ZodObject<{
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
}, "strip", z.ZodTypeAny, {
    version: number;
    customerId: string;
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
    id: string;
    status: "Issued" | "Settled";
    tenantId: string;
    totalNet: number;
    totalGross: number;
    subtotalNet: number;
    totalDiscount: number;
    taxRate: number;
    currency: string;
    createdAt: Date;
    updatedAt: Date;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    notes?: string | undefined;
    settledAt?: Date | undefined;
}, {
    version: number;
    customerId: string;
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
    id: string;
    status: "Issued" | "Settled";
    tenantId: string;
    totalNet: number;
    totalGross: number;
    subtotalNet: number;
    totalDiscount: number;
    createdAt: Date;
    updatedAt: Date;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    settledAt?: Date | undefined;
}>;
export type CreditNote = z.infer<typeof CreditNoteSchema>;
export declare const CreateCreditNoteInputSchema: z.ZodObject<{
    customerId: z.ZodString;
    tenantId: z.ZodString;
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
    customerId: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[];
    tenantId: string;
    taxRate: number;
    currency: string;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    notes?: string | undefined;
}, {
    customerId: string;
    lines: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[];
    tenantId: string;
    invoiceId: string;
    creditNumber: string;
    reason: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
}>;
export type CreateCreditNoteInput = z.infer<typeof CreateCreditNoteInputSchema>;
export declare const UpdateCreditNoteInputSchema: z.ZodObject<{
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
export type UpdateCreditNoteInput = z.infer<typeof UpdateCreditNoteInputSchema>;
export declare class CreditNoteEntity {
    private props;
    private constructor();
    static create(props: CreateCreditNoteInput & {
        tenantId: string;
    }): CreditNoteEntity;
    static fromPersistence(props: CreditNote): CreditNoteEntity;
    update(props: UpdateCreditNoteInput): void;
    settle(): void;
    canBeSettled(): boolean;
    private validateStatusTransition;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get invoiceId(): string;
    get creditNumber(): string;
    get lines(): CreditNoteLine[];
    get subtotalNet(): number;
    get totalDiscount(): number;
    get totalNet(): number;
    get totalGross(): number;
    get taxRate(): number;
    get currency(): string;
    get reason(): string;
    get notes(): string | undefined;
    get status(): CreditNoteStatusType;
    get settledAt(): Date | undefined;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): CreditNote;
    toJSON(): Omit<CreditNote, 'tenantId'>;
}
//# sourceMappingURL=credit-note.d.ts.map