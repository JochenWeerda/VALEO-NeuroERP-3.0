export interface TelemetryRecordProps {
    readonly telemetryId?: string;
    readonly tenantId: string;
    readonly vehicleId: string;
    readonly recordedAt: Date;
    readonly lat: number;
    readonly lon: number;
    readonly speedKph?: number;
    readonly temperatureC?: number;
    readonly fuelLevelPercent?: number;
    readonly meta?: Record<string, unknown>;
}
export declare class TelemetryRecord {
    readonly telemetryId: string;
    readonly tenantId: string;
    readonly vehicleId: string;
    readonly recordedAt: Date;
    readonly lat: number;
    readonly lon: number;
    readonly speedKph?: number;
    readonly temperatureC?: number;
    readonly fuelLevelPercent?: number;
    readonly meta?: Record<string, unknown>;
    private constructor();
    static create(props: TelemetryRecordProps): TelemetryRecord;
}
//# sourceMappingURL=telemetry-record.d.ts.map