import { z } from 'zod';
export declare const ContractPositionCubeSchema: z.ZodObject<{
    tenantId: z.ZodString;
    commodity: z.ZodString;
    month: z.ZodString;
    shortPosition: z.ZodNumber;
    longPosition: z.ZodNumber;
    netPosition: z.ZodNumber;
    hedgingRatio: z.ZodOptional<z.ZodNumber>;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    commodity: string;
    month: string;
    shortPosition: number;
    longPosition: number;
    netPosition: number;
    lastUpdated: string;
    hedgingRatio?: number | undefined;
}, {
    tenantId: string;
    commodity: string;
    month: string;
    shortPosition: number;
    longPosition: number;
    netPosition: number;
    lastUpdated: string;
    hedgingRatio?: number | undefined;
}>;
export declare const WeighingVolumeCubeSchema: z.ZodObject<{
    tenantId: z.ZodString;
    commodity: z.ZodString;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    period: z.ZodString;
    totalWeight: z.ZodNumber;
    totalTickets: z.ZodNumber;
    avgWeight: z.ZodNumber;
    withinTolerance: z.ZodNumber;
    outsideTolerance: z.ZodNumber;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalWeight: number;
    totalTickets: number;
    avgWeight: number;
    withinTolerance: number;
    outsideTolerance: number;
    customerId?: string | undefined;
    siteId?: string | undefined;
}, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalWeight: number;
    totalTickets: number;
    avgWeight: number;
    withinTolerance: number;
    outsideTolerance: number;
    customerId?: string | undefined;
    siteId?: string | undefined;
}>;
export declare const QualityCubeSchema: z.ZodObject<{
    tenantId: z.ZodString;
    commodity: z.ZodString;
    period: z.ZodString;
    totalSamples: z.ZodNumber;
    passedSamples: z.ZodNumber;
    failedSamples: z.ZodNumber;
    passRate: z.ZodNumber;
    failureRate: z.ZodNumber;
    avgMoisture: z.ZodOptional<z.ZodNumber>;
    avgProtein: z.ZodOptional<z.ZodNumber>;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalSamples: number;
    passedSamples: number;
    failedSamples: number;
    passRate: number;
    failureRate: number;
    avgMoisture?: number | undefined;
    avgProtein?: number | undefined;
}, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalSamples: number;
    passedSamples: number;
    failedSamples: number;
    passRate: number;
    failureRate: number;
    avgMoisture?: number | undefined;
    avgProtein?: number | undefined;
}>;
export declare const RegulatoryCubeSchema: z.ZodObject<{
    tenantId: z.ZodString;
    commodity: z.ZodString;
    labelType: z.ZodString;
    period: z.ZodString;
    totalEligible: z.ZodNumber;
    totalIneligible: z.ZodNumber;
    eligibilityRate: z.ZodNumber;
    ineligibilityRate: z.ZodNumber;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    labelType: string;
    totalEligible: number;
    totalIneligible: number;
    eligibilityRate: number;
    ineligibilityRate: number;
}, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    labelType: string;
    totalEligible: number;
    totalIneligible: number;
    eligibilityRate: number;
    ineligibilityRate: number;
}>;
export declare const FinanceCubeSchema: z.ZodObject<{
    tenantId: z.ZodString;
    commodity: z.ZodString;
    customerId: z.ZodOptional<z.ZodString>;
    period: z.ZodString;
    totalRevenue: z.ZodNumber;
    totalCost: z.ZodNumber;
    grossMargin: z.ZodNumber;
    marginPercentage: z.ZodNumber;
    outstandingInvoices: z.ZodNumber;
    overdueInvoices: z.ZodNumber;
    lastUpdated: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalRevenue: number;
    totalCost: number;
    grossMargin: number;
    marginPercentage: number;
    outstandingInvoices: number;
    overdueInvoices: number;
    customerId?: string | undefined;
}, {
    tenantId: string;
    commodity: string;
    lastUpdated: string;
    period: string;
    totalRevenue: number;
    totalCost: number;
    grossMargin: number;
    marginPercentage: number;
    outstandingInvoices: number;
    overdueInvoices: number;
    customerId?: string | undefined;
}>;
export declare const CubeQueryBaseSchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const ContractPositionQuerySchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
} & {
    month: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    month?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    commodity?: string | undefined;
    month?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const ContractPositionResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        tenantId: z.ZodString;
        commodity: z.ZodString;
        month: z.ZodString;
        shortPosition: z.ZodNumber;
        longPosition: z.ZodNumber;
        netPosition: z.ZodNumber;
        hedgingRatio: z.ZodOptional<z.ZodNumber>;
        lastUpdated: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        commodity: string;
        month: string;
        shortPosition: number;
        longPosition: number;
        netPosition: number;
        lastUpdated: string;
        hedgingRatio?: number | undefined;
    }, {
        tenantId: string;
        commodity: string;
        month: string;
        shortPosition: number;
        longPosition: number;
        netPosition: number;
        lastUpdated: string;
        hedgingRatio?: number | undefined;
    }>, "many">;
    summary: z.ZodOptional<z.ZodObject<{
        totalShort: z.ZodNumber;
        totalLong: z.ZodNumber;
        netExposure: z.ZodNumber;
        avgHedgingRatio: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        totalShort: number;
        totalLong: number;
        netExposure: number;
        avgHedgingRatio?: number | undefined;
    }, {
        totalShort: number;
        totalLong: number;
        netExposure: number;
        avgHedgingRatio?: number | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    data: {
        tenantId: string;
        commodity: string;
        month: string;
        shortPosition: number;
        longPosition: number;
        netPosition: number;
        lastUpdated: string;
        hedgingRatio?: number | undefined;
    }[];
    summary?: {
        totalShort: number;
        totalLong: number;
        netExposure: number;
        avgHedgingRatio?: number | undefined;
    } | undefined;
}, {
    data: {
        tenantId: string;
        commodity: string;
        month: string;
        shortPosition: number;
        longPosition: number;
        netPosition: number;
        lastUpdated: string;
        hedgingRatio?: number | undefined;
    }[];
    summary?: {
        totalShort: number;
        totalLong: number;
        netExposure: number;
        avgHedgingRatio?: number | undefined;
    } | undefined;
}>;
export declare const WeighingVolumeQuerySchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
} & {
    period: z.ZodOptional<z.ZodString>;
    groupBy: z.ZodDefault<z.ZodEnum<["day", "week", "month"]>>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    groupBy: "month" | "day" | "week";
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    groupBy?: "month" | "day" | "week" | undefined;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const WeighingVolumeResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        tenantId: z.ZodString;
        commodity: z.ZodString;
        customerId: z.ZodOptional<z.ZodString>;
        siteId: z.ZodOptional<z.ZodString>;
        period: z.ZodString;
        totalWeight: z.ZodNumber;
        totalTickets: z.ZodNumber;
        avgWeight: z.ZodNumber;
        withinTolerance: z.ZodNumber;
        outsideTolerance: z.ZodNumber;
        lastUpdated: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalWeight: number;
        totalTickets: number;
        avgWeight: number;
        withinTolerance: number;
        outsideTolerance: number;
        customerId?: string | undefined;
        siteId?: string | undefined;
    }, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalWeight: number;
        totalTickets: number;
        avgWeight: number;
        withinTolerance: number;
        outsideTolerance: number;
        customerId?: string | undefined;
        siteId?: string | undefined;
    }>, "many">;
    summary: z.ZodOptional<z.ZodObject<{
        totalWeight: z.ZodNumber;
        totalTickets: z.ZodNumber;
        avgWeightPerTicket: z.ZodNumber;
        overallToleranceRate: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        totalWeight: number;
        totalTickets: number;
        avgWeightPerTicket: number;
        overallToleranceRate: number;
    }, {
        totalWeight: number;
        totalTickets: number;
        avgWeightPerTicket: number;
        overallToleranceRate: number;
    }>>;
}, "strip", z.ZodTypeAny, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalWeight: number;
        totalTickets: number;
        avgWeight: number;
        withinTolerance: number;
        outsideTolerance: number;
        customerId?: string | undefined;
        siteId?: string | undefined;
    }[];
    summary?: {
        totalWeight: number;
        totalTickets: number;
        avgWeightPerTicket: number;
        overallToleranceRate: number;
    } | undefined;
}, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalWeight: number;
        totalTickets: number;
        avgWeight: number;
        withinTolerance: number;
        outsideTolerance: number;
        customerId?: string | undefined;
        siteId?: string | undefined;
    }[];
    summary?: {
        totalWeight: number;
        totalTickets: number;
        avgWeightPerTicket: number;
        overallToleranceRate: number;
    } | undefined;
}>;
export declare const QualityQuerySchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
} & {
    period: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const QualityResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        tenantId: z.ZodString;
        commodity: z.ZodString;
        period: z.ZodString;
        totalSamples: z.ZodNumber;
        passedSamples: z.ZodNumber;
        failedSamples: z.ZodNumber;
        passRate: z.ZodNumber;
        failureRate: z.ZodNumber;
        avgMoisture: z.ZodOptional<z.ZodNumber>;
        avgProtein: z.ZodOptional<z.ZodNumber>;
        lastUpdated: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalSamples: number;
        passedSamples: number;
        failedSamples: number;
        passRate: number;
        failureRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalSamples: number;
        passedSamples: number;
        failedSamples: number;
        passRate: number;
        failureRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }>, "many">;
    summary: z.ZodOptional<z.ZodObject<{
        totalSamples: z.ZodNumber;
        overallPassRate: z.ZodNumber;
        avgMoisture: z.ZodOptional<z.ZodNumber>;
        avgProtein: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        totalSamples: number;
        overallPassRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }, {
        totalSamples: number;
        overallPassRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalSamples: number;
        passedSamples: number;
        failedSamples: number;
        passRate: number;
        failureRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }[];
    summary?: {
        totalSamples: number;
        overallPassRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    } | undefined;
}, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalSamples: number;
        passedSamples: number;
        failedSamples: number;
        passRate: number;
        failureRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    }[];
    summary?: {
        totalSamples: number;
        overallPassRate: number;
        avgMoisture?: number | undefined;
        avgProtein?: number | undefined;
    } | undefined;
}>;
export declare const RegulatoryQuerySchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
} & {
    labelType: z.ZodOptional<z.ZodString>;
    period: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    labelType?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    labelType?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const RegulatoryResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        tenantId: z.ZodString;
        commodity: z.ZodString;
        labelType: z.ZodString;
        period: z.ZodString;
        totalEligible: z.ZodNumber;
        totalIneligible: z.ZodNumber;
        eligibilityRate: z.ZodNumber;
        ineligibilityRate: z.ZodNumber;
        lastUpdated: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        labelType: string;
        totalEligible: number;
        totalIneligible: number;
        eligibilityRate: number;
        ineligibilityRate: number;
    }, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        labelType: string;
        totalEligible: number;
        totalIneligible: number;
        eligibilityRate: number;
        ineligibilityRate: number;
    }>, "many">;
    summary: z.ZodOptional<z.ZodObject<{
        totalEligible: z.ZodNumber;
        totalIneligible: z.ZodNumber;
        overallEligibilityRate: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        totalEligible: number;
        totalIneligible: number;
        overallEligibilityRate: number;
    }, {
        totalEligible: number;
        totalIneligible: number;
        overallEligibilityRate: number;
    }>>;
}, "strip", z.ZodTypeAny, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        labelType: string;
        totalEligible: number;
        totalIneligible: number;
        eligibilityRate: number;
        ineligibilityRate: number;
    }[];
    summary?: {
        totalEligible: number;
        totalIneligible: number;
        overallEligibilityRate: number;
    } | undefined;
}, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        labelType: string;
        totalEligible: number;
        totalIneligible: number;
        eligibilityRate: number;
        ineligibilityRate: number;
    }[];
    summary?: {
        totalEligible: number;
        totalIneligible: number;
        overallEligibilityRate: number;
    } | undefined;
}>;
export declare const FinanceQuerySchema: z.ZodObject<{
    tenantId: z.ZodString;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
} & {
    period: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    page: number;
    pageSize: number;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
}, {
    tenantId: string;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    period?: string | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
}>;
export declare const FinanceResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        tenantId: z.ZodString;
        commodity: z.ZodString;
        customerId: z.ZodOptional<z.ZodString>;
        period: z.ZodString;
        totalRevenue: z.ZodNumber;
        totalCost: z.ZodNumber;
        grossMargin: z.ZodNumber;
        marginPercentage: z.ZodNumber;
        outstandingInvoices: z.ZodNumber;
        overdueInvoices: z.ZodNumber;
        lastUpdated: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalRevenue: number;
        totalCost: number;
        grossMargin: number;
        marginPercentage: number;
        outstandingInvoices: number;
        overdueInvoices: number;
        customerId?: string | undefined;
    }, {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalRevenue: number;
        totalCost: number;
        grossMargin: number;
        marginPercentage: number;
        outstandingInvoices: number;
        overdueInvoices: number;
        customerId?: string | undefined;
    }>, "many">;
    summary: z.ZodOptional<z.ZodObject<{
        totalRevenue: z.ZodNumber;
        totalCost: z.ZodNumber;
        totalMargin: z.ZodNumber;
        avgMarginPercentage: z.ZodNumber;
        totalOutstanding: z.ZodNumber;
        totalOverdue: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        totalRevenue: number;
        totalCost: number;
        totalMargin: number;
        avgMarginPercentage: number;
        totalOutstanding: number;
        totalOverdue: number;
    }, {
        totalRevenue: number;
        totalCost: number;
        totalMargin: number;
        avgMarginPercentage: number;
        totalOutstanding: number;
        totalOverdue: number;
    }>>;
}, "strip", z.ZodTypeAny, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalRevenue: number;
        totalCost: number;
        grossMargin: number;
        marginPercentage: number;
        outstandingInvoices: number;
        overdueInvoices: number;
        customerId?: string | undefined;
    }[];
    summary?: {
        totalRevenue: number;
        totalCost: number;
        totalMargin: number;
        avgMarginPercentage: number;
        totalOutstanding: number;
        totalOverdue: number;
    } | undefined;
}, {
    data: {
        tenantId: string;
        commodity: string;
        lastUpdated: string;
        period: string;
        totalRevenue: number;
        totalCost: number;
        grossMargin: number;
        marginPercentage: number;
        outstandingInvoices: number;
        overdueInvoices: number;
        customerId?: string | undefined;
    }[];
    summary?: {
        totalRevenue: number;
        totalCost: number;
        totalMargin: number;
        avgMarginPercentage: number;
        totalOutstanding: number;
        totalOverdue: number;
    } | undefined;
}>;
export declare const CubeRefreshRequestSchema: z.ZodObject<{
    cubeNames: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    force: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    force: boolean;
    cubeNames?: string[] | undefined;
}, {
    cubeNames?: string[] | undefined;
    force?: boolean | undefined;
}>;
export declare const CubeRefreshResultSchema: z.ZodObject<{
    cubeName: z.ZodString;
    success: z.ZodBoolean;
    recordCount: z.ZodOptional<z.ZodNumber>;
    executionTimeMs: z.ZodNumber;
    error: z.ZodOptional<z.ZodString>;
    refreshedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    cubeName: string;
    success: boolean;
    executionTimeMs: number;
    refreshedAt: string;
    recordCount?: number | undefined;
    error?: string | undefined;
}, {
    cubeName: string;
    success: boolean;
    executionTimeMs: number;
    refreshedAt: string;
    recordCount?: number | undefined;
    error?: string | undefined;
}>;
export declare const BulkCubeRefreshResponseSchema: z.ZodObject<{
    totalRequested: z.ZodNumber;
    successful: z.ZodNumber;
    failed: z.ZodNumber;
    results: z.ZodArray<z.ZodObject<{
        cubeName: z.ZodString;
        success: z.ZodBoolean;
        recordCount: z.ZodOptional<z.ZodNumber>;
        executionTimeMs: z.ZodNumber;
        error: z.ZodOptional<z.ZodString>;
        refreshedAt: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        cubeName: string;
        success: boolean;
        executionTimeMs: number;
        refreshedAt: string;
        recordCount?: number | undefined;
        error?: string | undefined;
    }, {
        cubeName: string;
        success: boolean;
        executionTimeMs: number;
        refreshedAt: string;
        recordCount?: number | undefined;
        error?: string | undefined;
    }>, "many">;
    totalExecutionTimeMs: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    failed: number;
    totalRequested: number;
    successful: number;
    results: {
        cubeName: string;
        success: boolean;
        executionTimeMs: number;
        refreshedAt: string;
        recordCount?: number | undefined;
        error?: string | undefined;
    }[];
    totalExecutionTimeMs: number;
}, {
    failed: number;
    totalRequested: number;
    successful: number;
    results: {
        cubeName: string;
        success: boolean;
        executionTimeMs: number;
        refreshedAt: string;
        recordCount?: number | undefined;
        error?: string | undefined;
    }[];
    totalExecutionTimeMs: number;
}>;
//# sourceMappingURL=cube-contracts.d.ts.map