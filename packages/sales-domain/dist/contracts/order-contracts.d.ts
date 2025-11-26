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
export declare const OrderStatusContractSchema: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
export declare const CreateOrderContractSchema: z.ZodObject<{
    currency: z.ZodDefault<z.ZodString>;
    taxRate: z.ZodDefault<z.ZodNumber>;
    notes: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Draft", "Confirmed", "Invoiced", "Cancelled"]>;
    customerId: z.ZodString;
    tenantId: z.ZodString;
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
    currency: string;
    taxRate: number;
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}, {
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    orderNumber: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
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
    notes?: string | null | undefined;
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        discount: number;
        description?: string | undefined;
    }[] | undefined;
    expectedDeliveryDate?: Date | null | undefined;
}, {
    notes?: string | null | undefined;
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    lines?: {
        name: string;
        sku: string;
        quantity: number;
        unitPrice: number;
        description?: string | undefined;
        discount?: number | undefined;
    }[] | undefined;
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
}, "tenantId">, "strip", z.ZodTypeAny, {
    id: string;
    currency: string;
    taxRate: number;
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    orderNumber: string;
    notes?: string | undefined;
    expectedDeliveryDate?: Date | undefined;
}, {
    id: string;
    status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
    orderNumber: string;
    currency?: string | undefined;
    taxRate?: number | undefined;
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
    search?: string | undefined;
    customerId?: string | undefined;
    expectedDeliveryDateFrom?: string | undefined;
    expectedDeliveryDateTo?: string | undefined;
}, {
    status?: "Draft" | "Confirmed" | "Invoiced" | "Cancelled" | undefined;
    search?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
    customerId?: string | undefined;
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
    }, "tenantId">, "strip", z.ZodTypeAny, {
        id: string;
        currency: string;
        taxRate: number;
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        orderNumber: string;
        notes?: string | undefined;
        expectedDeliveryDate?: Date | undefined;
    }, {
        id: string;
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        orderNumber: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
        expectedDeliveryDate?: Date | undefined;
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
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        orderNumber: string;
        notes?: string | undefined;
        expectedDeliveryDate?: Date | undefined;
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
        status: "Draft" | "Confirmed" | "Invoiced" | "Cancelled";
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
        orderNumber: string;
        currency?: string | undefined;
        taxRate?: number | undefined;
        notes?: string | undefined;
        expectedDeliveryDate?: Date | undefined;
    }[];
    pagination: {
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=order-contracts.d.ts.map