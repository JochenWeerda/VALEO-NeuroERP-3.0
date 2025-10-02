export interface KPIContext {
    commodity?: string;
    contract?: string;
    batch?: string;
    site?: string;
    customer?: string;
    supplier?: string;
    period?: string;
}
export interface KPIMetadata {
    calculationMethod?: string;
    dataSource?: string;
    lastUpdated?: Date;
    confidence?: number;
    unit?: string;
}
export declare class KPI {
    readonly id: string;
    readonly tenantId: string;
    readonly name: string;
    readonly description: string;
    value: number | string | boolean;
    readonly unit: string;
    readonly context: KPIContext;
    readonly calculatedAt: Date;
    readonly metadata?: KPIMetadata | undefined;
    readonly version: number;
    constructor(id: string, tenantId: string, name: string, description: string, value: number | string | boolean, unit: string, context: KPIContext, calculatedAt: Date, metadata?: KPIMetadata | undefined, version?: number);
    static create(params: {
        id: string;
        tenantId: string;
        name: string;
        description: string;
        value: number | string | boolean;
        unit: string;
        context?: KPIContext;
        metadata?: KPIMetadata;
    }): KPI;
    updateValue(newValue: number | string | boolean): KPI;
    isExpired(maxAgeMinutes?: number): boolean;
    toJSON(): {
        id: string;
        tenantId: string;
        name: string;
        description: string;
        value: string | number | boolean;
        unit: string;
        context: KPIContext;
        calculatedAt: string;
        metadata: KPIMetadata | undefined;
        version: number;
    };
}
//# sourceMappingURL=kpi.d.ts.map