export type ReportType = 'Contracts' | 'Inventory' | 'Weighing' | 'Finance' | 'Quality' | 'Production' | 'Regulatory' | 'Custom';
export type ReportFormat = 'json' | 'csv' | 'excel' | 'pdf';
export interface ReportParameters {
    tenantId: string;
    dateFrom?: Date;
    dateTo?: Date;
    commodity?: string;
    customerId?: string;
    supplierId?: string;
    siteId?: string;
    status?: string;
    filters?: Record<string, any>;
}
export interface ReportMetadata {
    totalRecords?: number;
    executionTimeMs?: number;
    dataSource?: string;
    generatedBy?: string;
    checksum?: string;
}
export declare class Report {
    readonly id: string;
    readonly tenantId: string;
    readonly type: ReportType;
    readonly parameters: ReportParameters;
    readonly generatedAt: Date;
    uri?: string | undefined;
    readonly format: ReportFormat;
    readonly metadata?: ReportMetadata | undefined;
    readonly version: number;
    constructor(id: string, tenantId: string, type: ReportType, parameters: ReportParameters, generatedAt: Date, uri?: string | undefined, format?: ReportFormat, metadata?: ReportMetadata | undefined, version?: number);
    static create(params: {
        id: string;
        tenantId: string;
        type: ReportType;
        parameters: ReportParameters;
        format?: ReportFormat;
        metadata?: ReportMetadata;
    }): Report;
    setUri(uri: string): Report;
    updateMetadata(metadata: Partial<ReportMetadata>): Report;
    isExpired(maxAgeHours?: number): boolean;
    getFileName(): string;
    toJSON(): {
        id: string;
        tenantId: string;
        type: ReportType;
        parameters: ReportParameters;
        generatedAt: string;
        uri: string | undefined;
        format: ReportFormat;
        metadata: ReportMetadata | undefined;
        version: number;
    };
}
//# sourceMappingURL=report.d.ts.map