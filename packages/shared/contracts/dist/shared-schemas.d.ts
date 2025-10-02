import { z } from 'zod';
export declare const UUID: z.ZodString;
export declare const Email: z.ZodString;
export declare const PhoneNumber: z.ZodString;
export declare const URL: z.ZodString;
export declare const Address: z.ZodObject<{
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
}>;
export type Address = z.infer<typeof Address>;
export declare const ContactInfo: z.ZodObject<{
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
export type ContactInfo = z.infer<typeof ContactInfo>;
export declare const Currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
export declare const Money: z.ZodObject<{
    amount: z.ZodNumber;
    currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
}, "strip", z.ZodTypeAny, {
    amount: number;
    currency: "EUR" | "USD" | "GBP" | "CHF";
}, {
    amount: number;
    currency: "EUR" | "USD" | "GBP" | "CHF";
}>;
export type Money = z.infer<typeof Money>;
export declare const ISODateString: z.ZodString;
export declare const TimeWindow: z.ZodObject<{
    from: z.ZodString;
    to: z.ZodString;
}, "strip", z.ZodTypeAny, {
    from: string;
    to: string;
}, {
    from: string;
    to: string;
}>;
export type TimeWindow = z.infer<typeof TimeWindow>;
export declare const PaginationParams: z.ZodObject<{
    page: z.ZodDefault<z.ZodNumber>;
    limit: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    page: number;
    limit: number;
}, {
    page?: number | undefined;
    limit?: number | undefined;
}>;
export type PaginationParams = z.infer<typeof PaginationParams>;
export declare const PaginatedResponse: <T extends z.ZodType>(itemSchema: T) => z.ZodObject<{
    items: z.ZodArray<T, "many">;
    total: z.ZodNumber;
    page: z.ZodNumber;
    limit: z.ZodNumber;
    hasNext: z.ZodBoolean;
    hasPrev: z.ZodBoolean;
}, "strip", z.ZodTypeAny, {
    page: number;
    limit: number;
    items: T["_output"][];
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
}, {
    page: number;
    limit: number;
    items: T["_input"][];
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
}>;
export type PaginatedResponse<T> = {
    items: T[];
    total: number;
    page: number;
    limit: number;
    hasNext: boolean;
    hasPrev: boolean;
};
export declare const TenantContext: z.ZodObject<{
    tenantId: z.ZodString;
    userId: z.ZodOptional<z.ZodString>;
    roles: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    roles: string[];
    userId?: string | undefined;
}, {
    tenantId: string;
    userId?: string | undefined;
    roles?: string[] | undefined;
}>;
export type TenantContext = z.infer<typeof TenantContext>;
export declare const ApiResponse: <T extends z.ZodType>(dataSchema: T) => z.ZodObject<{
    success: z.ZodBoolean;
    data: z.ZodOptional<T>;
    error: z.ZodOptional<z.ZodObject<{
        code: z.ZodString;
        message: z.ZodString;
        details: z.ZodOptional<z.ZodAny>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        message: string;
        details?: any;
    }, {
        code: string;
        message: string;
        details?: any;
    }>>;
    timestamp: z.ZodString;
    requestId: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, z.objectUtil.addQuestionMarks<z.baseObjectOutputType<{
    success: z.ZodBoolean;
    data: z.ZodOptional<T>;
    error: z.ZodOptional<z.ZodObject<{
        code: z.ZodString;
        message: z.ZodString;
        details: z.ZodOptional<z.ZodAny>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        message: string;
        details?: any;
    }, {
        code: string;
        message: string;
        details?: any;
    }>>;
    timestamp: z.ZodString;
    requestId: z.ZodOptional<z.ZodString>;
}>, any> extends infer T_1 ? { [k in keyof T_1]: T_1[k]; } : never, z.baseObjectInputType<{
    success: z.ZodBoolean;
    data: z.ZodOptional<T>;
    error: z.ZodOptional<z.ZodObject<{
        code: z.ZodString;
        message: z.ZodString;
        details: z.ZodOptional<z.ZodAny>;
    }, "strip", z.ZodTypeAny, {
        code: string;
        message: string;
        details?: any;
    }, {
        code: string;
        message: string;
        details?: any;
    }>>;
    timestamp: z.ZodString;
    requestId: z.ZodOptional<z.ZodString>;
}> extends infer T_2 ? { [k_1 in keyof T_2]: T_2[k_1]; } : never>;
export type ApiResponse<T> = {
    success: boolean;
    data?: T;
    error?: {
        code: string;
        message: string;
        details?: any;
    };
    timestamp: string;
    requestId?: string;
};
//# sourceMappingURL=shared-schemas.d.ts.map