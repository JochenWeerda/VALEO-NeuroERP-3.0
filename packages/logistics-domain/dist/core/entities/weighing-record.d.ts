export interface WeighingRecordProps {
    readonly weighingId?: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly grossWeightKg: number;
    readonly tareWeightKg: number;
    readonly source: 'bridge' | 'sensor';
    readonly capturedAt?: Date;
}
export declare class WeighingRecord {
    readonly weighingId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly grossWeightKg: number;
    readonly tareWeightKg: number;
    readonly netWeightKg: number;
    readonly source: 'bridge' | 'sensor';
    readonly capturedAt: Date;
    private constructor();
    static create(props: WeighingRecordProps): WeighingRecord;
}
//# sourceMappingURL=weighing-record.d.ts.map