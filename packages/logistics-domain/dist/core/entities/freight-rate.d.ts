export interface FreightSurcharge {
    readonly type: string;
    readonly amount: number;
}
export interface FreightRateProps {
    readonly rateId?: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly currency: string;
    readonly baseAmount: number;
    readonly surcharges?: FreightSurcharge[];
    readonly explain?: string;
    readonly calculatedAt?: Date;
}
export declare class FreightRate {
    readonly rateId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly currency: string;
    readonly baseAmount: number;
    readonly surcharges: FreightSurcharge[];
    readonly totalAmount: number;
    readonly explain?: string;
    readonly calculatedAt: Date;
    private constructor();
    static create(props: FreightRateProps): FreightRate;
}
//# sourceMappingURL=freight-rate.d.ts.map