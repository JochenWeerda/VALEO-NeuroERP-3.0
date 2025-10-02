import { z } from 'zod';
export declare const KpiContextSchema: z.ZodObject<{
    commodity: z.ZodOptional<z.ZodString>;
    contract: z.ZodOptional<z.ZodString>;
    batch: z.ZodOptional<z.ZodString>;
    site: z.ZodOptional<z.ZodString>;
    customer: z.ZodOptional<z.ZodString>;
    supplier: z.ZodOptional<z.ZodString>;
    period: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    commodity?: string | undefined;
    period?: string | undefined;
    contract?: string | undefined;
    batch?: string | undefined;
    site?: string | undefined;
    customer?: string | undefined;
    supplier?: string | undefined;
}, {
    commodity?: string | undefined;
    period?: string | undefined;
    contract?: string | undefined;
    batch?: string | undefined;
    site?: string | undefined;
    customer?: string | undefined;
    supplier?: string | undefined;
}>;
export declare const KpiMetadataSchema: z.ZodObject<{
    calculationMethod: z.ZodOptional<z.ZodString>;
    dataSource: z.ZodOptional<z.ZodString>;
    lastUpdated: z.ZodOptional<z.ZodDate>;
    confidence: z.ZodOptional<z.ZodNumber>;
    unit: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    lastUpdated?: Date | undefined;
    unit?: string | undefined;
    confidence?: number | undefined;
    dataSource?: string | undefined;
    calculationMethod?: string | undefined;
}, {
    lastUpdated?: Date | undefined;
    unit?: string | undefined;
    confidence?: number | undefined;
    dataSource?: string | undefined;
    calculationMethod?: string | undefined;
}>;
export declare const CreateKpiRequestSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodString;
    value: z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>;
    unit: z.ZodString;
    context: z.ZodOptional<z.ZodObject<{
        commodity: z.ZodOptional<z.ZodString>;
        contract: z.ZodOptional<z.ZodString>;
        batch: z.ZodOptional<z.ZodString>;
        site: z.ZodOptional<z.ZodString>;
        customer: z.ZodOptional<z.ZodString>;
        supplier: z.ZodOptional<z.ZodString>;
        period: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }>>;
    metadata: z.ZodOptional<z.ZodObject<{
        calculationMethod: z.ZodOptional<z.ZodString>;
        dataSource: z.ZodOptional<z.ZodString>;
        lastUpdated: z.ZodOptional<z.ZodDate>;
        confidence: z.ZodOptional<z.ZodNumber>;
        unit: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    name: string;
    description: string;
    value: string | number | boolean;
    unit: string;
    context?: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    } | undefined;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}, {
    name: string;
    description: string;
    value: string | number | boolean;
    unit: string;
    context?: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    } | undefined;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}>;
export declare const UpdateKpiRequestSchema: z.ZodObject<{
    value: z.ZodOptional<z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>>;
    context: z.ZodOptional<z.ZodObject<{
        commodity: z.ZodOptional<z.ZodString>;
        contract: z.ZodOptional<z.ZodString>;
        batch: z.ZodOptional<z.ZodString>;
        site: z.ZodOptional<z.ZodString>;
        customer: z.ZodOptional<z.ZodString>;
        supplier: z.ZodOptional<z.ZodString>;
        period: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }>>;
    metadata: z.ZodOptional<z.ZodObject<{
        calculationMethod: z.ZodOptional<z.ZodString>;
        dataSource: z.ZodOptional<z.ZodString>;
        lastUpdated: z.ZodOptional<z.ZodDate>;
        confidence: z.ZodOptional<z.ZodNumber>;
        unit: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    value?: string | number | boolean | undefined;
    context?: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    } | undefined;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}, {
    value?: string | number | boolean | undefined;
    context?: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    } | undefined;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}>;
