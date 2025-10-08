import { z } from 'zod';
export declare const AddressContractSchema: z.ZodObject<{
    street: z.ZodString;
    city: z.ZodString;
    postalCode: z.ZodString;
    country: z.ZodString;
    state: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    street: string;
    city: string;
    postalCode: string;
    country: string;
    state?: string | undefined;
}, {
    street: string;
    city: string;
    postalCode: string;
    country: string;
    state?: string | undefined;
}>;
export declare const CustomerStatusContractSchema: z.ZodEnum<["Active", "Prospect", "Blocked"]>;
export declare const CreateCustomerContractSchema: z.ZodObject<{
    number: z.ZodString;
    name: z.ZodString;
    status: z.ZodEnum<["Active", "Prospect", "Blocked"]>;
    email: z.ZodOptional<z.ZodString>;
    phone: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    tenantId: z.ZodString;
    ownerUserId: z.ZodOptional<z.ZodString>;
    vatId: z.ZodOptional<z.ZodString>;
    billingAddress: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>;
} & {
    shippingAddresses: z.ZodDefault<z.ZodOptional<z.ZodArray<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>, "many">>>;
}, "strip", z.ZodTypeAny, {
    number: string;
    name: string;
    status: "Active" | "Prospect" | "Blocked";
    tags: string[];
    tenantId: string;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    shippingAddresses: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[];
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
}, {
    number: string;
    name: string;
    status: "Active" | "Prospect" | "Blocked";
    tenantId: string;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    email?: string | undefined;
    phone?: string | undefined;
    tags?: string[] | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
}>;
export declare const UpdateCustomerContractSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    vatId: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    billingAddress: z.ZodOptional<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>>;
    shippingAddresses: z.ZodOptional<z.ZodArray<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>, "many">>;
    email: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    phone: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    status: z.ZodOptional<z.ZodEnum<["Active", "Prospect", "Blocked"]>>;
    ownerUserId: z.ZodOptional<z.ZodNullable<z.ZodString>>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    email?: string | null | undefined;
    phone?: string | null | undefined;
    tags?: string[] | undefined;
    ownerUserId?: string | null | undefined;
    vatId?: string | null | undefined;
    billingAddress?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
}, {
    name?: string | undefined;
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    email?: string | null | undefined;
    phone?: string | null | undefined;
    tags?: string[] | undefined;
    ownerUserId?: string | null | undefined;
    vatId?: string | null | undefined;
    billingAddress?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    } | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
}>;
export declare const CustomerResponseContractSchema: z.ZodObject<Omit<{
    id: z.ZodString;
    tenantId: z.ZodString;
    number: z.ZodString;
    name: z.ZodString;
    vatId: z.ZodOptional<z.ZodString>;
    billingAddress: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>;
    shippingAddresses: z.ZodDefault<z.ZodArray<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        state: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }>, "many">>;
    email: z.ZodOptional<z.ZodString>;
    phone: z.ZodOptional<z.ZodString>;
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    status: z.ZodEnum<["Active", "Prospect", "Blocked"]>;
    ownerUserId: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    version: z.ZodNumber;
}, "tenantId">, "strip", z.ZodTypeAny, {
    number: string;
    name: string;
    id: string;
    createdAt: Date;
    status: "Active" | "Prospect" | "Blocked";
    tags: string[];
    updatedAt: Date;
    version: number;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    shippingAddresses: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[];
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
}, {
    number: string;
    name: string;
    id: string;
    createdAt: Date;
    status: "Active" | "Prospect" | "Blocked";
    updatedAt: Date;
    version: number;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    email?: string | undefined;
    phone?: string | undefined;
    tags?: string[] | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
}>;
export declare const CustomerQueryContractSchema: z.ZodObject<{
    search: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodEnum<["Active", "Prospect", "Blocked"]>>;
    tags: z.ZodOptional<z.ZodString>;
    ownerUserId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
    pageSize: z.ZodDefault<z.ZodOptional<z.ZodEffects<z.ZodString, number, string>>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    tags?: string | undefined;
    search?: string | undefined;
    ownerUserId?: string | undefined;
}, {
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    tags?: string | undefined;
    search?: string | undefined;
    ownerUserId?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
export declare const CustomerListResponseContractSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<Omit<{
        id: z.ZodString;
        tenantId: z.ZodString;
        number: z.ZodString;
        name: z.ZodString;
        vatId: z.ZodOptional<z.ZodString>;
        billingAddress: z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            state: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }>;
        shippingAddresses: z.ZodDefault<z.ZodArray<z.ZodObject<{
            street: z.ZodString;
            city: z.ZodString;
            postalCode: z.ZodString;
            country: z.ZodString;
            state: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }, {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }>, "many">>;
        email: z.ZodOptional<z.ZodString>;
        phone: z.ZodOptional<z.ZodString>;
        tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        status: z.ZodEnum<["Active", "Prospect", "Blocked"]>;
        ownerUserId: z.ZodOptional<z.ZodString>;
        createdAt: z.ZodDate;
        updatedAt: z.ZodDate;
        version: z.ZodNumber;
    }, "tenantId">, "strip", z.ZodTypeAny, {
        number: string;
        name: string;
        id: string;
        createdAt: Date;
        status: "Active" | "Prospect" | "Blocked";
        tags: string[];
        updatedAt: Date;
        version: number;
        billingAddress: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        };
        shippingAddresses: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }[];
        email?: string | undefined;
        phone?: string | undefined;
        ownerUserId?: string | undefined;
        vatId?: string | undefined;
    }, {
        number: string;
        name: string;
        id: string;
        createdAt: Date;
        status: "Active" | "Prospect" | "Blocked";
        updatedAt: Date;
        version: number;
        billingAddress: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        };
        email?: string | undefined;
        phone?: string | undefined;
        tags?: string[] | undefined;
        ownerUserId?: string | undefined;
        vatId?: string | undefined;
        shippingAddresses?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }[] | undefined;
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
        number: string;
        name: string;
        id: string;
        createdAt: Date;
        status: "Active" | "Prospect" | "Blocked";
        tags: string[];
        updatedAt: Date;
        version: number;
        billingAddress: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        };
        shippingAddresses: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }[];
        email?: string | undefined;
        phone?: string | undefined;
        ownerUserId?: string | undefined;
        vatId?: string | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        number: string;
        name: string;
        id: string;
        createdAt: Date;
        status: "Active" | "Prospect" | "Blocked";
        updatedAt: Date;
        version: number;
        billingAddress: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        };
        email?: string | undefined;
        phone?: string | undefined;
        tags?: string[] | undefined;
        ownerUserId?: string | undefined;
        vatId?: string | undefined;
        shippingAddresses?: {
            street: string;
            city: string;
            postalCode: string;
            country: string;
            state?: string | undefined;
        }[] | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
//# sourceMappingURL=customer-contracts.d.ts.map