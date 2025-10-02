export interface EmissionFactorDetail {
    readonly factor: string;
    readonly value: number;
    readonly unit: string;
}
export interface EmissionRecordProps {
    readonly emissionId?: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly co2eKg: number;
    readonly method: string;
    readonly factors?: EmissionFactorDetail[];
    readonly calculatedAt?: Date;
}
export declare class EmissionRecord {
    readonly emissionId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly co2eKg: number;
    readonly method: string;
    readonly factors: EmissionFactorDetail[];
    readonly calculatedAt: Date;
    private constructor();
    static create(props: EmissionRecordProps): EmissionRecord;
}
//# sourceMappingURL=emission-record.d.ts.map