import { z } from 'zod';
declare const BusinessDaysSchema: z.ZodObject<{
    mon: z.ZodDefault<z.ZodBoolean>;
    tue: z.ZodDefault<z.ZodBoolean>;
    wed: z.ZodDefault<z.ZodBoolean>;
    thu: z.ZodDefault<z.ZodBoolean>;
    fri: z.ZodDefault<z.ZodBoolean>;
    sat: z.ZodDefault<z.ZodBoolean>;
    sun: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    mon: boolean;
    tue: boolean;
    wed: boolean;
    thu: boolean;
    fri: boolean;
    sat: boolean;
    sun: boolean;
}, {
    mon?: boolean | undefined;
    tue?: boolean | undefined;
    wed?: boolean | undefined;
    thu?: boolean | undefined;
    fri?: boolean | undefined;
    sat?: boolean | undefined;
    sun?: boolean | undefined;
}>;
declare const CreateCalendarInputSchema: z.ZodObject<{
    key: z.ZodString;
    name: z.ZodString;
    holidays: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    businessDays: z.ZodDefault<z.ZodObject<{
        mon: z.ZodDefault<z.ZodBoolean>;
        tue: z.ZodDefault<z.ZodBoolean>;
        wed: z.ZodDefault<z.ZodBoolean>;
        thu: z.ZodDefault<z.ZodBoolean>;
        fri: z.ZodDefault<z.ZodBoolean>;
        sat: z.ZodDefault<z.ZodBoolean>;
        sun: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    }, {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    name: string;
    key: string;
    holidays: string[];
    businessDays: {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    };
}, {
    name: string;
    key: string;
    holidays?: string[] | undefined;
    businessDays?: {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    } | undefined;
}>;
declare const UpdateCalendarInputSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    holidays: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    businessDays: z.ZodOptional<z.ZodObject<{
        mon: z.ZodDefault<z.ZodBoolean>;
        tue: z.ZodDefault<z.ZodBoolean>;
        wed: z.ZodDefault<z.ZodBoolean>;
        thu: z.ZodDefault<z.ZodBoolean>;
        fri: z.ZodDefault<z.ZodBoolean>;
        sat: z.ZodDefault<z.ZodBoolean>;
        sun: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    }, {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    holidays?: string[] | undefined;
    businessDays?: {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    } | undefined;
}, {
    name?: string | undefined;
    holidays?: string[] | undefined;
    businessDays?: {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    } | undefined;
}>;
declare const CalendarQuerySchema: z.ZodObject<{
    key: z.ZodOptional<z.ZodString>;
    name: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
    pageSize: z.ZodDefault<z.ZodEffects<z.ZodString, number, string>>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    name?: string | undefined;
    key?: string | undefined;
}, {
    name?: string | undefined;
    key?: string | undefined;
    page?: string | undefined;
    pageSize?: string | undefined;
}>;
declare const CalendarResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodNullable<z.ZodString>;
    key: z.ZodString;
    name: z.ZodString;
    holidays: z.ZodArray<z.ZodString, "many">;
    businessDays: z.ZodObject<{
        mon: z.ZodDefault<z.ZodBoolean>;
        tue: z.ZodDefault<z.ZodBoolean>;
        wed: z.ZodDefault<z.ZodBoolean>;
        thu: z.ZodDefault<z.ZodBoolean>;
        fri: z.ZodDefault<z.ZodBoolean>;
        sat: z.ZodDefault<z.ZodBoolean>;
        sun: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    }, {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    }>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    name: string;
    tenantId: string | null;
    version: number;
    id: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    holidays: string[];
    businessDays: {
        mon: boolean;
        tue: boolean;
        wed: boolean;
        thu: boolean;
        fri: boolean;
        sat: boolean;
        sun: boolean;
    };
}, {
    name: string;
    tenantId: string | null;
    version: number;
    id: string;
    createdAt: string;
    updatedAt: string;
    key: string;
    holidays: string[];
    businessDays: {
        mon?: boolean | undefined;
        tue?: boolean | undefined;
        wed?: boolean | undefined;
        thu?: boolean | undefined;
        fri?: boolean | undefined;
        sat?: boolean | undefined;
        sun?: boolean | undefined;
    };
}>;
declare const CalendarListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodNullable<z.ZodString>;
        key: z.ZodString;
        name: z.ZodString;
        holidays: z.ZodArray<z.ZodString, "many">;
        businessDays: z.ZodObject<{
            mon: z.ZodDefault<z.ZodBoolean>;
            tue: z.ZodDefault<z.ZodBoolean>;
            wed: z.ZodDefault<z.ZodBoolean>;
            thu: z.ZodDefault<z.ZodBoolean>;
            fri: z.ZodDefault<z.ZodBoolean>;
            sat: z.ZodDefault<z.ZodBoolean>;
            sun: z.ZodDefault<z.ZodBoolean>;
        }, "strip", z.ZodTypeAny, {
            mon: boolean;
            tue: boolean;
            wed: boolean;
            thu: boolean;
            fri: boolean;
            sat: boolean;
            sun: boolean;
        }, {
            mon?: boolean | undefined;
            tue?: boolean | undefined;
            wed?: boolean | undefined;
            thu?: boolean | undefined;
            fri?: boolean | undefined;
            sat?: boolean | undefined;
            sun?: boolean | undefined;
        }>;
        createdAt: z.ZodString;
        updatedAt: z.ZodString;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        name: string;
        tenantId: string | null;
        version: number;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        holidays: string[];
        businessDays: {
            mon: boolean;
            tue: boolean;
            wed: boolean;
            thu: boolean;
            fri: boolean;
            sat: boolean;
            sun: boolean;
        };
    }, {
        name: string;
        tenantId: string | null;
        version: number;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        holidays: string[];
        businessDays: {
            mon?: boolean | undefined;
            tue?: boolean | undefined;
            wed?: boolean | undefined;
            thu?: boolean | undefined;
            fri?: boolean | undefined;
            sat?: boolean | undefined;
            sun?: boolean | undefined;
        };
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
        name: string;
        tenantId: string | null;
        version: number;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        holidays: string[];
        businessDays: {
            mon: boolean;
            tue: boolean;
            wed: boolean;
            thu: boolean;
            fri: boolean;
            sat: boolean;
            sun: boolean;
        };
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}, {
    data: {
        name: string;
        tenantId: string | null;
        version: number;
        id: string;
        createdAt: string;
        updatedAt: string;
        key: string;
        holidays: string[];
        businessDays: {
            mon?: boolean | undefined;
            tue?: boolean | undefined;
            wed?: boolean | undefined;
            thu?: boolean | undefined;
            fri?: boolean | undefined;
            sat?: boolean | undefined;
            sun?: boolean | undefined;
        };
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export { CreateCalendarInputSchema, UpdateCalendarInputSchema, CalendarQuerySchema, CalendarResponseSchema, CalendarListResponseSchema, BusinessDaysSchema, };
//# sourceMappingURL=calendar-contracts.d.ts.map