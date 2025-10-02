export type CarrierDocumentType = 'label' | 'manifest' | 'invoice';
export interface CarrierDocumentProps {
    readonly documentId?: string;
    readonly tenantId: string;
    readonly carrierId: string;
    readonly type: CarrierDocumentType;
    readonly reference: string;
    readonly payload: Record<string, unknown>;
    readonly createdAt?: Date;
}
export declare class CarrierDocument {
    readonly documentId: string;
    readonly tenantId: string;
    readonly carrierId: string;
    readonly type: CarrierDocumentType;
    readonly reference: string;
    readonly payload: Record<string, unknown>;
    readonly createdAt: Date;
    private constructor();
    static create(props: CarrierDocumentProps): CarrierDocument;
}
//# sourceMappingURL=carrier-document.d.ts.map