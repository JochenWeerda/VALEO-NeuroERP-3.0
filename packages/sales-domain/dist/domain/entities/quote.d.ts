import { z } from 'zod';
export declare const QuoteStatus: {
    readonly DRAFT: "Draft";
    readonly SENT: "Sent";
    readonly ACCEPTED: "Accepted";
    readonly REJECTED: "Rejected";
    readonly EXPIRED: "Expired";
};
export type QuoteStatusType = typeof QuoteStatus[keyof typeof QuoteStatus];
export declare const QuoteLineSchema: z.ZodObject<{
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
export type QuoteLine = z.infer<typeof QuoteLineSchema>;
export declare const QuoteSchema: z.ZodObject<{
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
}, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    tenantId: string;
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
    quoteNumber: string;
    validUntil: Date;
    notes?: string | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
    tenantId: string;
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
    quoteNumber: string;
    validUntil: Date;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
}>;
export type Quote = z.infer<typeof QuoteSchema>;
export declare const CreateQuoteInputSchema: z.ZodObject<{
    status: z.ZodEnum<["Draft", "Sent", "Accepted", "Rejected", "Expired"]>;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    quoteNumber: z.ZodString;
    validUntil: z.ZodDate;
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
    quoteNumber: string;
    validUntil: Date;
    notes?: string | undefined;
}, {
    status: "Draft" | "Sent" | "Accepted" | "Rejected" | "Expired";
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
    quoteNumber: string;
    validUntil: Date;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
}>;
export type CreateQuoteInput = z.infer<typeof CreateQuoteInputSchema>;
export declare const UpdateQuoteInputSchema: z.ZodObject<{
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
    notes?: string | null | undefined;
    validUntil?: Date | undefined;
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
    notes?: string | null | undefined;
    validUntil?: Date | undefined;
}>;
export type UpdateQuoteInput = z.infer<typeof UpdateQuoteInputSchema>;
export declare class QuoteEntity {
    private props;
    private constructor();
    static create(props: CreateQuoteInput & {
        tenantId: string;
    }): QuoteEntity;
    static fromPersistence(props: any): QuoteEntity;
    update(props: UpdateQuoteInput): void;
    send(): void;
    accept(): void;
    reject(): void;
    expire(): void;
    isExpired(): boolean;
    canBeAccepted(): boolean;
    canBeSent(): boolean;
    private validateStatusTransition;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get quoteNumber(): string;
    get lines(): QuoteLine[];
    get subtotalNet(): number;
    get totalDiscount(): number;
    get totalNet(): number;
    get totalGross(): number;
    get taxRate(): number;
    get currency(): string;
    get validUntil(): Date;
    get notes(): string | undefined;
    get status(): QuoteStatusType;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Quote;
    toJSON(): Omit<Quote, 'tenantId'>;
}
//# sourceMappingURL=quote.d.ts.map