export declare const KpiResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodString;
    value: z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>;
    unit: z.ZodString;
    context: z.ZodObject<{
        commodity: z.ZodOptional<z.ZodString>;
        contract: z.ZodOptional<z.ZodString>;
        batch: z.ZodOptional<z.ZodString>;
        site: z.ZodOptional<z.ZodString>;
        customer: z.ZodOptional<z.ZodString>;
        supplier: z.ZodOptional<z.ZodString>;
        period: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }, {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    }>;
    calculatedAt: z.ZodString;
    metadata: z.ZodOptional<z.ZodObject<{
        calculationMethod: z.ZodOptional<z.ZodString>;
        dataSource: z.ZodOptional<z.ZodString>;
        lastUpdated: z.ZodOptional<z.ZodDate>;
        confidence: z.ZodOptional<z.ZodNumber>;
        unit: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }, {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    }>>;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    name: string;
    description: string;
    value: string | number | boolean;
    version: number;
    unit: string;
    context: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    };
    calculatedAt: string;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}, {
    id: string;
    tenantId: string;
    name: string;
    description: string;
    value: string | number | boolean;
    version: number;
    unit: string;
    context: {
        commodity?: string | undefined;
        period?: string | undefined;
        contract?: string | undefined;
        batch?: string | undefined;
        site?: string | undefined;
        customer?: string | undefined;
        supplier?: string | undefined;
    };
    calculatedAt: string;
    metadata?: {
        lastUpdated?: Date | undefined;
        unit?: string | undefined;
        confidence?: number | undefined;
        dataSource?: string | undefined;
        calculationMethod?: string | undefined;
    } | undefined;
}>;
export declare const KpiQuerySchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customer: z.ZodOptional<z.ZodString>;
    site: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    name?: string | undefined;
    commodity?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    site?: string | undefined;
    customer?: string | undefined;
}, {
    name?: string | undefined;
    commodity?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
    site?: string | undefined;
    customer?: string | undefined;
}>;
export declare const KpiListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        name: z.ZodString;
        description: z.ZodString;
        value: z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>;
        unit: z.ZodString;
        context: z.ZodObject<{
            commodity: z.ZodOptional<z.ZodString>;
            contract: z.ZodOptional<z.ZodString>;
            batch: z.ZodOptional<z.ZodString>;
            site: z.ZodOptional<z.ZodString>;
            customer: z.ZodOptional<z.ZodString>;
            supplier: z.ZodOptional<z.ZodString>;
            period: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        }, {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        }>;
        calculatedAt: z.ZodString;
        metadata: z.ZodOptional<z.ZodObject<{
            calculationMethod: z.ZodOptional<z.ZodString>;
            dataSource: z.ZodOptional<z.ZodString>;
            lastUpdated: z.ZodOptional<z.ZodDate>;
            confidence: z.ZodOptional<z.ZodNumber>;
            unit: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        }, {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        }>>;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        tenantId: string;
        name: string;
        description: string;
        value: string | number | boolean;
        version: number;
        unit: string;
        context: {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        };
        calculatedAt: string;
        metadata?: {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        } | undefined;
    }, {
        id: string;
        tenantId: string;
        name: string;
        description: string;
        value: string | number | boolean;
        version: number;
        unit: string;
        context: {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        };
        calculatedAt: string;
        metadata?: {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        } | undefined;
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
        tenantId: string;
        name: string;
        description: string;
        value: string | number | boolean;
        version: number;
        unit: string;
        context: {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        };
        calculatedAt: string;
        metadata?: {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        } | undefined;
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
        tenantId: string;
        name: string;
        description: string;
        value: string | number | boolean;
        version: number;
        unit: string;
        context: {
            commodity?: string | undefined;
            period?: string | undefined;
            contract?: string | undefined;
            batch?: string | undefined;
            site?: string | undefined;
            customer?: string | undefined;
            supplier?: string | undefined;
        };
        calculatedAt: string;
        metadata?: {
            lastUpdated?: Date | undefined;
            unit?: string | undefined;
            confidence?: number | undefined;
            dataSource?: string | undefined;
            calculationMethod?: string | undefined;
        } | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export declare const RecalculateKpisRequestSchema: z.ZodObject<{
    kpiNames: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    force: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    force: boolean;
    kpiNames?: string[] | undefined;
}, {
    force?: boolean | undefined;
    kpiNames?: string[] | undefined;
}>;
export declare const KpiCalculationResultSchema: z.ZodObject<{
    kpiId: z.ZodString;
    kpiName: z.ZodString;
    success: z.ZodBoolean;
    value: z.ZodOptional<z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>>;
    error: z.ZodOptional<z.ZodString>;
    executionTimeMs: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    success: boolean;
    executionTimeMs: number;
    kpiId: string;
    kpiName: string;
    value?: string | number | boolean | undefined;
    error?: string | undefined;
}, {
    success: boolean;
    executionTimeMs: number;
    kpiId: string;
    kpiName: string;
    value?: string | number | boolean | undefined;
    error?: string | undefined;
}>;
export declare const BulkKpiRecalculationResponseSchema: z.ZodObject<{
    totalRequested: z.ZodNumber;
    successful: z.ZodNumber;
    failed: z.ZodNumber;
    results: z.ZodArray<z.ZodObject<{
        kpiId: z.ZodString;
        kpiName: z.ZodString;
        success: z.ZodBoolean;
        value: z.ZodOptional<z.ZodUnion<[z.ZodNumber, z.ZodString, z.ZodBoolean]>>;
        error: z.ZodOptional<z.ZodString>;
        executionTimeMs: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        success: boolean;
        executionTimeMs: number;
        kpiId: string;
        kpiName: string;
        value?: string | number | boolean | undefined;
        error?: string | undefined;
    }, {
        success: boolean;
        executionTimeMs: number;
        kpiId: string;
        kpiName: string;
        value?: string | number | boolean | undefined;
        error?: string | undefined;
    }>, "many">;
    executionTimeMs: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    failed: number;
    executionTimeMs: number;
    totalRequested: number;
    successful: number;
    results: {
        success: boolean;
        executionTimeMs: number;
        kpiId: string;
        kpiName: string;
        value?: string | number | boolean | undefined;
        error?: string | undefined;
    }[];
}, {
    failed: number;
    executionTimeMs: number;
    totalRequested: number;
    successful: number;
    results: {
        success: boolean;
        executionTimeMs: number;
        kpiId: string;
        kpiName: string;
        value?: string | number | boolean | undefined;
        error?: string | undefined;
    }[];
}>;
//# sourceMappingURL=kpi-contracts.d.ts.map