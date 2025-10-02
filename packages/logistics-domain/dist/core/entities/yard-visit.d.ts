import { TimeWindow } from '../value-objects/time-window';
export type YardStatus = 'scheduled' | 'checked_in' | 'at_dock' | 'checked_out' | 'no_show';
export interface YardVisitProps {
    readonly visitId?: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly gate: string;
    readonly dock?: string;
    readonly scheduledWindow?: {
        from: Date;
        to: Date;
    };
    readonly status?: YardStatus;
    readonly checkinAt?: Date;
    readonly checkoutAt?: Date;
}
export declare class YardVisit {
    readonly visitId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly gate: string;
    readonly dock?: string;
    readonly scheduledWindow?: TimeWindow;
    readonly checkinAt?: Date;
    readonly checkoutAt?: Date;
    private _status;
    private constructor();
    static create(props: YardVisitProps): YardVisit;
    get status(): YardStatus;
    updateStatus(status: YardStatus): void;
}
//# sourceMappingURL=yard-visit.d.ts.map