import { z } from 'zod';
export declare const OrderStatus: {
    readonly DRAFT: "Draft";
    readonly CONFIRMED: "Confirmed";
    readonly INVOICED: "Invoiced";
    readonly CANCELLED: "Cancelled";
};
export type OrderStatusType = typeof OrderStatus[keyof typeof OrderStatus];
export declare const OrderLineSchema: z.ZodObject<{
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
export type OrderLine = z.infer<typeof OrderLineSchema>;
export declare const OrderSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    orderNumber: z.ZodString;
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
    expectedDeliveryDate: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Cancelled" | "Draft" | "Confirmed" | "Invoiced";
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
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Cancelled" | "Draft" | "Confirmed" | "Invoiced";
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
    orderNumber: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}>;
export type Order = z.infer<typeof OrderSchema>;
export declare const CreateOrderInputSchema: z.ZodObject<{
    status: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
    tenantId: z.ZodString;
    customerId: z.ZodString;
    taxRate: z.ZodDefault<z.ZodNumber>;
    currency: z.ZodDefault<z.ZodString>;
    notes: z.ZodOptional<z.ZodString>;
    orderNumber: z.ZodString;
    expectedDeliveryDate: z.ZodOptional<z.ZodDate>;
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
    status: "Cancelled" | "Draft" | "Confirmed" | "Invoiced";
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
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}, {
    status: "Cancelled" | "Draft" | "Confirmed" | "Invoiced";
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
    orderNumber: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}>;
export type CreateOrderInput = z.infer<typeof CreateOrderInputSchema>;
export declare const UpdateOrderInputSchema: z.ZodObject<{
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
    expectedDeliveryDate: z.ZodOptional<z.ZodNullable<z.ZodDate>>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "Cancelled" | "Draft" | "Confirmed" | "Invoiced" | undefined;
    lines?: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[] | undefined;
    notes?: string | null | undefined;
    expectedDeliveryDate?: Date | null | undefined;
}, {
    status?: "Cancelled" | "Draft" | "Confirmed" | "Invoiced" | undefined;
    lines?: {
        sku: string;
        name: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[] | undefined;
    notes?: string | null | undefined;
    expectedDeliveryDate?: Date | null | undefined;
}>;
export type UpdateOrderInput = z.infer<typeof UpdateOrderInputSchema>;
export declare class OrderEntity {
    private props;
    private constructor();
    static create(props: CreateOrderInput & {
        tenantId: string;
    }): OrderEntity;
    static fromPersistence(props: any): OrderEntity;
    update(props: UpdateOrderInput): void;
    confirm(): void;
    markAsInvoiced(): void;
    cancel(): void;
    canBeConfirmed(): boolean;
    canBeInvoiced(): boolean;
    canBeCancelled(): boolean;
    private validateStatusTransition;
    get id(): string;
    get tenantId(): string;
    get customerId(): string;
    get orderNumber(): string;
    get lines(): OrderLine[];
    get subtotalNet(): number;
    get totalDiscount(): number;
    get totalNet(): number;
    get totalGross(): number;
    get taxRate(): number;
    get currency(): string;
    get expectedDeliveryDate(): Date | undefined;
    get notes(): string | undefined;
    get status(): OrderStatusType;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Order;
    toJSON(): Omit<Order, 'tenantId'>;
}
//# sourceMappingURL=order.d.ts.map