import { z } from 'zod';
export declare const CustomerStatus: {
    readonly ACTIVE: "Active";
    readonly PROSPECT: "Prospect";
    readonly BLOCKED: "Blocked";
};
export type CustomerStatusType = typeof CustomerStatus[keyof typeof CustomerStatus];
export declare const AddressSchema: z.ZodObject<{
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
export type Address = z.infer<typeof AddressSchema>;
export declare const CustomerSchema: z.ZodObject<{
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
}, "strip", z.ZodTypeAny, {
    number: string;
    id: string;
    tenantId: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    status: "Active" | "Prospect" | "Blocked";
    name: string;
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
    tags: string[];
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
}, {
    number: string;
    id: string;
    tenantId: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
    status: "Active" | "Prospect" | "Blocked";
    name: string;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
    tags?: string[] | undefined;
}>;
export type Customer = z.infer<typeof CustomerSchema>;
export declare const CreateCustomerInputSchema: z.ZodObject<{
    number: z.ZodString;
    tenantId: z.ZodString;
    email: z.ZodOptional<z.ZodString>;
    phone: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["Active", "Prospect", "Blocked"]>;
    ownerUserId: z.ZodOptional<z.ZodString>;
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
    tags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
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
    tenantId: string;
    status: "Active" | "Prospect" | "Blocked";
    name: string;
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
    tags: string[];
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
}, {
    number: string;
    tenantId: string;
    status: "Active" | "Prospect" | "Blocked";
    name: string;
    billingAddress: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    };
    email?: string | undefined;
    phone?: string | undefined;
    ownerUserId?: string | undefined;
    vatId?: string | undefined;
    shippingAddresses?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string | undefined;
    }[] | undefined;
    tags?: string[] | undefined;
}>;
export type CreateCustomerInput = z.infer<typeof CreateCustomerInputSchema>;
export declare const UpdateCustomerInputSchema: z.ZodObject<{
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
    email?: string | null | undefined;
    phone?: string | null | undefined;
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    ownerUserId?: string | null | undefined;
    name?: string | undefined;
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
    tags?: string[] | undefined;
}, {
    email?: string | null | undefined;
    phone?: string | null | undefined;
    status?: "Active" | "Prospect" | "Blocked" | undefined;
    ownerUserId?: string | null | undefined;
    name?: string | undefined;
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
    tags?: string[] | undefined;
}>;
export type UpdateCustomerInput = z.infer<typeof UpdateCustomerInputSchema>;
export declare class CustomerEntity {
    private props;
    private constructor();
    static create(props: CreateCustomerInput & {
        tenantId: string;
    }): CustomerEntity;
    static fromPersistence(props: Customer): CustomerEntity;
    update(props: UpdateCustomerInput): void;
    changeStatus(newStatus: CustomerStatusType): void;
    addTag(tag: string): void;
    removeTag(tag: string): void;
    addShippingAddress(address: Address): void;
    removeShippingAddress(index: number): void;
    get id(): string;
    get tenantId(): string;
    get number(): string;
    get name(): string;
    get vatId(): string | undefined;
    get billingAddress(): Address;
    get shippingAddresses(): Address[];
    get email(): string | undefined;
    get phone(): string | undefined;
    get tags(): string[];
    get status(): CustomerStatusType;
    get ownerUserId(): string | undefined;
    get createdAt(): Date;
    get updatedAt(): Date;
    get version(): number;
    toPersistence(): Customer;
    toJSON(): Omit<Customer, 'tenantId'>;
}
//# sourceMappingURL=customer.d.ts.map