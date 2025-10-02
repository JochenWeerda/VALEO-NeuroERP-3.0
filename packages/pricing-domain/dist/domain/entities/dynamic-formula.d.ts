import { z } from 'zod';
export declare const FormulaInputSourceEnum: z.ZodEnum<["Index", "Futures", "Basis", "FX", "Custom", "Static"]>;
export type FormulaInputSource = z.infer<typeof FormulaInputSourceEnum>;
export declare const FormulaInputSchema: z.ZodObject<{
    key: z.ZodString;
    source: z.ZodEnum<["Index", "Futures", "Basis", "FX", "Custom", "Static"]>;
    sourceRef: z.ZodOptional<z.ZodString>;
    fallback: z.ZodOptional<z.ZodNumber>;
    description: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    key: string;
    source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
    description?: string | undefined;
    sourceRef?: string | undefined;
    fallback?: number | undefined;
}, {
    key: string;
    source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
    description?: string | undefined;
    sourceRef?: string | undefined;
    fallback?: number | undefined;
}>;
export type FormulaInput = z.infer<typeof FormulaInputSchema>;
export declare const RoundingConfigSchema: z.ZodObject<{
    step: z.ZodOptional<z.ZodNumber>;
    mode: z.ZodDefault<z.ZodEnum<["up", "down", "nearest"]>>;
}, "strip", z.ZodTypeAny, {
    mode: "up" | "down" | "nearest";
    step?: number | undefined;
}, {
    step?: number | undefined;
    mode?: "up" | "down" | "nearest" | undefined;
}>;
export type RoundingConfig = z.infer<typeof RoundingConfigSchema>;
export declare const PriceCapsSchema: z.ZodObject<{
    min: z.ZodOptional<z.ZodNumber>;
    max: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    min?: number | undefined;
    max?: number | undefined;
}, {
    min?: number | undefined;
    max?: number | undefined;
}>;
export type PriceCaps = z.infer<typeof PriceCapsSchema>;
export declare const DynamicFormulaSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    expression: z.ZodString;
    inputs: z.ZodArray<z.ZodObject<{
        key: z.ZodString;
        source: z.ZodEnum<["Index", "Futures", "Basis", "FX", "Custom", "Static"]>;
        sourceRef: z.ZodOptional<z.ZodString>;
        fallback: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }>, "many">;
    rounding: z.ZodOptional<z.ZodObject<{
        step: z.ZodOptional<z.ZodNumber>;
        mode: z.ZodDefault<z.ZodEnum<["up", "down", "nearest"]>>;
    }, "strip", z.ZodTypeAny, {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    }, {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    }>>;
    caps: z.ZodOptional<z.ZodObject<{
        min: z.ZodOptional<z.ZodNumber>;
        max: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        min?: number | undefined;
        max?: number | undefined;
    }, {
        min?: number | undefined;
        max?: number | undefined;
    }>>;
    sku: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    active: z.ZodDefault<z.ZodBoolean>;
    testInputs: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodNumber>>;
    expectedResult: z.ZodOptional<z.ZodNumber>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    active: boolean;
    tenantId: string;
    name: string;
    validFrom: string;
    expression: string;
    inputs: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[];
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    rounding?: {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    expression: string;
    inputs: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[];
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    active?: boolean | undefined;
    id?: string | undefined;
    validTo?: string | undefined;
    createdAt?: string | undefined;
    createdBy?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    rounding?: {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}>;
export type DynamicFormula = z.infer<typeof DynamicFormulaSchema>;
export declare const CreateDynamicFormulaSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodString>;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    expression: z.ZodString;
    inputs: z.ZodArray<z.ZodObject<{
        key: z.ZodString;
        source: z.ZodEnum<["Index", "Futures", "Basis", "FX", "Custom", "Static"]>;
        sourceRef: z.ZodOptional<z.ZodString>;
        fallback: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }>, "many">;
    rounding: z.ZodOptional<z.ZodObject<{
        step: z.ZodOptional<z.ZodNumber>;
        mode: z.ZodDefault<z.ZodEnum<["up", "down", "nearest"]>>;
    }, "strip", z.ZodTypeAny, {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    }, {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    }>>;
    caps: z.ZodOptional<z.ZodObject<{
        min: z.ZodOptional<z.ZodNumber>;
        max: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        min?: number | undefined;
        max?: number | undefined;
    }, {
        min?: number | undefined;
        max?: number | undefined;
    }>>;
    sku: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    validFrom: z.ZodString;
    validTo: z.ZodOptional<z.ZodString>;
    active: z.ZodDefault<z.ZodBoolean>;
    testInputs: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodNumber>>;
    expectedResult: z.ZodOptional<z.ZodNumber>;
    createdAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodOptional<z.ZodString>;
    updatedBy: z.ZodOptional<z.ZodString>;
}, "id" | "createdAt" | "updatedAt">, "strip", z.ZodTypeAny, {
    active: boolean;
    tenantId: string;
    name: string;
    validFrom: string;
    expression: string;
    inputs: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[];
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    rounding?: {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}, {
    tenantId: string;
    name: string;
    validFrom: string;
    expression: string;
    inputs: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[];
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    active?: boolean | undefined;
    validTo?: string | undefined;
    createdBy?: string | undefined;
    updatedBy?: string | undefined;
    rounding?: {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}>;
export type CreateDynamicFormula = z.infer<typeof CreateDynamicFormulaSchema>;
export declare const UpdateDynamicFormulaSchema: z.ZodObject<Omit<{
    id: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    tenantId: z.ZodOptional<z.ZodString>;
    name: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    expression: z.ZodOptional<z.ZodString>;
    inputs: z.ZodOptional<z.ZodArray<z.ZodObject<{
        key: z.ZodString;
        source: z.ZodEnum<["Index", "Futures", "Basis", "FX", "Custom", "Static"]>;
        sourceRef: z.ZodOptional<z.ZodString>;
        fallback: z.ZodOptional<z.ZodNumber>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }, {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }>, "many">>;
    rounding: z.ZodOptional<z.ZodOptional<z.ZodObject<{
        step: z.ZodOptional<z.ZodNumber>;
        mode: z.ZodDefault<z.ZodEnum<["up", "down", "nearest"]>>;
    }, "strip", z.ZodTypeAny, {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    }, {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    }>>>;
    caps: z.ZodOptional<z.ZodOptional<z.ZodObject<{
        min: z.ZodOptional<z.ZodNumber>;
        max: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        min?: number | undefined;
        max?: number | undefined;
    }, {
        min?: number | undefined;
        max?: number | undefined;
    }>>>;
    sku: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    commodity: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    validFrom: z.ZodOptional<z.ZodString>;
    validTo: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    active: z.ZodOptional<z.ZodDefault<z.ZodBoolean>>;
    testInputs: z.ZodOptional<z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodNumber>>>;
    expectedResult: z.ZodOptional<z.ZodOptional<z.ZodNumber>>;
    createdAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    createdBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedAt: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    updatedBy: z.ZodOptional<z.ZodOptional<z.ZodString>>;
}, "id" | "tenantId" | "createdAt" | "createdBy">, "strip", z.ZodTypeAny, {
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    active?: boolean | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    expression?: string | undefined;
    inputs?: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[] | undefined;
    rounding?: {
        mode: "up" | "down" | "nearest";
        step?: number | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}, {
    sku?: string | undefined;
    commodity?: string | undefined;
    description?: string | undefined;
    active?: boolean | undefined;
    name?: string | undefined;
    validFrom?: string | undefined;
    validTo?: string | undefined;
    updatedAt?: string | undefined;
    updatedBy?: string | undefined;
    expression?: string | undefined;
    inputs?: {
        key: string;
        source: "Index" | "Futures" | "Basis" | "FX" | "Custom" | "Static";
        description?: string | undefined;
        sourceRef?: string | undefined;
        fallback?: number | undefined;
    }[] | undefined;
    rounding?: {
        step?: number | undefined;
        mode?: "up" | "down" | "nearest" | undefined;
    } | undefined;
    caps?: {
        min?: number | undefined;
        max?: number | undefined;
    } | undefined;
    testInputs?: Record<string, number> | undefined;
    expectedResult?: number | undefined;
}>;
export type UpdateDynamicFormula = z.infer<typeof UpdateDynamicFormulaSchema>;
export declare const FormulaEvaluationResultSchema: z.ZodObject<{
    formulaId: z.ZodString;
    result: z.ZodNumber;
    inputs: z.ZodRecord<z.ZodString, z.ZodNumber>;
    expression: z.ZodString;
    cappedValue: z.ZodOptional<z.ZodNumber>;
    roundedValue: z.ZodNumber;
    calculatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    expression: string;
    inputs: Record<string, number>;
    formulaId: string;
    result: number;
    roundedValue: number;
    calculatedAt: string;
    cappedValue?: number | undefined;
}, {
    expression: string;
    inputs: Record<string, number>;
    formulaId: string;
    result: number;
    roundedValue: number;
    calculatedAt: string;
    cappedValue?: number | undefined;
}>;
export type FormulaEvaluationResult = z.infer<typeof FormulaEvaluationResultSchema>;
//# sourceMappingURL=dynamic-formula.d.ts.map