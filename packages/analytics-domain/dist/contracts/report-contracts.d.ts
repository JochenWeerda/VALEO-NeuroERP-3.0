import { z } from 'zod';
export declare const ReportTypeSchema: z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>;
export declare const ReportFormatSchema: z.ZodEnum<["json", "csv", "excel", "pdf"]>;
export declare const ReportParametersSchema: z.ZodObject<{
    tenantId: z.ZodString;
    dateFrom: z.ZodOptional<z.ZodString>;
    dateTo: z.ZodOptional<z.ZodString>;
    commodity: z.ZodOptional<z.ZodString>;
    customerId: z.ZodOptional<z.ZodString>;
    supplierId: z.ZodOptional<z.ZodString>;
    siteId: z.ZodOptional<z.ZodString>;
    status: z.ZodOptional<z.ZodString>;
    filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    filters?: Record<string, any> | undefined;
    status?: string | undefined;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    supplierId?: string | undefined;
    dateFrom?: string | undefined;
    dateTo?: string | undefined;
}, {
    tenantId: string;
    filters?: Record<string, any> | undefined;
    status?: string | undefined;
    commodity?: string | undefined;
    customerId?: string | undefined;
    siteId?: string | undefined;
    supplierId?: string | undefined;
    dateFrom?: string | undefined;
    dateTo?: string | undefined;
}>;
export declare const ReportMetadataSchema: z.ZodObject<{
    totalRecords: z.ZodOptional<z.ZodNumber>;
    executionTimeMs: z.ZodOptional<z.ZodNumber>;
    dataSource: z.ZodOptional<z.ZodString>;
    generatedBy: z.ZodOptional<z.ZodString>;
    checksum: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    executionTimeMs?: number | undefined;
    dataSource?: string | undefined;
    totalRecords?: number | undefined;
    generatedBy?: string | undefined;
    checksum?: string | undefined;
}, {
    executionTimeMs?: number | undefined;
    dataSource?: string | undefined;
    totalRecords?: number | undefined;
    generatedBy?: string | undefined;
    checksum?: string | undefined;
}>;
export declare const GenerateReportRequestSchema: z.ZodObject<{
    type: z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>;
    parameters: z.ZodObject<{
        tenantId: z.ZodString;
        dateFrom: z.ZodOptional<z.ZodString>;
        dateTo: z.ZodOptional<z.ZodString>;
        commodity: z.ZodOptional<z.ZodString>;
        customerId: z.ZodOptional<z.ZodString>;
        supplierId: z.ZodOptional<z.ZodString>;
        siteId: z.ZodOptional<z.ZodString>;
        status: z.ZodOptional<z.ZodString>;
        filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    }, {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    }>;
    format: z.ZodDefault<z.ZodEnum<["json", "csv", "excel", "pdf"]>>;
}, "strip", z.ZodTypeAny, {
    type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
    parameters: {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    };
    format: "json" | "csv" | "excel" | "pdf";
}, {
    type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
    parameters: {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    };
    format?: "json" | "csv" | "excel" | "pdf" | undefined;
}>;
export declare const ReportResponseSchema: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    type: z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>;
    parameters: z.ZodObject<{
        tenantId: z.ZodString;
        dateFrom: z.ZodOptional<z.ZodString>;
        dateTo: z.ZodOptional<z.ZodString>;
        commodity: z.ZodOptional<z.ZodString>;
        customerId: z.ZodOptional<z.ZodString>;
        supplierId: z.ZodOptional<z.ZodString>;
        siteId: z.ZodOptional<z.ZodString>;
        status: z.ZodOptional<z.ZodString>;
        filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
    }, "strip", z.ZodTypeAny, {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    }, {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    }>;
    generatedAt: z.ZodString;
    uri: z.ZodOptional<z.ZodString>;
    format: z.ZodEnum<["json", "csv", "excel", "pdf"]>;
    metadata: z.ZodOptional<z.ZodObject<{
        totalRecords: z.ZodOptional<z.ZodNumber>;
        executionTimeMs: z.ZodOptional<z.ZodNumber>;
        dataSource: z.ZodOptional<z.ZodString>;
        generatedBy: z.ZodOptional<z.ZodString>;
        checksum: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        executionTimeMs?: number | undefined;
        dataSource?: string | undefined;
        totalRecords?: number | undefined;
        generatedBy?: string | undefined;
        checksum?: string | undefined;
    }, {
        executionTimeMs?: number | undefined;
        dataSource?: string | undefined;
        totalRecords?: number | undefined;
        generatedBy?: string | undefined;
        checksum?: string | undefined;
    }>>;
    version: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    id: string;
    tenantId: string;
    type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
    version: number;
    parameters: {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    };
    generatedAt: string;
    format: "json" | "csv" | "excel" | "pdf";
    metadata?: {
        executionTimeMs?: number | undefined;
        dataSource?: string | undefined;
        totalRecords?: number | undefined;
        generatedBy?: string | undefined;
        checksum?: string | undefined;
    } | undefined;
    uri?: string | undefined;
}, {
    id: string;
    tenantId: string;
    type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
    version: number;
    parameters: {
        tenantId: string;
        filters?: Record<string, any> | undefined;
        status?: string | undefined;
        commodity?: string | undefined;
        customerId?: string | undefined;
        siteId?: string | undefined;
        supplierId?: string | undefined;
        dateFrom?: string | undefined;
        dateTo?: string | undefined;
    };
    generatedAt: string;
    format: "json" | "csv" | "excel" | "pdf";
    metadata?: {
        executionTimeMs?: number | undefined;
        dataSource?: string | undefined;
        totalRecords?: number | undefined;
        generatedBy?: string | undefined;
        checksum?: string | undefined;
    } | undefined;
    uri?: string | undefined;
}>;
export declare const ReportQuerySchema: z.ZodObject<{
    type: z.ZodOptional<z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>>;
    from: z.ZodOptional<z.ZodString>;
    to: z.ZodOptional<z.ZodString>;
    format: z.ZodOptional<z.ZodEnum<["json", "csv", "excel", "pdf"]>>;
    page: z.ZodDefault<z.ZodNumber>;
    pageSize: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    page: number;
    pageSize: number;
    type?: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom" | undefined;
    from?: string | undefined;
    to?: string | undefined;
    format?: "json" | "csv" | "excel" | "pdf" | undefined;
}, {
    type?: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom" | undefined;
    from?: string | undefined;
    to?: string | undefined;
    page?: number | undefined;
    pageSize?: number | undefined;
    format?: "json" | "csv" | "excel" | "pdf" | undefined;
}>;
export declare const ReportListResponseSchema: z.ZodObject<{
    data: z.ZodArray<z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        type: z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>;
        parameters: z.ZodObject<{
            tenantId: z.ZodString;
            dateFrom: z.ZodOptional<z.ZodString>;
            dateTo: z.ZodOptional<z.ZodString>;
            commodity: z.ZodOptional<z.ZodString>;
            customerId: z.ZodOptional<z.ZodString>;
            supplierId: z.ZodOptional<z.ZodString>;
            siteId: z.ZodOptional<z.ZodString>;
            status: z.ZodOptional<z.ZodString>;
            filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
        }, "strip", z.ZodTypeAny, {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        }, {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        }>;
        generatedAt: z.ZodString;
        uri: z.ZodOptional<z.ZodString>;
        format: z.ZodEnum<["json", "csv", "excel", "pdf"]>;
        metadata: z.ZodOptional<z.ZodObject<{
            totalRecords: z.ZodOptional<z.ZodNumber>;
            executionTimeMs: z.ZodOptional<z.ZodNumber>;
            dataSource: z.ZodOptional<z.ZodString>;
            generatedBy: z.ZodOptional<z.ZodString>;
            checksum: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        }, {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        }>>;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    }, {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
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
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
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
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    }[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}>;
export declare const ReportContentResponseSchema: z.ZodObject<{
    report: z.ZodObject<{
        id: z.ZodString;
        tenantId: z.ZodString;
        type: z.ZodEnum<["Contracts", "Inventory", "Weighing", "Finance", "Quality", "Production", "Regulatory", "Custom"]>;
        parameters: z.ZodObject<{
            tenantId: z.ZodString;
            dateFrom: z.ZodOptional<z.ZodString>;
            dateTo: z.ZodOptional<z.ZodString>;
            commodity: z.ZodOptional<z.ZodString>;
            customerId: z.ZodOptional<z.ZodString>;
            supplierId: z.ZodOptional<z.ZodString>;
            siteId: z.ZodOptional<z.ZodString>;
            status: z.ZodOptional<z.ZodString>;
            filters: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodAny>>;
        }, "strip", z.ZodTypeAny, {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        }, {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        }>;
        generatedAt: z.ZodString;
        uri: z.ZodOptional<z.ZodString>;
        format: z.ZodEnum<["json", "csv", "excel", "pdf"]>;
        metadata: z.ZodOptional<z.ZodObject<{
            totalRecords: z.ZodOptional<z.ZodNumber>;
            executionTimeMs: z.ZodOptional<z.ZodNumber>;
            dataSource: z.ZodOptional<z.ZodString>;
            generatedBy: z.ZodOptional<z.ZodString>;
            checksum: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        }, {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        }>>;
        version: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    }, {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    }>;
    content: z.ZodAny;
    contentType: z.ZodString;
    contentLength: z.ZodNumber;
}, "strip", z.ZodTypeAny, {
    report: {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    };
    contentType: string;
    contentLength: number;
    content?: any;
}, {
    report: {
        id: string;
        tenantId: string;
        type: "Contracts" | "Inventory" | "Weighing" | "Finance" | "Quality" | "Production" | "Regulatory" | "Custom";
        version: number;
        parameters: {
            tenantId: string;
            filters?: Record<string, any> | undefined;
            status?: string | undefined;
            commodity?: string | undefined;
            customerId?: string | undefined;
            siteId?: string | undefined;
            supplierId?: string | undefined;
            dateFrom?: string | undefined;
            dateTo?: string | undefined;
        };
        generatedAt: string;
        format: "json" | "csv" | "excel" | "pdf";
        metadata?: {
            executionTimeMs?: number | undefined;
            dataSource?: string | undefined;
            totalRecords?: number | undefined;
            generatedBy?: string | undefined;
            checksum?: string | undefined;
        } | undefined;
        uri?: string | undefined;
    };
    contentType: string;
    contentLength: number;
    content?: any;
}>;
export declare const ReportGenerationStatusSchema: z.ZodEnum<["pending", "processing", "completed", "failed"]>;
export declare const ReportGenerationResultSchema: z.ZodObject<{
    reportId: z.ZodString;
    status: z.ZodEnum<["pending", "processing", "completed", "failed"]>;
    progress: z.ZodOptional<z.ZodNumber>;
    message: z.ZodOptional<z.ZodString>;
    uri: z.ZodOptional<z.ZodString>;
    error: z.ZodOptional<z.ZodString>;
    executionTimeMs: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    status: "completed" | "failed" | "pending" | "processing";
    reportId: string;
    message?: string | undefined;
    executionTimeMs?: number | undefined;
    error?: string | undefined;
    uri?: string | undefined;
    progress?: number | undefined;
}, {
    status: "completed" | "failed" | "pending" | "processing";
    reportId: string;
    message?: string | undefined;
    executionTimeMs?: number | undefined;
    error?: string | undefined;
    uri?: string | undefined;
    progress?: number | undefined;
}>;
//# sourceMappingURL=report-contracts.d.ts.map