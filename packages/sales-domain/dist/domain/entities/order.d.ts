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
    expectedDeliveryDate: z.ZodOptional<z.ZodDate>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
    tenantId: string;
    totalNet: number;
    totalGross: number;
    subtotalNet: number;
    totalDiscount: number;
    taxRate: number;
    currency: string;
    createdAt: Date;
    updatedAt: Date;
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
    tenantId: string;
    totalNet: number;
    totalGross: number;
    subtotalNet: number;
    totalDiscount: number;
    createdAt: Date;
    updatedAt: Date;
    orderNumber: string;
    taxRate?: number | undefined;
    currency?: string | undefined;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}>;
export type Order = z.infer<typeof OrderSchema>;
export declare const CreateOrderInputSchema: z.ZodObject<{
    customerId: z.ZodString;
    status: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
    tenantId: z.ZodString;
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
    tenantId: string;
    taxRate: number;
    currency: string;
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
    tenantId: string;
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
    expectedDeliveryDate: z.ZodOptional<z.ZodNullable<z.ZodDate>>;
    notes: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>>;
}, "strip", z.ZodTypeAny, {
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[] | undefined;
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    notes?: string | null | undefined;
    expectedDeliveryDate?: Date | null | undefined;
}, {
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[] | undefined;
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
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
    static fromPersistence(props: Order): OrderEntity;
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