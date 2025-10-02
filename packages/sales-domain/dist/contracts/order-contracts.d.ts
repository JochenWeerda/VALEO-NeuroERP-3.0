import { z } from 'zod';
export declare const OrderLineContractSchema: z.ZodObject<{
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
export declare const OrderStatusContractSchema: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
export declare const CreateOrderContractSchema: z.ZodObject<{
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
export declare const UpdateOrderContractSchema: z.ZodObject<{
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
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
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
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
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
export declare const OrderResponseContractSchema: z.ZodObject<Omit<{
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
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    totalNet: number;
    totalGross: number;
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
export declare const OrderQueryContractSchema: z.ZodObject<{
    customerId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>>;
    search: z.ZodOptional<z.ZodString>;
    expectedDeliveryDateFrom: z.ZodOptional<z.ZodString>;
    expectedDeliveryDateTo: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
    pageSize: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    customerId?: string | undefined;
    search?: string | undefined;
    expectedDeliveryDateFrom?: string | undefined;
    expectedDeliveryDateTo?: string | undefined;
}, {
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    customerId?: string | undefined;
    search?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    expectedDeliveryDateFrom?: string | undefined;
    expectedDeliveryDateTo?: string | undefined;
}>;
export declare const OrderListResponseContractSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<Omit<{
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
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        totalNet: number;
        totalGross: number;
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=order-contracts.d.ts.map