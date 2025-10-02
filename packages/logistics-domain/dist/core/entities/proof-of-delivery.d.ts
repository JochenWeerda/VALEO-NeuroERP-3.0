export interface ProofOfDeliveryProps {
    readonly podId?: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly stopId: string;
    readonly signedBy: string;
    readonly capturedAt?: Date;
    readonly signatureRef?: string;
    readonly photoRefs?: string[];
    readonly scans?: string[];
    readonly exceptions?: string[];
}
export declare class ProofOfDelivery {
    readonly podId: string;
    readonly tenantId: string;
    readonly shipmentId: string;
    readonly stopId: string;
    readonly signedBy: string;
    readonly capturedAt: Date;
    readonly signatureRef?: string;
    readonly photoRefs?: string[];
    readonly scans?: string[];
    readonly exceptions?: string[];
    private constructor();
    static create(props: ProofOfDeliveryProps): ProofOfDelivery;
}
//# sourceMappingURL=proof-of-delivery.d.ts.map