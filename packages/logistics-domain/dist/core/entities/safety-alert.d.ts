export type SafetyAlertType = 'dangerous_goods' | 'temperature' | 'geofence' | 'weight';
export type SafetyAlertSeverity = 'info' | 'warning' | 'critical';
export interface SafetyAlertProps {
    readonly alertId?: string;
    readonly tenantId: string;
    readonly referenceId: string;
    readonly shipmentId?: string;
    readonly type: SafetyAlertType;
    readonly severity: SafetyAlertSeverity;
    readonly message: string;
    readonly detectedAt?: Date;
    readonly acknowledgedBy?: string;
    readonly acknowledgedAt?: Date;
}
export declare class SafetyAlert {
    readonly alertId: string;
    readonly tenantId: string;
    readonly referenceId: string;
    readonly shipmentId?: string;
    readonly type: SafetyAlertType;
    readonly severity: SafetyAlertSeverity;
    readonly message: string;
    readonly detectedAt: Date;
    readonly acknowledgedBy?: string;
    readonly acknowledgedAt?: Date;
    private constructor();
    static create(props: SafetyAlertProps): SafetyAlert;
    acknowledge(userId: string): SafetyAlert;
}
//# sourceMappingURL=safety-alert.d.ts.map