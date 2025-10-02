import { z } from 'zod';
export declare const Supplier: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    code: z.ZodOptional<z.ZodString>;
    contactInfo: z.ZodObject<{
        name: z.ZodString;
        email: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodString>;
        address: z.ZodOptional<z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            coordinates: z.ZodOptional<z.ZodObject<{
                lat: z.ZodNumber;
                lon: z.ZodNumber;
            }, "strip", z.ZodTypeAny, {
                lat: number;
                lon: number;
            }, {
                lat: number;
                lon: number;
            }>>;
            gln: z.ZodOptional<z.ZodString>;
            name: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        email?: string | undefined;
        phone?: string | undefined;
        address?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }, {
        name: string;
        email?: string | undefined;
        phone?: string | undefined;
        address?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    }>;
    taxId: z.ZodOptional<z.ZodString>;
    paymentTerms: z.ZodDefault<z.ZodNumber>;
    status: z.ZodEnum<["ACTIVE", "INACTIVE", "SUSPENDED"]>;
    isPreferred: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "ACTIVE" | "INACTIVE" | "SUSPENDED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    contactInfo: {
        name: string;
        email?: string | undefined;
        phone?: string | undefined;
        address?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    };
    paymentTerms: number;
    isPreferred: boolean;
    code?: string | undefined;
    taxId?: string | undefined;
}, {
    status: "ACTIVE" | "INACTIVE" | "SUSPENDED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    contactInfo: {
        name: string;
        email?: string | undefined;
        phone?: string | undefined;
        address?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            coordinates?: {
                lat: number;
                lon: number;
            } | undefined;
            gln?: string | undefined;
            name?: string | undefined;
        } | undefined;
    };
    code?: string | undefined;
    taxId?: string | undefined;
    paymentTerms?: number | undefined;
    isPreferred?: boolean | undefined;
}>;
export type Supplier = z.infer<typeof Supplier>;
export declare const PurchaseOrder: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    orderNumber: z.ZodString;
    supplierId: z.ZodString;
    orderDate: z.ZodString;
    requestedDeliveryDate: z.ZodOptional<z.ZodString>;
    actualDeliveryDate: z.ZodOptional<z.ZodString>;
    subtotal: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    taxAmount: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    total: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    currency: z.ZodDefault<z.ZodString>;
    status: z.ZodEnum<["DRAFT", "SENT", "CONFIRMED", "PARTIALLY_RECEIVED", "RECEIVED", "CANCELLED"]>;
    lineItems: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        itemId: z.ZodString;
        description: z.ZodString;
        quantity: z.ZodNumber;
        unitPrice: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        totalPrice: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        receivedQuantity: z.ZodDefault<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        description: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        itemId: string;
        receivedQuantity: number;
    }, {
        id: string;
        description: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        itemId: string;
        receivedQuantity?: number | undefined;
    }>, "many">;
    createdBy: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "DRAFT" | "SENT" | "CANCELLED" | "CONFIRMED" | "PARTIALLY_RECEIVED" | "RECEIVED";
    currency: string;
    tenantId: string;
    total: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    supplierId: string;
    subtotal: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    lineItems: {
        id: string;
        description: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        itemId: string;
        receivedQuantity: number;
    }[];
    orderNumber: string;
    orderDate: string;
    requestedDeliveryDate?: string | undefined;
    actualDeliveryDate?: string | undefined;
}, {
    status: "DRAFT" | "SENT" | "CANCELLED" | "CONFIRMED" | "PARTIALLY_RECEIVED" | "RECEIVED";
    tenantId: string;
    total: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    supplierId: string;
    subtotal: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    taxAmount: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    lineItems: {
        id: string;
        description: string;
        quantity: number;
        unitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        totalPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        itemId: string;
        receivedQuantity?: number | undefined;
    }[];
    orderNumber: string;
    orderDate: string;
    currency?: string | undefined;
    requestedDeliveryDate?: string | undefined;
    actualDeliveryDate?: string | undefined;
}>;
export type PurchaseOrder = z.infer<typeof PurchaseOrder>;
export declare const PurchaseRequisition: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    title: z.ZodString;
    description: z.ZodString;
    requestedBy: z.ZodString;
    priority: z.ZodEnum<["LOW", "MEDIUM", "HIGH", "URGENT"]>;
    requiredBy: z.ZodString;
    estimatedCost: z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>;
    budgetCode: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "ORDERED"]>;
    items: z.ZodArray<z.ZodObject<{
        description: z.ZodString;
        quantity: z.ZodNumber;
        estimatedUnitPrice: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        category: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        description: string;
        quantity: number;
        estimatedUnitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        category?: string | undefined;
    }, {
        description: string;
        quantity: number;
        estimatedUnitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        category?: string | undefined;
    }>, "many">;
    approvals: z.ZodDefault<z.ZodArray<z.ZodObject<{
        approverId: z.ZodString;
        status: z.ZodEnum<["PENDING", "APPROVED", "REJECTED"]>;
        comments: z.ZodOptional<z.ZodString>;
        approvedAt: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        status: "PENDING" | "APPROVED" | "REJECTED";
        approverId: string;
        approvedAt?: string | undefined;
        comments?: string | undefined;
    }, {
        status: "PENDING" | "APPROVED" | "REJECTED";
        approverId: string;
        approvedAt?: string | undefined;
        comments?: string | undefined;
    }>, "many">>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "DRAFT" | "APPROVED" | "REJECTED" | "SUBMITTED" | "ORDERED";
    tenantId: string;
    items: {
        description: string;
        quantity: number;
        estimatedUnitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        category?: string | undefined;
    }[];
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
    title: string;
    requestedBy: string;
    requiredBy: string;
    estimatedCost: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    approvals: {
        status: "PENDING" | "APPROVED" | "REJECTED";
        approverId: string;
        approvedAt?: string | undefined;
        comments?: string | undefined;
    }[];
    budgetCode?: string | undefined;
}, {
    status: "DRAFT" | "APPROVED" | "REJECTED" | "SUBMITTED" | "ORDERED";
    tenantId: string;
    items: {
        description: string;
        quantity: number;
        estimatedUnitPrice: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        category?: string | undefined;
    }[];
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
    title: string;
    requestedBy: string;
    requiredBy: string;
    estimatedCost: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    };
    budgetCode?: string | undefined;
    approvals?: {
        status: "PENDING" | "APPROVED" | "REJECTED";
        approverId: string;
        approvedAt?: string | undefined;
        comments?: string | undefined;
    }[] | undefined;
}>;
export type PurchaseRequisition = z.infer<typeof PurchaseRequisition>;
export declare const RFQ: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    title: z.ZodString;
    description: z.ZodString;
    items: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        description: z.ZodString;
        quantity: z.ZodNumber;
        unitOfMeasure: z.ZodString;
        specifications: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        id: string;
        description: string;
        quantity: number;
        unitOfMeasure: string;
        specifications?: Record<string, any> | undefined;
    }, {
        id: string;
        description: string;
        quantity: number;
        unitOfMeasure: string;
        specifications?: Record<string, any> | undefined;
    }>, "many">;
    supplierIds: z.ZodArray<z.ZodString, "many">;
    responseDeadline: z.ZodString;
    validUntil: z.ZodString;
    status: z.ZodEnum<["DRAFT", "PUBLISHED", "CLOSED", "CANCELLED"]>;
    responses: z.ZodDefault<z.ZodArray<z.ZodObject<{
        supplierId: z.ZodString;
        submittedAt: z.ZodString;
        totalAmount: z.ZodObject<{
            amount: z.ZodNumber;
            currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
        }, "strip", z.ZodTypeAny, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }, {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        }>;
        lineItems: z.ZodArray<z.ZodObject<{
            itemId: z.ZodString;
            unitPrice: z.ZodObject<{
                amount: z.ZodNumber;
                currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
            }, "strip", z.ZodTypeAny, {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            }, {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            }>;
            totalPrice: z.ZodObject<{
                amount: z.ZodNumber;
                currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
            }, "strip", z.ZodTypeAny, {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            }, {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            }>;
            leadTimeDays: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }, {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }>, "many">;
        notes: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        supplierId: string;
        lineItems: {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }[];
        submittedAt: string;
        totalAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }, {
        supplierId: string;
        lineItems: {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }[];
        submittedAt: string;
        totalAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }>, "many">>;
    createdBy: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "DRAFT" | "CANCELLED" | "CLOSED" | "PUBLISHED";
    tenantId: string;
    items: {
        id: string;
        description: string;
        quantity: number;
        unitOfMeasure: string;
        specifications?: Record<string, any> | undefined;
    }[];
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    title: string;
    supplierIds: string[];
    responseDeadline: string;
    validUntil: string;
    responses: {
        supplierId: string;
        lineItems: {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }[];
        submittedAt: string;
        totalAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }[];
}, {
    status: "DRAFT" | "CANCELLED" | "CLOSED" | "PUBLISHED";
    tenantId: string;
    items: {
        id: string;
        description: string;
        quantity: number;
        unitOfMeasure: string;
        specifications?: Record<string, any> | undefined;
    }[];
    id: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    title: string;
    supplierIds: string[];
    responseDeadline: string;
    validUntil: string;
    responses?: {
        supplierId: string;
        lineItems: {
            unitPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            totalPrice: {
                amount: number;
                currency: "EUR" | "USD" | "GBP" | "CHF";
            };
            itemId: string;
            leadTimeDays: number;
        }[];
        submittedAt: string;
        totalAmount: {
            amount: number;
            currency: "EUR" | "USD" | "GBP" | "CHF";
        };
        notes?: string | undefined;
    }[] | undefined;
}>;
export type RFQ = z.infer<typeof RFQ>;
//# sourceMappingURL=procurement-schemas.d.ts.map