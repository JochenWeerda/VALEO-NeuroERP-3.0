import { z } from 'zod';
export declare const ConditionTypeEnum: z.ZodEnum<["Discount", "Markup", "Rebate", "Surcharge"]>;
export type ConditionType = z.infer<typeof ConditionTypeEnum>;
export declare const ConditionScopeEnum: z.ZodEnum<["SKU", "Commodity", "All"]>;
export type ConditionScope = z.infer<typeof ConditionScopeEnum>;
export declare const ConditionMethodEnum: z.ZodEnum<["ABS", "PCT"]>;
export type ConditionMethod = z.infer<typeof ConditionMethodEnum>;
export declare const ChannelEnum: z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI", "All"]>;
export type Channel = z.infer<typeof ChannelEnum>;
export declare const ConditionRuleSchema: z.ZodObject<{
    ruleId: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["Discount", "Markup", "Rebate", "Surcharge"]>;
    scope: z.ZodEnum<["SKU", "Commodity", "All"]>;
    selector: z.ZodOptional<z.ZodObject<{
        sku: z.ZodOptional<z.ZodString>;
        commodity: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        sku?: string | undefined;
        commodity?: string | undefined;
    }, {
        sku?: string | undefined;
        commodity?: string | undefined;
    }>>;
    method: z.ZodEnum<["ABS", "PCT"]>;
    value: z.ZodNumber;
    minQty: z.ZodOptional<z.ZodNumber>;
    maxQty: z.ZodOptional<z.ZodNumber>;
    channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI", "All"]>>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodString>;
    stackable: z.ZodDefault<z.ZodBoolean>;
    description: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    value: number;
    type: "Discount" | "Markup" | "Rebate" | "Surcharge";
    scope: "SKU" | "Commodity" | "All";
    method: "ABS" | "PCT";
    stackable: boolean;
    minQty?: number | undefined;
    maxQty?: number | undefined;
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    ruleId?: string | undefined;
    selector?: {
        sku?: string | undefined;
        commodity?: string | undefined;
    } | undefined;
    channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
}, {
    value: number;
    type: "Discount" | "Markup" | "Rebate" | "Surcharge";
    scope: "SKU" | "Commodity" | "All";
    method: "ABS" | "PCT";
    minQty?: number | undefined;
    maxQty?: number | undefined;
    description?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    ruleId?: string | undefined;
    selector?: {
        sku?: string | undefined;
        commodity?: string | undefined;
    } | undefined;
    channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    stackable?: boolean | undefined;
}>;
export type ConditionRule = z.infer<typeof ConditionRuleSchema>;
export declare const ConditionSetSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    key: z.ZodString;
    keyType: z.ZodEnum<["Customer", "Segment", "Region", "PaymentTerm"]>;
    rules: z.ZodArray<z.ZodObject<{
        ruleId: z.ZodOptional<z.ZodString>;
        type: z.ZodEnum<["Discount", "Markup", "Rebate", "Surcharge"]>;
        scope: z.ZodEnum<["SKU", "Commodity", "All"]>;
        selector: z.ZodOptional<z.ZodObject<{
            sku: z.ZodOptional<z.ZodString>;
            commodity: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }>>;
        method: z.ZodEnum<["ABS", "PCT"]>;
        value: z.ZodNumber;
        minQty: z.ZodOptional<z.ZodNumber>;
        maxQty: z.ZodOptional<z.ZodNumber>;
        channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI", "All"]>>;
        validFrom: z.ZodOptional<z.ZodString>;
        validTo: z.ZodOptional<z.ZodString>;
        stackable: z.ZodDefault<z.ZodBoolean>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }>, "many">;
    priority: z.ZodDefault<z.ZodNumber>;
    conflictStrategy: z.ZodDefault<z.ZodEnum<["FirstWins", "LastWins", "MaxWins", "MinWins", "Stack"]>>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    active: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    active: boolean;
    tenantId: string;
    name: string;
    validFrom: string;
    key: string;
    keyType: "Customer" | "Segment" | "Region" | "PaymentTerm";
    rules: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }[];
    priority: number;
    conflictStrategy: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack";
    description?: string | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    key: string;
    keyType: "Customer" | "Segment" | "Region" | "PaymentTerm";
    rules: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }[];
    description?: string | undefined;
    active?: boolean | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    priority?: number | undefined;
    conflictStrategy?: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack" | undefined;
}>;
export type ConditionSet = z.infer<typeof ConditionSetSchema>;
export declare const CreateConditionSetSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    key: z.ZodString;
    keyType: z.ZodEnum<["Customer", "Segment", "Region", "PaymentTerm"]>;
    rules: z.ZodArray<z.ZodObject<{
        ruleId: z.ZodOptional<z.ZodString>;
        type: z.ZodEnum<["Discount", "Markup", "Rebate", "Surcharge"]>;
        scope: z.ZodEnum<["SKU", "Commodity", "All"]>;
        selector: z.ZodOptional<z.ZodObject<{
            sku: z.ZodOptional<z.ZodString>;
            commodity: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }>>;
        method: z.ZodEnum<["ABS", "PCT"]>;
        value: z.ZodNumber;
        minQty: z.ZodOptional<z.ZodNumber>;
        maxQty: z.ZodOptional<z.ZodNumber>;
        channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI", "All"]>>;
        validFrom: z.ZodOptional<z.ZodString>;
        validTo: z.ZodOptional<z.ZodString>;
        stackable: z.ZodDefault<z.ZodBoolean>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }>, "many">;
    priority: z.ZodDefault<z.ZodNumber>;
    conflictStrategy: z.ZodDefault<z.ZodEnum<["FirstWins", "LastWins", "MaxWins", "MinWins", "Stack"]>>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    active: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt">, "strip", z.ZodTypeAny, {
    active: boolean;
    tenantId: string;
    name: string;
    validFrom: string;
    key: string;
    keyType: "Customer" | "Segment" | "Region" | "PaymentTerm";
    rules: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }[];
    priority: number;
    conflictStrategy: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack";
    description?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    key: string;
    keyType: "Customer" | "Segment" | "Region" | "PaymentTerm";
    rules: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }[];
    description?: string | undefined;
    active?: boolean | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    priority?: number | undefined;
    conflictStrategy?: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack" | undefined;
}>;
export type CreateConditionSet = z.infer<typeof CreateConditionSetSchema>;
export declare const UpdateConditionSetSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    tenantId: z.ZodOptional<z.ZodString>;
    name: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    key: z.ZodOptional<z.ZodString>;
    keyType: z.ZodOptional<z.ZodEnum<["Customer", "Segment", "Region", "PaymentTerm"]>>;
    rules: z.ZodOptional<z.ZodArray<z.ZodObject<{
        ruleId: z.ZodOptional<z.ZodString>;
        type: z.ZodEnum<["Discount", "Markup", "Rebate", "Surcharge"]>;
        scope: z.ZodEnum<["SKU", "Commodity", "All"]>;
        selector: z.ZodOptional<z.ZodObject<{
            sku: z.ZodOptional<z.ZodString>;
            commodity: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }, {
            sku?: string | undefined;
            commodity?: string | undefined;
        }>>;
        method: z.ZodEnum<["ABS", "PCT"]>;
        value: z.ZodNumber;
        minQty: z.ZodOptional<z.ZodNumber>;
        maxQty: z.ZodOptional<z.ZodNumber>;
        channel: z.ZodOptional<z.ZodEnum<["Web", "Mobile", "BackOffice", "EDI", "All"]>>;
        validFrom: z.ZodOptional<z.ZodString>;
        validTo: z.ZodOptional<z.ZodString>;
        stackable: z.ZodDefault<z.ZodBoolean>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }, {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }>, "many">>;
    priority: z.ZodOptional<z.ZodDefault<z.ZodNumber>>;
    conflictStrategy: z.ZodOptional<z.ZodDefault<z.ZodEnum<["FirstWins", "LastWins", "MaxWins", "MinWins", "Stack"]>>>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    active: z.ZodOptional<z.ZodDefault<z.ZodBoolean>>;
    createdAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    createdBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
}, "id" | "tenantId" | "createdAt" | "createdBy">, "strip", z.ZodTypeAny, {
    description?: string | undefined;
    active?: boolean | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    key?: string | undefined;
    keyType?: "Customer" | "Segment" | "Region" | "PaymentTerm" | undefined;
    rules?: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        stackable: boolean;
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
    }[] | undefined;
    priority?: number | undefined;
    conflictStrategy?: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack" | undefined;
}, {
    description?: string | undefined;
    active?: boolean | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    key?: string | undefined;
    keyType?: "Customer" | "Segment" | "Region" | "PaymentTerm" | undefined;
    rules?: {
        value: number;
        type: "Discount" | "Markup" | "Rebate" | "Surcharge";
        scope: "SKU" | "Commodity" | "All";
        method: "ABS" | "PCT";
        minQty?: number | undefined;
        maxQty?: number | undefined;
        description?: string | undefined;
        validFrom?: string | undefined;
        validTo?: string | undefined;
        ruleId?: string | undefined;
        selector?: {
            sku?: string | undefined;
            commodity?: string | undefined;
        } | undefined;
        channel?: "All" | "Web" | "Mobile" | "BackOffice" | "EDI" | undefined;
        stackable?: boolean | undefined;
    }[] | undefined;
    priority?: number | undefined;
    conflictStrategy?: "FirstWins" | "LastWins" | "MaxWins" | "MinWins" | "Stack" | undefined;
}>;
export type UpdateConditionSet = z.infer<typeof UpdateConditionSetSchema>;
//# sourceMappingURL=condition-set.d.ts.map